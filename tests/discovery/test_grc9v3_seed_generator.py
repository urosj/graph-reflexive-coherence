"""Tests for deterministic GRC9V3 discovery seed generation."""

from __future__ import annotations

import json
import unittest

from pygrc.discovery import (
    GRC9V3_COMPLEX_HYBRID_NAMES,
    GRC9V3_PRESSURE_BOUNDARY_NAMES,
    GRC9V3_RUNTIME_TESTABLE,
    default_grc9v3_hypothesis_catalog,
    generate_grc9v3_complex_hybrid_example,
    generate_grc9v3_pressure_boundary_example,
    generate_grc9v3_seed,
    generate_grc9v3_seed_perturbation,
    generated_lane_name,
    perturbation_lane_name,
)
from pygrc.models import GRC9V3


class GRC9V3SeedGeneratorTest(unittest.TestCase):
    def test_scheduled_catalog_controls_generate_valid_constructor_payloads(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()

        generated = []
        for family in catalog.seed_families:
            if not family.scheduled_for_generation:
                continue
            self.assertEqual(GRC9V3_RUNTIME_TESTABLE, family.runtime_status)
            for control in (*family.positive_controls, *family.negative_controls):
                seed = generate_grc9v3_seed(
                    family.seed_family,
                    control.control_role,
                    catalog=catalog,
                )
                generated.append(seed)
                self.assertEqual(
                    generated_lane_name(family.seed_family, control.control_role),
                    seed.lane_name,
                )
                self.assertEqual(family.profile, seed.profile)
                self.assertGreater(len(seed.ownership_tags), 0)
                self.assertGreater(len(seed.required_checkpoint_overlays), 0)
                GRC9V3.from_state(
                    state=dict(seed.state_payload),
                    params=dict(seed.expected_runtime_config),
                )

        self.assertGreater(len(generated), 0)

    def test_seed_generation_is_deterministic_and_json_safe(self) -> None:
        first = generate_grc9v3_seed("hybrid_spark_gate")
        second = generate_grc9v3_seed("hybrid_spark_gate")

        self.assertEqual(first.to_mapping(), second.to_mapping())
        self.assertEqual(
            first.to_mapping(),
            json.loads(json.dumps(first.to_mapping())),
        )

    def test_non_scheduled_family_cannot_generate(self) -> None:
        with self.assertRaises(ValueError):
            generate_grc9v3_seed("column_diagnostic_proxy")

    def test_negative_control_records_parent_seed(self) -> None:
        seed = generate_grc9v3_seed("hybrid_spark_gate", "negative_control")

        self.assertEqual("hybrid_spark_gate_positive_control", seed.negative_control_of)

    def test_perturbation_lane_name_matches_convention(self) -> None:
        seed = generate_grc9v3_seed_perturbation(
            "hybrid_spark_gate",
            "active_degree",
            "-1",
        )

        self.assertEqual(
            perturbation_lane_name(
                "hybrid_spark_gate",
                "positive_control",
                "active_degree",
                "-1",
            ),
            seed.lane_name,
        )
        self.assertEqual("hybrid_spark_gate_positive_control", seed.perturbation_of)
        self.assertEqual(8.0, seed.seed_parameters["active_degree"])

    def test_perturbing_missing_parameter_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_grc9v3_seed_perturbation(
                "hybrid_spark_gate",
                "not_a_parameter",
                "+1",
            )

    def test_string_parameter_delta_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_grc9v3_seed_perturbation(
                "hessian_backend_comparison",
                "hessian_backend",
                "+1",
                parent_control_role="baseline_control",
            )

    def test_appendix_e_seed_uses_cell_division_overlays(self) -> None:
        seed = generate_grc9v3_seed("appendix_e_cell_division")

        self.assertIn("node_overlay", seed.required_checkpoint_overlays)
        self.assertIn("module_overlay", seed.required_checkpoint_overlays)
        self.assertIn("port_overlay", seed.required_checkpoint_overlays)
        self.assertNotIn("choice_overlay", seed.required_checkpoint_overlays)

    def test_state_payload_has_explicit_port_structure_and_consistent_identity(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()

        for family in catalog.seed_families:
            if not family.scheduled_for_generation:
                continue
            control = (*family.positive_controls, *family.negative_controls)[0]
            seed = generate_grc9v3_seed(
                family.seed_family,
                control.control_role,
                catalog=catalog,
            )
            state = seed.state_payload
            live_nodes = {int(node["node_id"]) for node in state["topology"]["nodes"]}
            port_structure = state["topology"]["port_structure"]
            self.assertIn("port_to_edge", port_structure)
            self.assertGreater(len(port_structure["port_to_edge"]), 0)
            self.assertTrue(set(int(node_id) for node_id in state["sink_set"]) <= live_nodes)
            for sink_id, members in state["basins"].items():
                self.assertIn(int(sink_id), live_nodes)
                self.assertTrue(set(int(member) for member in members) <= live_nodes)

    def test_budget_preservation_positive_control_has_controlled_initial_error(self) -> None:
        seed = generate_grc9v3_seed("budget_preservation")
        coherence_sum = sum(
            float(node["coherence"]) for node in seed.state_payload["nodes"].values()
        )

        self.assertEqual(0.25, seed.seed_parameters["budget_error"])
        self.assertAlmostEqual(
            0.25,
            coherence_sum - float(seed.state_payload["budget_target"]),
        )
        self.assertAlmostEqual(
            0.25,
            float(seed.state_payload["cached_quantities"]["initial_budget_error"]),
        )

    def test_capability_modes_are_rejected_at_generation_validation(self) -> None:
        with self.assertRaises(ValueError):
            generate_grc9v3_seed(
                "hybrid_spark_gate",
                parameter_overrides={"spark_signed_crossing": True},
            )
        with self.assertRaises(ValueError):
            generate_grc9v3_seed(
                "hybrid_spark_gate",
                parameter_overrides={"boundary_mode": "barrier"},
            )

    def test_complex_hybrid_examples_generate_connected_runtime_states(self) -> None:
        generated = [
            generate_grc9v3_complex_hybrid_example(example_name)
            for example_name in GRC9V3_COMPLEX_HYBRID_NAMES
        ]

        self.assertEqual(len(GRC9V3_COMPLEX_HYBRID_NAMES), len(generated))
        for seed in generated:
            self.assertIn(seed.control_role, {"complex_control", "perturbation_control"})
            self.assertEqual(
                generated_lane_name(seed.seed_family, seed.control_role),
                seed.lane_name,
            )
            self.assertTrue(seed.graph_preconditions["connected_graph"])
            topology = seed.state_payload["topology"]
            self.assertIn("port_to_edge", topology["port_structure"])
            self.assertGreater(len(topology["port_structure"]["port_to_edge"]), 0)
            GRC9V3.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )

    def test_complex_hessian_pair_uses_same_graph_with_different_backend(self) -> None:
        row_basis = generate_grc9v3_complex_hybrid_example("complex_hessian_row_basis")
        wls = generate_grc9v3_complex_hybrid_example(
            "complex_hessian_weighted_least_squares"
        )

        self.assertEqual(row_basis.state_payload["topology"], wls.state_payload["topology"])
        self.assertEqual(row_basis.state_payload["nodes"], wls.state_payload["nodes"])
        self.assertEqual(row_basis.state_payload["basins"], wls.state_payload["basins"])
        self.assertEqual(
            "row_basis_diagonal",
            row_basis.expected_runtime_config["constitutive_semantic_modes"][
                "hessian_backend"
            ],
        )
        self.assertEqual(
            "weighted_least_squares",
            wls.expected_runtime_config["constitutive_semantic_modes"][
                "hessian_backend"
            ],
        )

    def test_pressure_boundary_examples_generate_expected_growth_sources(self) -> None:
        expected_event_kinds = {
            "pressure_boundary_growth_positive_control": ("growth",),
            "pressure_boundary_growth_no_growth_control": (),
            "generic_front_capacity_growth_comparison": ("growth",),
            "complex_spark_expansion_pressure_boundary_growth": (
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
                "growth",
            ),
        }

        self.assertEqual(
            set(expected_event_kinds),
            set(GRC9V3_PRESSURE_BOUNDARY_NAMES),
        )
        for example_name in GRC9V3_PRESSURE_BOUNDARY_NAMES:
            with self.subTest(example_name=example_name):
                seed = generate_grc9v3_pressure_boundary_example(example_name)
                self.assertEqual(
                    generated_lane_name(example_name, "positive_control"),
                    seed.lane_name,
                )
                self.assertEqual("grc9v3_pressure_boundary_examples_v1", seed.profile)
                model = GRC9V3.from_state(
                    state=dict(seed.state_payload),
                    params=dict(seed.expected_runtime_config),
                )
                event_kinds: list[str] = []
                growth_sources: list[str] = []
                for _ in range(4):
                    step = model.step()
                    for event in step.events:
                        event_kinds.append(event.kind)
                        if event.kind == "growth":
                            growth_sources.append(
                                str(event.payload.get("growth_parent_capacity_source"))
                            )

                self.assertEqual(
                    expected_event_kinds[example_name],
                    tuple(event_kinds),
                )
                if example_name in {
                    "pressure_boundary_growth_positive_control",
                    "complex_spark_expansion_pressure_boundary_growth",
                }:
                    self.assertEqual(["pressure_boundary"], growth_sources)
                elif example_name == "generic_front_capacity_growth_comparison":
                    self.assertEqual(["spark_expansion_front"], growth_sources)
                else:
                    self.assertEqual([], growth_sources)


if __name__ == "__main__":
    unittest.main()
