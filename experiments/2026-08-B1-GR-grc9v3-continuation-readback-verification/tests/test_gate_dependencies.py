from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_all import prerequisite_anchor_path  # noqa: E402
from serialize_theory_contract import serialize  # noqa: E402


class GateDependencyTest(unittest.TestCase):
    def test_serial_dependency_map_is_complete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            serialize(output)
            record = json.loads((output / "gate_dependency_map.json").read_text(encoding="utf-8"))
        payload = record["payload"]
        gates = [f"GRV{index}" for index in range(9)]
        self.assertEqual(gates, payload["gate_order"])
        self.assertEqual([], payload["dependencies"]["GRV0"])
        for index in range(1, 9):
            self.assertEqual([gates[index - 1]], payload["dependencies"][gates[index]])

    def test_orchestrator_maps_each_gate_to_predecessor_anchor(self) -> None:
        self.assertEqual(
            ROOT / "outputs/gates/grv1_acceptance_anchor.json",
            prerequisite_anchor_path("GRV2"),
        )
        self.assertEqual(
            ROOT / "outputs/gates/grv7_acceptance_anchor.json",
            prerequisite_anchor_path("GRV8"),
        )
        with self.assertRaises(ValueError):
            prerequisite_anchor_path("GRV0")


if __name__ == "__main__":
    unittest.main()
