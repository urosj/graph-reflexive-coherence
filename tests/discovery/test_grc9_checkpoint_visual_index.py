"""Tests for GRC9 checkpoint and visual index generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9_checkpoint_visual_index as exported_runner
from pygrc.discovery.grc9_checkpoint_visual_index import (
    run_grc9_checkpoint_visual_index,
)


class GRC9CheckpointVisualIndexTest(unittest.TestCase):
    def test_checkpoint_visual_index_links_selector_motifs_to_exact_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_checkpoint_visual_index(
                session_id="S0995",
                selector_session_id="S0022",
                session_root=Path(tmpdir) / "S0995",
            )

            self.assertEqual(51, len(session.records))
            self.assertTrue(
                all(not record.missing_exact_steps for record in session.records)
            )
            self.assertTrue(
                all(record.checkpoint_links for record in session.records)
            )

    def test_complex_motifs_link_event_steps_and_report_unrendered_visuals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_checkpoint_visual_index(
                session_id="S0994",
                selector_session_id="S0022",
                session_root=Path(tmpdir) / "S0994",
            )
            complex_records = [
                record
                for record in session.records
                if record.lane_name.startswith("all_events_complex")
            ]

            self.assertEqual(5, len(complex_records))
            for record in complex_records:
                self.assertEqual(tuple(range(6)), record.event_steps)
                self.assertEqual("not_rendered", record.visual_status)
                self.assertEqual(7, len(record.checkpoint_links))

    def test_missing_artifact_root_skips_motif_instead_of_failing_session(self) -> None:
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
            session = run_grc9_checkpoint_visual_index(
                session_id="S0993",
                selector_session_id="S0992",
                session_root=tmp_path / "S0993",
                selector_manifest_path=manifest_path,
            )

            self.assertEqual(0, len(session.records))
            self.assertEqual(1, len(session.skipped_motifs))
            self.assertIn("artifact_root", session.skipped_motifs[0].reason)

    def test_checkpoint_visual_index_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9_checkpoint_visual_index)


if __name__ == "__main__":
    unittest.main()
