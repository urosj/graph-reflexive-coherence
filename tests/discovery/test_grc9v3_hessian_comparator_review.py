"""Tests for GRC9V3 Hessian comparator review."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import (
    run_grc9v3_hessian_comparator_review as exported_runner,
)
from pygrc.discovery.grc9v3_hessian_comparator_review import (
    run_grc9v3_hessian_comparator_review,
)


class GRC9V3HessianComparatorReviewTest(unittest.TestCase):
    def test_hessian_review_reclassifies_s0008_hessian_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9v3_hessian_comparator_review(
                session_id="S0991",
                session_root=Path(tmpdir) / "S0991",
                update_experimental_log=False,
            )

            diagnostic = [
                item
                for item in session.lane_reviews
                if item.classification == "diagnostic_comparator"
            ]
            probes = [
                item
                for item in session.lane_reviews
                if item.classification == "eventful_backend_probe"
            ]
            self.assertEqual(2, len(diagnostic))
            self.assertEqual(2, len(probes))
            self.assertTrue(all(item.event_count == 0 for item in diagnostic))
            self.assertTrue(all(not item.event_motif_eligible for item in diagnostic))
            self.assertEqual(
                {"row_basis_diagonal", "weighted_least_squares"},
                {item.backend for item in diagnostic},
            )

            by_pair_id = {item.pair_id: item for item in session.pair_reviews}
            diagnostic_pair = by_pair_id["s0008_hessian_diagnostic_pair"]
            self.assertEqual("no_event_delta_found", diagnostic_pair.event_delta_status)
            self.assertEqual(
                "preserve_as_diagnostic_comparator",
                diagnostic_pair.review_action,
            )
            self.assertTrue(diagnostic_pair.same_initial_topology)
            self.assertTrue(diagnostic_pair.same_initial_node_state)

            probe_pair = by_pair_id["s0991_hessian_eventful_probe_pair"]
            self.assertEqual(
                "eventful_no_backend_event_delta",
                probe_pair.event_delta_status,
            )
            self.assertTrue(all(item.event_count > 0 for item in probes))
            self.assertTrue(probe_pair.same_initial_topology)
            self.assertTrue(probe_pair.same_initial_node_state)

            self.assertTrue(Path(session.report_path).exists())
            self.assertTrue(Path(session.review_index_path).exists())

    def test_hessian_comparator_review_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9v3_hessian_comparator_review)


if __name__ == "__main__":
    unittest.main()
