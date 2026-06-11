"""Validate the N04 movement fixture manifest.

This is an experiment-local schema and consistency validator. It does not
import or mutate `src/pygrc`.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
MANIFEST_PATH = N04 / "configs/movement_fixture_manifest_v1.json"
OUTPUT_PATH = N04 / "outputs/movement_fixture_manifest_validation.json"
REPORT_PATH = N04 / "reports/movement_fixture_manifest_validation.md"


REQUIRED_METRICS = {
    "epsilon_budget",
    "configured_displacement_min",
    "null_calibration_k",
    "identity_mass_ratio_min",
    "width_relative_change_max",
    "profile_similarity_min",
}
REQUIRED_TOPOLOGY_POLICY = {
    "fixed_substrate_required",
    "topology_changed_required",
    "topology_changed_allowed",
}
REQUIRED_LANES = {"U0", "B0", "B1", "B1_reversed", "K1", "K1_reversed"}
REQUIRED_FORMULAS = {
    "uniform",
    "symmetric_bump",
    "locally_tapered_asymmetric_bump",
    "zero_sum_kick",
}
REQUIRED_DEFAULT_EDGE_PROPERTIES = {
    "weight",
    "base_conductance",
    "temporal_delay",
    "proper_time_delay",
}
REQUIRED_INITIALIZER_DEFAULTS = {
    "baseline_coherence",
    "bump_amplitude",
    "tilt_epsilon",
    "kick_mask_node_count",
}


def _load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("manifest root must be an object")
    return data


def _connected(node_ids: set[int], edges: list[dict[str, Any]]) -> bool:
    if not node_ids:
        return False
    adjacency = {node_id: set() for node_id in node_ids}
    for edge in edges:
        u = edge["u"]
        v = edge["v"]
        adjacency[u].add(v)
        adjacency[v].add(u)
    start = next(iter(node_ids))
    seen = {start}
    queue: deque[int] = deque([start])
    while queue:
        node = queue.popleft()
        for other in adjacency[node]:
            if other not in seen:
                seen.add(other)
                queue.append(other)
    return seen == node_ids


def _validate_fixture(fixture_id: str, fixture: dict[str, Any]) -> dict[str, Any]:
    if fixture.get("status") == "deferred":
        return {
            "fixture_id": fixture_id,
            "status": "deferred",
            "passed": True,
            "checks": {"deferred_reason_present": bool(fixture.get("reason"))},
        }

    nodes = fixture.get("nodes", [])
    edges = fixture.get("edges", [])
    node_ids = [node.get("node_id") for node in nodes]
    edge_ids = [edge.get("edge_id") for edge in edges]
    node_id_set = set(node_ids)
    edge_endpoint_ids = {endpoint for edge in edges for endpoint in (edge.get("u"), edge.get("v"))}
    coordinate_policy = fixture.get("coordinate_policy", {})
    basin_seed = fixture.get("basin_seed", {})
    front_rear = fixture.get("front_rear_definition", {})
    fixture_type = fixture.get("type")

    checks = {
        "node_count_matches": fixture.get("node_count") == len(nodes),
        "edge_count_matches": fixture.get("edge_count") == len(edges),
        "node_ids_unique": len(node_ids) == len(node_id_set),
        "edge_ids_unique": len(edge_ids) == len(set(edge_ids)),
        "edge_endpoints_exist": edge_endpoint_ids <= node_id_set,
        "connected": _connected(node_id_set, edges),
        "coordinate_policy_present": {
            "node_coordinate_policy",
            "centroid_coordinate_frame",
            "coordinate_periodic",
            "coordinate_mapping",
            "ring_unwrap_policy",
        }
        <= set(coordinate_policy),
        "edge_weights_present": all("weight" in edge for edge in edges),
        "edge_conductance_present": all("base_conductance" in edge for edge in edges),
        "edge_temporal_delay_present": all("temporal_delay" in edge for edge in edges),
        "edge_proper_time_delay_present": all("proper_time_delay" in edge for edge in edges),
        "edge_weights_positive": all(edge.get("weight", 0.0) > 0.0 for edge in edges),
        "edge_delays_positive": all(
            edge.get("temporal_delay", 0.0) > 0.0
            and edge.get("proper_time_delay", 0.0) > 0.0
            for edge in edges
        ),
        "front_rear_direction_present": bool(front_rear.get("direction_source"))
        and bool(front_rear.get("direction_vector")),
        "basin_center_exists": basin_seed.get("center_node_id") in node_id_set,
        "basin_support_exists": set(basin_seed.get("initial_support_nodes", [])) <= node_id_set,
        "total_budget_positive": fixture.get("total_budget", 0.0) > 0.0,
    }

    if fixture_type == "chain":
        checks["chain_edge_count"] = len(edges) == len(nodes) - 1
        checks["chain_nonperiodic"] = coordinate_policy.get("coordinate_periodic") is False
        checks["chain_unwrap_not_applicable"] = (
            coordinate_policy.get("ring_unwrap_policy") == "not_applicable"
        )
        checks["chain_mapping_declared"] = coordinate_policy.get("coordinate_mapping") == "x_i = node_index"
    elif fixture_type == "ring":
        checks["ring_edge_count"] = len(edges) == len(nodes)
        checks["ring_periodic"] = coordinate_policy.get("coordinate_periodic") is True
        checks["ring_unwrap_declared"] = coordinate_policy.get("ring_unwrap_policy") in {
            "circular_mean",
            "tracked_basin_representative",
        }
        checks["ring_coordinate_mapping_declared"] = "theta_i = 2*pi*i/N" in str(
            coordinate_policy.get("coordinate_mapping")
        )
        checks["ring_direction_mapping_declared"] = "clockwise direction" in str(
            coordinate_policy.get("coordinate_mapping")
        )
        checks["ring_antipodal_tie_break_declared"] = (
            coordinate_policy.get("antipodal_tie_break")
            == "negative_signed_distance_for_even_N"
        )
        checks["ring_antipodal_tie_break_note_present"] = bool(
            coordinate_policy.get("antipodal_tie_break_note")
        )
        checks["ring_has_wrap_edge"] = any(
            {edge.get("u"), edge.get("v")} == {0, fixture.get("node_count") - 1}
            for edge in edges
        )
    else:
        checks["known_fixture_type"] = False

    return {
        "fixture_id": fixture_id,
        "status": "active",
        "passed": all(bool(value) for value in checks.values()),
        "checks": checks,
    }


def _validate_lanes(manifest: dict[str, Any]) -> dict[str, Any]:
    lanes = manifest.get("lanes", {})
    formulas = manifest.get("initializer_formulas", {})
    lane_checks: dict[str, Any] = {}

    for lane_id, lane in lanes.items():
        initializer = lane.get("initializer")
        check = {
            "initializer_resolves": initializer in formulas,
            "expected_claim_ceiling_present": bool(lane.get("expected_claim_ceiling")),
        }
        if "front_rear_definition" in lane:
            front_rear = lane["front_rear_definition"]
            direction_source = front_rear.get("direction_source")
            check["front_rear_direction_source_valid"] = direction_source in {
                "packet_route",
                "centroid_velocity",
                "configured",
                "perturbation",
                "none",
            }
            check["front_rear_direction_present"] = (
                direction_source == "none"
                or bool(front_rear.get("direction_vector"))
            )
        if "reversal_of" in lane:
            check["reversal_target_exists"] = lane["reversal_of"] in lanes
        if "kick" in lane:
            check["kick_resolves"] = lane["kick"] in formulas
            check["kick_delta_positive"] = lane.get("kick_delta", 0.0) > 0.0
            check["kick_mask_node_count_positive"] = lane.get("kick_mask_node_count", 0) > 0
        if initializer == "locally_tapered_asymmetric_bump":
            check["tilt_epsilon_positive"] = lane.get("tilt_epsilon", 0.0) > 0.0
            check["bump_amplitude_positive"] = lane.get("bump_amplitude", 0.0) > 0.0
        lane_checks[lane_id] = {
            "passed": all(bool(value) for value in check.values()),
            "checks": check,
        }

    return {
        "required_lanes_present": REQUIRED_LANES <= set(lanes),
        "lane_checks": lane_checks,
        "all_lanes_passed": all(item["passed"] for item in lane_checks.values()),
    }


def validate_manifest() -> dict[str, Any]:
    manifest = _load_manifest()
    metrics = manifest.get("metric_defaults", {})
    formulas = manifest.get("initializer_formulas", {})
    fixtures = manifest.get("fixtures", {})
    default_edge_properties = manifest.get("default_edge_properties", {})
    initializer_defaults = manifest.get("initializer_defaults", {})
    topology_policy = manifest.get("topology_policy", {})

    fixture_results = {
        fixture_id: _validate_fixture(fixture_id, fixture)
        for fixture_id, fixture in fixtures.items()
    }
    lane_results = _validate_lanes(manifest)

    checks = {
        "schema_matches": manifest.get("schema") == "movement_fixture_manifest_v1",
        "topology_events_disabled": manifest.get("topology_events_enabled") is False,
        "adaptive_topology_entry_blocked": manifest.get("adaptive_topology_entry_allowed") is False,
        "topology_policy_present": REQUIRED_TOPOLOGY_POLICY <= set(topology_policy),
        "topology_policy_blocks_changes": topology_policy.get("fixed_substrate_required") is True
        and topology_policy.get("topology_changed_required") is False
        and topology_policy.get("topology_changed_allowed") is False,
        "required_metrics_present": REQUIRED_METRICS <= set(metrics),
        "required_formulas_present": REQUIRED_FORMULAS <= set(formulas),
        "initializer_defaults_present": REQUIRED_INITIALIZER_DEFAULTS <= set(initializer_defaults),
        "initializer_defaults_positive": all(
            initializer_defaults.get(key, 0.0) > 0.0 for key in REQUIRED_INITIALIZER_DEFAULTS
        ),
        "default_edge_properties_present": REQUIRED_DEFAULT_EDGE_PROPERTIES
        <= set(default_edge_properties),
        "default_edge_properties_positive": all(
            default_edge_properties.get(key, 0.0) > 0.0
            for key in REQUIRED_DEFAULT_EDGE_PROPERTIES
        ),
        "null_envelope_present": "null_displacement_envelope" in manifest,
        "null_envelope_calibration_status_present": "calibrated"
        in manifest.get("null_displacement_envelope", {}),
        "fixtures_present": {"S0_chain_v1", "S1_ring_v1", "S3_grid_v1"} <= set(fixtures),
        "active_fixtures_passed": all(result["passed"] for result in fixture_results.values()),
        "lanes_passed": lane_results["required_lanes_present"] and lane_results["all_lanes_passed"],
    }

    return {
        "schema": "movement_fixture_manifest_validation_v1",
        "manifest_path": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "fixture_results": fixture_results,
        "lane_results": lane_results,
        "metric_defaults": metrics,
        "topology_policy": topology_policy,
        "default_edge_properties": default_edge_properties,
        "initializer_defaults": initializer_defaults,
        "claim_flags": {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
        },
        "effective_displacement_min_rule": manifest["null_displacement_envelope"][
            "effective_displacement_min_rule"
        ],
        "notes": [
            "S0 and S1 are active first-tranche fixtures.",
            "S3 is declared but deferred until S0/S1 observables and classifier are validated.",
            "Ring centroid movement must use the declared unwrap policy.",
            "Topology events are disabled for the first movement tranche.",
        ],
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Movement Fixture Manifest Validation",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_fixture_manifest.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Top-Level Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(["", "## Fixtures", "", "| Fixture | Status | Passed |", "|---|---|---:|"])
    for fixture_id, fixture_result in result["fixture_results"].items():
        lines.append(
            f"| `{fixture_id}` | `{fixture_result['status']}` | `{fixture_result['passed']}` |"
        )

    lines.extend(["", "## Lanes", "", "| Lane | Passed |", "|---|---:|"])
    for lane_id, lane_result in result["lane_results"]["lane_checks"].items():
        lines.append(f"| `{lane_id}` | `{lane_result['passed']}` |")

    lines.extend(["", "## Notes", ""])
    for note in result["notes"]:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Edge Defaults",
            "",
            "```json",
            json.dumps(result["default_edge_properties"], indent=2, sort_keys=True),
            "```",
            "",
            "## Required Parameters",
            "",
            "- Edge weights, conductance, temporal delay, and proper-time delay are validated.",
            "- Ring coordinate mapping declares `theta_i = 2*pi*i/N` and clockwise direction.",
            "- Even-N ring antipodal tie-break is explicitly declared.",
            "- Initializer defaults are validated.",
            "- B1/B1 reversed declare bump amplitude and tilt epsilon.",
            "- K1/K1 reversed declare kick mask node count.",
        ]
    )
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = validate_manifest()
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
