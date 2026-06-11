"""Tests for GRCL-9V3 Revision 1 lowering into GRC9V3State."""

from __future__ import annotations

from collections import deque
import json
import unittest
from typing import Any

from pygrc.core import GRCParams
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3_SOURCE_FIXTURE_NAMES,
    GRCL9V3GrowthLocus,
    GRCL9V3HybridSparkRegion,
    GRCL9V3SourceDocument,
    default_grcl9v3_source_fixtures,
    grcl9v3_source_fixture_by_name,
)
from pygrc.models import (
    GRC9V3,
    GRCL9V3_PROJECTOR_REVISION,
    GRC9V3State,
    lower_grcl9v3_fixture_by_name,
    lower_grcl9v3_source_to_grc9v3_state,
)


class GRCL9V3LowererTest(unittest.TestCase):
    def test_all_default_fixtures_lower_to_connected_grc9v3_states(self) -> None:
        for fixture in default_grcl9v3_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                result = lower_grcl9v3_source_to_grc9v3_state(fixture)
                state = result.state

                self.assertIsInstance(state, GRC9V3State)
                self.assertTrue(_is_connected(state))
                for node_id in state.topology.iter_live_node_ids():
                    occupied = [
                        slot
                        for slot in state.topology.iter_port_slots(node_id)
                        if state.topology.port_is_occupied(node_id, slot)
                    ]
                    self.assertLessEqual(len(occupied), 9)
                self.assertAlmostEqual(
                    sum(node.coherence for node in state.nodes.values()),
                    state.budget_target,
                )

    def test_lowering_is_deterministic_and_does_not_mutate_source(self) -> None:
        fixture = grcl9v3_source_fixture_by_name()["hybrid_spark_gate_positive_control"]
        before = fixture.to_mapping()

        first = lower_grcl9v3_source_to_grc9v3_state(fixture)
        second = lower_grcl9v3_source_to_grc9v3_state(fixture)

        self.assertEqual(before, fixture.to_mapping())
        self.assertEqual(_state_signature(first.state), _state_signature(second.state))

    def test_lowering_accepts_mapping_input(self) -> None:
        fixture = grcl9v3_source_fixture_by_name()["growth_pressure_positive_control"]
        result = lower_grcl9v3_source_to_grc9v3_state(fixture.to_mapping())

        self.assertEqual("growth_pressure_positive_control", result.source.fixture_name)
        self.assertIsInstance(result.state, GRC9V3State)

    def test_lowering_initializes_replay_rng_state(self) -> None:
        state = lower_grcl9v3_fixture_by_name("quiescent_hybrid_control_no_event_control").state

        self.assertIsNotNone(state.rng_state)
        self.assertEqual("grcl9v3_lowering_params", state.cached_quantities["rng_seed_source"])
        self.assertEqual(0, state.cached_quantities["rng_seed"])

    def test_provenance_covers_every_lowered_node_and_edge(self) -> None:
        for fixture in default_grcl9v3_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                state = lower_grcl9v3_source_to_grc9v3_state(fixture).state
                provenance = state.cached_quantities["grcl9v3_provenance"]
                node_ids = {str(node_id) for node_id in state.topology.iter_live_node_ids()}
                edge_ids = {str(edge_id) for edge_id in state.topology.iter_live_edge_ids()}

                self.assertEqual(node_ids, set(provenance["nodes"]))
                self.assertEqual(edge_ids, set(provenance["edges"]))
                for node_id in state.topology.iter_live_node_ids():
                    payload = state.topology.node_payload(node_id)
                    self.assertEqual(
                        GRCL9V3_PROJECTOR_REVISION,
                        payload["grcl9v3_projector_revision"],
                    )
                    self.assertIn("grcl9v3_construct_id", payload)
                    self.assertIn("grcl9v3_motif_role", payload)
                    self.assertIn("grcl9v3_ownership", payload)
                for edge_id in state.topology.iter_live_edge_ids():
                    payload = state.topology.edge_payload(edge_id)
                    self.assertEqual(
                        GRCL9V3_PROJECTOR_REVISION,
                        payload["grcl9v3_projector_revision"],
                    )
                    self.assertIn("grcl9v3_construct_id", payload)
                    self.assertIn("grcl9v3_edge_kind", payload)
                    self.assertIn("grcl9v3_ownership", payload)

    def test_expected_region_caches_are_populated(self) -> None:
        spark_state = lower_grcl9v3_fixture_by_name(
            "hybrid_spark_gate_positive_control"
        ).state
        self.assertEqual(
            1,
            len(spark_state.cached_quantities["grcl9v3_expected_saturated_node_ids"]),
        )
        self.assertEqual(
            spark_state.cached_quantities["grcl9v3_expected_saturated_node_ids"],
            spark_state.cached_quantities["grcl9v3_expected_tensor_hotspot_node_ids"],
        )
        self.assertEqual(
            spark_state.cached_quantities["grcl9v3_expected_saturated_node_ids"],
            spark_state.cached_quantities["grcl9v3_expected_hessian_profile_node_ids"],
        )
        self.assertEqual(
            spark_state.cached_quantities["grcl9v3_expected_saturated_node_ids"],
            spark_state.cached_quantities["grcl9v3_expected_column_proxy_node_ids"],
        )

        expansion_state = lower_grcl9v3_fixture_by_name(
            "spark_to_expansion_positive_control"
        ).state
        self.assertEqual(
            1,
            len(expansion_state.cached_quantities["grcl9v3_expected_expansion_region_ids"]),
        )
        self.assertFalse(expansion_state.expansion_registry)

        choice_state = lower_grcl9v3_fixture_by_name("choice_collapse_positive_control").state
        self.assertEqual(
            2,
            len(choice_state.cached_quantities["grcl9v3_expected_choice_region_ids"]),
        )

        growth_state = lower_grcl9v3_fixture_by_name("growth_pressure_positive_control").state
        self.assertEqual(
            1,
            len(growth_state.cached_quantities["grcl9v3_expected_growth_locus_ids"]),
        )
        self.assertEqual(
            "legacy_diagnostic",
            growth_state.cached_quantities["grcl9v3_growth_semantics_status"],
        )
        self.assertTrue(growth_state.cached_quantities["grcl9v3_legacy_growth_locus_ids"])

        transport_state = lower_grcl9v3_fixture_by_name(
            "transport_basin_rerouting_positive_control"
        ).state
        self.assertEqual(
            3,
            len(transport_state.cached_quantities["grcl9v3_expected_transport_region_ids"]),
        )

        quiescent_state = lower_grcl9v3_fixture_by_name(
            "quiescent_hybrid_control_no_event_control"
        ).state
        self.assertEqual(
            1,
            len(quiescent_state.cached_quantities["grcl9v3_expected_quiescent_region_ids"]),
        )

        appendix_state = lower_grcl9v3_fixture_by_name(
            "appendix_e_cell_division_positive_control"
        ).state
        self.assertEqual(
            3,
            len(appendix_state.cached_quantities["grcl9v3_expected_appendix_e_region_ids"]),
        )

    def test_front_capacity_growth_provenance_is_cached(self) -> None:
        document = _front_growth_document()

        state = lower_grcl9v3_source_to_grc9v3_state(document).state
        sources = state.cached_quantities["grcl9v3_growth_parent_capacity_sources"]
        eligible_ports = state.cached_quantities["grcl9v3_front_growth_eligible_ports"]

        self.assertEqual("front_capacity", state.cached_quantities["grcl9v3_growth_semantics_status"])
        self.assertFalse(state.cached_quantities["grcl9v3_legacy_growth_locus_ids"])
        self.assertEqual(1, len(sources))
        parent_id = next(iter(sources))
        self.assertEqual("spark_expansion_front", sources[parent_id]["front_capacity_source"])
        self.assertEqual([5], eligible_ports[parent_id])

    def test_pressure_boundary_front_capacity_is_cached_as_expected_region(self) -> None:
        document = _pressure_boundary_growth_document()

        state = lower_grcl9v3_source_to_grc9v3_state(document).state
        sources = state.cached_quantities["grcl9v3_growth_parent_capacity_sources"]
        expected_regions = state.cached_quantities[
            "grcl9v3_expected_pressure_boundary_region_ids"
        ]

        self.assertEqual("front_capacity", state.cached_quantities["grcl9v3_growth_semantics_status"])
        self.assertEqual(1, len(expected_regions))
        parent_id = str(expected_regions[0])
        self.assertIn(parent_id, sources)
        self.assertEqual("pressure_boundary", sources[parent_id]["front_capacity_source"])
        self.assertEqual([6], state.cached_quantities["grcl9v3_front_growth_eligible_ports"][parent_id])

    def test_front_capacity_growth_gates_parent_port_selection(self) -> None:
        params = GRCParams.from_mapping(
            {
                "dt": 0.1,
                "evolution": {
                    "lambda_birth": 100.0,
                    "alpha_seed": 0.25,
                    "w_bond": 1.0,
                    "rng_seed": 0,
                },
                "constitutive_semantic_modes": {
                    "growth_parent_eligibility": "grcl9v3_front_capacity",
                },
            }
        )
        lowered = lower_grcl9v3_source_to_grc9v3_state(
            _front_growth_document(),
            params=params,
        )
        model = GRC9V3(
            params=params,
            state=lowered.state,
        )

        events = model.apply_growth()

        self.assertEqual(["growth"], [event.kind for event in events])
        self.assertEqual(5, events[0].payload["parent_port_id"])
        self.assertEqual("grcl9v3_front_capacity", events[0].payload["growth_parent_eligibility_mode"])
        self.assertEqual("spark_expansion_front", events[0].payload["growth_parent_capacity_source"])

    def test_front_capacity_growth_can_propagate_bounded_child_front(self) -> None:
        params = GRCParams.from_mapping(
            {
                "dt": 0.1,
                "evolution": {
                    "lambda_birth": 100.0,
                    "alpha_seed": 0.25,
                    "w_bond": 1.0,
                    "rng_seed": 0,
                },
                "constitutive_semantic_modes": {
                    "growth_parent_eligibility": "grcl9v3_front_capacity",
                },
            }
        )
        motif_id = "grc9v3-motif-s0006-hybrid-spark-gate-positive-control"
        document = GRCL9V3SourceDocument(
            fixture_name="propagated_front_growth_fixture",
            manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
            expected_selector_ids=("front_growth_provenance",),
            constructs=(
                GRCL9V3HybridSparkRegion(
                    construct_id="spark_region",
                    motif_id=motif_id,
                    source_role="positive_control",
                    ownership="grc9v3_hybrid",
                    candidate_region_id="candidate",
                    saturation_profile={"active_degree": 9},
                    spark_threshold=0.05,
                ),
                GRCL9V3GrowthLocus(
                    construct_id="front_growth",
                    motif_id=motif_id,
                    source_role="positive_control",
                    ownership="grc9_mechanical",
                    parent_region_id="growth_parent",
                    inactive_parent_port=5,
                    outward_pressure_profile={
                        "pressure": "front",
                        "propagate_child_front": True,
                        "child_front_port": 2,
                        "child_front_max_depth": 1,
                        "child_front_activation_delay_steps": 3,
                    },
                    lambda_birth=1.0,
                    growth_semantics="front_capacity",
                    front_capacity_source="spark_expansion_front",
                    front_source_construct_id="spark_region",
                ),
            ),
            notes={
                "composed_source_ancestry": (
                    "corrected_front_growth_positive_control",
                    "corrected_multi_center_relay_attempt",
                )
            },
            compiled_source_provenance={
                "composed_source_ancestry": (
                    "corrected_front_growth_positive_control",
                    "corrected_multi_center_relay_attempt",
                )
            },
        )
        lowered = lower_grcl9v3_source_to_grc9v3_state(document, params=params)
        model = GRC9V3(params=params, state=lowered.state)

        events = model.apply_growth()

        self.assertEqual(["growth"], [event.kind for event in events])
        child_id = str(events[0].payload["child_node_id"])
        eligible_ports = model._state.cached_quantities["grcl9v3_front_growth_eligible_ports"]
        sources = model._state.cached_quantities["grcl9v3_growth_parent_capacity_sources"]
        self.assertEqual([2], eligible_ports[child_id])
        self.assertEqual("propagated_front_growth", sources[child_id]["front_capacity_source"])
        self.assertEqual(1, sources[child_id]["front_generation_depth"])
        self.assertEqual(3, sources[child_id]["front_activation_step_index"])

    def test_appendix_e_fixtures_use_explicit_bridge_edges(self) -> None:
        for fixture_name in (
            "appendix_e_cell_division_positive_control",
            "appendix_e_cell_division_negative_control",
        ):
            with self.subTest(fixture=fixture_name):
                state = lower_grcl9v3_fixture_by_name(fixture_name).state
                bridge_edge_ids = state.cached_quantities["grcl9v3_bridge_edge_ids"]

                self.assertEqual(1, len(bridge_edge_ids))
                payload = state.topology.edge_payload(bridge_edge_ids[0])
                self.assertEqual("bridge", payload["grcl9v3_edge_kind"])
                self.assertEqual(True, payload["grcl9v3_bridge"])
                self.assertEqual("mechanism_isolation", payload["grcl9v3_bridge_role"])

    def test_assembly_policy_and_motif_registry_are_populated(self) -> None:
        result = lower_grcl9v3_fixture_by_name("spark_to_expansion_positive_control")
        state = result.state
        policy = state.cached_quantities["grcl9v3_assembly_policy"]
        registry = state.cached_quantities["grcl9v3_motif_registry"]

        self.assertEqual("deterministic_role_ordered_ports", policy["port_assignment_mode"])
        self.assertEqual("source_budget_partition", policy["mass_partition_mode"])
        self.assertEqual("bridge", policy["bridge_edge_policy"])
        self.assertEqual("row_basis_diagonal", policy["hessian_backend"])
        self.assertTrue(registry)
        motif_id = result.source.constructs[0].motif_id
        self.assertIn(motif_id, registry)
        self.assertTrue(registry[motif_id]["node_ids"])
        self.assertTrue(registry[motif_id]["edge_ids"])
        self.assertIn(
            "spark_to_expansion_positive_control_expansion_region",
            registry[motif_id]["source_construct_ids"],
        )

    def test_hessian_backend_default_is_source_owned_not_runtime_param_fallback(self) -> None:
        state = lower_grcl9v3_fixture_by_name(
            "quiescent_hybrid_control_no_event_control",
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "hessian_backend": "weighted_least_squares",
                },
            },
        ).state

        policy = state.cached_quantities["grcl9v3_assembly_policy"]
        self.assertEqual("row_basis_diagonal", policy["hessian_backend"])
        self.assertEqual("row_basis_diagonal", state.edge_label_params["hessian_backend"])

    def test_non_executable_constructs_are_rejected_by_lowerer(self) -> None:
        fixture = grcl9v3_source_fixture_by_name()["hybrid_spark_gate_positive_control"]
        construct = fixture.constructs[0]
        replacement = GRCL9V3HybridSparkRegion(
            construct_id=construct.construct_id,  # type: ignore[attr-defined]
            motif_id=construct.motif_id,  # type: ignore[attr-defined]
            source_role=construct.source_role,  # type: ignore[attr-defined]
            ownership=construct.ownership,  # type: ignore[attr-defined]
            expected_selector_ids=construct.expected_selector_ids,  # type: ignore[attr-defined]
            executable=False,
            non_claims=(
                "no_grcl9v3_lowering_result_claim",
                "no_runtime_event_claim",
                "no_lorentzian_causal_layer_claim",
                "no_visual_only_promotion",
                "runtime_evidence_required",
                "non_executable_source_construct",
            ),
            candidate_region_id=construct.candidate_region_id,  # type: ignore[attr-defined]
            saturation_profile=construct.saturation_profile,  # type: ignore[attr-defined]
            spark_gate_intent=construct.spark_gate_intent,  # type: ignore[attr-defined]
            spark_threshold=construct.spark_threshold,  # type: ignore[attr-defined]
        )
        document = type(fixture)(
            fixture_name=fixture.fixture_name,
            manifest_entry_id=fixture.manifest_entry_id,
            expected_selector_ids=fixture.expected_selector_ids,
            constructs=(replacement, *fixture.constructs[1:]),
            expected_telemetry=fixture.expected_telemetry,
            notes=fixture.notes,
        )

        with self.assertRaisesRegex(ValueError, "non-executable"):
            lower_grcl9v3_source_to_grc9v3_state(document)

    def test_duplicate_construct_kinds_are_rejected_by_lowerer(self) -> None:
        fixture = grcl9v3_source_fixture_by_name()["hybrid_spark_gate_positive_control"]
        construct = fixture.constructs[0]
        duplicate_spark = GRCL9V3HybridSparkRegion(
            construct_id="duplicate_spark_region",
            motif_id=construct.motif_id,  # type: ignore[attr-defined]
            source_role=construct.source_role,  # type: ignore[attr-defined]
            ownership=construct.ownership,  # type: ignore[attr-defined]
            candidate_region_id="duplicate_candidate",
            saturation_profile={"active_degree": 9},
        )
        duplicate = type(fixture)(
            fixture_name=fixture.fixture_name,
            manifest_entry_id=fixture.manifest_entry_id,
            expected_selector_ids=fixture.expected_selector_ids,
            constructs=(*fixture.constructs, duplicate_spark),
            expected_telemetry=fixture.expected_telemetry,
            notes=fixture.notes,
        )

        with self.assertRaisesRegex(ValueError, "unsupported repeats"):
            lower_grcl9v3_source_to_grc9v3_state(duplicate)

    def test_builtin_fixture_names_lower_by_name(self) -> None:
        for fixture_name in GRCL9V3_SOURCE_FIXTURE_NAMES:
            with self.subTest(fixture=fixture_name):
                result = lower_grcl9v3_fixture_by_name(fixture_name)
                self.assertEqual(fixture_name, result.source.fixture_name)


