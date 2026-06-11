"""CLI smoke tests for the representative GRCV2 experiment lane."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.cli.grcv2_representative_experiment import main


class GRCV2RepresentativeExperimentCliTest(unittest.TestCase):
    """Validate the CLI entrypoint for representative experiment generation."""

    def test_main_writes_artifacts_into_requested_lane(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exit_code = main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--experiment-path",
                    "grcv2/test-cli",
                    "--family",
                    "balanced_baseline",
                    "--steps",
                    "2",
                    "--rng-seed",
                    "5",
                ]
            )

            root = Path(temp_dir) / "outputs" / "grcv2" / "test-cli"
            cell1_dirs = tuple((root / "balanced_baseline" / "cell-1").iterdir())
            cell4_dirs = tuple((root / "balanced_baseline" / "cell-4").iterdir())
            self.assertEqual(1, len(cell1_dirs))
            self.assertEqual(1, len(cell4_dirs))
            self.assertTrue((cell1_dirs[0] / "telemetry" / "run_summary.json").exists())
            self.assertTrue((cell4_dirs[0] / "telemetry" / "run_summary.json").exists())

        self.assertEqual(0, exit_code)


if __name__ == "__main__":
    unittest.main()
