"""Tests for GRC9/GRCL-9 growth supersession summary."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.telemetry import (
    GROWTH_SUPERSESSION_SUMMARY_VERSION,
    run_growth_supersession_summary,
)
from pygrc.telemetry.grc9_grcl9_growth_supersession_summary import (
    build_growth_supersession_summary,
)


class GrowthSupersessionSummaryTest(unittest.TestCase):
    def test_build_summary_counts_linked_and_unresolved_records(self) -> None:
        classification = {
            "session_id": "S1001",
            "retained_non_growth_records": [{"old_motif_id": "keep"}],
            "superseded_records": [
                {"family": "grc9", "old_motif_id": "old-a", "record_name": "a"},
                {"family": "grcl9", "old_motif_id": "old-b", "record_name": "b"},
            ],
        }
        grc9_catalog = {
            "session_id": "S1002",
            "summary": {"accepted_legacy_broad_growth_count": 0},
            "accepted_corrected_growth_motifs": [
                {"motif_id": "new-a", "supersedes_old_motif_ids": ["old-a"]}
            ],
            "accepted_corrected_control_motifs": [],
            "rejected_motifs": [],
        }
        grcl9_catalog = {
            "session_id": "S1003",
            "summary": {"accepted_legacy_broad_growth_count": 0},
            "accepted_corrected_growth_motifs": [],
            "accepted_corrected_control_motifs": [],
            "rejected_motifs": [],
        }

        payload = build_growth_supersession_summary(
            session_id="S1004",
            session_root=Path("root"),
            classification=classification,
            grc9_catalog=grc9_catalog,
            grcl9_catalog=grcl9_catalog,
            classification_path=Path("classification.json"),
            grc9_catalog_path=Path("grc9.json"),
            grcl9_catalog_path=Path("grcl9.json"),
        )

        self.assertEqual(GROWTH_SUPERSESSION_SUMMARY_VERSION, payload["summary_version"])
        self.assertEqual(1, payload["summary"]["retained_non_growth_record_count"])
        self.assertEqual(2, payload["summary"]["superseded_record_count"])
        self.assertEqual(1, payload["summary"]["accepted_corrected_growth_record_count"])
        self.assertEqual(1, payload["summary"]["unresolved_superseded_record_count"])
        self.assertEqual(
            [{"family": "grcl9", "old_motif_id": "old-b", "record_name": "b", "catalog_session_id": "", "classification_status": ""}],
            payload["unresolved_superseded_records"],
        )

    def test_runner_writes_summary_artifacts_and_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "outputs" / "grcl9" / "lowering"
            classification_path = root / "sessions" / "S1001" / "growth_record_classification.json"
            grc9_catalog_path = (
                Path(temp_dir)
                / "outputs"
                / "grc9"
                / "phenomenology_discovery"
                / "sessions"
                / "S1002"
                / "corrected_grc9_growth_catalog.json"
            )
            grcl9_catalog_path = root / "sessions" / "S1003" / "corrected_grcl9_growth_catalog.json"
            _write_json(
                classification_path,
                {
                    "session_id": "S1001",
                    "grc9_catalog_paths": ["old-grc9.json"],
                    "grcl9_catalog_paths": ["old-grcl9.json"],
                    "retained_non_growth_records": [{"old_motif_id": "keep"}],
                    "superseded_records": [
                        {
                            "family": "grc9",
                            "old_motif_id": "old-a",
                            "record_name": "growth_a",
                            "catalog_session_id": "S0001",
                            "classification_status": "superseded_by_growth_semantics_correction",
                        }
                    ],
                },
            )
            _write_json(
                classification_path.parent / "session_manifest.json",
                {"replay_command": "classify"},
            )
            _write_json(
                grc9_catalog_path,
                {
                    "session_id": "S1002",
                    "summary": {"accepted_legacy_broad_growth_count": 0},
                    "accepted_corrected_growth_motifs": [
                        {"motif_id": "new-a", "supersedes_old_motif_ids": ["old-a"]}
                    ],
                    "accepted_corrected_control_motifs": [],
                    "rejected_motifs": [],
                },
            )
            _write_json(
                grc9_catalog_path.parent / "session_manifest.json",
                {"replay_command": "grc9-catalog"},
            )
            _write_json(
                grcl9_catalog_path,
                {
                    "session_id": "S1003",
                    "summary": {"accepted_legacy_broad_growth_count": 0},
                    "accepted_corrected_growth_motifs": [],
                    "accepted_corrected_control_motifs": [],
                    "rejected_motifs": [],
                },
            )
            _write_json(
                grcl9_catalog_path.parent / "session_manifest.json",
                {"replay_command": "grcl9-catalog"},
            )

            session = run_growth_supersession_summary(
                session_id="S1004",
                output_root=root,
                classification_path=classification_path,
                grc9_catalog_path=grc9_catalog_path,
                grcl9_catalog_path=grcl9_catalog_path,
            )

            payload = _read_json(session.summary_path)
            self.assertEqual(1, session.retained_non_growth_count)
            self.assertEqual(1, session.superseded_count)
            self.assertEqual(1, session.accepted_corrected_growth_count)
            self.assertEqual(0, session.unresolved_superseded_count)
            self.assertEqual("classify", payload["replay_commands"]["classification"])
            self.assertTrue(session.report_path.exists())
            self.assertTrue(session.markdown_path.exists())
            self.assertTrue((session.session_root / "session_manifest.json").exists())
            self.assertTrue((root / "ExperimentalLog.md").exists())

    def test_runner_is_exported_from_telemetry_package(self) -> None:
        from pygrc.telemetry.grc9_grcl9_growth_supersession_summary import (
            run_growth_supersession_summary as direct_runner,
        )

        self.assertIs(run_growth_supersession_summary, direct_runner)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

