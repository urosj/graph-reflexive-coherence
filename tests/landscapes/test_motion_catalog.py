from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes.motion_catalog import (
    MOTION_REVIEWED_CATALOG_VERSION,
    run_motion_reviewed_catalog_session,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


class MotionReviewedCatalogTest(unittest.TestCase):
    def test_catalog_distinguishes_s0004_diagnostic_from_s0005_promoted_fission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "motion"
            s0004 = root / "sessions" / "S0004"
            s0005 = root / "sessions" / "S0005"
            _write_json(
                s0004 / "run_report.json",
                {"session_version": "motion_landscape_bridge_iter12_1_v1"},
            )
            _write_json(
                s0004 / "interpretation" / "motion_interpretation_summary.json",
                {
                    "session_id": "S0004",
                    "session_version": "motion_interpretation_iter12_2_v1",
                    "runs": [
                        {
                            "key": "dense_branching_probe",
                            "runtime_family": "grc9v3",
                            "motion_record_counts": {"identity": 700, "topological": 2},
                            "motion_relationship_counts": {
                                "identity": {"split": 700},
                                "topological": {"emerged": 2},
                            },
                            "catalog_recommendation": "review_identity_split_with_promotion_gate",
                            "motion_report_dir": "outputs/test/s0004/motion_reports",
                            "calibration_notes": ["dense split requires promotion review"],
                        }
                    ],
                },
            )
            _write_json(
                s0004 / "interpretation" / "dense_window_calibration_summary.json",
                {
                    "session_id": "S0004",
                    "session_version": "motion_dense_window_calibration_iter12_3_v1",
                    "runs": [
                        {
                            "key": "dense_branching_probe",
                            "catalog_guidance": (
                                "catalog_dense_carrier_branching_as_diagnostic_not_identity_fission"
                            ),
                        }
                    ],
                },
            )
            _write_json(
                s0004 / "interpretation" / "identity_fission_promotion_summary.json",
                {
                    "session_id": "S0004",
                    "session_version": "motion_identity_fission_promotion_iter12_4_v1",
                    "runs": [
                        {
                            "key": "dense_branching_probe",
                            "runtime_family": "grc9v3",
                            "promoted_identity_fission_count": 0,
                            "catalog_guidance": "keep_dense_branching_diagnostic_not_identity_fission",
                        }
                    ],
                },
            )

            _write_json(
                s0005 / "run_report.json",
                {"session_version": "motion_dense_fission_iter12_5_v1"},
            )
            _write_json(
                s0005 / "landscape_motion_summary.json",
                {
                    "session_id": "S0005",
                    "session_version": "motion_dense_fission_iter12_5_v1",
                    "runs": [
                        {
                            "key": "motion_dense_confirmed_fission",
                            "runtime_family": "grc9v3",
                            "motion_relationship_counts": {
                                "identity": {"split": 501},
                                "topological": {"split": 501},
                            },
                        }
                    ],
                },
            )
            _write_json(
                s0005 / "interpretation" / "identity_fission_promotion_summary.json",
                {
                    "session_id": "S0005",
                    "session_version": "motion_identity_fission_promotion_iter12_4_v1",
                    "runs": [
                        {
                            "key": "motion_dense_confirmed_fission",
                            "runtime_family": "grc9v3",
                            "promoted_identity_fission_count": 501,
                            "catalog_guidance": "promote_supported_identity_fission_candidates",
                        }
                    ],
                },
            )

            catalog = run_motion_reviewed_catalog_session(
                output_root=root,
                session_id="S0099",
                source_session_ids=("S0004", "S0005"),
            )

            self.assertEqual(MOTION_REVIEWED_CATALOG_VERSION, catalog["session_version"])
            by_key = {entry["key"]: entry for entry in catalog["entries"]}
            self.assertEqual("diagnostic", by_key["dense_branching_probe"]["status"])
            self.assertEqual(
                "keep_dense_branching_diagnostic_not_identity_fission",
                by_key["dense_branching_probe"]["catalog_decision"],
            )
            self.assertEqual("accepted", by_key["motion_dense_confirmed_fission"]["status"])
            self.assertEqual(
                "promote_supported_identity_fission_candidates",
                by_key["motion_dense_confirmed_fission"]["catalog_decision"],
            )
            self.assertIn(
                "motion-catalog-s0005-motion_dense_confirmed_fission",
                catalog["aggregate"]["accepted_entry_ids"],
            )
            self.assertTrue((root / "sessions" / "S0099" / "reviewed_motion_catalog.md").exists())
            self.assertTrue((root / "sessions" / "S0099" / "session_manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
