"""Tests for GRC9V3 visual review indexing."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9v3_visual_review as exported_runner
from pygrc.discovery.grc9v3_visual_review import run_grc9v3_visual_review


class GRC9V3VisualReviewTest(unittest.TestCase):
    def test_visual_review_renders_and_links_checkpoint_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            manifest_path = tmp_path / "selector_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "motifs": [
                            {
                                "motif_id": "grc9v3-motif-test-visual",
                                "lane": "complex_spark_expansion_hierarchy_complex_control",
                                "phenomenon": "complex_spark_expansion_hierarchy_complex_control",
                                "confidence_label": "strong_candidate",
                                "confidence_score": 5,
                                "step_window": [0, 3],
                                "session_ids": ["S0008"],
                                "notes": {
                                    "artifact_root": (
                                        "outputs/grc9v3/phenomenology_discovery/"
                                        "sessions/S0008/generated_lanes/"
                                        "complex_spark_expansion_hierarchy_complex_control"
                                    )
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            session = run_grc9v3_visual_review(
                session_id="S0994",
                selector_session_id="S0993",
                session_root=tmp_path / "S0994",
                selector_manifest_path=manifest_path,
                update_experimental_log=False,
            )

            self.assertEqual(1, len(session.records))
            record = session.records[0]
            self.assertEqual("rendered_complete", record.visual_status)
            self.assertEqual("enabled", record.overlay_status)
            self.assertEqual((), record.missing_overlay_keys)
            self.assertEqual((), record.missing_visual_artifacts)
            self.assertEqual((), record.missing_exact_steps)
            self.assertEqual((0,), record.event_steps)
            self.assertEqual(3, len(record.checkpoint_links))
            self.assertTrue(all(Path(path).exists() for path in record.visual_artifacts))

            report = json.loads(Path(session.report_path).read_text(encoding="utf-8"))
            self.assertEqual(0, report["records_with_missing_visuals_count"])
            self.assertEqual(0, report["records_with_missing_overlays_count"])
            self.assertEqual({"enabled": 1}, report["overlay_status_counts"])

    def test_visual_review_skips_missing_artifact_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            manifest_path = tmp_path / "selector_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "motifs": [
                            {
                                "motif_id": "manual_missing_artifact_root",
                                "lane": "manual_lane",
                                "phenomenon": "manual",
                                "confidence_label": "candidate",
                                "confidence_score": 3,
                                "step_window": [0, 1],
                                "session_ids": ["S0000"],
                                "notes": {},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            session = run_grc9v3_visual_review(
                session_id="S0992",
                selector_session_id="S0991",
                session_root=tmp_path / "S0992",
                selector_manifest_path=manifest_path,
                render_visuals=False,
                update_experimental_log=False,
            )

            self.assertEqual(0, len(session.records))
            self.assertEqual(1, len(session.skipped_motifs))
            self.assertIn("artifact_root", session.skipped_motifs[0].reason)

    def test_visual_review_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9v3_visual_review)


if __name__ == "__main__":
    unittest.main()
