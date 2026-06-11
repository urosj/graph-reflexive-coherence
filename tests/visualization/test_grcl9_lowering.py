"""Tests for GRCL-9 lowering visualization wrappers."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.telemetry import run_grcl9_lowering_replay_session
from pygrc.visualization import render_grcl9_lowering_visual_session


class GRCL9VisualizationTest(unittest.TestCase):
    def test_visualization_renders_behavior_graph_and_boundary_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay = run_grcl9_lowering_replay_session(
                session_id="S9101",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="landscape_seed_examples",
                fixture_names=("corrected_front_growth_positive_high",),
                requested_steps=2,
            )

            result = render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
            )

            self.assertEqual(1, len(result.lanes))
            lane = result.lanes[0]
            self.assertTrue(Path(lane.trajectory_path).exists())
            self.assertTrue(Path(lane.event_timeline_path).exists())
            self.assertTrue(Path(lane.graph_sequence_path).exists())
            self.assertTrue(Path(lane.graph_html_path).exists())
            self.assertTrue(Path(lane.grcl9_overlay_path).exists())
            self.assertTrue(Path(lane.grcl9_overlay_summary_path).exists())
            self.assertTrue(Path(lane.boundary_panel_path).exists())
            self.assertTrue(result.visualization_manifest_path.exists())
            self.assertTrue(result.index_path.exists())
            self.assertTrue(lane.connected)
            self.assertEqual("corrected_front_capacity_evidence", lane.evidence_status)
            self.assertEqual("grc9_front_capacity", lane.growth_parent_eligibility_mode)

    def test_visualization_makes_bridge_edges_and_boundary_claims_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay = run_grcl9_lowering_replay_session(
                session_id="S9102",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                fixture_names=("post_expansion_fission_min_mass_pass",),
                requested_steps=1,
            )

            result = render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
            )
            lane = result.lanes[0]
            summary = _read_json(Path(lane.grcl9_overlay_summary_path))
            boundary = Path(lane.boundary_panel_path).read_text(encoding="utf-8")

            self.assertEqual(1, lane.bridge_edge_count)
            self.assertEqual([2], summary["bridge_edge_ids"])
            self.assertIn("fission_separable_bridge", summary["motif_roles"])
            self.assertIn("Source Intent", boundary)
            self.assertIn("Runtime Observation", boundary)
            self.assertIn("preconditions and intent labels", boundary)

    def test_visualization_marks_collapse_adjacent_structural_probes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay = run_grcl9_lowering_replay_session(
                session_id="S9103",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="landscape_seed_examples",
                fixture_names=("cell_basin_merge_before_persistence_probe",),
                requested_steps=1,
            )

            result = render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
            )
            lane = result.lanes[0]
            summary = _read_json(Path(lane.grcl9_overlay_summary_path))
            boundary = Path(lane.boundary_panel_path).read_text(encoding="utf-8")

            self.assertEqual(1, len(summary["collapse_adjacent_visuals"]))
            visual = summary["collapse_adjacent_visuals"][0]
            self.assertEqual("collapse_adjacent_structural_probe", visual["visual_kind"])
            self.assertEqual(2, visual["source_node_id"])
            self.assertEqual(1, visual["target_node_id"])
            self.assertEqual(
                [
                    "basin_merge_pressure_candidate",
                    "fission_persistence_failed_candidate",
                ],
                visual["selector_ids"],
            )
            self.assertIn("does not claim a GRC9 collapse event", visual["claim_boundary"])
            self.assertIn("Collapse-Adjacent Structural Probe", boundary)
            self.assertIn("not runtime collapse", boundary)

    def test_visualization_marks_long_window_collapse_like_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay = run_grcl9_lowering_replay_session(
                session_id="S9104",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="landscape_seed_examples",
                fixture_names=("cell_developed_basin_centroid_collapse_long_window",),
                requested_steps=24,
            )

            result = render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
            )
            lane = result.lanes[0]
            summary = _read_json(Path(lane.grcl9_overlay_summary_path))

            self.assertEqual(8, lane.bridge_edge_count)
            self.assertEqual(1, len(summary["collapse_adjacent_visuals"]))
            visual = summary["collapse_adjacent_visuals"][0]
            self.assertEqual("collapse_adjacent_structural_probe", visual["visual_kind"])
            self.assertEqual("runtime_collapse_like_long_window", visual["selector_ids"][0])
            self.assertEqual(2, visual["source_node_id"])
            self.assertEqual(1, visual["target_node_id"])

    def test_visualization_marks_full_capacity_cascade_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay = run_grcl9_lowering_replay_session(
                session_id="S9105",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="legacy_growth_landscape_seed_examples",
                fixture_names=("cell_full_capacity_phenomenology_cascade",),
                requested_steps=24,
                force_legacy_growth=True,
            )

            with self.assertRaisesRegex(ValueError, "force-legacy-growth"):
                render_grcl9_lowering_visual_session(session_root=replay.session_root)
            result = render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
                force_legacy_growth=True,
            )
            lane = result.lanes[0]
            summary = _read_json(Path(lane.grcl9_overlay_summary_path))

            self.assertEqual("passed", lane.selector_status)
            self.assertTrue(lane.connected)
            self.assertEqual(24, summary["node_count"])
            self.assertEqual(28, summary["edge_count"])
            self.assertIn("candidate", summary["motif_roles"])
            self.assertIn("growth_parent", summary["motif_roles"])
            self.assertIn("fission_sink_a", summary["motif_roles"])
            self.assertEqual(1, len(summary["collapse_adjacent_visuals"]))

    def test_visualization_marks_legacy_growth_as_non_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay = run_grcl9_lowering_replay_session(
                session_id="S9107",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="legacy_growth_landscape_seed_examples",
                fixture_names=("growth_pressure_lambda_high",),
                requested_steps=1,
                force_legacy_growth=True,
            )

            result = render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
                force_legacy_growth=True,
            )
            lane = result.lanes[0]
            summary = _read_json(Path(lane.grcl9_overlay_summary_path))
            boundary = Path(lane.boundary_panel_path).read_text(encoding="utf-8")
            index = result.index_path.read_text(encoding="utf-8")

            self.assertEqual("legacy_broad_growth_non_evidence", lane.evidence_status)
            self.assertEqual("legacy_any_inactive_port", lane.growth_parent_eligibility_mode)
            self.assertTrue(lane.legacy_broad_growth_non_evidence)
            self.assertEqual(
                "legacy_broad_growth_non_evidence",
                summary["growth_metadata"]["evidence_status"],
            )
            self.assertIn("Legacy broad-growth count", boundary)
            self.assertIn("legacy_broad_growth_non_evidence", index)

    def test_visualization_writes_phase_diagram_summary_and_matrix_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay = run_grcl9_lowering_replay_session(
                session_id="S9106",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="legacy_growth_landscape_seed_examples",
                fixture_names=(
                    "cell_full_capacity_phase_balanced_no_growth",
                    "cell_full_capacity_phase_balanced_low_growth",
                    "cell_full_capacity_phase_balanced_nominal_growth",
                    "cell_full_capacity_phase_mild_no_growth",
                    "cell_full_capacity_phase_mild_low_growth",
                    "cell_full_capacity_phase_mild_nominal_growth",
                    "cell_full_capacity_phase_threshold_no_growth",
                    "cell_full_capacity_phase_threshold_low_growth",
                    "cell_full_capacity_phase_threshold_nominal_growth",
                    "cell_full_capacity_phase_deep_no_growth",
                    "cell_full_capacity_phase_deep_low_growth",
                    "cell_full_capacity_phase_deep_nominal_growth",
                ),
                requested_steps=24,
                force_legacy_growth=True,
            )

            result = render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
                force_legacy_growth=True,
            )
            reports_root = replay.session_root / "reports"
            summary_path = reports_root / "phase_diagram_summary.json"
            summary_md_path = reports_root / "phase_diagram_summary.md"
            visual_index_path = result.visualization_root / "phase_diagram_visual_index.md"

            self.assertTrue(summary_path.exists())
            self.assertTrue(summary_md_path.exists())
            self.assertTrue(visual_index_path.exists())

            summary = _read_json(summary_path)
            self.assertEqual("grcl9_phase_diagram_summary_v1", summary["summary_version"])
            self.assertEqual(12, summary["lane_count"])
            self.assertEqual(12, len(summary["lanes"]))
            self.assertEqual("runaway", summary["phase_matrix"]["mild:low_growth"]["event_amplification_class"])
            self.assertEqual(
                "runtime_collapse_like_observed",
                summary["phase_matrix"]["threshold:nominal_growth"]["classification"],
            )

            summary_md = summary_md_path.read_text(encoding="utf-8")
            visual_index = visual_index_path.read_text(encoding="utf-8")
            self.assertIn("GRCL-9 Phase Diagram Summary", summary_md)
            self.assertIn("GRCL-9 Phase Diagram Visual Index", visual_index)
            self.assertIn("[sequence]", visual_index)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
