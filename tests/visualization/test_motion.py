"""Tests for motion inference visualization review."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes.motion_examples import run_motion_structural_examples
from pygrc.landscapes.motion_seed_examples import run_motion_long_composite_examples
from pygrc.visualization import (
    render_motion_animated_visual_session,
    render_motion_visual_session,
)


class MotionVisualizationTest(unittest.TestCase):
    def test_motion_visual_session_renders_structural_examples(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "motion"
            examples = run_motion_structural_examples(
                output_root=output_root,
                session_id="S9401",
            )

            result = render_motion_visual_session(session_root=examples.session_root)

            self.assertEqual(len(examples.runs), len(result.records))
            self.assertTrue(result.visual_manifest_path.exists())
            self.assertTrue(result.report_path.exists())
            self.assertTrue(result.readme_path.exists())
            self.assertEqual(
                "static_two_checkpoint_rendering_complete_temporal_animation_deferred",
                result.to_mapping()["temporal_rendering_status"],
            )

            by_name = {record.example_name: record for record in result.records}
            self.assertIn("identity_split_control", by_name)
            split_record = by_name["identity_split_control"]
            self.assertTrue(split_record.graph_path.exists())
            self.assertTrue(split_record.timeline_path.exists())
            self.assertGreater(split_record.graph_path.stat().st_size, 1000)
            self.assertGreater(split_record.timeline_path.stat().st_size, 1000)

            summary = _read_json(split_record.summary_path)
            self.assertTrue(summary["no_visual_only_promotion"])
            self.assertEqual("none", summary["visual_claims"])
            self.assertIn("identity_split_control", summary["example_name"])
            self.assertIn(
                "motion_identity_step0000_0001_split_basin_parent_to_basin_child_a_basin_child_b",
                summary["motion_record_ids"],
            )
            self.assertIn(
                "motion_topological_step0000_0001_support_split",
                summary["motion_record_ids"],
            )
            self.assertEqual(["checkpoint_0000", "checkpoint_0001"], summary["checkpoint_ids"])
            self.assertEqual(
                ["checkpoint_0000", "checkpoint_0001"],
                summary["checkpoint_linkage"]["checkpoint_ids"],
            )
            self.assertIn(
                "sparse_graph_overlay",
                summary["rendered_surfaces"]["graph_surface_modes"],
            )
            self.assertIn(
                "dense_record_panel",
                summary["rendered_surfaces"]["graph_surface_modes"],
            )
            self.assertEqual(
                [2, 3],
                summary["motion_highlights"]["topological_born_node_ids"],
            )
            self.assertEqual(
                [1, 2, 3],
                summary["motion_highlights"]["topological_evidence_node_ids"],
            )
            self.assertIn(
                "deferred",
                summary["rendered_surfaces"]["temporal_checkpoint_series_animation"],
            )

    def test_motion_visual_session_can_render_one_example(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "motion"
            examples = run_motion_structural_examples(
                output_root=output_root,
                session_id="S9402",
            )

            result = render_motion_visual_session(
                session_root=examples.session_root,
                example_names=("coherence_transfer_control",),
            )

            self.assertEqual(1, len(result.records))
            record = result.records[0]
            self.assertEqual("coherence_transfer_control", record.example_name)
            summary = _read_json(record.summary_path)
            self.assertIn(
                "motion_coherence_step0000_0001_1_to_2_direct",
                summary["motion_record_ids"],
            )
            self.assertEqual(["coherence"], summary["motion_kinds"])
            self.assertEqual(["drifted"], summary["relationships"])
            self.assertIn("step_rows_path", summary["source_telemetry"])
            self.assertIn("graph_checkpoint_index_path", summary["source_telemetry"])

    def test_negative_control_renders_without_non_stationary_highlights(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "motion"
            examples = run_motion_structural_examples(
                output_root=output_root,
                session_id="S9403",
                example_names=("no_motion_negative_control",),
            )

            result = render_motion_visual_session(session_root=examples.session_root)

            self.assertEqual(1, len(result.records))
            record = result.records[0]
            self.assertEqual("no_motion_negative_control", record.example_name)
            self.assertTrue(record.graph_path.exists())
            self.assertTrue(record.timeline_path.exists())
            summary = _read_json(record.summary_path)
            self.assertEqual(["identity", "representative"], summary["motion_kinds"])
            self.assertEqual(["stationary"], summary["relationships"])
            self.assertEqual([], summary["non_stationary_motion_record_ids"])
            self.assertEqual([], summary["motion_highlights"]["old_carrier_node_ids"])
            self.assertEqual([], summary["motion_highlights"]["new_carrier_node_ids"])
            self.assertEqual([], summary["motion_highlights"]["topological_born_node_ids"])
            self.assertEqual([], summary["motion_highlights"]["topological_removed_node_ids"])

    def test_motion_animated_visual_session_renders_long_window_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "motion"
            session = run_motion_long_composite_examples(
                output_root=output_root,
                session_id="S9404",
                seed_names=("motion_long_relay_walk_frontier",),
                render_visuals=False,
            )

            result = render_motion_animated_visual_session(session_root=session.session_root)

            self.assertEqual(1, len(result.records))
            record = result.records[0]
            self.assertEqual("motion_long_relay_walk_frontier", record.example_name)
            self.assertEqual(21, record.frame_count)
            self.assertTrue(record.motion_animation_path.exists())
            self.assertTrue(record.motion_sequence_path.exists())
            self.assertTrue(record.graph_engine_animation_path.exists())
            self.assertTrue(record.graph_engine_sequence_path.exists())
            self.assertGreater(record.motion_animation_path.stat().st_size, 1000)
            summary = _read_json(record.animated_summary_path)
            self.assertTrue(summary["no_visual_only_promotion"])
            self.assertEqual("none", summary["visual_claims"])
            self.assertEqual(21, summary["rendered_surfaces"]["motion_frame_count"])
            self.assertEqual(21, len(summary["frame_checkpoint_linkage"]))
            self.assertIn(
                "motion_identity_step0004_0005_walked_relay_basin_0_to_relay_basin_1",
                summary["motion_record_ids"],
            )
            active_frames = [
                frame
                for frame in summary["frame_checkpoint_linkage"]
                if frame["active_motion_record_ids"]
            ]
            self.assertGreaterEqual(len(active_frames), 4)
            static_summary = _read_json(record.visual_dir / "motion_visual_summary.json")
            self.assertEqual(
                "rendered_graph_engine_and_motion_overlay_animation",
                static_summary["rendered_surfaces"]["temporal_checkpoint_series_animation"],
            )

    def test_motion_animated_visual_session_handles_two_checkpoint_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "motion"
            examples = run_motion_structural_examples(
                output_root=output_root,
                session_id="S9405",
                example_names=("coherence_transfer_control",),
            )

            result = render_motion_animated_visual_session(session_root=examples.session_root)

            self.assertEqual(1, len(result.records))
            record = result.records[0]
            self.assertEqual(2, record.frame_count)
            self.assertTrue(record.motion_animation_path.exists())
            summary = _read_json(record.animated_summary_path)
            self.assertEqual(2, len(summary["frame_checkpoint_linkage"]))
            self.assertEqual(
                "graph_engine_sequence_and_motion_animation_complete",
                result.to_mapping()["temporal_rendering_status"],
            )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
