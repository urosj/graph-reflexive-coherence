from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from interventions import apply_clone_intervention  # noqa: E402


class InterventionTest(unittest.TestCase):
    def test_intervention_clones_and_obeys_rebuild_order(self) -> None:
        original = {"nodes": {"0": {"coherence": 1.0}}, "trace": []}
        def first(state): state["trace"].append("first")
        def second(state): state["trace"].append("second")
        result = apply_clone_intervention(original, [(('nodes', '0', 'coherence'), 2.0)], rebuild_steps=[("first", first), ("second", second)])
        self.assertEqual(1.0, original["nodes"]["0"]["coherence"])
        self.assertEqual(2.0, result.state["nodes"]["0"]["coherence"])
        self.assertEqual(["first", "second"], result.state["trace"])
        self.assertEqual(("first", "second"), result.rebuild_order)


if __name__ == "__main__":
    unittest.main()
