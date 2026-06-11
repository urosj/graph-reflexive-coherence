"""Tests for GRC9 discovery selector validation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import GRC9DiscoveryManifest
from pygrc.discovery.grc9_selector_validation import run_grc9_selector_validation


class GRC9SelectorValidationTest(unittest.TestCase):
    def test_selector_validation_finds_expected_fixture_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_selector_validation(
                session_id="S0998",
                source_session_ids=("S0005", "S0006", "S0021"),
                session_root=Path(tmpdir) / "S0998",
            )

            by_lane = {validation.lane_name: validation for validation in session.validations}

            self.assertEqual("strong_candidate", by_lane["spark_column_proxy_eps_fail"].confidence_label)
            self.assertIn(
                "target_signature_suppressed",
                by_lane["spark_column_proxy_eps_fail"].passed_selector_ids,
            )
            self.assertIn(
                "dual_spark_present",
                by_lane["dual_spark_combo"].passed_selector_ids,
            )
            self.assertIn(
                "fission_confirmed_twice",
                by_lane["spark_growth_fission_combo"].passed_selector_ids,
            )
            self.assertGreaterEqual(session.to_mapping()["motif_count"], 20)
            self.assertIn("no_expectation_lane_count", session.to_mapping())

    def test_selector_manifest_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0999"
            session = run_grc9_selector_validation(
                session_id="S0999",
                source_session_ids=("S0006", "S0021"),
                session_root=root,
            )
            manifest_payload = json.loads(Path(session.manifest_path).read_text())
            restored = GRC9DiscoveryManifest.from_mapping(manifest_payload)

            self.assertEqual(manifest_payload, restored.to_mapping())
            self.assertGreater(len(restored.selectors), 0)
            self.assertGreater(len(restored.motifs), 0)

    def test_selector_validation_scores_targeted_diagnostic_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_selector_validation(
                session_id="S0997",
                source_session_ids=("S0010",),
                session_root=Path(tmpdir) / "S0997",
            )
            by_lane = {validation.lane_name: validation for validation in session.validations}

            self.assertIn(
                "row_tensor_strong_anisotropy",
                by_lane["row_tensor_strong_anisotropy_control"].passed_selector_ids,
            )
            self.assertIn(
                "coarse_sparse_profile",
                by_lane["coarse_cache_populated_sparse_profile_control"].passed_selector_ids,
            )
            self.assertIn(
                "budget_uniform_shift_observed",
                by_lane["budget_uniform_shift_trigger_control"].passed_selector_ids,
            )
            self.assertIn(
                "transport_short_path_dominant",
                by_lane["transport_short_path_dominant_control"].passed_selector_ids,
            )
            self.assertTrue(
                all(validation.confidence_label == "candidate" for validation in session.validations)
            )

    def test_selector_validation_scores_complex_event_stability_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_selector_validation(
                session_id="S0996",
                source_session_ids=("S0020",),
                session_root=Path(tmpdir) / "S0996",
            )

            self.assertEqual(5, len(session.validations))
            for validation in session.validations:
                self.assertIn("dual_spark_present", validation.passed_selector_ids)
                self.assertIn("dual_expansion_present", validation.passed_selector_ids)
                self.assertIn("growth_event_present", validation.passed_selector_ids)
                self.assertIn("fission_confirmed_summary", validation.passed_selector_ids)
                self.assertEqual((), validation.missing_selector_ids)

    def test_selector_validation_reports_lanes_without_expectations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0993"
            session = run_grc9_selector_validation(
                session_id="S0993",
                source_session_ids=("S0005", "S0006", "S0021"),
                session_root=root,
            )

            payload = session.to_mapping()
            summary = (root / "reports" / "selector_validation_summary.md").read_text()
            self.assertEqual(
                len(session.no_expectation_lanes),
                payload["no_expectation_lane_count"],
            )
            self.assertIn("Lanes without selector expectations", summary)


if __name__ == "__main__":
    unittest.main()
