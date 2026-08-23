"""Focused tests for the B2-GR Iteration 1 admission package."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = EXPERIMENT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from b2_artifact_io import (  # noqa: E402
    B1_ROOT,
    assert_envelope_digest,
    find_absolute_paths,
    receipt_digest,
    semantic_digest,
)
from build_i1_source_handoff_inventory import (  # noqa: E402
    build_payload,
    graph_source_record,
    source_contract,
    theory_source_record,
)


class I1SourceHandoffInventoryTests(unittest.TestCase):
    def test_source_contract_has_expected_precedence_and_unique_ids(self) -> None:
        contract = source_contract()
        self.assertEqual(len(contract["source_precedence"]), 5)
        rows = [*contract["graph_sources"], *contract["theory_sources"]]
        ids = [row["source_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(rows), 17)

    def test_graph_sources_are_tracked_and_envelopes_are_valid(self) -> None:
        for contract in source_contract()["graph_sources"]:
            record = graph_source_record(contract)
            self.assertTrue(record["exists"])
            self.assertTrue(record["tracked"])
            self.assertEqual(len(record["sha256"]), 64)
            if record["payload_sha256"] is not None:
                artifact = json.loads((B1_ROOT / contract["path"]).read_text(encoding="utf-8"))
                assert_envelope_digest(artifact)

    def test_theory_sources_bind_pinned_revision(self) -> None:
        for contract in source_contract()["theory_sources"]:
            record = theory_source_record(contract)
            self.assertEqual(record["pinned_blob_sha256"], contract["expected_sha256"])
            self.assertEqual(record["consumption_mode"], "pinned_revision_blob")

    def test_payload_preserves_claim_boundary(self) -> None:
        payload = build_payload()
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(payload["passed_check_count"], payload["check_count"])
        self.assertEqual(payload["accepted_starting_boundary"]["maximum_retention_rung"], "GRR2")
        self.assertEqual(payload["admitted_route"]["lane_id"], "GRC_UNCHANGED_CONSTRUCTIBILITY")
        self.assertFalse(payload["admitted_route"]["mechanical_impossibility_established"])
        self.assertFalse(payload["claim_boundary"]["B2_positive_evidence_opened"])
        self.assertFalse(payload["claim_boundary"]["GRR_rung_assigned"])
        self.assertFalse(payload["claim_boundary"]["ready_for_I2"])
        self.assertEqual(find_absolute_paths(payload), [])

    def test_preacceptance_handoff_state_is_resolved_by_closeout_anchor(self) -> None:
        resolution = build_payload()["source_precedence_resolution"]
        self.assertEqual(resolution["embedded_handoff_status"], "candidate_pending_closeout_review")
        self.assertFalse(resolution["embedded_handoff_grv_c6_assigned"])
        self.assertEqual(resolution["authoritative_closeout_status"], "accepted")
        self.assertEqual(resolution["authoritative_closeout_rung"], "GRV-C6")

    def test_semantic_and_receipt_digests_are_order_independent(self) -> None:
        self.assertEqual(semantic_digest({"a": 1, "b": 2}), semantic_digest({"b": 2, "a": 1}))
        receipt = {"gate_id": "B2-I1", "status": "awaiting_scientific_review"}
        with_digest = {**receipt, "receipt_payload_sha256": receipt_digest(receipt)}
        self.assertEqual(receipt_digest(with_digest), with_digest["receipt_payload_sha256"])

    def test_path_audit_distinguishes_json_pointers_from_local_paths(self) -> None:
        self.assertEqual(find_absolute_paths({"pointer": "/payload/summary"}), [])
        self.assertEqual(find_absolute_paths({"path": "/home/example/result.json"}), ["$.path"])


if __name__ == "__main__":
    unittest.main()
