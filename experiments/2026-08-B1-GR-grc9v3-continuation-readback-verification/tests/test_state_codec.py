from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from state_codec import canonical_clone, decode_json_state, encode_json_state, exact_deep_clone  # noqa: E402


class StateCodecTest(unittest.TestCase):
    def test_json_round_trip_is_canonical(self) -> None:
        state = {"nodes": {"1": {"coherence": 2.0}, "0": {"coherence": 1.0}}, "edge_order": [0]}
        self.assertEqual(canonical_clone(state), decode_json_state(encode_json_state(state)))

    def test_deep_clone_does_not_alias(self) -> None:
        state = {"nested": {"value": 1}}
        clone = exact_deep_clone(state)
        clone["nested"]["value"] = 2
        self.assertEqual(1, state["nested"]["value"])


if __name__ == "__main__":
    unittest.main()
