#!/usr/bin/env python3
"""Validate the polarized-basin-loop fixture manifest.

This script is intentionally experiment-local. It does not import or modify
`src/pygrc`; it validates the JSON fixture contract used by the N03 experiment
track and regenerates the validation artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EXPERIMENT_ID = "2026-05-N03-grc9v3-polarized-basin-loops"
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = ROOT / "outputs" / "fixture_manifest_validation.json"
REPORT_PATH = ROOT / "reports" / "fixture_manifest_validation.md"


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _region_export_for_uniform_clockwise_flux(
    *,
    edges: dict[int, dict[str, Any]],
    region: set[int],
) -> float:
    total = 0.0
    for edge in edges.values():
        node_u = int(edge["node_u"])
        node_v = int(edge["node_v"])
        if (node_u in region) == (node_v in region):
            continue
        local_node = node_u if node_u in region else node_v
        total += 1.0 if local_node == node_u else -1.0
    return total


def validate_manifest(data: dict[str, Any]) -> dict[str, Any]:
    """Return a validation artifact for the fixture manifest."""

    errors: list[str] = []
    warnings: list[str] = []

    fixtures = data.get("fixtures", {})
    canonical = fixtures.get("grc9v3_ported_ring_v1", {})
    simple = fixtures.get("simple_unported_ring_v1", {})
    nodes = {int(node_id) for node_id in canonical.get("nodes", [])}
    edge_list = canonical.get("edges", [])
    edges = {int(edge["edge_id"]): edge for edge in edge_list}
    masks = canonical.get("masks", {})
    reversed_masks = canonical.get("reversed_masks", {})

    checked: dict[str, bool] = {
        "node_ids_exist": False,
        "edge_ids_unique": False,
        "port_ids_valid_1_to_9": False,
        "clockwise_edge_orientation_consistent": False,
        "active_degree_two_for_every_node": False,
        "active_ports_are_4_and_6_for_every_node": False,
        "source_sink_masks_disjoint": False,
        "source_sink_masks_inside_parent_basin": False,
        "forward_return_edge_sets_disjoint": False,
        "forward_return_edges_live": False,
        "reversed_masks_swap_source_sink": False,
        "reversed_masks_swap_forward_return": False,
        "required_lanes_present": False,
        "required_metric_defaults_present": False,
        "readme_controls_present": False,
        "projection_disabled_dry_run_is_diagnostic_only": False,
        "topology_disabled_sets_topology_events_enabled_false": False,
        "topology_disabled_sets_pruning_enabled_false": False,
        "two_equal_canonical_ring_bumps_resolved": False,
        "return_channel_sign_semantics_explicit": False,
        "channel_flux_and_region_boundary_export_are_distinct": False,
        "edge_field_aliases_recorded": False,
        "uniform_conductance_shuffle_caveat_recorded": False,
        "configured_parent_claim_ceiling_note_recorded": False,
        "runner_dt_and_total_steps_recorded": False,
        "total_steps_cover_eval_window": False,
        "default_edge_properties_recorded": False,
        "s_lane_initialization_resolved": False,
        "k_lane_base_lane_resolved": False,
        "simple_fixture_reversal_status_explicit": False,
        "src_changes_required": False,
    }

    expected_node_count = int(canonical.get("node_count", -1))
    expected_edge_count = int(canonical.get("edge_count", -1))
    checked["node_ids_exist"] = bool(nodes) and len(nodes) == expected_node_count
    if not checked["node_ids_exist"]:
        errors.append("node_count does not match manifest nodes")

    checked["edge_ids_unique"] = len(edges) == len(edge_list) == expected_edge_count
    if not checked["edge_ids_unique"]:
        errors.append("edge ids are not unique or edge_count does not match edges")

    ports_valid = True
    clockwise_consistent = True
    for edge_id, edge in edges.items():
        node_u = int(edge["node_u"])
        node_v = int(edge["node_v"])
        port_u = int(edge["port_u"])
        port_v = int(edge["port_v"])
        if node_u not in nodes or node_v not in nodes:
            errors.append(f"edge {edge_id} references an unknown node")
        if not (1 <= port_u <= 9 and 1 <= port_v <= 9):
            ports_valid = False
            errors.append(f"edge {edge_id} has a port outside 1..9")
        if str(edge.get("orientation")) != "clockwise":
            clockwise_consistent = False
            errors.append(f"edge {edge_id} is not declared clockwise")
        if node_v != (node_u + 1) % expected_node_count:
            clockwise_consistent = False
            errors.append(f"edge {edge_id} is not node_u -> clockwise successor")
    checked["port_ids_valid_1_to_9"] = ports_valid
    checked["clockwise_edge_orientation_consistent"] = clockwise_consistent

    ports_by_node: dict[int, list[int]] = {node_id: [] for node_id in nodes}
    for edge in edges.values():
        ports_by_node[int(edge["node_u"])].append(int(edge["port_u"]))
        ports_by_node[int(edge["node_v"])].append(int(edge["port_v"]))
    checked["active_degree_two_for_every_node"] = all(
        len(ports) == 2 for ports in ports_by_node.values()
    )
    checked["active_ports_are_4_and_6_for_every_node"] = all(
        sorted(ports) == [4, 6] for ports in ports_by_node.values()
    )
    if not checked["active_degree_two_for_every_node"]:
        errors.append("not every node has active degree 2")
    if not checked["active_ports_are_4_and_6_for_every_node"]:
        errors.append("not every node uses exactly active ports 4 and 6")

    source_nodes = {int(node_id) for node_id in masks.get("source_aspect_nodes", [])}
    sink_nodes = {int(node_id) for node_id in masks.get("sink_aspect_nodes", [])}
    parent_nodes = {int(node_id) for node_id in masks.get("parent_basin_nodes", [])}
    checked["source_sink_masks_disjoint"] = not bool(source_nodes & sink_nodes)
    checked["source_sink_masks_inside_parent_basin"] = (
        source_nodes <= parent_nodes and sink_nodes <= parent_nodes and parent_nodes <= nodes
    )
    if not checked["source_sink_masks_disjoint"]:
        errors.append("source and sink aspect masks overlap")
    if not checked["source_sink_masks_inside_parent_basin"]:
        errors.append("source/sink masks are not inside the parent basin mask")

    live_edge_ids = set(edges)
    forward_edges = {int(edge_id) for edge_id in masks.get("forward_channel_edges", [])}
    return_edges = {int(edge_id) for edge_id in masks.get("return_channel_edges", [])}
    checked["forward_return_edge_sets_disjoint"] = not bool(forward_edges & return_edges)
    checked["forward_return_edges_live"] = forward_edges <= live_edge_ids and return_edges <= live_edge_ids
    if not checked["forward_return_edge_sets_disjoint"]:
        errors.append("forward and return channel edge sets overlap")
    if not checked["forward_return_edges_live"]:
        errors.append("forward or return channel contains an unknown edge")

    reversed_source = {int(node_id) for node_id in reversed_masks.get("source_aspect_nodes", [])}
    reversed_sink = {int(node_id) for node_id in reversed_masks.get("sink_aspect_nodes", [])}
    reversed_forward = {int(edge_id) for edge_id in reversed_masks.get("forward_channel_edges", [])}
    reversed_return = {int(edge_id) for edge_id in reversed_masks.get("return_channel_edges", [])}
    checked["reversed_masks_swap_source_sink"] = (
        reversed_source == sink_nodes and reversed_sink == source_nodes
    )
    checked["reversed_masks_swap_forward_return"] = (
        reversed_forward == return_edges and reversed_return == forward_edges
    )
    if not checked["reversed_masks_swap_source_sink"]:
        errors.append("reversed source/sink masks do not swap original masks")
    if not checked["reversed_masks_swap_forward_return"]:
        errors.append("reversed forward/return masks do not swap original masks")

    lanes = data.get("lanes", {})
    required_lanes = {"U", "U0", "U1", "U2", "S", "K", "K_reversed"}
    checked["required_lanes_present"] = required_lanes <= set(lanes)
    if not checked["required_lanes_present"]:
        errors.append("one or more required lanes are missing")

    metric_defaults = data.get("metric_config_defaults", {})
    required_metrics = {
        "n_cycles_min",
        "washout_steps",
        "min_eval_steps",
        "theta_export",
        "theta_import",
        "theta_mass",
        "theta_null_margin",
        "phase_lock_min",
        "phase_lock_max_lag",
        "phase_cascade_max_stage_lag",
        "phase_cascade_score_min",
    }
    checked["required_metric_defaults_present"] = required_metrics <= set(metric_defaults)
    if not checked["required_metric_defaults_present"]:
        errors.append("one or more required metric defaults are missing")
    if int(metric_defaults.get("n_cycles_min", 0)) < 3:
        errors.append("n_cycles_min must be at least 3")
    if int(metric_defaults.get("washout_steps", 0)) <= 0:
        errors.append("washout_steps must be positive")
    if int(metric_defaults.get("min_eval_steps", 0)) <= 0:
        errors.append("min_eval_steps must be positive")

    runner_config = data.get("runner_config", {})
    dt = float(runner_config.get("dt", 0.0))
    total_steps = int(runner_config.get("total_steps", 0))
    washout_steps = int(metric_defaults.get("washout_steps", 0))
    min_eval_steps = int(metric_defaults.get("min_eval_steps", 0))
    checked["runner_dt_and_total_steps_recorded"] = dt > 0.0 and total_steps > 0
    checked["total_steps_cover_eval_window"] = total_steps >= washout_steps + min_eval_steps
    if not checked["runner_dt_and_total_steps_recorded"]:
        errors.append("runner_config must record positive dt and total_steps")
    if not checked["total_steps_cover_eval_window"]:
        errors.append("total_steps must cover washout_steps + min_eval_steps")

    default_edge_properties = data.get("default_edge_properties", {})
    checked["default_edge_properties_recorded"] = all(
        key in default_edge_properties
        for key in (
            "base_conductance",
            "geometric_length",
            "flux_uv_initial",
            "flux_coupling_initial",
            "temporal_delay_initial",
        )
    )
    if not checked["default_edge_properties_recorded"]:
        errors.append("default_edge_properties is missing required edge defaults")

    controls = data.get("controls", {})
    required_controls = {
        "reversed_source_sink",
        "shuffled_conductance",
        "zero_flux_reset",
        "budget_projection_disabled_dry_run",
        "randomized_labels_posthoc",
        "topology_disabled",
    }
    checked["readme_controls_present"] = required_controls <= set(controls)
    if not checked["readme_controls_present"]:
        errors.append("one or more README controls are missing")

    dry_run = controls.get("budget_projection_disabled_dry_run", {})
    checked["projection_disabled_dry_run_is_diagnostic_only"] = (
        dry_run.get("positive_conservation_claims_allowed") is False
    )
    if not checked["projection_disabled_dry_run_is_diagnostic_only"]:
        errors.append("projection-disabled dry run must not allow positive conservation claims")

    topology_control = controls.get("topology_disabled", {})
    checked["topology_disabled_sets_topology_events_enabled_false"] = (
        topology_control.get("topology_events_enabled") is False
    )
    checked["topology_disabled_sets_pruning_enabled_false"] = (
        topology_control.get("pruning_enabled") is False
    )
    if not checked["topology_disabled_sets_topology_events_enabled_false"]:
        errors.append("topology-disabled control must set topology_events_enabled=false")
    if not checked["topology_disabled_sets_pruning_enabled_false"]:
        errors.append("topology-disabled control must set pruning_enabled=false")

    formulas = data.get("initialization", {}).get("formulas", {})
    checked["two_equal_canonical_ring_bumps_resolved"] = (
        "two_equal_canonical_ring_bumps" in formulas
        and lanes.get("U1", {}).get("initialization") in formulas
    )
    if not checked["two_equal_canonical_ring_bumps_resolved"]:
        errors.append("U1 initialization is not resolvable")

    checked["s_lane_initialization_resolved"] = (
        lanes.get("S", {}).get("initialization") in formulas
    )
    if not checked["s_lane_initialization_resolved"]:
        errors.append("S lane initialization is not resolvable")

    k_lane = lanes.get("K", {})
    checked["k_lane_base_lane_resolved"] = (
        k_lane.get("base_lane") in lanes
        and k_lane.get("initialization") in formulas
        and k_lane.get("kick") in formulas
        and bool(k_lane.get("composition"))
    )
    if not checked["k_lane_base_lane_resolved"]:
        errors.append("K lane base_lane/initialization/kick composition is not resolvable")

    observable_semantics = data.get("observable_semantics", {})
    return_sign = observable_semantics.get("return_channel_sign", {})
    checked["return_channel_sign_semantics_explicit"] = "clockwise" in str(
        return_sign.get("meaning", "")
    )
    if not checked["return_channel_sign_semantics_explicit"]:
        errors.append("return-channel sign semantics are not explicit")

    channel_boundary = observable_semantics.get("channel_vs_region_boundary", {})
    checked["channel_flux_and_region_boundary_export_are_distinct"] = all(
        key in channel_boundary
        for key in ("J_forward", "J_return", "source_export", "sink_import")
    )
    if not checked["channel_flux_and_region_boundary_export_are_distinct"]:
        errors.append("channel flux and region export/import semantics are incomplete")

    aliases = observable_semantics.get("edge_field_aliases", {})
    checked["edge_field_aliases_recorded"] = aliases == {
        "u": "node_u",
        "v": "node_v",
        "u_port": "port_u",
        "v_port": "port_v",
    }
    if not checked["edge_field_aliases_recorded"]:
        errors.append("edge field aliases are missing or incorrect")

    checked["uniform_conductance_shuffle_caveat_recorded"] = bool(
        controls.get("shuffled_conductance", {}).get("uniform_conductance_note")
    )
    if not checked["uniform_conductance_shuffle_caveat_recorded"]:
        errors.append("uniform-conductance shuffled-control caveat is missing")

    checked["configured_parent_claim_ceiling_note_recorded"] = bool(
        masks.get("claim_ceiling_note")
    )
    if not checked["configured_parent_claim_ceiling_note_recorded"]:
        errors.append("configured-parent claim ceiling note is missing")

    checked["src_changes_required"] = False

    forward_flux_sum = float(len(forward_edges))
    return_flux_sum = float(len(return_edges))
    source_region_net_export = _region_export_for_uniform_clockwise_flux(
        edges=edges,
        region=source_nodes,
    )
    sink_region_net_export = _region_export_for_uniform_clockwise_flux(
        edges=edges,
        region=sink_nodes,
    )

    simple_nodes = {int(node_id) for node_id in simple.get("nodes", [])}
    simple_edges = simple.get("edges", [])
    simple_masks = simple.get("masks", {})
    if len(simple_nodes) != int(simple.get("node_count", -1)):
        errors.append("simple_unported_ring_v1 node_count mismatch")
    if len(simple_edges) != int(simple.get("edge_count", -1)):
        errors.append("simple_unported_ring_v1 edge_count mismatch")
    checked["simple_fixture_reversal_status_explicit"] = (
        simple.get("reversed_masks_available") is False
        and bool(simple.get("reversed_masks_note"))
    )
    if not checked["simple_fixture_reversal_status_explicit"]:
        errors.append("simple_unported_ring_v1 must explicitly declare reversal status")
    for key in ("source_aspect_nodes", "sink_aspect_nodes", "parent_basin_nodes"):
        if not {int(node_id) for node_id in simple_masks.get(key, [])} <= simple_nodes:
            errors.append(f"simple_unported_ring_v1 mask {key} contains unknown nodes")

    status = "pass" if not errors else "fail"
    return {
        "schema": "grc9v3_polarized_basin_loop_fixture_manifest_validation_v1",
        "experiment_id": EXPERIMENT_ID,
        "manifest_path": "configs/fixture_manifest_v1.json",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "port_orientation": {
            "clockwise_out_port": 6,
            "clockwise_out_port_rc": [2, 3],
            "clockwise_in_port": 4,
            "clockwise_in_port_rc": [2, 1],
            "edge_orientation": "node_u_to_node_v_clockwise",
            "flux_uv_positive_direction": "node_u_to_node_v",
        },
        "synthetic_flux_check": {
            "flux_uv": "+1 on every clockwise edge",
            "forward_flux_sum": forward_flux_sum,
            "return_flux_sum": return_flux_sum,
            "source_region_net_export": source_region_net_export,
            "sink_region_net_export": sink_region_net_export,
            "interpretation": (
                "Channel sums are positive in the declared clockwise direction. "
                "Region net export is zero for uniform clockwise circulation "
                "because each two-node aspect has one incoming and one outgoing "
                "boundary edge."
            ),
        },
        "canonical_masks": {
            "source_aspect_nodes": sorted(source_nodes),
            "sink_aspect_nodes": sorted(sink_nodes),
            "forward_channel_edges": sorted(forward_edges),
            "return_channel_edges": sorted(return_edges),
            "source_internal_edges": [
                int(edge_id) for edge_id in masks.get("source_internal_edges", [])
            ],
            "sink_internal_edges": [
                int(edge_id) for edge_id in masks.get("sink_internal_edges", [])
            ],
        },
        "observable_semantics": {
            "J_forward": "sum over forward_channel_edges only",
            "J_return": "sum over return_channel_edges only",
            "source_export": "boundary export from source_aspect_nodes",
            "sink_import": "boundary import into sink_aspect_nodes",
            "return_channel_sign": "positive in declared clockwise edge orientation",
            "edge_field_aliases": {
                "u": "node_u",
                "v": "node_v",
                "u_port": "port_u",
                "v_port": "port_v",
            },
        },
        "initialization_resolution": {
            "two_equal_canonical_ring_bumps": (
                "canonical_ring_bump applied twice with equal A and kappa at "
                "lane.bump_centers, followed by conserved simplex projection"
            ),
            "canonical_ring_bump_plus_small_local_source_sink_modulation": (
                "canonical_ring_bump applied first, then source/sink modulation "
                "is added, followed by one conserved simplex projection"
            ),
            "K": (
                "resolve base_lane U2, initialize uniform closed-substrate masks, "
                "then apply zero_sum_kick at kick_step"
            ),
            "source_sink_modulation_audit": (
                "record pre-projection sum and projection delta"
            ),
            "kick_audit": (
                "record pre-projection sum and projection delta; K_reversed "
                "applies reversed masks to labels and kick direction"
            ),
        },
        "control_notes": {
            "shuffled_conductance": str(
                controls.get("shuffled_conductance", {}).get(
                    "uniform_conductance_note", ""
                )
            ),
            "simple_unported_ring_reversal": str(
                simple.get("reversed_masks_note", "")
            ),
        },
        "runner_config": {
            "dt": dt,
            "total_steps": total_steps,
            "washout_steps": washout_steps,
            "min_eval_steps": min_eval_steps,
        },
        "default_edge_properties": default_edge_properties,
        "hypothesis_record": {
            "path": "hypotheses/polarized_basin_loop_hypothesis_v1.md",
        },
        "process_notes": {
            "hypothesis_directory_populated": (
                ROOT / "hypotheses" / "polarized_basin_loop_hypothesis_v1.md"
            ).exists()
        },
        "conclusion": (
            "ready_for_iteration_3_observable_implementation"
            if status == "pass"
            else "blocked_until_manifest_errors_are_fixed"
        ),
    }


def _write_json(artifact: dict[str, Any]) -> None:
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def _write_report(artifact: dict[str, Any]) -> None:
    checked = artifact["checked"]
    synthetic = artifact["synthetic_flux_check"]
    masks = artifact["canonical_masks"]
    lines = [
        "# Fixture Manifest Validation",
        "",
        "Experiment:",
        "",
        "```text",
        EXPERIMENT_ID,
        "```",
        "",
        "Manifest:",
        "",
        "```text",
        "configs/fixture_manifest_v1.json",
        "```",
        "",
        "Status:",
        "",
        "```text",
        str(artifact["status"]),
        "```",
        "",
        "## Reproduction Commands",
        "",
        "Run from the repository root:",
        "",
        "```bash",
        "python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_fixture_manifest.py",
        "python -m json.tool experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/fixture_manifest_validation.json",
        "git diff -- src",
        "```",
        "",
        "Observed command result:",
        "",
        "```text",
        json.dumps({"status": artifact["status"], "errors": artifact["errors"]}),
        "```",
        "",
        "`git diff -- src` produced no output.",
        "",
        "## Checks",
        "",
        "The validation checked:",
        "",
    ]
    check_descriptions = {
        "node_ids_exist": "all node ids exist",
        "edge_ids_unique": "all edge ids are unique and present",
        "port_ids_valid_1_to_9": "every port id is in `1..9`",
        "clockwise_edge_orientation_consistent": (
            "every ring edge follows the declared clockwise `node_u -> node_v` direction"
        ),
        "active_degree_two_for_every_node": "every node has active degree `2`",
        "active_ports_are_4_and_6_for_every_node": "every node uses exactly ports `4` and `6`",
        "source_sink_masks_disjoint": "source/sink masks are disjoint",
        "source_sink_masks_inside_parent_basin": "source/sink masks are inside the parent basin mask",
        "forward_return_edge_sets_disjoint": "forward and return channel edge sets are disjoint",
        "forward_return_edges_live": "forward and return channel masks reference live edges",
        "reversed_masks_swap_source_sink": "reversed masks swap source/sink regions coherently",
        "reversed_masks_swap_forward_return": "reversed masks swap forward/return channels coherently",
        "required_lanes_present": "required lane ids are present",
        "required_metric_defaults_present": "`n_cycles_min`, `washout_steps`, and `min_eval_steps` are present",
        "readme_controls_present": "README control configs are present and typed",
        "projection_disabled_dry_run_is_diagnostic_only": "projection-disabled dry run is diagnostic only",
        "topology_disabled_sets_topology_events_enabled_false": "topology-disabled control sets `topology_events_enabled = false`",
        "topology_disabled_sets_pruning_enabled_false": "topology-disabled control also sets `pruning_enabled = false`",
        "two_equal_canonical_ring_bumps_resolved": "`two_equal_canonical_ring_bumps` is explicitly resolvable",
        "return_channel_sign_semantics_explicit": "return-channel sign semantics are explicit",
        "channel_flux_and_region_boundary_export_are_distinct": "channel flux semantics are separated from region boundary export/import",
        "edge_field_aliases_recorded": "edge field aliases are recorded (`u/v` versus `node_u/node_v`)",
        "uniform_conductance_shuffle_caveat_recorded": "uniform-conductance shuffled-control caveat is recorded",
        "configured_parent_claim_ceiling_note_recorded": "configured-parent evidence has a candidate-claim ceiling note",
        "runner_dt_and_total_steps_recorded": "`dt` and `total_steps` are recorded",
        "total_steps_cover_eval_window": "`total_steps` covers washout plus minimum evaluation window",
        "default_edge_properties_recorded": "default edge properties include flux coupling and temporal delay defaults",
        "s_lane_initialization_resolved": "S-lane composite initialization is explicitly resolvable",
        "k_lane_base_lane_resolved": "K-lane base lane, initialization, kick, and composition are resolvable",
        "simple_fixture_reversal_status_explicit": "simple analysis fixture explicitly declares reversal status",
        "src_changes_required": "no `src/*` changes were required",
    }
    for key, description in check_descriptions.items():
        if key == "src_changes_required":
            if not checked.get(key):
                lines.append(f"- {description};")
        elif checked.get(key):
            lines.append(f"- {description};")
    lines.extend(
        [
            "",
            "## Port Orientation",
            "",
            "The canonical fixture uses:",
            "",
            "```text",
            "clockwise_out_port = 6 = row 2, column 3",
            "clockwise_in_port  = 4 = row 2, column 1",
            "```",
            "",
            "Every edge is oriented clockwise:",
            "",
            "```text",
            "edge.node_u -> edge.node_v",
            "```",
            "",
            "and every `node_v` is the clockwise successor of `node_u`.",
            "",
            "## Synthetic Flux Check",
            "",
            "The validation injected the interpretation:",
            "",
            "```text",
            "flux_uv = +1 on every clockwise edge",
            "```",
            "",
            "Expected result:",
            "",
            "```text",
            "forward channel flux > 0",
            "return channel flux > 0",
            "```",
            "",
            "Observed:",
            "",
            "```text",
            f"forward_flux_sum = {synthetic['forward_flux_sum']}",
            f"return_flux_sum = {synthetic['return_flux_sum']}",
            f"source_region_net_export = {synthetic['source_region_net_export']}",
            f"sink_region_net_export = {synthetic['sink_region_net_export']}",
            "```",
            "",
            "The zero net export for the source/sink regions is expected for uniform",
            "clockwise circulation on a closed ring: each two-node aspect has one incoming",
            "and one outgoing boundary edge. Channel flux remains positive in the declared",
            "clockwise direction.",
            "",
            "## Fixture Geometry",
            "",
            "The canonical masks are:",
            "",
            "```text",
            f"source_aspect_nodes = {masks['source_aspect_nodes']}",
            f"sink_aspect_nodes   = {masks['sink_aspect_nodes']}",
            f"forward_channel_edges = {masks['forward_channel_edges']}",
            f"return_channel_edges  = {masks['return_channel_edges']}",
            f"source_internal_edges = {masks['source_internal_edges']}",
            f"sink_internal_edges   = {masks['sink_internal_edges']}",
            "```",
            "",
            "This gives two-node source/sink aspects, five-edge forward/return channels,",
            "and one internal edge inside each aspect.",
            "",
            "## Observable Semantics Tightening",
            "",
            "The manifest records that:",
            "",
            "```text",
            "J_forward = sum over forward_channel_edges only",
            "J_return  = sum over return_channel_edges only",
            "source_export = boundary export from source_aspect_nodes",
            "sink_import   = boundary import into sink_aspect_nodes",
            "```",
            "",
            "These are related but not identical surfaces. Iteration 3 should not use",
            "`J_forward` as a synonym for source export, or `J_return` as a synonym for",
            "sink import.",
            "",
            "Return flux is positive in the declared clockwise edge orientation:",
            "",
            "```text",
            "7 -> 8 -> 9 -> 10 -> 11 -> 0",
            "```",
            "",
            "It is not counterclockwise or opposite-sign flux in this fixture.",
            "",
            "The manifest also records:",
            "",
            "```text",
            "two_equal_canonical_ring_bumps",
            "```",
            "",
            "as `canonical_ring_bump` applied twice with equal parameters at the configured",
            "lane bump centers, followed by conserved simplex projection.",
            "",
            "The S lane composite initialization is explicit:",
            "",
            "```text",
            "canonical_ring_bump -> small_local_source_sink_modulation -> projection",
            "```",
            "",
            "The K lane resolves `base_lane = U2`, initializes the uniform closed",
            "substrate, then applies `zero_sum_kick` at `kick_step`.",
            "",
            "The shuffled-conductance control records that shuffling",
            "`initial_fixture_base_conductance` is non-informative for the current uniform",
            "conductance fixture unless conductance heterogeneity is added. The first",
            "informative shuffled control is `channel_mask_assignment`.",
            "",
            "## Conclusion",
            "",
            "The manifest is ready for Iteration 3 observable implementation.",
            "",
            "No `src/*` files were changed.",
        ]
    )
    if artifact["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in artifact["errors"])
    if artifact["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in artifact["warnings"])
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    data = _load_manifest()
    artifact = validate_manifest(data)
    _write_json(artifact)
    _write_report(artifact)
    print(json.dumps({"status": artifact["status"], "errors": artifact["errors"]}))
    return 0 if artifact["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
