#!/usr/bin/env python3
"""RGATC admission/closeout pressure only; no numerical campaign execution."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SIDE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIDE / "tool/src"))
from grcv4_explorer import atc, atc_pc, atc_ci, atc_cip, atc_rgatc as rg
from grcv4_explorer.canonical import record_digest, file_sha256
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.forensic import contract_provenance
from grcv4_explorer.paths import repository_root


class RGATCResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = repository_root()
        cls.old = atc_cip.load_current_forensic_context(cls.root, SIDE)
        cls.context = rg.load_current_forensic_context(cls.root, SIDE)
        cls.ledger = cls.context.documents_by_record[rg.RECORD_ID].data
        cls.admission = rg.pinned_admission(SIDE)

    def test_all_four_predecessor_graphs_preserved(self):
        self.assertEqual(self.old.graph_digest,
            "541bf8c23afcca2f5f3b3a61e9c986e9720b270610759b2e0f4c8105673cb89c")
        for key, row in self.old.nodes.items():
            self.assertEqual(row, self.context.nodes[key])
        edges = {e["edge_id"]: e for e in self.context.propagation_edges}
        for e in self.old.propagation_edges:
            self.assertEqual(e, edges[e["edge_id"]])
        self.assertEqual(self.old.graph["annotation_edges"], self.context.graph["annotation_edges"])
        for mod in (atc, atc_pc, atc_ci, atc_cip):
            for n in range(1, 29):
                did = f"ATC7-DB-{n:02d}"
                before = mod.debt_lifecycle(self.old, did)["rows"]
                after = mod.debt_lifecycle(self.context, did)["rows"]
                self.assertEqual([{k:v for k,v in r.items() if k != "edge_refs"} for r in before],
                                 [{k:v for k,v in r.items() if k != "edge_refs"} for r in after])

    def test_seven_claims_and_conditioned_full_ancestry(self):
        for cid in rg.CLAIMS:
            trace = rg.reconstruction_path(self.context, cid)
            row = trace["rows"][0]
            self.assertTrue(row["source_ref"]); self.assertTrue(row["edge_refs"])
            self.assertEqual(trace["trace_digest"], record_digest(trace, "trace_digest"))
            self.assertEqual(row["payload"]["profile_scope"], ["A_RG2b"])
            self.assertEqual(row["payload"]["claim_class"], "conditional")
            self.assertFalse(row["payload"]["native_authority"])
            self.assertFalse(row["payload"]["domain_widening_inferred"])
        value = rg.reconstruction_path(self.context, rg.CLAIMS[-1])["rows"][0]["payload"]
        nodes = {n["identifier"] for n in value["nodes"]}
        self.assertTrue(set(rg.INHERITED) <= nodes)
        # NONCI is a sibling consequence, not an invented prerequisite to execution.
        self.assertNotIn("RGATC-A-NONCI", nodes)
        self.assertEqual([n["identifier"] for n in value["predecessor_contracts_not_sufficient_proof"]],
                         ["D10.2-EC-PARENT-REAL-RG2B"])
        old = contract_provenance(self.old, "D10.2-EC-PARENT-REAL-RG2B")
        new = contract_provenance(self.context, "D10.2-EC-PARENT-REAL-RG2B")
        self.assertEqual(old["rows"][0]["payload"], new["rows"][0]["payload"])

    def test_all_28_debts_reciprocal_and_local(self):
        counts = dict(closed=0, partial=0, not_activated=0)
        for d in self.ledger["debts"]:
            row = rg.debt_lifecycle(self.context, d["origin_debt_id"])["rows"][0]
            self.assertEqual(row["payload"], d)
            self.assertTrue(row["source_ref"]); self.assertTrue(row["edge_refs"])
            self.assertFalse(d["global_discharged"])
            counts[d["A_RG2b_research_status"]] += 1
        self.assertEqual(counts, dict(closed=14, partial=6, not_activated=8))
        row = rg.debt_lifecycle(self.context, "ATC7-DB-24")["rows"][0]
        self.assertIn("scoped_source_admission", {e["relation"] for e in row["edge_refs"]})

    def test_five_realization_closeout_is_not_universal_or_native(self):
        trace = rg.candidate_a_closure(self.context)
        self.assertEqual(trace["trace_digest"], record_digest(trace, "trace_digest"))
        self.assertEqual({r["row_id"] for r in trace["rows"]},
                         {"A_OS", "A_CI", "A_PC", "A_CI_PC", "A_RG2b"})
        self.assertEqual(sum(r["payload"]["accepted_research_claims"] for r in trace["rows"]), 55)
        self.assertEqual(sum(r["payload"]["claim_classes"]["conditional"] for r in trace["rows"]), 54)
        self.assertEqual(sum(r["payload"]["claim_classes"]["negative"] for r in trace["rows"]), 1)
        for r in trace["rows"]:
            p = r["payload"]
            self.assertTrue(r["source_ref"]); self.assertTrue(p["research_program_closed"])
            self.assertEqual(sum(p["debt_statuses"].values()), 28)
            for k in ("native_authority", "ATC2_closed", "ATC3_closed",
                      "universal_realization_support", "origin_debts_globally_closed"):
                self.assertFalse(p[k])
        with self.assertRaises(KeyError):
            rg.candidate_a_closure(self.old)

    def test_no_backward_promotion_or_other_family_authority(self):
        for cid in rg.CLAIMS:
            with self.assertRaises(KeyError):
                atc_cip.reconstruction_path(self.old, cid)
        self.assertEqual(rg.reconstruction_path(self.context, "ATC7-CL-03")["rows"][0]["classification"],
                         "proposed_origin_not_accepted")
        self.assertEqual(rg.reconstruction_path(self.context, "ATC-PC-CARRIER-02")["rows"][0]["classification"],
                         "superseded_selection_explicit_loss_control")
        for cid in ("RGATC-UNKNOWN", "C_RG2b", "ATC-C-RG2B-01"):
            with self.assertRaises(KeyError):
                rg.reconstruction_path(self.context, cid)

    def test_rehashed_ledger_cannot_widen_or_rewire(self):
        mutations = [
            lambda d:d.update(native_authority=True),
            lambda d:d.update(ATC2_closed=True),
            lambda d:d.update(ATC3_closed=True),
            lambda d:d["claims"][0].update(claim_class="normative"),
            lambda d:d["claims"][0].update(statement="C1 completion-independent theorem"),
            lambda d:d["claims"][0].update(profile_scope=["C_RG2b"]),
            lambda d:d["claims"][0].update(predecessor_contract_ids=[]),
            lambda d:d["claims"][2].update(predecessor_claim_ids=[]),
            lambda d:d["claims"][5]["source_ref"].update(json_pointer="/proposed_claims/0"),
            lambda d:d["debts"][0].update(global_discharged=True),
            lambda d:d["debts"][4].update(A_RG2b_research_status="not_activated"),
            lambda d:d["debts"][23].update(admission_evidence=False),
            lambda d:d["debts"][3].update(successor_claim_ids=[]),
            lambda d:d["debts"][0].update(closure_requirement="weaker"),
            lambda d:d["review_disposition"].update(ER_full_local_rerun=True),
            lambda d:d["review_disposition"].update(independent_retained_record_comparison="PASS"),
        ]
        for i, mutate in enumerate(mutations):
            value = copy.deepcopy(self.ledger); mutate(value)
            value["record_digest"] = record_digest(value, "record_digest")
            with self.subTest(mutation=i), self.assertRaises(SourceAdmissionError):
                rg._validate_ledger(self.root, value)

    def test_rehashed_admission_and_predecessor_drift_reject(self):
        value = copy.deepcopy(self.admission); value["scope"] = "all families"
        value["record_digest"] = record_digest(value, "record_digest")
        with patch.object(rg, "load_json_object", return_value=value):
            with self.assertRaises(SourceAdmissionError):
                rg.pinned_admission(SIDE)
        value = copy.deepcopy(self.admission); value["historical_graph_digest"] = "0"*64
        with self.assertRaises(SourceAdmissionError):
            rg._build_context(self.root, SIDE, value)

    def test_inventory_covers_package_code_and_new_sources(self):
        inventory = rg._inventory(self.root)
        for name in ("rgatc_reference.py", "rgatc_oracle.py", "MANIFEST-ER.json",
                     "predecessor/deps/retained/arithmetic/certify_atc_sector_readback_point.py",
                     "predecessor/README.md"):
            self.assertIn(rg.EVIDENCE + "/package/" + name, inventory)
        for directory in (rg.EVIDENCE, rg.ADMISSION_EVIDENCE):
            with patch.object(rg, "_inventory", return_value=inventory + [directory + "/unreviewed.json"]):
                self.assertEqual(rg.observe_sources(self.root, self.admission)["state"],
                                 "new_unprocessed_source_available")
                with self.assertRaises(SourceAdmissionError):
                    rg._build_context(self.root, SIDE, self.admission)
        for name in ("rgatc_reference.py", "rgatc_oracle.py", "RGATC-Review.md",
                     "ATCCandidateAResearchClosure.md"):
            def changed(path):
                return "0"*64 if path.name == name else file_sha256(path)
            with patch.object(rg, "file_sha256", side_effect=changed):
                self.assertEqual(rg.observe_sources(self.root, self.admission)["state"],
                                 "admitted_source_identity_changed")
                with self.assertRaises(SourceAdmissionError):
                    rg._build_context(self.root, SIDE, self.admission)
        value = copy.deepcopy(self.admission)
        value["evidence_files"][rg.EVIDENCE + "/missing.json"] = "0"*64
        self.assertEqual(rg.observe_sources(self.root, value)["state"], "admitted_source_missing")
        with self.assertRaises(SourceAdmissionError):
            rg._build_context(self.root, SIDE, value)

    def test_portable_refs_and_reviewed_certificates_unchanged(self):
        for value in ("/outside.json", "../outside.json"):
            with self.assertRaises(SourceAdmissionError):
                rg._path(self.root, value)
        expected = {
            "RGATC-ER-Certificate.json": "756e135d386a7685eb70332596e48af3d40e51019d6042c9d3f1d6860c69b73c",
            "predecessor/RGATC-TA-Certificate.json": "857e15f3e2a25f76f016e336af11fc84ba7c21401bf16e3a9d5b11e3bb14c162",
        }
        for name, sha in expected.items():
            self.assertEqual(file_sha256(self.root / rg.EVIDENCE / "package" / name), sha)
        value = json.loads((self.root / rg.EVIDENCE / "package/RGATC-ER-Certificate.json").read_text())
        self.assertFalse(value["independent_acceptance"])
        self.assertFalse(value["native_profile_admission"])

    def test_cli_dispatch_from_side_directory(self):
        for args in (("audit",), ("discover",), ("summary",),
                     ("claim", rg.CLAIMS[-1]), ("debt", "ATC7-DB-24")):
            result = subprocess.run([sys.executable, str(SIDE/"tool/scripts/run.py"),
                "atc-rgatc-query", *args], cwd=SIDE, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            if args[0] == "audit":
                self.assertEqual(data["accepted_research_claims"], 7)
                self.assertEqual(len(data["closed_candidate_a_research_programs"]), 5)
        result = subprocess.run([sys.executable, str(SIDE/"tool/scripts/run.py"),
            "atc-rgatc-query", "summary", "ignored"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
