from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes.motion_examples import run_motion_structural_examples
from pygrc.landscapes.motion_landscape_bridge import (
    MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION,
    run_motion_landscape_bridge_session,
)
from pygrc.visualization.motion import render_motion_visual_session


class MotionLandscapeBridgeTest(unittest.TestCase):
    def test_bridge_runs_motion_observers_over_selected_landscape_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            examples = run_motion_structural_examples(
                output_root=root / "motion_examples",
                session_id="S9601",
                example_names=("identity_walking_control",),
            )
            source_run = examples.runs[0]
            manifest_path = root / "landscape" / "session_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "session_id": "LS9601",
                        "iteration": "test_landscape_inference",
                        "selected_seeds": [
                            {
                                "key": "identity_walking_landscape_probe",
                                "artifact_root": str(source_run.run_dir),
                                "runtime_family": "grc9v3",
                                "source_seed_name": "Identity Walking Landscape Probe",
                                "source_seed_path": "configs/landscapes/seed/test.seed.yaml",
                                "checkpoint_count_loaded": 2,
                                "primitive_counts_by_type": {"basin": 2, "valley": 1},
                                "relationship_counts": {"emerged": 1},
                            }
                        ],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            session = run_motion_landscape_bridge_session(
                landscape_manifest_path=manifest_path,
                output_root=root / "motion",
                session_id="S9602",
                observers=("identity", "topological"),
                render_visuals=False,
            )

            self.assertEqual(MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION, session.to_mapping()["session_version"])
            self.assertEqual(1, len(session.runs))
            run = session.runs[0]
            self.assertEqual("identity_walking_landscape_probe", run.key)
            self.assertIn("walked", run.observer_relationships["identity"])
            self.assertTrue((source_run.run_dir / "motion_reports" / "identity_report.json").exists())
            report = json.loads(
                (session.session_root / "run_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(1, report["selected_landscape_example_count"])
            summary = json.loads(
                (session.session_root / "landscape_motion_summary.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(1, summary["selected_landscape_example_count"])
            self.assertEqual(
                {"walked": 1},
                summary["runs"][0]["motion_relationship_counts"]["identity"],
            )
            self.assertTrue((session.session_root / "landscape_motion_summary.md").exists())

            visual_session = render_motion_visual_session(session_root=session.session_root)
            self.assertEqual(1, len(visual_session.records))
            self.assertEqual(
                "identity_walking_landscape_probe",
                visual_session.records[0].example_name,
            )


if __name__ == "__main__":
    unittest.main()
