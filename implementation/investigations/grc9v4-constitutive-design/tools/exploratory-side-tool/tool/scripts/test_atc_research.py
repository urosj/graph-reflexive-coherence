#!/usr/bin/env python3
"""Focused ATC source/lineage pressure; no numerical research campaign."""
import copy
import json
import subprocess
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SIDE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIDE / "tool/src"))
from grcv4_explorer import atc
from grcv4_explorer.canonical import load_json_object, record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.paths import repository_root
from grcv4_explorer.forensic import reconstruction_path as historical_query


class ATCResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = repository_root()
        cls.old = atc.load_pre_atc_context(cls.root, SIDE)
        cls.context = atc.load_current_forensic_context(cls.root, SIDE)
        cls.ledger = cls.context.documents_by_record[atc.RECORD_ID].data

    def test_cli_dispatch_and_historical_argument_rejection(self):
        runner = SIDE / "tool/scripts/run.py"
        for operation in ("audit", "discover"):
            result = subprocess.run([sys.executable, str(runner), "atc-query", operation],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            if operation == "audit":
                self.assertEqual(value["accepted_research_claims"], 36)
                self.assertFalse(value["native_authority"])
            else:
                self.assertEqual(value["state"], "current_bundle_exact")
        invalid = subprocess.run([sys.executable, str(runner), "doctor", "unexpected"],
                                 capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)

    def test_navigation_compatibility_is_exact_and_path_scoped(self):
        legacy = dict(path=atc._REVIEW_README,
                      sha256="036d7783a0b8ef7d24629967e5fa4bd3b86f9cba86a047411b19140c3d3662ad")
        self.assertTrue(atc._source_binding_matches(self.root, legacy))
        self.assertFalse(atc._source_binding_matches(self.root, {**legacy, "sha256": "0" * 64}))
        self.assertFalse(atc._source_binding_matches(self.root, {**legacy, "path": atc.LEDGER}))
        original = (self.root / atc._REVIEW_README).read_bytes()
        with patch.object(Path, "read_bytes", return_value=original + b"changed verdict"):
            self.assertFalse(atc._source_binding_matches(self.root, legacy))

    def test_exact_historical_graph_is_preserved(self):
        for key, node in self.old.nodes.items():
            self.assertEqual(node, self.context.nodes[key])
        edges = {e['edge_id']: e for e in self.context.propagation_edges}
        for edge in self.old.propagation_edges:
            self.assertEqual(edge, edges[edge['edge_id']])
        self.assertEqual(self.old.graph['annotation_edges'], self.context.graph['annotation_edges'])
        with self.assertRaises(KeyError):
            historical_query(self.old, 'ATC-LSF-G7-CL-06')

    def test_all_claims_have_complete_ancestry_and_exact_traces(self):
        claims = {c['claim_id']: c for c in self.ledger['claims']}
        for cid in claims:
            with self.subTest(claim=cid):
                trace = atc.reconstruction_path(self.context, cid)
                self.assertEqual(trace['trace_digest'], record_digest(trace, 'trace_digest'))
                self.assertEqual(trace['rows'][0]['classification'], 'accepted_bounded_research_reconstruction')
                payload = trace['rows'][0]['payload']
                reached = {cid}
                while True:
                    predecessors = {p for c in reached for p in claims[c]['predecessor_claim_ids']}
                    if predecessors <= reached:
                        break
                    reached |= predecessors
                self.assertEqual(reached, {n['identifier'] for n in payload['nodes']})
                self.assertTrue(payload['verification_obligations_excluded'])
                self.assertFalse(payload['native_authority'])
                self.assertTrue(trace['rows'][0]['edge_refs'])
                self.assertEqual(trace['rows'][0]['source_ref']['path'], atc.LEDGER)
                for n in payload['nodes']:
                    self.assertIn(n['attributes']['claim_class'], ('conditional', 'negative'))
                    self.assertEqual(n['attributes']['profile_scope'], ['A_OS'])

    def test_all_origin_proposals_remain_proposals(self):
        for c in self.ledger['origin_claims']:
            trace = atc.reconstruction_path(self.context, c['id'])
            self.assertEqual(trace['rows'][0]['classification'], 'proposed_origin_not_accepted')
            self.assertNotIn('current_claim:' + c['id'], self.context.nodes)
        with self.assertRaises(KeyError):
            atc.reconstruction_path(self.context, 'ATC-LSF-CI-UNACCEPTED')

    def test_all_debt_traces_keep_scope_and_forward_work(self):
        self.assertEqual(self.ledger['classifications'], dict(closed=13, partial=6, not_activated=9))
        for d in self.ledger['debts']:
            trace = atc.debt_lifecycle(self.context, d['debt_id'])
            self.assertEqual(trace['trace_digest'], record_digest(trace, 'trace_digest'))
            self.assertEqual(trace['rows'][0]['classification'], d['transformation'])
            self.assertFalse(trace['rows'][0]['payload']['global_discharged'])
            self.assertEqual(len(trace['rows']), 2 if d['verification_obligation'] else 1)
            if d['verification_obligation']:
                self.assertEqual(trace['rows'][1]['classification'], 'forward_verification_routing')
        for did in ('ATC7-DB-11', 'ATC7-DB-22'):
            self.assertEqual(atc.debt_lifecycle(self.context, did)['rows'][0]['payload']['A_OS_research_status'], 'not_activated')

    def test_no_native_or_aggregate_authority(self):
        for key in ('ATC2_closed', 'ATC3_closed', 'native_authority'):
            self.assertFalse(self.ledger[key])

    def test_new_missing_changed_source_fail_closed(self):
        inventory = atc._inventory(self.root)
        for changed in (inventory + [atc.EVIDENCE + '/UNPROCESSED.json'], inventory[1:]):
            with self.subTest(inventory=len(changed)), patch.object(atc, '_inventory', return_value=changed):
                with self.assertRaises(SourceAdmissionError):
                    atc.load_current_forensic_context(self.root, SIDE)
        original = atc.file_sha256
        def changed_hash(path):
            return '0' * 64 if path == self.root / atc.LEDGER else original(path)
        with patch.object(atc, 'file_sha256', side_effect=changed_hash):
            with self.assertRaises(SourceAdmissionError):
                atc.load_current_forensic_context(self.root, SIDE)

    def test_recomputed_manifest_digest_does_not_bypass_pin(self):
        source = load_json_object(SIDE / 'records' / atc.ADMISSION)
        source['graph_digest'] = '0' * 64
        source['record_digest'] = record_digest(source, 'record_digest')
        with patch.object(atc, 'load_json_object', return_value=source):
            with self.assertRaises(SourceAdmissionError):
                atc.load_current_forensic_context(self.root, SIDE)

    def test_recomputed_ledger_cannot_widen_or_lose_lineage(self):
        def mutation(field, value):
            result = copy.deepcopy(self.ledger)
            result[field] = value
            return result
        variants = [mutation('ATC2_closed', True), mutation('native_authority', True),
                    mutation('claims', self.ledger['claims'][1:]), mutation('debts', self.ledger['debts'][1:])]
        for field, value in [('claim_class', 'normative'), ('profile_scope', ['A_OS', 'A_CI']),
                             ('predecessor_claim_ids', ['ATC-LSF-G7-CL-06']), ('debt_ids', ['ATC7-DB-11'])]:
            record = copy.deepcopy(self.ledger)
            record['claims'][0][field] = value
            variants.append(record)
        for index, data in enumerate(variants):
            with self.subTest(mutation=index):
                data['record_digest'] = record_digest(data, 'record_digest')
                with self.assertRaises(SourceAdmissionError):
                    atc._validate_ledger(self.root, data)

    def test_path_escape_rejected(self):
        for path in ('../outside.json', '/outside.json'):
            with self.subTest(path=path), self.assertRaises(SourceAdmissionError):
                atc._path(self.root, path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
