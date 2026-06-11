"""Lane A readiness conformance tests for GRC9V3."""

from __future__ import annotations

from dataclasses import fields
import json
from pathlib import Path
import re
import tempfile
import unittest

from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import (
    port_id_to_slot,
    port_to_rc,
    rc_to_port,
    slot_to_port_id,
)
from pygrc.telemetry.grc9v3_contract import (
    GRC9V3CompletionEvidence,
    GRC9V3ExpansionEvidence,
    GRC9V3SparkEvidence,
)

from scripts.run_grc9v3_representative_runtime import build_representative_hybrid_model


_REPO_ROOT = Path(__file__).resolve().parents[2]
_TRACE_SCHEMA_PATH = _REPO_ROOT / "implementation" / "GRC9V3-LaneA-SparkGateTraceSchema.md"
_GAP_LEDGER_PATH = (
    _REPO_ROOT / "outputs" / "grc9v3" / "hessian_readiness" / "theory_runtime_gap_ledger.json"
)
_JSON_BLOCK_PATTERN = re.compile(r"```json\n(.*?)\n```", re.DOTALL)


def _params(
    *,
    evolution_overrides: dict[str, object] | None = None,
    **modes: object,
) -> dict[str, object]:
    evolution: dict[str, object] = {
        "alpha": 1e-12,
        "beta": 1e-12,
        "gamma": 1e-12,
        "eta": 1.0,
        "kappa_c": 1.0,
        "v0": 1.0,
        "rho": 1.0,
        "eps_tau": 1e-12,
        "site_potential_selection": "quadratic",
        "site_potential_params": {"mu": 0.0, "scale": 0.0},
        "eps_gradient": 0.01,
        "eps_hessian": 0.01,
        "eps_spark": 0.0,
        "D_eff_target": 16,
        "w_bond": 1.0,
    }
    if evolution_overrides:
        evolution.update(evolution_overrides)
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": dict(modes),
    }


def _topology(
    connections: list[tuple[int, int, int, int, int]],
    *,
    extra_nodes: tuple[int, ...] = (),
) -> dict[str, object]:
    node_ids = set(extra_nodes)
    incidence: dict[str, list[int]] = {str(node_id): [] for node_id in extra_nodes}
    edges: list[dict[str, object]] = []
    for edge_id, node_a, port_a, node_b, port_b in connections:
        node_ids.update({node_a, node_b})
        incidence.setdefault(str(node_a), []).append(edge_id)
        incidence.setdefault(str(node_b), []).append(edge_id)
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": port_id_to_slot(port_a)},
                "endpoint_b": {"node_id": node_b, "slot": port_id_to_slot(port_b)},
                "payload": {},
            }
        )
    return {
        "nodes": [{"node_id": node_id, "payload": {}} for node_id in sorted(node_ids)],
        "edges": sorted(edges, key=lambda item: int(item["edge_id"])),
        "incidence": {
            node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
        },
        "port_structure": {},
    }


def _port_edge(
    *,
    node_u: int,
    port_u: int,
    node_v: int,
    port_v: int,
    conductance: float = 1.0,
    flux_uv: float = 0.0,
) -> dict[str, int | float]:
    return {
        "node_u": node_u,
        "port_u": port_u,
        "node_v": node_v,
        "port_v": port_v,
        "conductance": conductance,
        "flux_uv": flux_uv,
    }


def _spark_state(
    active_degree: int,
    *,
    signed_hessian: tuple[float, float, float] = (-0.1, 0.2, 0.3),
) -> dict[str, object]:
    connections = [
        (port_id - 1, 0, port_id, port_id, 1)
        for port_id in range(1, active_degree + 1)
    ]
    nodes: dict[str, dict[str, object]] = {
        "0": {
            "coherence": 9.0,
            "gradient_row_basis": [0.0, 0.0, 0.0],
            "signed_hessian_row_basis": list(signed_hessian),
            "basin_mass": 9.0,
            "basin_id": "root",
            "depth": 0,
        }
    }
    port_edges: dict[str, dict[str, int | float]] = {}
    for port_id in range(1, active_degree + 1):
        nodes[str(port_id)] = {
            "coherence": 1.0,
            "gradient_row_basis": [1.0, 0.0, 0.0],
            "signed_hessian_row_basis": [1.0, 1.0, 1.0],
            "basin_mass": 1.0,
            "basin_id": port_id,
        }
        port_edges[str(port_id - 1)] = _port_edge(
            node_u=0,
            port_u=port_id,
            node_v=port_id,
            port_v=1,
        )
    return {
        "topology": _topology(connections, extra_nodes=(0,)),
        "nodes": nodes,
        "port_edges": port_edges,
        "sink_set": [0],
        "basins": {"0": sorted(int(node_id) for node_id in nodes)},
    }


