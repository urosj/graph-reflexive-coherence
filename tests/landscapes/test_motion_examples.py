from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes.motion_examples import (
    MOTION_EXAMPLES_SESSION_VERSION,
    default_motion_structural_example_specs,
    run_motion_structural_examples,
)


class MotionStructuralExamplesTest(unittest.TestCase):
    def test_default_examples_cover_iteration_8_categories(self) -> None:
        specs = default_motion_structural_example_specs()
        names = {spec.example_name for spec in specs}

        self.assertIn("coherence_transfer_control", names)
        self.assertIn("representative_drift_control", names)
        self.assertIn("identity_walking_control", names)
        self.assertIn("identity_split_control", names)
        self.assertIn("identity_merge_control", names)
        self.assertIn("identity_collapse_control", names)
        self.assertIn("grc9_port_frontier_motion", names)
        self.assertIn("grc9v3_hybrid_refinement_motion", names)
        self.assertIn("grc9v3_column_coarse_motion_diagnostic", names)
        self.assertIn("no_motion_negative_control", names)
        self.assertTrue(any(spec.negative_control for spec in specs))
        self.assertTrue(any(spec.evidence_scale == "column_coarse_diagnostic" for spec in specs))

    def test_structural_examples_write_replayable_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            session = run_motion_structural_examples(
                output_root=Path(tmp),
                session_id="STEST",
            )

            session_root = Path(tmp) / "sessions" / "STEST"
            self.assertEqual(session_root, session.session_root)
            self.assertTrue((session_root / "session_manifest.json").exists())
            self.assertTrue((session_root / "run_report.json").exists())
            self.assertTrue((session_root / "README.md").exists())
            self.assertTrue((session_root / "rerun.sh").exists())

            report = json.loads((session_root / "run_report.json").read_text(encoding="utf-8"))

        self.assertEqual(MOTION_EXAMPLES_SESSION_VERSION, report["session_version"])
        self.assertEqual(10, report["example_count"])
        by_name = {example["example_name"]: example for example in report["examples"]}
        self.assertEqual(
            ["drifted"],
            by_name["coherence_transfer_control"]["observer_relationships"]["coherence"],
        )
        self.assertEqual(
            ["drifted"],
            by_name["representative_drift_control"]["observer_relationships"]["representative"],
        )
        self.assertEqual(
            ["walked"],
            by_name["identity_walking_control"]["observer_relationships"]["identity"],
        )
        self.assertEqual(
            ["split"],
            by_name["identity_split_control"]["observer_relationships"]["identity"],
        )
        self.assertEqual(
            ["split"],
            by_name["identity_split_control"]["observer_relationships"]["topological"],
        )
        self.assertEqual(
            ["merged"],
            by_name["identity_merge_control"]["observer_relationships"]["identity"],
        )
        self.assertEqual(
            ["merged"],
            by_name["identity_merge_control"]["observer_relationships"]["topological"],
        )
        self.assertEqual(
            ["collapsed"],
            by_name["identity_collapse_control"]["observer_relationships"]["identity"],
        )
        self.assertEqual(
            ["collapsed"],
            by_name["identity_collapse_control"]["observer_relationships"]["topological"],
        )
        self.assertEqual(
            ["drifted"],
            by_name["grc9_port_frontier_motion"]["observer_relationships"]["boundary"],
        )
        self.assertGreater(
            by_name["grc9v3_hybrid_refinement_motion"]["observer_record_counts"]["topological"],
            0,
        )
        self.assertEqual(
            "column_coarse_diagnostic",
            by_name["grc9v3_column_coarse_motion_diagnostic"]["evidence_scale"],
        )
        self.assertEqual(
            ["drifted"],
            by_name["grc9v3_column_coarse_motion_diagnostic"]["observer_relationships"]["boundary"],
        )
        self.assertEqual(
            [],
            by_name["no_motion_negative_control"]["observer_relationships"]["coherence"],
        )
        self.assertEqual(
            ["stationary"],
            by_name["no_motion_negative_control"]["observer_relationships"]["representative"],
        )
        self.assertEqual(
            ["stationary"],
            by_name["no_motion_negative_control"]["observer_relationships"]["identity"],
        )
        self.assertEqual(
            [],
            by_name["no_motion_negative_control"]["observer_relationships"]["boundary"],
        )
        self.assertEqual(
            [],
            by_name["no_motion_negative_control"]["observer_relationships"]["topological"],
        )

    def test_structural_examples_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_motion_structural_examples(output_root=root, session_id="STEST")
            first = (root / "sessions" / "STEST" / "run_report.json").read_text(encoding="utf-8")
            run_motion_structural_examples(output_root=root, session_id="STEST")
            second = (root / "sessions" / "STEST" / "run_report.json").read_text(encoding="utf-8")

        self.assertEqual(first, second)

    def test_can_run_single_example(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            session = run_motion_structural_examples(
                output_root=Path(tmp),
                session_id="STEST",
                example_names=("identity_walking_control",),
            )

        self.assertEqual(1, len(session.runs))
        self.assertEqual("identity_walking_control", session.runs[0].spec.example_name)


if __name__ == "__main__":
    unittest.main()
