"""Tests for GRCL-9 Revision 1 lowering into GRC9State."""

from __future__ import annotations

from collections import deque
import json
import unittest
from typing import Any

from pygrc.landscapes.extensions.grcl9 import (
    GRCL9_SOURCE_FIXTURE_NAMES,
    GRCL9GrowthLocus,
    GRCL9SourceDocument,
    GRCL9SparkCandidateRegion,
    default_grcl9_source_fixtures,
    grcl9_source_fixture_by_name,
)
from pygrc.models import (
    GRCL9_PROJECTOR_REVISION,
    lower_grcl9_fixture_by_name,
    lower_grcl9_source_to_grc9_state,
)
from pygrc.models import GRC9State


class GRCL9LowererTest(unittest.TestCase):
    def test_all_default_fixtures_lower_to_connected_grc9_states(self) -> None:
        for fixture in default_grcl9_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                result = lower_grcl9_source_to_grc9_state(fixture)
                state = result.state

                self.assertIsInstance(state, GRC9State)
                self.assertTrue(_is_connected(state))
                for node_id in state.topology.iter_live_node_ids():
                    occupied = [
                        slot
                        for slot in state.topology.iter_port_slots(node_id)
                        if state.topology.port_is_occupied(node_id, slot)
                    ]
                    self.assertLessEqual(len(occupied), 9)
                self.assertAlmostEqual(
                    sum(state.node_coherence.values()),
                    state.budget_target,
                )

    def test_lowering_is_deterministic_and_does_not_mutate_source(self) -> None:
        fixture = grcl9_source_fixture_by_name()["spark_column_proxy_eps_pass"]
        before = fixture.to_mapping()

        first = lower_grcl9_source_to_grc9_state(fixture)
        second = lower_grcl9_source_to_grc9_state(fixture)

        self.assertEqual(before, fixture.to_mapping())
        self.assertEqual(_state_signature(first.state), _state_signature(second.state))

    def test_lowering_accepts_mapping_input(self) -> None:
        fixture = grcl9_source_fixture_by_name()["growth_pressure_lambda_high"]
        result = lower_grcl9_source_to_grc9_state(fixture.to_mapping())

        self.assertEqual("growth_pressure_lambda_high", result.source.fixture_name)
        self.assertIsInstance(result.state, GRC9State)

    def test_provenance_covers_every_lowered_node_and_edge(self) -> None:
        for fixture in default_grcl9_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                state = lower_grcl9_source_to_grc9_state(fixture).state
                provenance = state.cached_quantities["grcl9_provenance"]
                node_ids = {str(node_id) for node_id in state.topology.iter_live_node_ids()}
                edge_ids = {str(edge_id) for edge_id in state.topology.iter_live_edge_ids()}

                self.assertEqual(node_ids, set(provenance["nodes"]))
                self.assertEqual(edge_ids, set(provenance["edges"]))
                for node_id in state.topology.iter_live_node_ids():
                    payload = state.topology.node_payload(node_id)
                    self.assertEqual(GRCL9_PROJECTOR_REVISION, payload["grcl9_projector_revision"])
                    self.assertIn("grcl9_source_construct_id", payload)
                    self.assertIn("grcl9_motif_role", payload)
                for edge_id in state.topology.iter_live_edge_ids():
                    payload = state.topology.edge_payload(edge_id)
                    self.assertEqual(GRCL9_PROJECTOR_REVISION, payload["grcl9_projector_revision"])
                    self.assertIn("grcl9_source_construct_id", payload)
                    self.assertIn("grcl9_edge_kind", payload)

    def test_spark_fixtures_record_expected_candidate_caches(self) -> None:
        for fixture_name in (
            "spark_column_proxy_eps_pass",
            "spark_column_proxy_eps_fail",
            "spark_instability_tau_pass",
            "spark_instability_tau_fail",
            "spark_to_expansion_d_eff_low",
            "spark_to_expansion_d_eff_high",
        ):
            with self.subTest(fixture=fixture_name):
                state = lower_grcl9_fixture_by_name(fixture_name).state
                saturated = state.cached_quantities["grcl9_expected_saturated_node_ids"]
                self.assertEqual(1, len(saturated))
                self.assertEqual(9, len(tuple(state.topology.incident_edge_ids(saturated[0]))))

        column_state = lower_grcl9_fixture_by_name("spark_column_proxy_eps_pass").state
        self.assertEqual(
            column_state.cached_quantities["grcl9_expected_saturated_node_ids"],
            column_state.cached_quantities["grcl9_expected_column_proxy_candidate_ids"],
        )

    def test_fission_fixtures_use_explicit_bridge_edges(self) -> None:
        for fixture_name in (
            "post_expansion_fission_min_mass_pass",
            "post_expansion_fission_min_mass_fail",
        ):
            with self.subTest(fixture=fixture_name):
                state = lower_grcl9_fixture_by_name(fixture_name).state
                bridge_edge_ids = state.cached_quantities["grcl9_bridge_edge_ids"]

                self.assertEqual(1, len(bridge_edge_ids))
                payload = state.topology.edge_payload(bridge_edge_ids[0])
                self.assertEqual("bridge", payload["grcl9_edge_kind"])
                self.assertEqual(True, payload["grcl9_bridge"])
                self.assertEqual("mechanism_isolation", payload["grcl9_bridge_role"])

    def test_assembly_policy_and_motif_registry_are_populated(self) -> None:
        state = lower_grcl9_fixture_by_name("spark_to_expansion_d_eff_high").state
        policy = state.cached_quantities["grcl9_assembly_policy"]
        registry = state.cached_quantities["grcl9_motif_registry"]

        self.assertEqual("deterministic_role_ordered_ports", policy["port_assignment_mode"])
        self.assertEqual("source_budget_partition", policy["mass_partition_mode"])
        self.assertEqual("bridge", policy["bridge_edge_policy"])
        self.assertEqual("equal", policy["distribution_weight_mode"])
        self.assertIn("expansion_refinement", registry)
        self.assertTrue(registry["expansion_refinement"]["node_ids"])
        self.assertTrue(registry["expansion_refinement"]["edge_ids"])
        self.assertIn(
            "spark_to_expansion_d_eff_high_expansion_region",
            registry["expansion_refinement"]["source_construct_ids"],
        )

    def test_front_capacity_growth_lowers_to_grc9_runtime_caches(self) -> None:
        document = GRCL9SourceDocument(
            fixture_name="front_growth",
            manifest_entry_id="grcl9_lowering_growth_pressure_v1",
            expected_selector_ids=("front_growth_provenance",),
            constructs=(
                GRCL9SparkCandidateRegion(
                    construct_id="spark_region",
                    motif_id="growth_pressure",
                    candidate_id="candidate",
                    coherence_allocation={"candidate": 1.0},
                    neighbor_coherence_profile={"active_degree": 9},
                    spark_gate_intent="saturation_column_proxy",
                ),
                GRCL9GrowthLocus(
                    construct_id="front_growth",
                    motif_id="growth_pressure",
                    parent_id="candidate",
                    inactive_parent_port=5,
                    pressure_profile={"pressure": "front"},
                    lambda_birth=1.5,
                    growth_semantics="front_capacity",
                    front_capacity_source="spark_expansion_front",
                    front_source_construct_id="spark_region",
                ),
            ),
        )

        result = lower_grcl9_source_to_grc9_state(document)
        state = result.state
        growth_parent = result.node_id_by_role["growth_parent"]
        parent_key = str(growth_parent)

        self.assertEqual(
            [5],
            state.cached_quantities["grc9_front_growth_eligible_ports"][parent_key],
        )
        source = state.cached_quantities["grc9_growth_parent_capacity_sources"][
            parent_key
        ]
        self.assertEqual("front_capacity", source["growth_semantics"])
        self.assertEqual("spark_expansion_front", source["front_capacity_source"])
        self.assertEqual("spark_region", source["front_source_construct_id"])
        self.assertEqual(
            "front_capacity",
            state.cached_quantities["grcl9_growth_semantics_status"],
        )

    def test_legacy_growth_lowers_as_non_evidence_metadata_without_front_cache(self) -> None:
        result = lower_grcl9_fixture_by_name("growth_pressure_lambda_high")
        state = result.state
        growth_parent = result.node_id_by_role["growth_parent"]
        parent_key = str(growth_parent)

        self.assertEqual({}, state.cached_quantities["grc9_front_growth_eligible_ports"])
        self.assertEqual([growth_parent], state.cached_quantities["grcl9_legacy_growth_locus_ids"])
        self.assertEqual(
            "legacy_growth_locus",
            state.cached_quantities["grcl9_growth_semantics_status"],
        )
        source = state.cached_quantities["grc9_growth_parent_capacity_sources"][
            parent_key
        ]
        self.assertEqual("legacy_growth_locus", source["growth_semantics"])
        self.assertEqual("legacy_source_growth_locus", source["front_capacity_source"])

    def test_builtin_fixture_names_lower_by_name(self) -> None:
        for fixture_name in GRCL9_SOURCE_FIXTURE_NAMES:
            with self.subTest(fixture=fixture_name):
                result = lower_grcl9_fixture_by_name(fixture_name)
                self.assertEqual(fixture_name, result.source.fixture_name)


def _is_connected(state: GRC9State) -> bool:
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


def _state_signature(state: GRC9State) -> str:
    payload: dict[str, Any] = {
        "nodes": [
            [node_id, state.topology.node_payload(node_id)]
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
        "node_coherence": state.node_coherence,
        "budget_target": state.budget_target,
        "cached_quantities": state.cached_quantities,
    }
    return json.dumps(payload, sort_keys=True, default=lambda value: value.__dict__)


if __name__ == "__main__":
    unittest.main()