def _schema_json_blocks(text: str) -> list[dict[str, object]]:
    return [
        json.loads(match.group(1))
        for match in _JSON_BLOCK_PATTERN.finditer(text)
    ]


def _json_block_with_key(
    blocks: list[dict[str, object]],
    key: str,
) -> dict[str, object]:
    for block in blocks:
        if key in block:
            return block
    raise AssertionError(f"schema JSON block with key {key!r} was not found")


def _json_section_with_key(
    blocks: list[dict[str, object]],
    section_name: str,
    field_name: str,
) -> dict[str, object]:
    for block in blocks:
        section = block.get(section_name)
        if isinstance(section, dict) and field_name in section:
            return section
    raise AssertionError(
        f"schema JSON section {section_name!r} with field {field_name!r} was not found"
    )


class GRC9V3HessianReadinessConformanceTest(unittest.TestCase):
    """Lock the current-hybrid Lane A surface before property experiments."""

    def test_port_row_column_mapping_is_total_for_all_nine_ports(self) -> None:
        expected = {
            1: (1, 1),
            2: (1, 2),
            3: (1, 3),
            4: (2, 1),
            5: (2, 2),
            6: (2, 3),
            7: (3, 1),
            8: (3, 2),
            9: (3, 3),
        }

        for port_id, row_column in expected.items():
            with self.subTest(port_id=port_id):
                self.assertEqual(row_column, port_to_rc(port_id))
                self.assertEqual(port_id, rc_to_port(*row_column))
                self.assertEqual(port_id - 1, port_id_to_slot(port_id))
                self.assertEqual(port_id, slot_to_port_id(port_id - 1))

    def test_zero_partial_and_saturated_active_degree_are_distinguished(self) -> None:
        zero_model = GRC9V3.from_state(state=_spark_state(0), params=_params())
        partial_model = GRC9V3.from_state(state=_spark_state(8), params=_params())
        saturated_model = GRC9V3.from_state(state=_spark_state(9), params=_params())

        self.assertEqual(0, len(tuple(zero_model.get_state().topology.incident_edge_ids(0))))
        self.assertEqual(8, len(tuple(partial_model.get_state().topology.incident_edge_ids(0))))
        self.assertEqual(9, len(tuple(saturated_model.get_state().topology.incident_edge_ids(0))))
        self.assertFalse(
            partial_model.get_state().topology.port_is_occupied(0, port_id_to_slot(9))
        )

        self.assertEqual([], zero_model.detect_hybrid_spark_candidates())
        self.assertEqual([], partial_model.detect_hybrid_spark_candidates())
        candidates = saturated_model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        self.assertEqual(9, candidates[0].payload["active_degree"])
        self.assertTrue(candidates[0].payload["saturation_gate"])
        self.assertTrue(candidates[0].payload["basin_interior_gate"])
        self.assertTrue(candidates[0].payload["signed_hessian_degeneracy_gate"])

    def test_positive_eps_spark_accepts_exact_hessian_degeneracy(self) -> None:
        model = GRC9V3.from_state(
            state=_spark_state(9, signed_hessian=(0.0, 0.2, 0.3)),
            params=_params(evolution_overrides={"eps_spark": 1e-6}),
        )

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual(1, len(candidates))
        self.assertEqual(0.0, candidates[0].payload["min_signed_hessian"])
        self.assertTrue(candidates[0].payload["signed_hessian_degeneracy_gate"])

    def test_inactive_port_does_not_contribute_to_fields_or_continuity(self) -> None:
        model = GRC9V3.from_state(state=_spark_state(8), params=_params())

        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.apply_continuity()
        state = model.get_state()

        self.assertFalse(state.topology.port_is_occupied(0, port_id_to_slot(9)))
        self.assertEqual([6, 7], state.cached_quantities["row_neighborhoods"]["0"]["3"])
        self.assertEqual(list(range(8)), state.cached_quantities["continuity_live_edge_ids"])
        self.assertEqual(0.0, model._build_nonnegative_port_field(field_name="conductance")[0][9])
        self.assertEqual(0.0, model._build_signed_flux_port_field()[0][9])

    def test_endpoint_ports_and_signed_flux_orientation_are_canonicalized(self) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology([(0, 1, 1, 0, 1)]),
                "nodes": {
                    "0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0},
                    "1": {"coherence": 2.0, "basin_mass": 2.0, "basin_id": 1},
                },
                "port_edges": {
                    "0": _port_edge(
                        node_u=1,
                        port_u=1,
                        node_v=0,
                        port_v=1,
                        conductance=1.0,
                        flux_uv=2.5,
                    )
                },
            },
            params=_params(),
        )

        edge = model.get_state().port_edges[0]

        self.assertEqual(0, edge.node_u)
        self.assertEqual(1, edge.port_u)
        self.assertEqual(1, edge.node_v)
        self.assertEqual(1, edge.port_v)
        self.assertEqual(-2.5, edge.flux_uv)
        flux_from_0 = model._oriented_flux(edge_id=0, node_id=0)
        flux_from_1 = model._oriented_flux(edge_id=0, node_id=1)
        self.assertEqual(-2.5, flux_from_0)
        self.assertEqual(2.5, flux_from_1)
        self.assertEqual(flux_from_0, -flux_from_1)

    def test_differential_transport_and_edge_labels_are_available(self) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology([(0, 0, 1, 1, 1)]),
                "nodes": {
                    "0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0},
                    "1": {"coherence": 3.0, "basin_mass": 3.0, "basin_id": 1},
                },
                "port_edges": {
                    "0": _port_edge(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=0.5,
                    )
                },
            },
            params=_params(),
        )

        model.rebuild_differential_state()
        differential_state = model.get_state()
        self.assertEqual(
            "row_basis_diagonal",
            differential_state.cached_quantities["hessian_backend"],
        )
        self.assertEqual([2.0, 0.0, 0.0], differential_state.nodes[0].gradient_row_basis)
        self.assertEqual(
            [2.0, 0.0, 0.0],
            differential_state.nodes[0].signed_hessian_row_basis,
        )
        self.assertEqual([0.0, 0.0, 0.0], differential_state.nodes[0].net_flux_summary)

        model.rebuild_transport_state()
        state = model.get_state()

        self.assertEqual("row_basis_diagonal", state.cached_quantities["hessian_backend"])
        self.assertEqual(3, len(state.nodes[0].gradient_row_basis))
        self.assertEqual(3, len(state.nodes[0].signed_hessian_row_basis))
        self.assertEqual(3, len(state.nodes[0].net_flux_summary))
        self.assertIn(0, state.base_conductance)
        self.assertIn(0, state.geometric_length)
        self.assertIn(0, state.temporal_delay)
        self.assertIn(0, state.flux_coupling)
        self.assertAlmostEqual(1.0, state.base_conductance[0])
        self.assertAlmostEqual(1.0, state.geometric_length[0])
        self.assertAlmostEqual(4.0, state.flux_coupling[0])
        self.assertAlmostEqual(0.2, state.temporal_delay[0])

    def test_sink_basin_hierarchy_is_available_before_spark_events(self) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology([], extra_nodes=(0,)),
                "nodes": {"0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0}},
            },
            params=_params(),
        )
        state = model.get_state()

        self.assertEqual({}, state.hierarchy)
        self.assertEqual({}, state.basins)
        self.assertEqual(model.get_params().params_hash, state.params_identity)

    def test_spark_expansion_budget_and_hierarchy_payloads_are_direct(self) -> None:
        model = build_representative_hybrid_model()

        result = model.step()
        events = {event.kind: event for event in result.events}
        state = model.get_state()

        candidate_payload = events["hybrid_spark_candidate"].payload
        expansion_payload = events["hybrid_mechanical_expansion"].payload
        completed_payload = events["hybrid_spark_completed"].payload

        self.assertLessEqual(
            {
                "sink_node_id",
                "candidate_node_id",
                "active_degree",
                "saturation_gate",
                "basin_interior_gate",
                "signed_hessian_degeneracy_gate",
                "min_signed_hessian",
            },
            set(candidate_payload),
        )
        self.assertIn("reassignment_map", expansion_payload)
        self.assertEqual(9, len(expansion_payload["reassignment_map"]))
        self.assertAlmostEqual(
            expansion_payload["budget_before"],
            expansion_payload["budget_after"],
        )
        self.assertEqual(0.0, expansion_payload["budget_error"])
        self.assertEqual(
            expansion_payload["reassignment_map"],
            state.cached_quantities["last_hybrid_expansion"]["reassignment_map"],
        )
        self.assertEqual([12, 16], completed_payload["stabilized_child_node_ids"])
        self.assertEqual({"root": ["12", "16"]}, state.hierarchy)

    def test_zero_column_profile_and_signed_flux_j_split_reconstruct_exactly(self) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology(
                    [
                        (0, 0, 1, 1, 1),
                        (1, 0, 4, 2, 1),
                    ]
                ),
                "nodes": {
                    "0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0},
                    "1": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 1},
                    "2": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 2},
                },
                "port_edges": {
                    "0": _port_edge(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=2.0,
                        flux_uv=2.5,
                    ),
                    "1": _port_edge(
                        node_u=0,
                        port_u=4,
                        node_v=2,
                        port_v=1,
                        conductance=4.0,
                        flux_uv=-1.5,
                    ),
                },
            },
            params=_params(),
        )

        conductance_coarse = model.coarse_grain_columns("conductance")
        conductance_reconstructed = model.split_columns(conductance_coarse)
        signed_flux_coarse = model.coarse_grain_columns("signed_flux")
        signed_flux_reconstructed = model.split_columns(signed_flux_coarse)

        self.assertEqual([6.0, 0.0, 0.0], conductance_coarse["by_node"]["0"]["column_totals"])
        self.assertEqual([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], conductance_coarse["by_node"]["0"]["profiles"][1])
        self.assertEqual([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], conductance_coarse["by_node"]["0"]["profiles"][2])
        for port_id in ("2", "3", "5", "6", "8", "9"):
            with self.subTest(port_id=port_id):
                self.assertEqual(0.0, conductance_reconstructed["port_field"]["0"][port_id])
        self.assertEqual("signed_flux_split", signed_flux_coarse["mode"])
        self.assertEqual(
            [2.5, 0.0, 0.0],
            signed_flux_coarse["positive"]["by_node"]["0"]["column_totals"],
        )
        self.assertEqual(
            [1.5, 0.0, 0.0],
            signed_flux_coarse["negative"]["by_node"]["0"]["column_totals"],
        )
        self.assertEqual(
            [1.0, 0.0, 0.0],
            signed_flux_coarse["positive"]["by_node"]["0"]["profiles"][0],
        )
        self.assertEqual(
            [0.0, 1.0, 0.0],
            signed_flux_coarse["negative"]["by_node"]["0"]["profiles"][0],
        )
        self.assertEqual(2.5, signed_flux_reconstructed["port_field"]["0"]["1"])
        self.assertEqual(-1.5, signed_flux_reconstructed["port_field"]["0"]["4"])

    def test_snapshot_uses_runtime_groups_documented_for_artifact_extraction(self) -> None:
        model = build_representative_hybrid_model()
        result = model.step()

        snapshot = model.snapshot()

        self.assertLessEqual(
            {
                "metadata",
                "topology",
                "basin_attributes",
                "edge_labels",
                "dynamics",
                "observables",
                "events",
                "caches",
            },
            set(snapshot),
        )
        self.assertNotIn("family_extensions", snapshot)
        self.assertIn("nodes", snapshot["basin_attributes"])
        self.assertIn("hierarchy", snapshot["basin_attributes"])
        self.assertIn("expansion_registry", snapshot["basin_attributes"])
        self.assertIn("base_conductance", snapshot["edge_labels"])
        self.assertIn("geometric_length", snapshot["edge_labels"])
        self.assertIn("temporal_delay", snapshot["edge_labels"])
        self.assertIn("flux_coupling", snapshot["edge_labels"])
        self.assertIn("state", snapshot["dynamics"])
        self.assertIn("port_edges", snapshot["dynamics"]["state"])
        self.assertIn("cached_quantities", snapshot["dynamics"]["state"])
        self.assertIn("coarse_cache", snapshot["caches"])

        expansion_event = {
            event.kind: event for event in result.events
        }["hybrid_mechanical_expansion"]
        expansion_id = expansion_event.payload["expansion_id"]
        registry_record = snapshot["basin_attributes"]["expansion_registry"][expansion_id]

        self.assertLessEqual(
            {
                "parent_sink_id",
                "module_node_ids",
                "expansion_step",
                "distribution_weights",
                "schedule",
            },
            set(registry_record),
        )
        self.assertNotIn("reassignment_map", registry_record)

        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot_path = Path(temp_dir) / "grc9v3_snapshot.json"
            model.save(str(snapshot_path))
            restored = GRC9V3.load(str(snapshot_path))
        restored_snapshot = restored.snapshot()

        self.assertEqual("GRC9V3", restored_snapshot["metadata"]["model_family"])
        self.assertEqual(
            snapshot["metadata"]["params_hash"],
            restored_snapshot["metadata"]["params_hash"],
        )
        self.assertIn("basin_attributes", restored_snapshot)
        self.assertIn("edge_labels", restored_snapshot)
        self.assertIn("dynamics", restored_snapshot)

    def test_lane_a_trace_schema_documents_minimal_contract(self) -> None:
        text = _TRACE_SCHEMA_PATH.read_text(encoding="utf-8")
        blocks = _schema_json_blocks(text)

        required_fields = (
            "schema_id",
            "spark_lane_id",
            "candidate_event.event_kind",
            "candidate_event.step_index",
            "candidate_event.candidate_node_id",
            "lane_a_gate_evidence.active_degree",
            "lane_a_gate_evidence.saturation_gate",
            "row_differential_evidence.gradient_norm",
            "row_differential_evidence.eps_gradient",
            "signed_hessian_evidence.min_signed_hessian",
            "signed_hessian_evidence.eps_spark",
            "signed_hessian_evidence.signed_hessian_degeneracy_gate",
            "mechanical_expansion_followup.present",
            "identity_event_followup.present",
            "derived_column_h_proxy.status",
            "derived_column_h_proxy.predicate_role",
            "derived_column_h_proxy.formula_status",
        )

        top_level = _json_block_with_key(blocks, "schema_id")
        self.assertEqual(
            "grc9v3_lane_a_spark_gate_trace_v1",
            top_level["schema_id"],
        )
        self.assertEqual("current_hybrid_signed_hessian", top_level["spark_lane_id"])

        run = _json_section_with_key(blocks, "run", "dt")
        self.assertEqual("number|null", run["dt"])
        self.assertIn("artifact_source", run)

        candidate_event = _json_section_with_key(
            blocks,
            "candidate_event",
            "candidate_node_id",
        )
        self.assertEqual("hybrid_spark_candidate", candidate_event["event_kind"])
        self.assertEqual("integer", candidate_event["step_index"])
        self.assertEqual("number|null", candidate_event["time"])
        self.assertEqual("integer", candidate_event["candidate_node_id"])

        gate_evidence = _json_section_with_key(
            blocks,
            "lane_a_gate_evidence",
            "candidate_condition",
        )
        self.assertEqual("boolean|null", gate_evidence["candidate_condition"])
        self.assertEqual(["derived_column_h_proxy"], gate_evidence["not_a_gate"])

        expansion = _json_section_with_key(
            blocks,
            "mechanical_expansion_followup",
            "reassignment_map_source",
        )
        self.assertIn("snapshot_basin_attributes_expansion_registry", expansion["reassignment_map_source"])

        blocked_proxy = next(
            block for block in blocks
            if block.get("status") == "blocked"
            and block.get("predicate_role") == "analysis_proxy_only"
        )
        self.assertEqual("undefined_in_iteration_3", blocked_proxy["formula_status"])
        self.assertIsNone(blocked_proxy["formula_version"])
        self.assertIsNone(blocked_proxy["near_zero_threshold"])

        proxy = _json_section_with_key(
            blocks,
            "derived_column_h_proxy",
            "candidate_source_artifact_fields",
        )
        self.assertEqual("analysis_proxy_only", proxy["predicate_role"])
        self.assertIn("snapshot.dynamics.state.port_edges", proxy["candidate_source_artifact_fields"])
        stale_overlay_path = ".".join(
            ("checkpoint", "family_extensions", "grc9v3", "port_overlays")
        )
        self.assertNotIn(stale_overlay_path, proxy["candidate_source_artifact_fields"])

        self.assertIn("## Telemetry Contract Mapping", text)
        self.assertIn('"candidate_condition": "boolean|null"', text)
        self.assertIn('"time": "number|null"', text)
        self.assertIn('"dt": "number|null"', text)
        self.assertIn('"formula_status": "undefined_in_iteration_3"', text)
        self.assertIn("No `grc9v3_column_h_proxy_v0` formula is defined", text)
        self.assertNotIn(
            '"candidate_condition": "saturation_gate AND basin_interior_gate',
            text,
        )

        for field_name in required_fields:
            with self.subTest(field_name=field_name):
                self.assertIn(f"- `{field_name}`", text)

        telemetry_fields = {
            "GRC9V3SparkEvidence": {
                field.name for field in fields(GRC9V3SparkEvidence)
            },
            "GRC9V3ExpansionEvidence": {
                field.name for field in fields(GRC9V3ExpansionEvidence)
            },
            "GRC9V3CompletionEvidence": {
                field.name for field in fields(GRC9V3CompletionEvidence)
            },
        }
        expected_telemetry_fields = {
            "GRC9V3SparkEvidence": (
                "candidate_node_id",
                "sink_node_id",
                "active_degree",
                "saturation_gate",
                "basin_interior_gate",
                "gradient_norm",
                "signed_hessian_degeneracy_gate",
                "min_signed_hessian",
                "signed_crossing_enabled",
                "signed_crossing_gate",
                "depth",
            ),
            "GRC9V3ExpansionEvidence": (
                "parent_sink_id",
                "module_node_ids",
                "budget_before",
                "budget_after",
                "budget_error",
                "budget_preservation_path",
                "reassignment_count",
            ),
            "GRC9V3CompletionEvidence": (
                "stabilized_child_node_ids",
                "stable_child_basin_count",
                "hierarchy_parent",
                "hierarchy_children",
            ),
        }

        for class_name, field_names in expected_telemetry_fields.items():
            for field_name in field_names:
                with self.subTest(class_name=class_name, field_name=field_name):
                    self.assertIn(field_name, telemetry_fields[class_name])
                    self.assertIn(f"`{class_name}.{field_name}`", text)

    def test_theory_runtime_gap_ledger_has_expected_surface_classification(self) -> None:
        ledger = json.loads(_GAP_LEDGER_PATH.read_text(encoding="utf-8"))
        surfaces = {entry["id"]: entry for entry in ledger["surfaces"]}

        self.assertEqual("current_hybrid_signed_hessian", ledger["spark_lane_id"])
        self.assertEqual("deferred_not_rejected", ledger["lane_b_status"])
        self.assertEqual(9, len(surfaces))
        self.assertEqual(7, ledger["summary"]["direct_surface_count"])
        self.assertEqual(1, ledger["summary"]["derived_surface_count"])
        self.assertEqual(1, ledger["summary"]["partial_surface_count"])
        self.assertEqual(0, ledger["summary"]["absent_surface_count"])

        expected_statuses = {
            "row_differential_state": "direct",
            "signed_hessian_hybrid_spark_candidate": "direct",
            "active_degree_saturation": "direct",
            "mechanical_expansion_mapping": "direct",
            "edge_labels": "direct",
            "coarse_graining_split": "direct",
            "sink_basin_hierarchy": "direct",
            "column_h_cancellation_diagnostic": "derived",
            "full_port_history_motion_observer": "partial",
        }
        for surface_id, expected_status in expected_statuses.items():
            with self.subTest(surface_id=surface_id):
                surface = surfaces[surface_id]
                self.assertEqual(expected_status, surface["lane_a_status"])
                self.assertTrue(surface["theory_facing_meaning"])
                self.assertTrue(surface["artifact_sources"])
                self.assertTrue(surface["experiment_impact"])
                self.assertIn("blocked_claims", surface)
                self.assertTrue(surface["required_change_for_lane_b"])

        column_h = surfaces["column_h_cancellation_diagnostic"]
        self.assertIn("Direct column-H triggered the spark is blocked in Lane A.", column_h["blocked_claims"])
        self.assertIn("canonical_column_h", column_h["required_change_for_lane_b"])

        motion = surfaces["full_port_history_motion_observer"]
        self.assertIn("ordered snapshot/checkpoint sequences", motion["artifact_sources"])


if __name__ == "__main__":
    unittest.main()
