"""Audit N04 Iteration 7-B packet-loop geometry coupling surfaces.

This audit reads native N03/E3 LGRC9V3 packet-loop telemetry and asks what is
visible before N04 boundary coupling is enabled. It does not define a movement
fixture, map the E3 route onto S0/S1, or emit movement evidence.
"""

from __future__ import annotations

import glob
import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
N03 = ROOT / "experiments/2026-05-N03-grc9v3-polarized-basin-loops"

E3_IMPORT = N04 / "outputs/e3_pulse_import_validation.json"
E3_ANIMATION = N03 / "outputs/e3_native_lgrc9v3_packet_loop_animation.json"
E3_TELEMETRY_DIR = (
    N03
    / "outputs/e3_native_lgrc9v3_packet_loop_animation"
    / "e3-native-lgrc9v3-packet-loop-animation"
    / "telemetry"
)
E3_STEPS = E3_TELEMETRY_DIR / "steps.jsonl"
E3_EVENTS = E3_TELEMETRY_DIR / "events.jsonl"
E3_CHECKPOINT_DIR = E3_TELEMETRY_DIR / "graph_checkpoints"
N04_CLASSIFIER = N04 / "outputs/movement_classifier_m0_m3_validation.json"

OUTPUT_PATH = N04 / "outputs/packet_loop_geometry_coupling_audit.json"
REPORT_PATH = N04 / "reports/packet_loop_geometry_coupling_audit.md"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


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


def _checkpoint_paths() -> list[Path]:
    return [
        Path(path)
        for path in sorted(glob.glob(str(E3_CHECKPOINT_DIR / "checkpoint-*.json")))
    ]


