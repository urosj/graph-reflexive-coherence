from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pygrc.telemetry.pressure_boundary_complex_source_comparison import (
    GRC9_FRONT_CAPACITY_SOURCES,
    GRC9V3_FRONT_CAPACITY_SOURCES,
    run_pressure_boundary_complex_source_comparison,
)


class PressureBoundaryComplexSourceComparisonTest(unittest.TestCase):
    def test_comparison_records_all_sources_and_legacy_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_pressure_boundary_complex_source_comparison(
                session_id="S0001",
                output_root=Path(tmp),
                grc9_steps=2,
                grc9v3_steps=2,
            )

        rows = tuple(report["rows"])
        self.assertEqual(
            len(rows),
            2 + len(GRC9_FRONT_CAPACITY_SOURCES) + len(GRC9V3_FRONT_CAPACITY_SOURCES),
        )
        grc9_variants = {
            row["variant"] for row in rows if row["family"] == "grc9"
        }
        grc9v3_variants = {
            row["variant"] for row in rows if row["family"] == "grc9v3"
        }
        self.assertEqual(
            grc9_variants,
            {"legacy_any_inactive_port", *GRC9_FRONT_CAPACITY_SOURCES},
        )
        self.assertEqual(
            grc9v3_variants,
            {"legacy_any_inactive_port", *GRC9V3_FRONT_CAPACITY_SOURCES},
        )

    def test_pressure_boundary_rows_are_distinguished_from_generic_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_pressure_boundary_complex_source_comparison(
                session_id="S0001",
                output_root=Path(tmp),
                grc9_steps=2,
                grc9v3_steps=2,
            )

        pressure_rows = [
            row for row in report["rows"] if row["variant"] == "pressure_boundary"
        ]
        self.assertEqual(len(pressure_rows), 2)
        self.assertTrue(
            all(row["evidence_status"] == "pressure_boundary_specific" for row in pressure_rows)
        )
        legacy_rows = [
            row for row in report["rows"] if row["variant"] == "legacy_any_inactive_port"
        ]
        self.assertEqual(len(legacy_rows), 2)
        self.assertTrue(
            all(row["evidence_status"] == "diagnostic_legacy_control" for row in legacy_rows)
        )
        self.assertTrue(
            all(row["growth_parent_eligibility_mode"] for row in report["rows"])
        )


if __name__ == "__main__":
    unittest.main()
