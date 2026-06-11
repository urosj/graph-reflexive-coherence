"""Tests for GRC9/GRCL-9 growth-correction record classification."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.telemetry import (
    GROWTH_RECORD_CLASSIFICATION_VERSION,
    run_growth_record_classification,
)
from pygrc.telemetry.grc9_grcl9_growth_record_classification import (
    RETAINED_STATUS,
    SUPERSEDED_STATUS,
    classify_reviewed_record,
)


class GrowthRecordClassificationTest(unittest.TestCase):
    def test_direct_classifier_retains_independent_non_growth_record(self) -> None:
        record = {
            "motif_id": "grc9-motif-spark",
            "seed_name": "spark_column_proxy_eps_pass",
            "review_status": "accepted",
            "predicted_evidence_fields": ["family_extensions.grc9.spark_evidence.kind"],
        }

        classified = classify_reviewed_record(
            family="grc9",
            catalog_path="catalog.json",
            catalog_session_id="S0001",
            record=record,
            replacement_candidates={},
        )

        self.assertEqual(RETAINED_STATUS, classified["classification_status"])
        self.assertFalse(classified["growth_dependent"])
        self.assertIsNone(classified["supersession_link"])
        self.assertFalse(classified["accepted_growth_after_classification"])

    def test_direct_classifier_supersedes_growth_record_and_links_candidate(self) -> None:
        record = {
            "motif_id": "grcl9_lowered_s0024_cell_growth",
            "fixture_name": "cell_growth",
            "review_status": "accepted",
            "event_counts_by_kind": {"growth": 3},
        }
        candidates = {
            "cell_growth": (
                {
                    "fixture_name": "corrected_cell_growth",
                    "motif_id": "corrected-motif",
                    "source_session_id": "S0031",
                },
            )
        }

        classified = classify_reviewed_record(
            family="grcl9",
            catalog_path="catalog.json",
            catalog_session_id="S0024",
            record=record,
            replacement_candidates=candidates,
        )

        self.assertEqual(SUPERSEDED_STATUS, classified["classification_status"])
        self.assertTrue(classified["growth_dependent"])
        self.assertEqual(
            "grcl9_lowered_s0024_cell_growth",
            classified["supersession_link"]["old_motif_id"],
        )
        self.assertEqual(1, classified["replacement_candidate_count"])
        self.assertFalse(classified["accepted_growth_after_classification"])

    def test_runner_writes_replayable_classification_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            grc9_catalog = root / "grc9" / "S0001" / "reviewed_motif_catalog.json"
            grcl9_catalog = root / "grcl9" / "S0002" / "reviewed_grcl9_lowered_motif_catalog.json"
            corrected_manifest = root / "corrected" / "selector_manifest.json"
            _write_json(
                grc9_catalog,
                {
                    "session_id": "S0001",
                    "accepted_motifs": [
                        {
                            "motif_id": "grc9-motif-spark",
                            "seed_name": "spark_column_proxy_eps_pass",
                            "review_status": "accepted",
                        },
                        {
                            "motif_id": "grc9-motif-growth",
                            "seed_name": "growth_pressure_lambda_high",
                            "review_status": "accepted",
                        },
                    ],
                },
            )
            _write_json(
                grcl9_catalog,
                {
                    "session_id": "S0002",
                    "accepted_motifs": [
                        {
                            "motif_id": "grcl9-motif-cell",
                            "fixture_name": "cell_full_capacity_phase_balanced_low_growth",
                            "review_status": "accepted",
                            "event_counts_by_kind": {"growth": 2},
                        }
                    ],
                },
            )
            _write_json(
                corrected_manifest,
                {
                    "motifs": [
                        {
                            "fixture_name": (
                                "corrected_cell_full_capacity_phase_balanced_low_growth"
                            ),
                            "motif_id": "corrected-cell-motif",
                            "source_session_id": "S0031",
                            "confidence_label": "strong_candidate",
                            "evidence_status": "accepted",
                        }
                    ]
                },
            )

            session = run_growth_record_classification(
                session_id="S9101",
                output_root=root / "outputs" / "grcl9" / "lowering",
                grc9_catalog_paths=(grc9_catalog,),
                grcl9_catalog_paths=(grcl9_catalog,),
                corrected_selector_manifest_path=corrected_manifest,
            )

            payload = _read_json(session.classification_path)
            self.assertEqual(
                GROWTH_RECORD_CLASSIFICATION_VERSION,
                payload["classification_version"],
            )
            self.assertEqual(3, session.reviewed_record_count)
            self.assertEqual(1, session.retained_non_growth_count)
            self.assertEqual(2, session.superseded_count)
            self.assertEqual(
                0,
                payload["summary"]["accepted_growth_after_classification_count"],
            )
            superseded = {
                item["record_name"]: item for item in payload["superseded_records"]
            }
            self.assertIn("growth_pressure_lambda_high", superseded)
            self.assertEqual(
                1,
                superseded[
                    "cell_full_capacity_phase_balanced_low_growth"
                ]["replacement_candidate_count"],
            )
            self.assertTrue((session.session_root / "session_manifest.json").exists())
            self.assertTrue((root / "outputs" / "grcl9" / "lowering" / "ExperimentalLog.md").exists())

    def test_runner_is_exported_from_telemetry_package(self) -> None:
        from pygrc.telemetry.grc9_grcl9_growth_record_classification import (
            run_growth_record_classification as direct_runner,
        )

        self.assertIs(run_growth_record_classification, direct_runner)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

