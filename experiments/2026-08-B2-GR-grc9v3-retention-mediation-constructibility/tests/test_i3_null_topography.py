"""Tests for the B2-GR I3 interpretive null-topography companion."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = EXPERIMENT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_i3_null_topography import (  # noqa: E402
    EXPECTED_SCOPES,
    load_artifact,
    render_html,
    validate_topography,
)


class I3NullTopographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact = load_artifact(
            EXPERIMENT_ROOT / "outputs/b2_i3_active_nulls.json"
        )
        cls.summary = validate_topography(cls.artifact)

    def test_scope_split_and_suffix_topology(self) -> None:
        self.assertEqual(self.summary["null_count"], 52)
        self.assertEqual(self.summary["rung_blocker_count"], 32)
        self.assertEqual(self.summary["governance_guard_count"], 20)
        self.assertEqual(self.summary["scope_counts"], EXPECTED_SCOPES)
        self.assertEqual(self.summary["suffix_violation_count"], 0)
        self.assertEqual(
            self.summary["lowest_rung_counts"],
            {"GRR1": 9, "GRR3": 11, "GRR4": 6, "GRR5": 6},
        )

    def test_all_sentinel_pairs_are_non_evidence_pass_throughs(self) -> None:
        self.assertEqual(self.summary["sentinel_pair_count"], 52)
        self.assertTrue(self.summary["all_sentinels_non_evidence_pass_through"])

    def test_render_is_deterministic_and_scientifically_bounded(self) -> None:
        first = render_html(self.artifact)
        second = render_html(self.artifact)
        self.assertEqual(first, second)
        self.assertIn(self.artifact["payload_sha256"], first)
        self.assertIn("Interpretive companion only", first)
        self.assertIn("validator pass-through", first)
        self.assertIn("not admissible scientific evidence", first)
        self.assertNotIn("sentinel passes (evidence admissible)", first)


if __name__ == "__main__":
    unittest.main()
