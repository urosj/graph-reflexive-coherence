from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_io import read_json  # noqa: E402
from classify_claims_and_extensions import (  # noqa: E402
    IMPLEMENTATION_STATUSES,
    REQUIRED_OBJECT_IDS,
    assumption_matrix,
    claim_classification,
    envelope_payload,
    equivalence_classification,
    ids_in,
    protected_manifest_v8,
    source_id_map,
    validate_accepted_chain,
    validate_policy,
    validate_prerequisite,
)
from route_contradictions_and_theory_reopening import (  # noqa: E402
    contradiction_entries,
    extension_decisions,
    theory_reopening_decision,
)


class GRV8ClassificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = read_json(ROOT / "configs/grv8_classification_policy.json")
        cls.sources = validate_policy(cls.policy)
        cls.proof_ids = {
            row["proof_note_id"]
            for row in envelope_payload("proof_note_registry")["records"]
        }
        cls.assumptions = assumption_matrix(
            cls.policy, cls.sources["claim_source"]["records"]
        )
        cls.claims = claim_classification(
            cls.policy, cls.sources["claim_source"]["records"], cls.proof_ids
        )
        cls.equivalence = equivalence_classification(cls.policy, cls.claims["rows"])

    def test_prerequisite_and_complete_accepted_chain_are_valid(self) -> None:
        receipt, anchor = validate_prerequisite()
        self.assertEqual(receipt["receipt_payload_sha256"], anchor["receipt_payload_sha256"])
        self.assertEqual([f"GRV{index}" for index in range(8)], [row["gate_id"] for row in validate_accepted_chain()])

    def test_every_assumption_and_claim_is_classified_once(self) -> None:
        source_assumptions = self.sources["assumption_source"]["records"]
        source_claims = self.sources["claim_source"]["records"]
        self.assertEqual(len(source_assumptions), len(self.assumptions["rows"]))
        self.assertEqual(len(source_claims), len(self.claims["rows"]))
        self.assertTrue(self.claims["all_source_claim_ids_classified"])

    def test_id_parser_does_not_extract_suffixes_from_other_ids(self) -> None:
        self.assertEqual([], ids_in("A-FAST-SLOW", "T"))
        self.assertEqual(["T-A01", "T-A02"], ids_in("`T-A01`, `T-A02`, `D-A01`", "T"))

    def test_failed_or_unidentifiable_assumptions_do_not_support_positive_claims(self) -> None:
        for row in self.claims["rows"]:
            if any(status in {"failed", "not_identifiable"} for status in row["assumption_statuses"].values()):
                self.assertNotEqual("bounded_supported_distinction", row["disposition"])

    def test_required_objects_and_all_six_statuses_are_present(self) -> None:
        rows = self.equivalence["rows"]
        self.assertEqual(REQUIRED_OBJECT_IDS, {row["object_id"] for row in rows})
        self.assertEqual(IMPLEMENTATION_STATUSES, {row["implementation_status"] for row in rows})
        for row in rows:
            self.assertTrue(row["maximum_supported_claim"])
            self.assertTrue(row["blocked_claims"])
            self.assertTrue(row["source_ids"])
            self.assertEqual(
                "bounded_B1_GR_unchanged_GRC9V3_evidence_envelope",
                row["classification_scope"],
            )

    def test_source_ids_bind_the_controlling_files_and_digests(self) -> None:
        mapping = source_id_map()
        self.assertEqual(set(mapping), set(self.claims["source_id_map"]))
        self.assertEqual(set(mapping), set(self.equivalence["source_id_map"]))
        for record in mapping.values():
            self.assertEqual(64, len(record["sha256"]))
            self.assertTrue(record["path"].startswith("core/"))

    def test_native_readback_and_closeout_are_not_manufactured(self) -> None:
        summary = self.equivalence["summary"]
        self.assertFalse(summary["native_readback_supported"])
        self.assertFalse(summary["native_writeback_supported"])
        self.assertFalse(summary["closed_read_write_loop_supported"])
        self.assertFalse(summary["geometry_mobility_extension_opened"])
        self.assertFalse(summary["retained_carrier_extension_opened"])
        self.assertFalse(summary["oriented_current_extension_selected"])

    def test_extension_and_theory_routes_preserve_the_boundary(self) -> None:
        decisions = {row["decision_id"]: row for row in extension_decisions(self.policy)}
        self.assertEqual("remain_explicitly_diagnostic", decisions["EXT-K"]["route"])
        self.assertTrue(decisions["EXT-GEOMETRY-MOBILITY"]["route"].startswith("not_opened"))
        self.assertTrue(decisions["EXT-RETAINED-CARRIER"]["route"].startswith("not_opened"))
        self.assertTrue(decisions["EXT-ORIENTED-CURRENT"]["route"].startswith("conditionally_selectable"))
        self.assertEqual("no_theory_reopening_required", theory_reopening_decision(self.policy)["route"])
        self.assertTrue(all(not row["theory_contradicted"] for row in contradiction_entries()))

    def test_protected_manifest_is_an_unchanged_successor(self) -> None:
        manifest = protected_manifest_v8()
        self.assertTrue(manifest["payload"]["unchanged_successor"])
        self.assertEqual(
            "b1_grv8_protected_paths_v8", manifest["payload"]["manifest_id"]
        )

    def test_grv8_schema_exposes_the_exact_status_enums(self) -> None:
        schema = json.loads((ROOT / "schemas/grv8_classification.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(IMPLEMENTATION_STATUSES, set(schema["$defs"]["implementationStatus"]["enum"]))


if __name__ == "__main__":
    unittest.main()
