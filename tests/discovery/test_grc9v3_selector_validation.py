"""Tests for GRC9V3 discovery selector validation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import (
    GRC9V3_SELECTOR_VALIDATION_VERSION,
    run_grc9v3_selector_validation,
)
from pygrc.discovery.grc9v3_selector_validation import GRC9V3_SELECTORS, _failure_kind


class GRC9V3SelectorValidationTest(unittest.TestCase):
    def test_selector_validation_scores_s0006_control_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "phenomenology_discovery" / "sessions" / "S0997"
            session = run_grc9v3_selector_validation(
                session_id="S0997",
                source_session_ids=("S0006",),
                session_root=root,
            )

            by_lane = {
                validation.lane_name: validation for validation in session.validations
            }

            self.assertEqual(19, len(session.validations))
            self.assertEqual(0, len(session.no_expectation_lanes))
            self.assertEqual(
                "strong_candidate",
                by_lane["appendix_e_cell_division_positive_control"].confidence_label,
            )
            self.assertIn(
                "appendix_e_completed",
                by_lane["appendix_e_cell_division_positive_control"].passed_selector_ids,
            )
            self.assertIn(
                "appendix_e_no_completion",
                by_lane["appendix_e_cell_division_negative_control"].passed_selector_ids,
            )
            self.assertIn(
                "collapse_event_present",
                by_lane["choice_collapse_positive_control"].passed_selector_ids,
            )
            self.assertIn(
                "choice_detected_present",
                by_lane["choice_collapse_negative_control"].passed_selector_ids,
            )
            self.assertIn(
                "growth_event_present",
                by_lane["growth_pressure_positive_control"].passed_selector_ids,
            )
            self.assertIn(
                "no_growth_events",
                by_lane["growth_pressure_negative_control"].passed_selector_ids,
            )
            self.assertIn(
                "budget_adjustment_observed",
                by_lane["budget_preservation_positive_control"].passed_selector_ids,
            )
            self.assertIn(
                "budget_no_adjustment",
                by_lane["budget_preservation_negative_control"].passed_selector_ids,
            )
            self.assertTrue(
                all(
                    validation.confidence_label == "strong_candidate"
                    for validation in session.validations
                )
            )

    def test_selector_validation_covers_hybrid_diagnostic_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "phenomenology_discovery" / "sessions" / "S0998"
            session = run_grc9v3_selector_validation(
                session_id="S0998",
                source_session_ids=("S0006",),
                session_root=root,
            )
            by_lane = {
                validation.lane_name: validation for validation in session.validations
            }

            transport = by_lane["transport_basin_rerouting_positive_control"]
            self.assertIn("transport_flux_present", transport.passed_selector_ids)
            self.assertIn("transport_potential_range_present", transport.passed_selector_ids)
            self.assertIn(
                "transport_positive_reroute_signature",
                transport.passed_selector_ids,
            )
            self.assertIn("tensor_anisotropy_present", transport.passed_selector_ids)
            self.assertIn("row_mismatch_sum_present", transport.passed_selector_ids)
            self.assertIn("sink_count_present", transport.passed_selector_ids)
            self.assertIn("basin_count_present", transport.passed_selector_ids)

            transport_negative = by_lane["transport_basin_rerouting_negative_control"]
            self.assertIn(
                "transport_negative_balanced_signature",
                transport_negative.passed_selector_ids,
            )

            hessian = by_lane["hessian_backend_comparison_positive_control"]
            self.assertIn(
                "hessian_weighted_least_squares_backend",
                hessian.passed_selector_ids,
            )
            self.assertIn("weighted_least_squares_available", hessian.passed_selector_ids)
            self.assertIn("previous_signed_hessian_available", hessian.passed_selector_ids)

            coarse = by_lane["coarse_cache_invalidation_positive_control"]
            self.assertIn("coarse_cache_state_recorded", coarse.passed_selector_ids)
            self.assertIn("coarse_cache_invalidated", coarse.passed_selector_ids)
            self.assertIn(
                "coarse_cache_invalidation_reason_recorded",
                coarse.passed_selector_ids,
            )

    def test_selector_validation_writes_replayable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "phenomenology_discovery" / "sessions" / "S0999"
            session = run_grc9v3_selector_validation(
                session_id="S0999",
                source_session_ids=("S0006",),
                session_root=root,
            )

            manifest = json.loads(Path(session.manifest_path).read_text())
            report = json.loads(
                (root / "reports" / "selector_validation_report.json").read_text()
            )
            session_manifest = json.loads((root / "session_manifest.json").read_text())
            summary = (root / "reports" / "selector_validation_summary.md").read_text()
            log = (root.parent.parent / "ExperimentalLog.md").read_text()

            self.assertEqual(GRC9V3_SELECTOR_VALIDATION_VERSION, manifest["manifest_version"])
            self.assertEqual("grc9v3", manifest["family"])
            self.assertEqual("S0999", report["session_id"])
            self.assertEqual(["S0006"], report["source_session_ids"])
            self.assertIn("--source-session-ids S0006", session_manifest["replay_command"])
            self.assertIn("appendix_e_cell_division_positive_control", summary)
            self.assertIn("S0999", log)
            self.assertIn("selector_validation", log)

            motifs = {item["lane"]: item for item in manifest["motifs"]}
            appendix_negative = motifs["appendix_e_cell_division_negative_control"]
            self.assertEqual("negative_control", appendix_negative["control_role"])
            self.assertEqual("negative_control_evidence", appendix_negative["notes"]["evidence_mode"])
            self.assertIn("does not claim", appendix_negative["notes"]["expected_outcome"])
            quiescent = motifs["quiescent_hybrid_control_no_event_control"]
            self.assertEqual("absence_evidence", quiescent["notes"]["evidence_mode"])
            self.assertIn("Strong absence-evidence controls", summary)
            self.assertIn("Transport Pair Distinction", summary)

    def test_selector_validation_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root_a = Path(tmpdir) / "phenomenology_discovery" / "sessions" / "S0995"
            root_b = Path(tmpdir) / "phenomenology_discovery" / "sessions" / "S0996"
            session_a = run_grc9v3_selector_validation(
                session_id="S0995",
                source_session_ids=("S0006",),
                session_root=root_a,
            )
            session_b = run_grc9v3_selector_validation(
                session_id="S0996",
                source_session_ids=("S0006",),
                session_root=root_b,
            )

            manifest_a = json.loads(Path(session_a.manifest_path).read_text())
            manifest_b = json.loads(Path(session_b.manifest_path).read_text())
            report_a = json.loads(
                (root_a / "reports" / "selector_validation_report.json").read_text()
            )
            report_b = json.loads(
                (root_b / "reports" / "selector_validation_report.json").read_text()
            )
            self.assertEqual(manifest_a["selectors"], manifest_b["selectors"])
            self.assertEqual(manifest_a["validations"], manifest_b["validations"])
            self.assertEqual(manifest_a["motifs"], manifest_b["motifs"])
            self.assertEqual(report_a["validations"], report_b["validations"])

    def test_selector_failures_classify_missing_surfaces(self) -> None:
        selector = GRC9V3_SELECTORS["transport_flux_present"]
        lane = {
            "summary": {},
            "steps": (),
            "events": (),
            "event_counts_by_kind": {},
        }
        passed, observed = selector.predicate(lane)
        self.assertFalse(passed)
        self.assertIsNone(observed)
        self.assertEqual("missing_surface", _failure_kind(lane, selector, passed))

    def test_complex_selector_validation_records_sequence_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "phenomenology_discovery" / "sessions" / "S0994"
            session = run_grc9v3_selector_validation(
                session_id="S0994",
                source_session_ids=("S0008",),
                session_root=root,
            )
            by_lane = {
                validation.lane_name: validation for validation in session.validations
            }

            complex_growth = by_lane[
                "complex_expansion_growth_budget_coarse_complex_control"
            ]
            self.assertEqual("strong_candidate", complex_growth.confidence_label)
            self.assertIn(
                "coarse_cache_invalidation_reason_recorded",
                complex_growth.passed_selector_ids,
            )
            self.assertIn("event_sequence_delta", complex_growth.notes)
            delta = json.loads(complex_growth.notes["event_sequence_delta"])
            self.assertEqual({"choice_detected": 2, "collapse": 1, "growth": 2}, delta["unexpected"])
            self.assertEqual({}, delta["missing"])
            self.assertTrue(delta["predicted_order_preserved"])


if __name__ == "__main__":
    unittest.main()
