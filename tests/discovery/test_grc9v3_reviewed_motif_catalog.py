"""Tests for GRC9V3 reviewed motif catalog generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9v3_reviewed_motif_catalog as exported_runner
from pygrc.discovery.grc9v3_reviewed_motif_catalog import (
    run_grc9v3_reviewed_motif_catalog,
)


class GRC9V3ReviewedMotifCatalogTest(unittest.TestCase):
    def test_s0009_review_catalog_preserves_status_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9v3_reviewed_motif_catalog(
                session_id="S0990",
                session_root=Path(tmpdir) / "S0990",
                update_experimental_log=False,
            )

            payload = session.to_mapping()
            self.assertEqual(7, payload["motif_count"])
            self.assertEqual(3, payload["accepted_count"])
            self.assertEqual(2, payload["strong_candidate_count"])
            self.assertEqual(2, payload["diagnostic_comparator_count"])
            self.assertEqual(0, payload["rejected_count"])
            self.assertEqual(0, payload["needs_rerun_count"])
            self.assertEqual(0, payload["duplicate_count"])
            self.assertEqual(payload["motif_count"], payload["review_history_count"])

            by_lane = {record.lane_name: record for record in session.records}
            self.assertEqual(
                "diagnostic_comparator",
                by_lane["complex_hessian_row_basis_complex_control"].review_status,
            )
            self.assertFalse(
                by_lane["complex_hessian_weighted_least_squares_complex_control"].event_motif_eligible
            )
            self.assertEqual(
                "strong_candidate",
                by_lane[
                    "complex_spark_choice_no_saturation_perturbation_perturbation_control"
                ].review_status,
            )
            self.assertEqual(
                "negative_control",
                by_lane[
                    "complex_growth_low_birth_perturbation_perturbation_control"
                ].catalog_category,
            )

            accepted = [
                record for record in session.records if record.review_status == "accepted"
            ]
            self.assertTrue(all(record.event_motif_eligible for record in accepted))
            self.assertTrue(all(record.visual_artifacts for record in accepted))
            self.assertTrue(all(record.checkpoint_links for record in accepted))
            self.assertTrue(
                all("no_visual_only_promotion" in record.non_claims for record in accepted)
            )
            self.assertTrue(
                by_lane[
                    "complex_expansion_growth_budget_coarse_complex_control"
                ].event_sequence_delta
            )
            self.assertTrue(session.diagnostic_records)

    def test_reviewed_catalog_round_trips_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9v3_reviewed_motif_catalog(
                session_id="S0989",
                session_root=Path(tmpdir) / "S0989",
                update_experimental_log=False,
            )
            restored = json.loads(Path(session.reviewed_catalog_path).read_text())

        self.assertEqual(
            session.to_mapping()["accepted_count"],
            restored["summary"]["accepted_count"],
        )
        self.assertEqual(
            session.to_mapping()["diagnostic_comparator_count"],
            restored["summary"]["diagnostic_comparator_count"],
        )
        self.assertEqual(7, len(restored["records"]))

    def test_markdown_summary_matches_json_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9v3_reviewed_motif_catalog(
                session_id="S0988",
                session_root=Path(tmpdir) / "S0988",
                update_experimental_log=False,
            )
            markdown = Path(session.markdown_catalog_path).read_text(encoding="utf-8")

        payload = session.to_mapping()
        self.assertIn(f"- Accepted: `{payload['accepted_count']}`", markdown)
        self.assertIn(
            f"- Diagnostic comparators: `{payload['diagnostic_comparator_count']}`",
            markdown,
        )

    def test_reviewed_motif_catalog_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9v3_reviewed_motif_catalog)


if __name__ == "__main__":
    unittest.main()
