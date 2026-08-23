from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_io import artifact_envelope, read_json  # noqa: E402
from build_grv8_closeout_candidate import (  # noqa: E402
    accepted_grv8,
    collect_evidence_bundle,
    handoff_payload,
    render_successor,
)


class GRV8CloseoutCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = read_json(ROOT / "configs/grv8_closeout_policy.json")
        cls.receipt, cls.anchor = accepted_grv8()
        cls.bundle_payload = collect_evidence_bundle(cls.policy)
        cls.bundle = artifact_envelope(
            cls.bundle_payload,
            schema_version="b1_grv8_evidence_bundle_manifest_v1",
            generating_command="test",
        )

    def test_accepted_grv8_anchor_binds_the_corrected_candidate(self) -> None:
        self.assertEqual("accepted", self.anchor["acceptance_status"])
        self.assertEqual(
            self.receipt["receipt_payload_sha256"],
            self.anchor["receipt_payload_sha256"],
        )
        self.assertEqual(
            "570f715a54b7235be81725907a71e4a4b461ece7",
            self.anchor["result_revision"],
        )

    def test_bundle_is_non_self_referential_and_covers_all_accepted_gates(self) -> None:
        self.assertEqual(
            [f"GRV{index}" for index in range(9)],
            [row["gate_id"] for row in self.bundle_payload["accepted_gate_results"]],
        )
        artifact_paths = {row["path"] for row in self.bundle_payload["artifacts"]}
        prefix = (
            "experiments/2026-08-B1-GR-grc9v3-continuation-readback-"
            "verification/"
        )
        for excluded in self.policy["bundle_excluded_paths"]:
            self.assertNotIn(prefix + excluded, artifact_paths)
        self.assertFalse(self.bundle_payload["grv_c6_assigned"])

    def test_handoff_is_general_and_orders_grc_before_lgrc(self) -> None:
        payload = handoff_payload(
            self.policy,
            self.bundle,
            "a" * 64,
            self.anchor,
        )
        self.assertEqual(
            [
                "GRC_UNCHANGED_CONSTRUCTIBILITY",
                "GRC_SELECTABLE_EXTENSIONS",
                "GRC_ANALYSIS_AND_IDENTIFIABILITY",
                "LGRC_SPECIFIC_INVESTIGATION",
            ],
            [row["lane_id"] for row in payload["handoff_lanes"]],
        )
        self.assertIn(
            "superseded_as_umbrella",
            payload["legacy_lgrc_handoff_disposition"],
        )
        self.assertFalse(payload["grv_c6_assigned"])

    def test_successor_references_the_preexecution_spec_and_route_boundary(self) -> None:
        successor = render_successor(self.policy, self.bundle, self.anchor)
        self.assertIn("## Preserved Pre-Execution Specification Reference", successor)
        self.assertIn("The first downstream work is GRC-side", successor)
        self.assertIn("GRV_C6_assigned = false", successor)
        self.assertIn(
            "GRC9V3ContinuationReadBackVerificationSpecification.md",
            successor,
        )
        self.assertIn("This successor does not copy or rewrite the predecessor", successor)


if __name__ == "__main__":
    unittest.main()
