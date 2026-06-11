"""Tests for GRC9V3 catalog breadth expansion."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9v3_catalog_breadth_expansion as exported_runner
from pygrc.discovery.grc9v3_catalog_breadth_expansion import (
    run_grc9v3_catalog_breadth_expansion,
)


class GRC9V3CatalogBreadthExpansionTest(unittest.TestCase):
    def test_breadth_expansion_merges_simple_controls_and_complex_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9v3_catalog_breadth_expansion(
                session_id="S0987",
                session_root=Path(tmpdir) / "S0987",
                update_experimental_log=False,
            )

            payload = session.to_mapping()
            self.assertEqual(26, payload["motif_count"])
            self.assertEqual(11, payload["accepted_count"])
            self.assertEqual(11, payload["strong_candidate_count"])
            self.assertEqual(4, payload["diagnostic_comparator_count"])
            self.assertEqual(0, payload["rejected_count"])
            self.assertEqual(0, payload["needs_rerun_count"])
            self.assertEqual(19, payload["simple_control_record_count"])
            self.assertEqual(7, payload["base_catalog_record_count"])
            self.assertEqual(payload["motif_count"], payload["review_history_count"])

            by_lane = {str(record["lane_name"]): record for record in session.records}
            self.assertEqual(
                "accepted",
                by_lane["hybrid_spark_gate_positive_control"]["review_status"],
            )
            self.assertEqual(
                "simple_lifecycle_motif",
                by_lane["growth_pressure_positive_control"]["catalog_category"],
            )
            self.assertEqual(
                "mechanism_diagnostic_motif",
                by_lane["budget_preservation_positive_control"]["catalog_category"],
            )
            self.assertEqual(
                "strong_candidate",
                by_lane["hybrid_spark_gate_negative_control"]["review_status"],
            )
            self.assertEqual(
                "quiescent_control",
                by_lane["quiescent_hybrid_control_no_event_control"]["catalog_category"],
            )
            self.assertEqual(
                "diagnostic_comparator",
                by_lane["hessian_backend_comparison_positive_control"]["review_status"],
            )
            self.assertEqual(
                "accepted",
                by_lane["complex_spark_expansion_hierarchy_complex_control"]["review_status"],
            )
            self.assertTrue(by_lane["hybrid_spark_gate_positive_control"]["checkpoint_links"])

    def test_expanded_catalog_round_trips_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9v3_catalog_breadth_expansion(
                session_id="S0986",
                session_root=Path(tmpdir) / "S0986",
                update_experimental_log=False,
            )
            restored = json.loads(Path(session.expanded_catalog_path).read_text())

        self.assertEqual(26, len(restored["records"]))
        self.assertEqual(11, restored["summary"]["accepted_count"])

    def test_breadth_expansion_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9v3_catalog_breadth_expansion)


if __name__ == "__main__":
    unittest.main()
