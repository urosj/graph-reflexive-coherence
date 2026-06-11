"""Tests for GRC9 selector feedback targeting."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9_selector_feedback as exported_runner
from pygrc.discovery.grc9_selector_feedback import run_grc9_selector_feedback


class GRC9SelectorFeedbackTest(unittest.TestCase):
    def test_feedback_classifies_misses_and_diagnostic_ambiguities(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_selector_feedback(
                session_id="S0997",
                source_session_id="S0022",
                session_root=Path(tmpdir) / "S0997",
            )

        payload = session.to_mapping()
        counts = payload["classification_counts"]
        self.assertEqual(6, counts["covered_by_existing_targeted_examples"])
        self.assertEqual(5, counts["selector_ambiguity_needs_targeted_examples"])
        by_lane = {item.lane_name: item for item in session.feedback_items}
        self.assertIn(
            "S0005/spark_column_proxy_emitter",
            by_lane["spark_precursor_positive_control"].targeted_coverage,
        )
        self.assertIn(
            "S0021/dual_spark_combo",
            by_lane["column_reassignment_positive_control"].targeted_coverage,
        )
        self.assertIn(
            "row_tensor_strong_anisotropy_control",
            by_lane["row_tensor_regime"].proposed_examples,
        )
        self.assertIn(
            "row_tensor_strong_anisotropy_control",
            by_lane["row_tensor_regime"].proposed_examples_available,
        )

    def test_missing_source_report_raises_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaisesRegex(
                FileNotFoundError,
                "selector feedback source report missing",
            ):
                run_grc9_selector_feedback(
                    session_id="S0996",
                    source_session_id="S0999",
                    session_root=Path(tmpdir) / "S0996",
                )

    def test_selector_feedback_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9_selector_feedback)


if __name__ == "__main__":
    unittest.main()