def _is_connected(state: GRC9V3State) -> bool:
    node_ids = tuple(state.topology.iter_live_node_ids())
    if not node_ids:
        return False
    seen = {node_ids[0]}
    queue: deque[int] = deque([node_ids[0]])
    while queue:
        node_id = queue.popleft()
        for neighbor in state.topology.neighbors(node_id):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen == set(node_ids)


def _state_signature(state: GRC9V3State) -> str:
    payload: dict[str, Any] = {
        "nodes": [
            [node_id, state.topology.node_payload(node_id), state.nodes[node_id]]
            for node_id in state.topology.iter_live_node_ids()
        ],
        "edges": [
            [
                edge_id,
                state.topology.edge_ports(edge_id),
                state.topology.edge_payload(edge_id),
                state.port_edges[edge_id],
            ]
            for edge_id in state.topology.iter_live_edge_ids()
        ],
        "budget_target": state.budget_target,
        "cached_quantities": state.cached_quantities,
    }
    return json.dumps(payload, sort_keys=True, default=lambda value: value.__dict__)


def _front_growth_document() -> GRCL9V3SourceDocument:
    motif_id = "grc9v3-motif-s0006-hybrid-spark-gate-positive-control"
    return GRCL9V3SourceDocument(
        fixture_name="front_growth_fixture",
        manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
        expected_selector_ids=("front_growth_provenance",),
        constructs=(
            GRCL9V3HybridSparkRegion(
                construct_id="spark_region",
                motif_id=motif_id,
                source_role="positive_control",
                ownership="grc9v3_hybrid",
                candidate_region_id="candidate",
                saturation_profile={"active_degree": 9},
                spark_threshold=0.05,
            ),
            GRCL9V3GrowthLocus(
                construct_id="front_growth",
                motif_id=motif_id,
                source_role="positive_control",
                ownership="grc9_mechanical",
                parent_region_id="growth_parent",
                inactive_parent_port=5,
                outward_pressure_profile={"pressure": "front"},
                lambda_birth=1.0,
                growth_semantics="front_capacity",
                front_capacity_source="spark_expansion_front",
                front_source_construct_id="spark_region",
            ),
        ),
        compiled_source_provenance={"composed_source_ancestry": ("spark", "growth")},
    )


def _pressure_boundary_growth_document() -> GRCL9V3SourceDocument:
    motif_id = "grc9v3-motif-s0006-growth-pressure-positive-control"
    return GRCL9V3SourceDocument(
        fixture_name="pressure_boundary_growth_fixture",
        manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
        expected_selector_ids=("pressure_boundary_growth_provenance",),
        constructs=(
            GRCL9V3GrowthLocus(
                construct_id="pressure_boundary_growth",
                motif_id=motif_id,
                source_role="positive_control",
                ownership="grc9_mechanical",
                parent_region_id="pressure_parent",
                inactive_parent_port=6,
                outward_pressure_profile={"pressure": "boundary_front"},
                lambda_birth=1.0,
                growth_semantics="front_capacity",
                front_capacity_source="pressure_boundary",
            ),
        ),
        compiled_source_provenance={
            "composed_source_ancestry": ("pressure_boundary", "growth")
        },
    )


if __name__ == "__main__":
    unittest.main()
