from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate_receipts import finalize_receipt, prerequisite_is_authorized, validate_acceptance_anchor, validate_receipt  # noqa: E402


class GateReceiptTest(unittest.TestCase):
    def receipt(self):
        return {"gate_id":"GRV0","input_execution_revision":"a"*40,"substrate_base_revision":"b"*40,"input_experiment_tree_sha256":"c"*64,"prerequisite_result_receipt_digests":[],"prerequisite_acceptance_anchors":[],"output_artifact_digests":{"outputs/example.json":"d"*64},"status":"awaiting_scientific_review","blocked_gates":["GRV1"],"claim_ceiling":"GRV-C1-candidate"}

    def test_receipt_is_non_self_referential(self) -> None:
        receipt = finalize_receipt(self.receipt())
        validate_receipt(receipt)
        bad = self.receipt()
        bad["output_artifact_digests"]["outputs/gates/grv0_result_receipt.json"] = "e" * 64
        with self.assertRaises(ValueError):
            finalize_receipt(bad)

    def test_only_human_anchor_authorizes_progression(self) -> None:
        anchor = {"gate_id":"GRV0","result_revision":"a"*40,"receipt_payload_sha256":"b"*64,"accepted_by":"experiment-owner","acceptance_role":"experiment_owner","review_method":"artifact_and_baseline_review","acceptance_timestamp":"2026-08-21T00:00:00Z","acceptance_status":"accepted","acceptance_signature_or_ref":"commit:example"}
        validate_acceptance_anchor(anchor)
        self.assertTrue(prerequisite_is_authorized(anchor))
        anchor["accepted_by"] = "run_all.py"
        with self.assertRaises(ValueError):
            validate_acceptance_anchor(anchor)


if __name__ == "__main__":
    unittest.main()