def _analyze_checkpoints(paths: list[Path]) -> dict[str, Any]:
    pole_coherence: dict[str, list[float]] = defaultdict(list)
    node_coherence: dict[int, list[float]] = defaultdict(list)
    pole_proper_time: dict[str, list[float]] = defaultdict(list)
    node_proper_time: dict[int, list[float]] = defaultdict(list)
    edge_delays: dict[int, set[float]] = defaultdict(set)
    edge_temporal_delays: dict[int, set[float]] = defaultdict(set)
    edge_conductance: dict[int, list[float]] = defaultdict(list)
    edge_base_conductance: dict[int, list[float]] = defaultdict(list)
    node_budget = []
    in_flight_budget = []
    total_budget = []
    budget_error = []
    topology_signatures = []
    labels = []

    for path in paths:
        checkpoint = _load_json(path)
        labels.append(checkpoint["checkpoint_label"])
        for node in checkpoint["node_records"]:
            pole = node["payload"]["pole"]
            node_id = int(node["node_id"])
            coherence = float(node["coherence"])
            proper_time = float(node["node_proper_time"])
            pole_coherence[pole].append(coherence)
            node_coherence[node_id].append(coherence)
            pole_proper_time[pole].append(proper_time)
            node_proper_time[node_id].append(proper_time)
        for edge in checkpoint["edge_records"]:
            edge_id = int(edge["edge_id"])
            edge_delays[edge_id].add(float(edge["edge_causal_delay"]))
            edge_temporal_delays[edge_id].add(float(edge["temporal_delay"]))
            edge_conductance[edge_id].append(float(edge["conductance"]))
            edge_base_conductance[edge_id].append(float(edge["base_conductance"]))

        ledger = checkpoint["family_extensions"]["lgrc9v3"]["packet_ledger"]
        node_budget.append(float(ledger["node_coherence_total"]))
        in_flight_budget.append(float(ledger["in_flight_packet_total"]))
        total_budget.append(float(ledger["conserved_budget_total"]))
        budget_error.append(abs(float(ledger["budget_error"])))
        topology_signatures.append(ledger["fixed_topology_signature"])

    pole_summary = {
        pole: {
            "min_coherence": min(values),
            "max_coherence": max(values),
            "amplitude": max(values) - min(values),
            "initial_coherence": values[0],
            "final_coherence": values[-1],
            "min_proper_time": min(pole_proper_time[pole]),
            "max_proper_time": max(pole_proper_time[pole]),
            "proper_time_span": max(pole_proper_time[pole]) - min(pole_proper_time[pole]),
        }
        for pole, values in sorted(pole_coherence.items())
    }
    node_summary = {
        str(node_id): {
            "min_coherence": min(values),
            "max_coherence": max(values),
            "amplitude": max(values) - min(values),
            "initial_coherence": values[0],
            "final_coherence": values[-1],
            "min_proper_time": min(node_proper_time[node_id]),
            "max_proper_time": max(node_proper_time[node_id]),
            "proper_time_span": max(node_proper_time[node_id])
            - min(node_proper_time[node_id]),
        }
        for node_id, values in sorted(node_coherence.items())
    }

    conductance_changed_edges = [
        edge_id
        for edge_id, values in edge_conductance.items()
        if max(values) != min(values)
    ]
    base_conductance_changed_edges = [
        edge_id
        for edge_id, values in edge_base_conductance.items()
        if max(values) != min(values)
    ]
    topology_changed = any(signature != topology_signatures[0] for signature in topology_signatures)

    return {
        "checkpoint_count": len(paths),
        "checkpoint_labels_sample": labels[:5] + labels[-5:],
        "pole_mass_oscillation": {
            "available": True,
            "pole_summary": pole_summary,
            "max_pole_amplitude": max(item["amplitude"] for item in pole_summary.values()),
            "changed_poles": [
                pole for pole, item in pole_summary.items() if item["amplitude"] > 0.0
            ],
        },
        "node_coherence_changes": {
            "available": True,
            "node_summary": node_summary,
            "route_node_ids": sorted(node_coherence),
            "off_route_node_ids": [],
            "near_route_vs_off_route_comparison_available": False,
            "reason": "E3 source fixture has only four route nodes and no off-route nodes.",
        },
        "edge_delay_and_proper_time": {
            "edge_delay_values_by_edge": {
                str(edge_id): sorted(values) for edge_id, values in edge_delays.items()
            },
            "temporal_delay_values_by_edge": {
                str(edge_id): sorted(values)
                for edge_id, values in edge_temporal_delays.items()
            },
            "edge_delay_asymmetry_detected": len(
                {value for values in edge_delays.values() for value in values}
            )
            > 1,
            "edge_delay_uniform": len(
                {value for values in edge_delays.values() for value in values}
            )
            == 1,
            "edge_delay_asymmetry_observed": len(
                {value for values in edge_delays.values() for value in values}
            )
            > 1,
            "node_proper_time_summary": {
                str(node_id): {
                    "min": min(values),
                    "max": max(values),
                    "span": max(values) - min(values),
                }
                for node_id, values in sorted(node_proper_time.items())
            },
            "final_node_proper_time_range": max(
                values[-1] for values in node_proper_time.values()
            )
            - min(values[-1] for values in node_proper_time.values()),
            "proper_time_phase_separation_observed": (
                max(values[-1] for values in node_proper_time.values())
                - min(values[-1] for values in node_proper_time.values())
            )
            > 0.0,
            "proper_time_phase_metric": "final_node_proper_time_range",
            "phase_series_available": True,
            "movement_relevance": "timing_geometry_surface",
            "movement_claim_allowed": False,
        },
        "conductance_and_coupling": {
            "conductance_changed_edges": conductance_changed_edges,
            "base_conductance_changed_edges": base_conductance_changed_edges,
            "conductance_changes_available": True,
            "conductance_coupling_changed": bool(
                conductance_changed_edges or base_conductance_changed_edges
            ),
            "conductance_change_observed": bool(conductance_changed_edges),
            "coupling_change_observed": bool(
                conductance_changed_edges or base_conductance_changed_edges
            ),
        },
        "budget_split": {
            "available": True,
            "node_budget_min": min(node_budget),
            "node_budget_max": max(node_budget),
            "in_flight_packet_budget_min": min(in_flight_budget),
            "in_flight_packet_budget_max": max(in_flight_budget),
            "total_budget_min": min(total_budget),
            "total_budget_max": max(total_budget),
            "max_checkpoint_budget_error": max(budget_error),
        },
        "topology": {
            "topology_changed": topology_changed,
            "node_count": len(node_coherence),
            "route_node_count": len(node_coherence),
            "off_route_node_count": 0,
        },
    }


