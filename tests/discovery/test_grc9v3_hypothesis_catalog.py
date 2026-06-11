"""Tests for the GRC9V3 runtime structure hypothesis catalog."""

from __future__ import annotations

from dataclasses import replace
import json
import unittest

from pygrc.discovery import (
    GRC9V3HypothesisCatalog,
    GRC9V3_RUNTIME_TESTABLE,
    default_grc9v3_hypothesis_catalog,
    default_grc9v3_mechanism_ledger,
    generated_lane_name,
    hypothesis_runtime_status_matches_grc9v3_ledger,
    is_generated_lane_name,
    is_grc9v3_discovery_profile_name,
)


class GRC9V3HypothesisCatalogTest(unittest.TestCase):
    def test_default_catalog_round_trips_through_json(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()
        payload = catalog.to_mapping()
        restored = GRC9V3HypothesisCatalog.from_mapping(json.loads(json.dumps(payload)))

        self.assertEqual(payload, restored.to_mapping())

    def test_catalog_covers_required_seed_families(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()
        seed_families = {item.seed_family for item in catalog.seed_families}

        self.assertTrue(
            {
                "hybrid_spark_gate",
                "spark_to_expansion",
                "column_diagnostic_proxy",
                "appendix_e_cell_division",
                "choice_collapse",
                "growth_pressure",
                "budget_preservation",
                "hessian_backend_comparison",
                "signed_crossing_spark",
                "transport_basin_rerouting",
                "coarse_cache_invalidation",
                "quiescent_hybrid_control",
            }.issubset(seed_families)
        )

    def test_catalog_entries_copy_runtime_status_from_ledger(self) -> None:
        ledger = default_grc9v3_mechanism_ledger()
        ledger_by_id = ledger.by_id()
        catalog = default_grc9v3_hypothesis_catalog(ledger)

        for seed_family in catalog.seed_families:
            self.assertEqual(
                ledger_by_id[seed_family.mechanism_id].runtime_status,
                seed_family.runtime_status,
            )
        for hypothesis in catalog.to_structure_hypotheses(ledger):
            mechanism_id = hypothesis["mechanism_id"]
            self.assertTrue(
                hypothesis_runtime_status_matches_grc9v3_ledger(
                    hypothesis,
                    ledger_by_id[mechanism_id],
                )
            )

    def test_testable_hypotheses_have_controls_predicted_fields_and_schedule(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()

        for seed_family in catalog.seed_families:
            if seed_family.runtime_status == GRC9V3_RUNTIME_TESTABLE:
                self.assertTrue(
                    seed_family.positive_controls or seed_family.negative_controls
                )
                self.assertGreater(len(seed_family.predicted_signatures), 0)
                self.assertTrue(seed_family.scheduled_for_generation)
            else:
                self.assertFalse(seed_family.scheduled_for_generation)

    def test_profiles_and_lanes_use_discovery_naming(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()

        for seed_family in catalog.seed_families:
            generated_lane_name(seed_family.seed_family, "positive_control")
        for profile in catalog.generated_profiles():
            self.assertTrue(is_grc9v3_discovery_profile_name(profile))
        for lane in catalog.generated_lanes():
            self.assertTrue(is_generated_lane_name(lane))
        self.assertIn(
            generated_lane_name("hybrid_spark_gate", "positive_control"),
            catalog.generated_lanes(),
        )

    def test_column_diagnostic_proxy_is_preserved_but_not_scheduled(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()
        family = next(
            item
            for item in catalog.seed_families
            if item.seed_family == "column_diagnostic_proxy"
        )

        self.assertFalse(family.scheduled_for_generation)
        self.assertEqual((), family.lanes)

    def test_appendix_e_requires_cell_division_overlays(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()
        family = next(
            item
            for item in catalog.seed_families
            if item.seed_family == "appendix_e_cell_division"
        )

        self.assertIn("node_overlay", family.required_checkpoint_overlays)
        self.assertIn("module_overlay", family.required_checkpoint_overlays)
        self.assertIn("port_overlay", family.required_checkpoint_overlays)
        self.assertNotIn("choice_overlay", family.required_checkpoint_overlays)

    def test_quiescent_control_expected_lifecycle_is_not_event_like(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()
        family = next(
            item
            for item in catalog.seed_families
            if item.seed_family == "quiescent_hybrid_control"
        )

        self.assertEqual(("quiescent_stable_window",), family.expected_lifecycle)

    def test_structure_hypotheses_are_manifest_like_and_pure_runtime(self) -> None:
        ledger = default_grc9v3_mechanism_ledger()
        hypotheses = default_grc9v3_hypothesis_catalog(ledger).to_structure_hypotheses(
            ledger
        )

        self.assertGreater(len(hypotheses), 0)
        for hypothesis in hypotheses:
            self.assertEqual("generate_grc9v3_seed", hypothesis["generator"])
            self.assertIn("ownership", hypothesis)
            self.assertIn("state_preconditions", hypothesis)
            self.assertIn("scheduled_for_generation", hypothesis["seed_parameters"])
            self.assertNotIn("source_constructs", hypothesis["seed_parameters"])

    def test_required_checkpoint_overlays_are_recorded_for_scheduled_families(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()

        for seed_family in catalog.seed_families:
            if seed_family.scheduled_for_generation:
                self.assertGreater(len(seed_family.required_checkpoint_overlays), 0)

    def test_to_structure_hypothesis_raises_on_ledger_mismatch(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()
        wrong_entry = default_grc9v3_mechanism_ledger().by_id()[
            "grc9v3_mech_spark_to_expansion"
        ]

        with self.assertRaises(ValueError):
            catalog.seed_families[0].to_structure_hypothesis(wrong_entry)

    def test_to_structure_hypothesis_raises_on_runtime_status_mismatch(self) -> None:
        catalog = default_grc9v3_hypothesis_catalog()
        seed_family = catalog.seed_families[0]
        mismatched = replace(
            seed_family,
            runtime_status="deferred",
            scheduled_for_generation=False,
        )
        ledger_entry = default_grc9v3_mechanism_ledger().by_id()[
            seed_family.mechanism_id
        ]

        with self.assertRaises(ValueError):
            mismatched.to_structure_hypothesis(ledger_entry)

    def test_duplicate_hypothesis_ids_raise(self) -> None:
        seed_family = default_grc9v3_hypothesis_catalog().seed_families[0]

        with self.assertRaises(ValueError):
            GRC9V3HypothesisCatalog(seed_families=(seed_family, seed_family))

    def test_hyphenated_hypothesis_ids_raise(self) -> None:
        seed_family = default_grc9v3_hypothesis_catalog().seed_families[0]

        with self.assertRaises(ValueError):
            replace(seed_family, hypothesis_id="grc9v3-hypothesis-bad")


if __name__ == "__main__":
    unittest.main()
