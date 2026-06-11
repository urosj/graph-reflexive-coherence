"""Replayable GRCV3 pressure-boundary evidence session tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pygrc.telemetry.grcv3_pressure_boundary_evidence import (
    run_grcv3_pressure_boundary_evidence_session,
)


class GRCV3PressureBoundaryEvidenceTest(unittest.TestCase):
    def test_session_writes_positive_and_compatibility_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = run_grcv3_pressure_boundary_evidence_session(
                session_id="S_TEST",
                output_root=Path(tmpdir) / "sessions",
            )

            session_dir = Path(report["session_root"])
            self.assertTrue((session_dir / "session_manifest.json").exists())
            self.assertTrue((session_dir / "source_fixtures" / "pressure_boundary_frontier.json").exists())
            self.assertEqual(
                [
                    "compat_missing_frontier_birth_mode",
                    "compat_disabled_frontier_birth_mode",
                    "pressure_boundary_frontier_birth_positive",
                ],
                [lane["lane_name"] for lane in report["lanes"]],
            )
            self.assertTrue(report["compatibility"]["missing_mode_no_birth"])
            self.assertTrue(report["compatibility"]["disabled_mode_no_birth"])
            self.assertEqual(0, report["lanes"][0]["frontier_birth_count"])
            self.assertEqual(0, report["lanes"][1]["frontier_birth_count"])
            self.assertEqual(1, report["lanes"][2]["frontier_birth_count"])
            self.assertEqual(1, report["lanes"][2]["pressure_boundary_birth_count"])
            self.assertTrue(report["lanes"][2]["selector_passed"])

            positive_summary_path = (
                session_dir
                / "lanes"
                / "pressure_boundary_frontier_birth_positive"
                / "telemetry"
                / "run_summary.json"
            )
            summary = json.loads(positive_summary_path.read_text(encoding="utf-8"))
            frontier_summary = summary["family_extensions"]["grcv3"]["frontier_birth_summary"]
            self.assertEqual("active_frontier_pressure", frontier_summary["frontier_birth_mode"])
            self.assertEqual(1, frontier_summary["pressure_boundary_birth_count"])
            self.assertIn("pressure_boundary", frontier_summary["frontier_sources_observed"])


if __name__ == "__main__":
    unittest.main()