def _event_budget_audit(events: list[dict[str, Any]]) -> dict[str, Any]:
    packet_events = [
        event
        for event in events
        if event["event_kind"]
        in {"lgrc9v3_packet_departure", "lgrc9v3_packet_arrival"}
    ]
    budget_errors = []
    for event in packet_events:
        budget_error = event["payload"].get("budget_error")
        if budget_error is not None:
            budget_errors.append(abs(float(budget_error)))
    return {
        "packet_event_count": len(packet_events),
        "max_event_budget_error": max(budget_errors) if budget_errors else None,
        "budget_error_values_available": bool(budget_errors),
    }


def validate_geometry_coupling() -> dict[str, Any]:
    e3_import = _load_json(E3_IMPORT)
    e3_animation = _load_json(E3_ANIMATION)
    classifier = _load_json(N04_CLASSIFIER)
    checkpoints = _analyze_checkpoints(_checkpoint_paths())
    event_audit = _event_budget_audit(_load_jsonl(E3_EVENTS))

    source_fixture_changes_detected = (
        checkpoints["pole_mass_oscillation"]["max_pole_amplitude"] > 0.0
        or checkpoints["edge_delay_and_proper_time"]["final_node_proper_time_range"] > 0.0
    )
    n04_mapping_defined = e3_import["fixture_mapping_prerequisite"][
        "mapping_strategy_defined"
    ]

    movement_claim_flags = {
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "movement_claim_inherited_from_n03": False,
        "native_lgrc9v3_e3_pulse_used": True,
        "native_grc9v3_proposal_flux_control_used": False,
    }

    checks = {
        "e3_import_passed": e3_import["status"] == "passed",
        "source_fixture_pole_mass_oscillation_measured": checkpoints[
            "pole_mass_oscillation"
        ]["max_pole_amplitude"]
        > 0.0,
        "budget_split_available_from_animation_telemetry": checkpoints[
            "budget_split"
        ]["available"],
        "node_plus_packet_budget_conserved": checkpoints["budget_split"][
            "max_checkpoint_budget_error"
        ]
        == 0.0
        and event_audit["max_event_budget_error"] == 0.0,
        "edge_delay_audit_available": bool(
            checkpoints["edge_delay_and_proper_time"]["edge_delay_values_by_edge"]
        ),
        "conductance_audit_available": checkpoints["conductance_and_coupling"][
            "conductance_changes_available"
        ],
        "boundary_coupling_disabled": e3_import["controls"][
            "pulse_active_boundary_coupling_disabled"
        ]["boundary_coupling_enabled"]
        is False,
        "pulse_activity_alone_does_not_claim_movement": e3_import["controls"][
            "pulse_active_boundary_coupling_disabled"
        ]["movement_claim_allowed"]
        is False,
        "no_direct_boundary_displacement_scripted": not any(
            [
                e3_import["adapter_boundary"]["direct_boundary_write"],
                e3_import["adapter_boundary"]["direct_support_mask_write"],
                e3_import["adapter_boundary"]["direct_centroid_write"],
            ]
        ),
        "n04_fixture_mapping_not_yet_defined": n04_mapping_defined is False,
        "movement_classifier_boundary_unchanged": classifier["status"] == "passed",
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "packet_loop_geometry_coupling_audit_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "runtime_family": "LGRC9V3",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_geometry_audit",
        "source_experiment": "N03",
        "source_result": e3_import["source_result"],
        "source_artifacts": {
            "e3_import": _artifact_record(E3_IMPORT),
            "e3_animation": _artifact_record(E3_ANIMATION),
            "e3_steps": _artifact_record(E3_STEPS),
            "e3_events": _artifact_record(E3_EVENTS),
        },
        "claim_ceiling": "packet_loop_geometry_coupling_audit",
        "claim_flags": movement_claim_flags,
        "boundary_coupled_movement_claim_allowed": False,
        "blocked_claims": [
            "movement_response",
            "identity_preserving_displacement",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "movement_inherited_from_n03",
        ],
        "checks": checks,
        "loop_dependency": e3_import["loop_dependency"],
        "pulse_context": {
            "pulse_active": True,
            "boundary_coupling_enabled": False,
            "packet_loop_observed": e3_import["controls"][
                "pulse_active_boundary_coupling_disabled"
            ]["packet_loop_observed"],
            "native_lgrc9v3_e3_pulse_used": True,
            "native_d2_3_equivalent": e3_import["pulse_metadata"][
                "native_d2_3_equivalent"
            ],
        },
        "geometry_coupling": {
            "source_fixture_changes_detected": source_fixture_changes_detected,
            "pole_coherence_oscillation_observed": checkpoints[
                "pole_mass_oscillation"
            ]["max_pole_amplitude"]
            > 0.0,
            "movement_relevant_state_change_observed": source_fixture_changes_detected,
            "movement_relevant_state_changed_on_e3_source_fixture": source_fixture_changes_detected,
            "movement_relevant_state_changed_on_n04_fixture": False,
            "n04_movement_fixture_state_changed": False,
            "n04_fixture_mapping_defined": n04_mapping_defined,
            "n04_fixture_mapping_required_before_boundary_coupling": True,
            "interpretation": (
                "E3 telemetry shows packet-driven pole coherence/proper-time "
                "changes on the four-node source fixture, but N04 movement "
                "geometry coupling remains unopened because the E3 route is not "
                "mapped onto S0/S1 and boundary coupling is disabled."
            ),
        },
        "layer_separation": {
            "layer_a_native_e3_source_fixture": {
                "state_changes_observed": source_fixture_changes_detected,
                "movement_claim_allowed": False,
            },
            "layer_b_imported_pulse_telemetry": {
                "telemetry_audited": True,
                "budget_split_available": checkpoints["budget_split"]["available"],
                "movement_claim_allowed": False,
            },
            "layer_c_n04_movement_substrate": {
                "mapping_defined": n04_mapping_defined,
                "state_changed": False,
                "movement_claim_allowed": False,
            },
        },
        "pole_mass_oscillation": checkpoints["pole_mass_oscillation"],
        "node_coherence_changes": checkpoints["node_coherence_changes"],
        "near_route_off_route_comparison": {
            "available": False,
            "reason": "all_four_nodes_are_route_nodes",
            "claim_impact": "does_not_block_packet_loop_geometry_coupling_audit_but_blocks_route_locality_claim",
            "blocked_claim": "route_localized_geometry_coupling",
            "allowed_claim": "native_route_wide_pulse_state_coupling",
        },
        "edge_delay_and_proper_time": checkpoints["edge_delay_and_proper_time"],
        "conductance_and_coupling": checkpoints["conductance_and_coupling"],
        "budget_split": checkpoints["budget_split"],
        "event_budget_audit": event_audit,
        "topology": checkpoints["topology"],
        "adapter_boundary": e3_import["adapter_boundary"],
        "fixture_mapping_prerequisite": e3_import["fixture_mapping_prerequisite"],
        "route_to_movement_substrate_mapping": {
            "defined": False,
            "source_fixture": "E3_four_node_source_fixture",
            "target_fixtures": ["S0_chain_v1", "S1_ring_v1"],
            "mapping_required_before_boundary_coupled_test": True,
        },
        "iteration_8_entry_requirement": {
            "route_to_movement_substrate_mapping_required": True,
            "mapping_status": "not_defined",
            "boundary_coupled_pulse_fixture_ready": False,
        },
        "movement_classifier_boundary": {
            "classifier_version": classifier["classifier_version"],
            "status": classifier["status"],
            "movement_claims_remain_false": True,
        },
        "environment": _environment_record(),
        "notes": [
            "Iteration 7-B audits geometry-coupling surfaces only.",
            "Boundary coupling remains disabled.",
            "No boundary, support-mask, centroid, or displacement state is directly scripted.",
            "E3 source telemetry contains exact node/in-flight packet budget split.",
            "Near-route versus off-route comparison is unavailable on the four-node E3 fixture because every node is on the route.",
            "N04 fixture mapping is still required before Iteration 8 can test boundary-coupled movement.",
        ],
    }


