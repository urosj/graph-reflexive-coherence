"""Tests for the GRC9 seeded structure hypothesis catalog."""

from __future__ import annotations

from dataclasses import replace
import json
import unittest

from pygrc.discovery import (
    GRC9HypothesisCatalog,
    RUNTIME_TESTABLE,
    default_grc9_hypothesis_catalog,
    default_grc9_mechanism_ledger,
    hypothesis_runtime_status_matches_ledger,
    is_generated_lane_name,
    is_discovery_profile_name,
)


class GRC9HypothesisCatalogTest(unittest.TestCase):
    def test_default_catalog_round_trips_through_json(self) -> None:
        catalog = default_grc9_hypothesis_catalog()
        payload = catalog.to_mapping()
        restored = GRC9HypothesisCatalog.from_mapping(json.loads(json.dumps(payload)))

        self.assertEqual(payload, restored.to_mapping())

    def test_catalog_covers_required_seed_families(self) -> None:
        catalog = default_grc9_hypothesis_catalog()
        seed_families = {item.seed_family for item in catalog.seed_families}

        self.assertTrue(
            {
                "spark_precursor",
                "expansion_module",
                "column_reassignment",
                "growth_pressure",
                "row_tensor_regime",
                "column_diagnostic_regime",
                "coarse_profile_sparsity",
                "budget_correction",
                "quiescent_basin",
                "transport_pathway",
                "fission_candidate",
            }.issubset(seed_families)
        )

    def test_catalog_entries_copy_runtime_status_from_ledger(self) -> None:
        ledger = default_grc9_mechanism_ledger()
        ledger_by_id = ledger.by_id()
        catalog = default_grc9_hypothesis_catalog(ledger)

        for seed_family in catalog.seed_families:
            self.assertEqual(
                ledger_by_id[seed_family.mechanism_id].runtime_status,
                seed_family.runtime_status,
            )
        for hypothesis in catalog.to_structure_hypotheses(ledger):
            mechanism_id = next(
                item.mechanism_id
                for item in catalog.seed_families
                if item.hypothesis_id == hypothesis.hypothesis_id
            )
            self.assertTrue(
                hypothesis_runtime_status_matches_ledger(
                    hypothesis,
                    ledger_by_id[mechanism_id],
                )
            )

    def test_testable_hypotheses_have_controls_and_predicted_fields(self) -> None:
        catalog = default_grc9_hypothesis_catalog()

        for seed_family in catalog.seed_families:
            if seed_family.runtime_status == RUNTIME_TESTABLE:
                self.assertTrue(
                    seed_family.positive_controls or seed_family.negative_controls
                )
                self.assertGreater(len(seed_family.predicted_signatures), 0)
                self.assertTrue(seed_family.scheduled_for_generation)
            else:
                self.assertFalse(seed_family.scheduled_for_generation)

    def test_profiles_and_lanes_use_discovery_naming(self) -> None:
        catalog = default_grc9_hypothesis_catalog()

        for profile in catalog.generated_profiles():
            self.assertTrue(is_discovery_profile_name(profile))
        for lane in catalog.generated_lanes():
            self.assertTrue(is_generated_lane_name(lane))
        self.assertIn("spark_precursor_positive_control", catalog.generated_lanes())

    def test_structure_hypotheses_are_manifest_compatible(self) -> None:
        ledger = default_grc9_mechanism_ledger()
        hypotheses = default_grc9_hypothesis_catalog(ledger).to_structure_hypotheses(
            ledger
        )

        self.assertGreater(len(hypotheses), 0)
        for hypothesis in hypotheses:
            payload = hypothesis.to_mapping()
            self.assertEqual("generate_grc9_seed", payload["generator"])
            self.assertIn("scheduled_for_generation", payload["seed_parameters"])

    def test_to_structure_hypothesis_raises_on_ledger_mismatch(self) -> None:
        catalog = default_grc9_hypothesis_catalog()
        wrong_entry = default_grc9_mechanism_ledger().by_id()[
            "grc9_mech_expansion_module"
        ]

        with self.assertRaises(ValueError):
            catalog.seed_families[0].to_structure_hypothesis(wrong_entry)

    def test_to_structure_hypothesis_raises_on_runtime_status_mismatch(self) -> None:
        catalog = default_grc9_hypothesis_catalog()
        seed_family = catalog.seed_families[0]
        mismatched = replace(
            seed_family,
            runtime_status="deferred",
            scheduled_for_generation=False,
        )
        ledger_entry = default_grc9_mechanism_ledger().by_id()[
            seed_family.mechanism_id
        ]

        with self.assertRaises(ValueError):
            mismatched.to_structure_hypothesis(ledger_entry)

    def test_duplicate_hypothesis_ids_raise(self) -> None:
        seed_family = default_grc9_hypothesis_catalog().seed_families[0]

        with self.assertRaises(ValueError):
            GRC9HypothesisCatalog(seed_families=(seed_family, seed_family))

    def test_hyphenated_hypothesis_ids_raise(self) -> None:
        seed_family = default_grc9_hypothesis_catalog().seed_families[0]

        with self.assertRaises(ValueError):
            replace(seed_family, hypothesis_id="grc9-hypothesis-bad")


if __name__ == "__main__":
    unittest.main()
