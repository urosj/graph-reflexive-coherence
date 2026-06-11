from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes.io import landscape_seed_to_data, load_landscape_seed
from pygrc.landscapes.motion_seed_examples import (
    MOTION_DENSE_FISSION_SESSION_VERSION,
    MOTION_LONG_COMPOSITES_SESSION_VERSION,
    MOTION_SEED_EXAMPLES_SESSION_VERSION,
    default_motion_authored_seed_specs,
    default_motion_dense_fission_seed_specs,
    default_motion_long_composite_seed_specs,
    run_motion_dense_fission_examples,
    run_motion_long_composite_examples,
    run_motion_authored_seed_examples,
)
from pygrc.landscapes.motion_interpretation import (
    run_motion_dense_window_calibration_session,
    run_motion_identity_fission_promotion_session,
)


class MotionSeedExamplesTest(unittest.TestCase):
    def test_default_authored_seeds_cover_basic_and_composite_targets(self) -> None:
        specs = default_motion_authored_seed_specs()
        names = {spec.seed_name for spec in specs}

        self.assertIn("motion_seed_coherence_transfer", names)
        self.assertIn("motion_seed_representative_drift", names)
        self.assertIn("motion_seed_identity_walking", names)
        self.assertIn("motion_seed_grc9_port_frontier", names)
        self.assertIn("motion_seed_grc9v3_hybrid_refinement", names)
        self.assertIn("motion_composite_walk_frontier_refinement", names)
        self.assertIn("motion_composite_split_merge_collapse", names)
        self.assertTrue(any(spec.source_status.startswith("composite") for spec in specs))

    def test_authored_seed_payloads_do_not_claim_runtime_motion(self) -> None:
        forbidden = {
            "motion_id",
            "motion_record",
            "motion_records",
            "relationship",
            "observed_motion",
            "runtime_motion",
            "checkpoint_ids",
            "step_rows",
            "event_rows",
            "graph_checkpoint",
            "transferred_mass",
        }
        for spec in default_motion_authored_seed_specs():
            payload = landscape_seed_to_data(spec.seed)
            self.assertEqual([], _forbidden_paths(payload, forbidden))
            extension = payload["extensions"]["motion_seed"]
            self.assertIn("no_runtime_motion_claim", extension["non_claims"])
            self.assertIn("target_motion_modes", extension)
            self.assertIn("projected_example_names", extension)

    def test_authored_seed_session_runs_observers_and_visuals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            session = run_motion_authored_seed_examples(
            output_root=Path(tmp),
            session_id="S9501",
                seed_names=(
                    "motion_seed_identity_walking",
                    "motion_composite_split_merge_collapse",
                ),
                render_visuals=True,
            )
            session_root = Path(tmp) / "sessions" / "S9501"
            report = json.loads((session_root / "run_report.json").read_text(encoding="utf-8"))

            self.assertEqual(MOTION_SEED_EXAMPLES_SESSION_VERSION, report["session_version"])
            self.assertEqual(2, report["source_seed_count"])
            self.assertEqual(2, report["projected_runtime_example_count"])
            self.assertTrue((session_root / "source_seeds" / "motion_seed_identity_walking.seed.json").exists())
            self.assertTrue(
                (
                    Path("configs/landscapes/seed/motion")
                    / "motion_seed_identity_walking.seed.yaml"
                ).exists()
            )
            self.assertTrue((session_root / "visualizations" / "visual_manifest.json").exists())
            visual_manifest = json.loads(
                (session_root / "visualizations" / "visual_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(2, visual_manifest["visual_count"])

            loaded = load_landscape_seed(
                session_root / "source_seeds" / "motion_seed_identity_walking.seed.json"
            )
            self.assertEqual("motion_seed_identity_walking", loaded.meta.name)

            by_seed = {run["seed_name"]: run for run in report["runs"]}
            self.assertEqual(
                "configs/landscapes/seed/motion/motion_seed_identity_walking.seed.yaml",
                by_seed["motion_seed_identity_walking"]["library_seed_path"],
            )
            self.assertEqual(
                ["walked"],
                by_seed["motion_seed_identity_walking"]["observer_relationships"]["identity"],
            )
            composite = by_seed["motion_composite_split_merge_collapse"]
            self.assertIn("split", composite["observer_relationships"]["identity"])
            self.assertIn("merged", composite["observer_relationships"]["identity"])
            self.assertIn("collapsed", composite["observer_relationships"]["topological"])
            self.assertIn("ambiguous", composite["observer_relationships"]["identity"])
            self.assertIsNotNone(report["visual_root"])

    def test_authored_seed_session_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_motion_authored_seed_examples(
                output_root=root,
                session_id="S9502",
                seed_names=("motion_seed_coherence_transfer",),
                render_visuals=False,
            )
            first = (root / "sessions" / "S9502" / "run_report.json").read_text(encoding="utf-8")
            run_motion_authored_seed_examples(
                output_root=root,
                session_id="S9502",
                seed_names=("motion_seed_coherence_transfer",),
                render_visuals=False,
            )
            second = (root / "sessions" / "S9502" / "run_report.json").read_text(encoding="utf-8")

        self.assertEqual(first, second)

    def test_long_composite_session_has_twenty_plus_step_examples(self) -> None:
        specs = default_motion_long_composite_seed_specs()
        self.assertEqual(4, len(specs))
        names = {spec.seed_name for spec in specs}
        self.assertIn("motion_long_relay_walk_frontier", names)
        self.assertIn("motion_long_split_merge_collapse_cascade", names)
        self.assertIn("motion_long_failed_relay_broken_continuity", names)
        self.assertIn("motion_long_no_motion_negative_control", names)
        self.assertTrue(
            all(
                len(spec.projected_examples[0].checkpoints) >= 20
                for spec in specs
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            session = run_motion_long_composite_examples(
                output_root=Path(tmp),
                session_id="S9503",
                render_visuals=False,
            )
            session_root = Path(tmp) / "sessions" / "S9503"
            report = json.loads((session_root / "run_report.json").read_text(encoding="utf-8"))

        self.assertEqual(MOTION_LONG_COMPOSITES_SESSION_VERSION, report["session_version"])
        self.assertEqual(4, report["source_seed_count"])
        self.assertEqual(4, report["projected_runtime_example_count"])
        by_seed = {run["seed_name"]: run for run in report["runs"]}
        relay = by_seed["motion_long_relay_walk_frontier"]
        self.assertGreaterEqual(
            relay["observer_relationships"]["identity"].count("walked"),
            4,
        )
        self.assertIn("drifted", relay["observer_relationships"]["boundary"])
        cascade = by_seed["motion_long_split_merge_collapse_cascade"]
        self.assertIn("split", cascade["observer_relationships"]["topological"])
        self.assertIn("merged", cascade["observer_relationships"]["topological"])
        self.assertIn("collapsed", cascade["observer_relationships"]["topological"])
        self.assertIn("ambiguous", cascade["observer_relationships"]["identity"])
        failed = by_seed["motion_long_failed_relay_broken_continuity"]
        self.assertNotIn("walked", failed["observer_relationships"]["identity"])
        self.assertIn("dissolved", failed["observer_relationships"]["identity"])
        self.assertIn("emerged", failed["observer_relationships"]["identity"])
        stable = by_seed["motion_long_no_motion_negative_control"]
        self.assertEqual(
            ["stationary"],
            sorted(set(stable["observer_relationships"]["identity"])),
        )
        self.assertEqual(
            ["stationary"],
            sorted(set(stable["observer_relationships"]["representative"])),
        )
        self.assertEqual(
            ["stationary"],
            sorted(set(stable["observer_relationships"]["boundary"])),
        )
        self.assertEqual([], stable["observer_relationships"]["topological"])

    def test_dense_fission_seed_promotes_identity_fission(self) -> None:
        specs = default_motion_dense_fission_seed_specs()
        self.assertEqual(1, len(specs))
        self.assertEqual("motion_dense_confirmed_fission", specs[0].seed_name)
        self.assertGreaterEqual(len(specs[0].projected_examples[0].checkpoints), 500)

        with tempfile.TemporaryDirectory() as tmp:
            session = run_motion_dense_fission_examples(
                output_root=Path(tmp),
                session_id="S9504",
                render_visuals=False,
            )
            session_root = Path(tmp) / "sessions" / "S9504"
            report = json.loads((session_root / "run_report.json").read_text(encoding="utf-8"))

            self.assertEqual(MOTION_DENSE_FISSION_SESSION_VERSION, report["session_version"])
            self.assertEqual(1, report["source_seed_count"])
            self.assertTrue((session_root / "landscape_motion_summary.json").exists())
            run = report["runs"][0]
            self.assertEqual("motion_dense_confirmed_fission", run["seed_name"])
            self.assertGreaterEqual(
                run["observer_relationships"]["identity"].count("split"),
                500,
            )

            dense = run_motion_dense_window_calibration_session(session_root=session_root)
            promotion = run_motion_identity_fission_promotion_session(session_root=session_root)

        dense_payload = dense.to_mapping()
        self.assertEqual(1, dense_payload["dense_window_count"])
        promoted = promotion.to_mapping()
        self.assertGreaterEqual(promoted["promoted_identity_fission_count"], 500)
        self.assertEqual(
            ["motion_dense_confirmed_fission"],
            promoted["aggregate"]["promoted_keys"],
        )


def _forbidden_paths(value: object, forbidden: set[str], prefix: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}"
            if str(key) in forbidden:
                paths.append(path)
            paths.extend(_forbidden_paths(item, forbidden, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.extend(_forbidden_paths(item, forbidden, f"{prefix}[{index}]"))
    return paths


if __name__ == "__main__":
    unittest.main()
