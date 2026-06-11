from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes.motion_interpretation import (
    MOTION_DENSE_WINDOW_CALIBRATION_VERSION,
    MOTION_IDENTITY_FISSION_PROMOTION_VERSION,
    MOTION_INTERPRETATION_VERSION,
    run_motion_identity_fission_promotion_session,
    run_motion_dense_window_calibration_session,
    run_motion_interpretation_session,
)


class MotionInterpretationTest(unittest.TestCase):
    def test_interpretation_labels_dense_split_and_family_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "S9901"
            root.mkdir(parents=True)
            (root / "landscape_motion_summary.json").write_text(
                json.dumps(
                    {
                        "session_id": "S9901",
                        "runs": [
                            {
                                "key": "relay_probe",
                                "runtime_family": "grc9v3",
                                "checkpoint_count_loaded": 24,
                                "primitive_counts_by_type": {"basin": 4, "valley": 3},
                                "landscape_relationship_counts": {"split": 1},
                                "motion_record_counts": {
                                    "boundary": 3,
                                    "coherence": 2,
                                    "identity": 80,
                                    "representative": 5,
                                    "topological": 1,
                                },
                                "motion_relationship_counts": {
                                    "boundary": {"drifted": 3},
                                    "coherence": {"drifted": 2},
                                    "identity": {"split": 80},
                                    "representative": {"stationary": 5},
                                    "topological": {"emerged": 1},
                                },
                                "visual_notes": [
                                    "identity emitted 80 records; dense visual timelines are sampled"
                                ],
                            },
                            {
                                "key": "grcv3_probe",
                                "runtime_family": "grcv3",
                                "checkpoint_count_loaded": 5,
                                "primitive_counts_by_type": {"basin": 2},
                                "landscape_relationship_counts": {},
                                "motion_record_counts": {
                                    "boundary": 0,
                                    "coherence": 1,
                                    "identity": 0,
                                    "representative": 0,
                                    "topological": 1,
                                },
                                "motion_relationship_counts": {
                                    "boundary": {},
                                    "coherence": {"drifted": 1},
                                    "identity": {},
                                    "representative": {},
                                    "topological": {"dissolved": 1},
                                },
                                "visual_notes": [],
                            },
                        ],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            session = run_motion_interpretation_session(session_root=root)

            payload = session.to_mapping()
            self.assertEqual(MOTION_INTERPRETATION_VERSION, payload["session_version"])
            by_key = {run["key"]: run for run in payload["runs"]}
            self.assertIn(
                "identity_split_overproduction_review",
                by_key["relay_probe"]["evidence_labels"],
            )
            self.assertIn("dense_timeline_sampled", by_key["relay_probe"]["evidence_labels"])
            self.assertIn(
                "boundary_motion_family_limited",
                by_key["grcv3_probe"]["evidence_labels"],
            )
            self.assertIn(
                "coherence_motion_accepted",
                by_key["grcv3_probe"]["evidence_labels"],
            )
            self.assertTrue((root / "interpretation" / "motion_interpretation_summary.json").exists())
            self.assertTrue((root / "interpretation" / "motion_interpretation.md").exists())
            self.assertTrue(
                (root / "interpretation" / "knowledge_graph_motion_case_study.md").exists()
            )
            written = json.loads(
                (root / "interpretation" / "motion_interpretation_summary.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                "interpretation_reads_existing_motion_and_landscape_summaries_only",
                written["source_runtime_boundary"],
            )

    def test_dense_window_calibration_keeps_branching_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "S9902"
            root.mkdir(parents=True)
            (root / "landscape_motion_summary.json").write_text(
                json.dumps(
                    {
                        "session_id": "S9902",
                        "runs": [
                            {
                                "key": "dense_identity_probe",
                                "runtime_family": "grc9v3",
                                "checkpoint_count_loaded": 101,
                                "primitive_counts_by_type": {"basin": 12},
                                "landscape_relationship_counts": {},
                                "motion_record_counts": {
                                    "boundary": 100,
                                    "coherence": 30,
                                    "identity": 700,
                                    "representative": 700,
                                    "topological": 2,
                                },
                                "motion_relationship_counts": {
                                    "boundary": {"stationary": 100},
                                    "coherence": {"drifted": 30},
                                    "identity": {"split": 700},
                                    "representative": {"stationary": 700},
                                    "topological": {"emerged": 2},
                                },
                                "motion_report_dir": "outputs/test/motion_reports",
                                "visual_notes": [],
                            },
                            {
                                "key": "dense_confirmed_candidate_probe",
                                "runtime_family": "grc9v3",
                                "checkpoint_count_loaded": 502,
                                "primitive_counts_by_type": {"basin": 1503},
                                "landscape_relationship_counts": {},
                                "motion_record_counts": {
                                    "identity": 2001,
                                    "representative": 0,
                                    "topological": 501,
                                },
                                "motion_relationship_counts": {
                                    "identity": {
                                        "split": 501,
                                        "dissolved": 1000,
                                        "emerged": 500,
                                    },
                                    "topological": {"split": 501},
                                },
                                "motion_report_dir": "outputs/test/confirmed_reports",
                                "visual_notes": [],
                            },
                            {
                                "key": "small_split_probe",
                                "runtime_family": "grc9v3",
                                "checkpoint_count_loaded": 4,
                                "primitive_counts_by_type": {"basin": 3},
                                "landscape_relationship_counts": {},
                                "motion_record_counts": {
                                    "boundary": 0,
                                    "coherence": 1,
                                    "identity": 8,
                                    "representative": 8,
                                    "topological": 0,
                                },
                                "motion_relationship_counts": {
                                    "coherence": {"drifted": 1},
                                    "identity": {"split": 8},
                                    "representative": {"stationary": 8},
                                },
                                "motion_report_dir": "outputs/test/small_reports",
                                "visual_notes": [],
                            },
                        ],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            session = run_motion_dense_window_calibration_session(session_root=root)

            payload = session.to_mapping()
            self.assertEqual(MOTION_DENSE_WINDOW_CALIBRATION_VERSION, payload["session_version"])
            by_key = {run["key"]: run for run in payload["runs"]}
            self.assertTrue(by_key["dense_identity_probe"]["dense_window"])
            self.assertIn(
                "catalog_as_dense_carrier_branching_not_fission",
                by_key["dense_identity_probe"]["calibration_labels"],
            )
            self.assertIn(
                "representative_stationary_identity_branching",
                by_key["dense_identity_probe"]["calibration_labels"],
            )
            self.assertEqual(
                "review_dense_identity_split_with_promotion_gate",
                by_key["dense_confirmed_candidate_probe"]["catalog_guidance"],
            )
            self.assertIn(
                "dense_identity_split_review_needed",
                by_key["dense_confirmed_candidate_probe"]["calibration_labels"],
            )
            self.assertFalse(by_key["small_split_probe"]["dense_window"])
            self.assertIn(
                "split_dominant_small_window_review",
                by_key["small_split_probe"]["calibration_labels"],
            )
            self.assertTrue(
                (root / "interpretation" / "dense_window_calibration_summary.json").exists()
            )
            self.assertTrue((root / "interpretation" / "dense_window_calibration.md").exists())

    def test_identity_fission_promotion_requires_compact_provenance_linkage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "S9903"
            root.mkdir(parents=True)
            supported_reports = root / "supported_reports"
            fanout_reports = root / "fanout_reports"
            supported_reports.mkdir()
            fanout_reports.mkdir()
            (supported_reports / "identity_report.json").write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "motion_id": "supported_split",
                                "relationship": "split",
                                "confidence": 0.86,
                                "evidence_quality": "strong",
                                "old_carriers": {"basin_ids": ["parent"]},
                                "new_carriers": {"basin_ids": ["child_a", "child_b"]},
                                "transferred_mass": 4.0,
                            }
                        ]
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            (supported_reports / "identity_summary.json").write_text(
                json.dumps(
                    {
                        "matches": [
                            {
                                "old_group_id": "parent",
                                "new_group_id": "child_a",
                                "hierarchy_provenance_continuity": 0.9,
                            },
                            {
                                "old_group_id": "parent",
                                "new_group_id": "child_b",
                                "hierarchy_provenance_continuity": 0.85,
                            },
                        ]
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            (fanout_reports / "identity_report.json").write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "motion_id": "fanout_split",
                                "relationship": "split",
                                "confidence": 0.6,
                                "evidence_quality": "partial",
                                "old_carriers": {"basin_ids": ["parent"]},
                                "new_carriers": {
                                    "basin_ids": [
                                        "a",
                                        "b",
                                        "c",
                                        "d",
                                        "e",
                                        "f",
                                        "g",
                                        "h",
                                    ]
                                },
                                "transferred_mass": 4.0,
                            }
                        ]
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            (fanout_reports / "identity_summary.json").write_text(
                json.dumps({"matches": []}, sort_keys=True),
                encoding="utf-8",
            )
            (root / "landscape_motion_summary.json").write_text(
                json.dumps(
                    {
                        "session_id": "S9903",
                        "runs": [
                            {
                                "key": "supported_fission_probe",
                                "runtime_family": "grc9v3",
                                "checkpoint_count_loaded": 2,
                                "primitive_counts_by_type": {"basin": 3},
                                "landscape_relationship_counts": {},
                                "motion_record_counts": {
                                    "identity": 1,
                                    "representative": 0,
                                },
                                "motion_relationship_counts": {
                                    "identity": {"split": 1},
                                    "representative": {},
                                },
                                "motion_report_dir": str(supported_reports),
                                "visual_notes": [],
                            },
                            {
                                "key": "fanout_probe",
                                "runtime_family": "grc9v3",
                                "checkpoint_count_loaded": 2,
                                "primitive_counts_by_type": {"basin": 8},
                                "landscape_relationship_counts": {},
                                "motion_record_counts": {
                                    "identity": 600,
                                    "representative": 600,
                                },
                                "motion_relationship_counts": {
                                    "identity": {"split": 600},
                                    "representative": {"stationary": 600},
                                },
                                "motion_report_dir": str(fanout_reports),
                                "visual_notes": [],
                            },
                        ],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            session = run_motion_identity_fission_promotion_session(session_root=root)

            payload = session.to_mapping()
            self.assertEqual(
                MOTION_IDENTITY_FISSION_PROMOTION_VERSION,
                payload["session_version"],
            )
            by_key = {run["key"]: run for run in payload["runs"]}
            self.assertEqual(1, by_key["supported_fission_probe"]["promoted_identity_fission_count"])
            self.assertIn(
                "accepted_identity_fission_candidate",
                by_key["supported_fission_probe"]["promotion_labels"],
            )
            self.assertEqual(0, by_key["fanout_probe"]["promoted_identity_fission_count"])
            self.assertIn("dense_fanout_rejected", by_key["fanout_probe"]["promotion_labels"])
            self.assertTrue(
                (root / "interpretation" / "identity_fission_promotion_summary.json").exists()
            )
            self.assertTrue((root / "interpretation" / "identity_fission_promotion.md").exists())


if __name__ == "__main__":
    unittest.main()
