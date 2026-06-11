"""Smoke tests for the public quickstart path."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
QUICKSTART_PATH = REPO_ROOT / "examples" / "quickstart" / "spark_a_cell.py"


def _load_quickstart_module() -> object:
    spec = importlib.util.spec_from_file_location(
        "pygrc_quickstart_spark_a_cell",
        QUICKSTART_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load quickstart module from {QUICKSTART_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QuickstartSmokeTest(unittest.TestCase):
    def test_spark_a_cell_emits_telemetry_and_visual_artifacts(self) -> None:
        module = _load_quickstart_module()

        previous_cwd = Path.cwd()
        os.chdir(REPO_ROOT)
        try:
            result = module.run_quickstart()
        finally:
            os.chdir(previous_cwd)

        self.assertEqual(
            {
                "choice_detected": 2,
                "collapse": 1,
                "hybrid_mechanical_expansion": 1,
                "hybrid_spark_candidate": 1,
                "hybrid_spark_completed": 1,
            },
            result["event_counts"],
        )

        for path in result["open_these"].values():
            artifact_path = REPO_ROOT / path
            self.assertTrue(artifact_path.exists(), path)
            self.assertGreater(artifact_path.stat().st_size, 0, path)

        for path in result["telemetry"].values():
            artifact_path = REPO_ROOT / path
            self.assertTrue(artifact_path.exists(), path)
            self.assertGreater(artifact_path.stat().st_size, 0, path)

        summary_path = REPO_ROOT / result["telemetry"]["summary"]
        checkpoint_index = summary_path.parent / "graph_checkpoints" / "index.json"
        self.assertTrue(checkpoint_index.exists())
        self.assertGreater(checkpoint_index.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