def write_report(result: dict[str, Any]) -> None:
    pole_rows = result["pole_mass_oscillation"]["pole_summary"]
    lines = [
        "# Packet-Loop Geometry Coupling Audit",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_packet_loop_geometry_coupling.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- Runtime family: `{result['runtime_family']}`",
        f"- Execution surface: `{result['execution_surface']}`",
        f"- Claim ceiling: `{result['claim_ceiling']}`",
        f"- Boundary coupling enabled: `{result['pulse_context']['boundary_coupling_enabled']}`",
        f"- Source fixture changes detected: `{result['geometry_coupling']['source_fixture_changes_detected']}`",
        f"- Proper-time phase separation observed: `{result['edge_delay_and_proper_time']['proper_time_phase_separation_observed']}`",
        f"- N04 fixture mapping defined: `{result['geometry_coupling']['n04_fixture_mapping_defined']}`",
        f"- Movement claim allowed: `{result['claim_flags']['movement_claim_allowed']}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Pole Mass Oscillation",
            "",
            "| Pole | Initial | Final | Min | Max | Amplitude | Proper-Time Span |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for pole, row in pole_rows.items():
        lines.append(
            "| `{}` | `{:.6f}` | `{:.6f}` | `{:.6f}` | `{:.6f}` | `{:.6f}` | `{:.6f}` |".format(
                pole,
                row["initial_coherence"],
                row["final_coherence"],
                row["min_coherence"],
                row["max_coherence"],
                row["amplitude"],
                row["proper_time_span"],
            )
        )

    budget = result["budget_split"]
    lines.extend(
        [
            "",
            "## Budget Split",
            "",
            f"- Node budget range: `{budget['node_budget_min']}` to `{budget['node_budget_max']}`",
            f"- In-flight packet budget range: `{budget['in_flight_packet_budget_min']}` to `{budget['in_flight_packet_budget_max']}`",
            f"- Total budget range: `{budget['total_budget_min']}` to `{budget['total_budget_max']}`",
            f"- Max checkpoint budget error: `{budget['max_checkpoint_budget_error']}`",
            f"- Max event budget error: `{result['event_budget_audit']['max_event_budget_error']}`",
            "",
            "## Edge And Route Locality",
            "",
            f"- Edge delay uniform: `{result['edge_delay_and_proper_time']['edge_delay_uniform']}`",
            f"- Edge delay asymmetry observed: `{result['edge_delay_and_proper_time']['edge_delay_asymmetry_observed']}`",
            f"- Conductance change observed: `{result['conductance_and_coupling']['conductance_change_observed']}`",
            f"- Coupling change observed: `{result['conductance_and_coupling']['coupling_change_observed']}`",
            f"- Near-route/off-route comparison available: `{result['near_route_off_route_comparison']['available']}`",
            f"- Near-route/off-route reason: `{result['near_route_off_route_comparison']['reason']}`",
            "",
            "## Iteration 8 Entry",
            "",
            f"- Route-to-substrate mapping required: `{result['iteration_8_entry_requirement']['route_to_movement_substrate_mapping_required']}`",
            f"- Mapping status: `{result['iteration_8_entry_requirement']['mapping_status']}`",
            f"- Boundary-coupled pulse fixture ready: `{result['iteration_8_entry_requirement']['boundary_coupled_pulse_fixture_ready']}`",
            "",
            "## Coupling Interpretation",
            "",
            result["geometry_coupling"]["interpretation"],
            "",
            "## Notes",
            "",
        ]
    )
    for note in result["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = validate_geometry_coupling()
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
