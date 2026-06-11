"""Cross-family pressure-boundary comparison tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pygrc.telemetry.pressure_boundary_cross_family import (
    build_pressure_boundary_cross_family_report,
    write_pressure_boundary_cross_family_session,
)


class PressureBoundaryCrossFamilyTest(unittest.TestCase):
    def test_current_evidence_rows_all_pass_shared_observable(self) -> None:
        report = build_pressure_boundary_cross_family_report()

        self.assertTrue(report["shared_result"])
        self.assertEqual(
            ["grc9", "grc9v3", "grcl9", "grcl9v3", "grcv3"],
            [row["family"] for row in report["families"]],
        )
        for row in report["families"]:
            self.assertGreater(row["pressure_boundary_birth_count"], 0)
            self.assertEqual(0, row["legacy_broad_growth_count"])
            self.assertTrue(row["evidence_passed"])

    def test_writes_replayable_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = write_pressure_boundary_cross_family_session(
                session_id="S_TEST",
                output_root=Path(tmpdir) / "cross_family",
            )

            session_dir = Path(report["session_root"])
            self.assertTrue((session_dir / "comparison_report.json").exists())
            self.assertTrue((session_dir / "comparison_report.md").exists())
            self.assertTrue((session_dir / "session_manifest.json").exists())
            self.assertIn("pressure_boundary_cross_family", report["replay_command"])


if __name__ == "__main__":
    unittest.main()
