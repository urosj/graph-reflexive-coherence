"""Tests for GRCL-9V3 lowered-source visualization review."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.telemetry import (
    run_grcl9v3_lowering_replay_session,
    run_grcl9v3_selector_validation,
)
from pygrc.visualization import render_grcl9v3_lowering_visual_review


class GRCL9V3VisualizationReviewTest(unittest.TestCase):
    def test_visual_review_renders_only_selector_backed_motifs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "grcl9v3" / "lowering"
            run_grcl9v3_lowering_replay_session(
                session_id="S9101",
                output_root=output_root,
                fixture_names=(
                    "hybrid_spark_gate_positive_control",
                    "growth_pressure_positive_control",
                    "quiescent_hybrid_control_no_event_control",
                ),
                requested_steps=2,
            )
            run_grcl9v3_selector_validation(
                session_id="S9102",
                source_session_ids=("S9101",),
                output_root=output_root,
            )

            result = render_grcl9v3_lowering_visual_review(
                session_id="S9103",
                selector_session_id="S9102",
                output_root=output_root,
            )

            rendered = {record.fixture_name: record for record in result.records}
            skipped = {record.fixture_name: record for record in result.skipped_records}
            self.assertIn("hybrid_spark_gate_positive_control", rendered)
            self.assertIn("growth_pressure_positive_control", rendered)
            self.assertIn("quiescent_hybrid_control_no_event_control", rendered)
            self.assertEqual({}, skipped)

            for record in rendered.values():
                self.assertEqual("rendered_supporting_only", record.visual_status)
                self.assertTrue(record.motif_id)
                self.assertTrue(Path(record.trajectory_path).exists())
                self.assertTrue(Path(record.event_timeline_path).exists())
                self.assertTrue(Path(record.graph_sequence_path).exists())
                self.assertTrue(Path(record.graph_animation_path).exists())
                self.assertTrue(Path(record.graph_layout_path).exists())
                self.assertTrue(Path(record.graph_html_path).exists())
                self.assertTrue(Path(record.grcl9v3_overlay_path).exists())
                self.assertTrue(Path(record.grcl9v3_overlay_summary_path).exists())
                self.assertTrue(Path(record.boundary_panel_path).exists())
                self.assertTrue(record.connected)

                overlay = _read_json(Path(record.grcl9v3_overlay_summary_path))
                boundary = Path(record.boundary_panel_path).read_text(encoding="utf-8")
                self.assertTrue(overlay["no_visual_only_promotion"])
                self.assertEqual("rendered_supporting_only", overlay["visual_status"])
                self.assertIn("selector_confidence_label", overlay)
                self.assertIn("selector_ids", overlay)
                self.assertIn("passed_selector_ids", overlay)
                self.assertIn("graph_surface_modes", overlay)
                self.assertIn("dense", overlay["graph_surface_modes"])
                self.assertIn("sparse", overlay["graph_surface_modes"])
                self.assertEqual(17, overlay["deterministic_layout"]["dense_graph_layout_seed"])
                self.assertEqual(29, overlay["deterministic_layout"]["sparse_overlay_layout_seed"])
                self.assertIn("source_runtime_visual_distinction", overlay)
                self.assertIn("expected_region_cache_names", overlay)
                self.assertIn("supporting evidence only", boundary)
                self.assertIn("selector telemetry is primary", boundary)
                self.assertIn("Runtime-added nodes", boundary)

            self.assertTrue(result.visual_index_path.exists())
            self.assertTrue(result.report_path.exists())
            self.assertTrue(result.summary_path.exists())
            self.assertTrue(result.session_manifest_path.exists())

    def test_ambiguous_selector_records_render_without_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "grcl9v3" / "lowering"
            run_grcl9v3_lowering_replay_session(
                session_id="S9201",
                output_root=output_root,
                fixture_names=("appendix_e_cell_division_positive_control",),
                requested_steps=2,
            )
            run_grcl9v3_selector_validation(
                session_id="S9202",
                source_session_ids=("S9201",),
                output_root=output_root,
            )

            result = render_grcl9v3_lowering_visual_review(
                session_id="S9203",
                selector_session_id="S9202",
                output_root=output_root,
            )

            self.assertEqual(1, len(result.records))
            record = result.records[0]
            self.assertEqual("candidate", record.confidence_label)
            overlay = _read_json(Path(record.grcl9v3_overlay_summary_path))
            self.assertTrue(overlay["no_visual_only_promotion"])
            self.assertEqual("candidate", overlay["selector_confidence_label"])
            self.assertEqual([], overlay["runtime_observation"]["missing_surface_selector_ids"])
            self.assertEqual([], overlay["missing_surface_selector_ids"])


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
