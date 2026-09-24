#!/usr/bin/env python3
"""Focused PC source-admission/lineage pressure; no numerical campaigns."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SIDE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIDE / "tool/src"))
from grcv4_explorer import atc, atc_pc as pc
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.paths import repository_root


class PCResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = repository_root()
        cls.old = atc.load_current_forensic_context(cls.root, SIDE)
        cls.context = pc.load_current_forensic_context(cls.root, SIDE)
        cls.ledger = cls.context.documents_by_record[pc.RECORD_ID].data
        cls.admission = pc.pinned_admission(SIDE)

    def test_historical_graph_and_debt_queries_preserved(self):
        for key, row in self.old.nodes.items():
            self.assertEqual(row, self.context.nodes[key])
        edges = {e['edge_id']: e for e in self.context.propagation_edges}
        for row in self.old.propagation_edges:
            self.assertEqual(row, edges[row['edge_id']])
        self.assertEqual(self.old.graph['annotation_edges'], self.context.graph['annotation_edges'])
        for d in self.ledger['debts']:
            did = d['origin_debt_id']
            old_rows = atc.debt_lifecycle(self.old, did)['rows']
            new_rows = atc.debt_lifecycle(self.context, did)['rows']
            self.assertEqual(len(old_rows), len(new_rows))
            for before, after in zip(old_rows, new_rows):
                self.assertEqual({k:v for k,v in before.items() if k != 'edge_refs'},
                                 {k:v for k,v in after.items() if k != 'edge_refs'})
                # The successor adds a parallel-scope lineage edge. Historical
                # meanings and every old edge remain, not an identical neighborhood.
                current_edges = {e['edge_id']: e for e in after['edge_refs']}
                for edge in before['edge_refs']:
                    self.assertEqual(edge, current_edges[edge['edge_id']])

    def test_full_pc_ancestry_and_authority_ceiling(self):
        for cid in pc.CLAIMS:
            trace = pc.reconstruction_path(self.context, cid)
            row = trace['rows'][0]
            self.assertEqual(row['classification'], 'accepted_bounded_research_reconstruction')
            self.assertTrue(row['edge_refs'])
            self.assertTrue(row['source_ref'])
            self.assertEqual(len(trace['trace_digest']), 64)
            value = row['payload']
            self.assertEqual(value['claim_class'], 'conditional')
            self.assertFalse(value['native_authority'])
            self.assertTrue(value['verification_obligations_excluded'])
            self.assertTrue(value['historical_controls_excluded'])
            self.assertEqual(value['profile_scope'], ['A_PC'])
        nodes = pc.reconstruction_path(self.context, pc.CLAIMS[-1])['rows'][0]['payload']['nodes']
        self.assertEqual({n['identifier'] for n in nodes}, set(pc.CLAIMS))

    def test_proposals_controls_and_ci_never_promoted(self):
        self.assertEqual(pc.reconstruction_path(self.context, 'ATC7-CL-18')['rows'][0]['classification'],
                         'proposed_origin_not_accepted')
        control = pc.reconstruction_path(self.context, 'ATC-PC-CARRIER-02')['rows'][0]
        self.assertEqual(control['classification'], 'superseded_selection_explicit_loss_control')
        self.assertFalse(control['payload']['selected_policy'])
        for cid in ('ATC-CI-STEP-01', 'ATC-CI-CHAIN-01', 'ATC-PC-UNKNOWN'):
            with self.subTest(cid=cid), self.assertRaises(KeyError):
                pc.reconstruction_path(self.context, cid)

    def test_all_28_scoped_debts_and_local_admission(self):
        counts = dict(closed=0, partial=0, not_activated=0)
        for d in self.ledger['debts']:
            row = pc.debt_lifecycle(self.context, d['origin_debt_id'])['rows'][0]
            self.assertEqual(row['payload'], d)
            self.assertTrue(row['source_ref'])
            self.assertTrue(row['edge_refs'])
            self.assertFalse(d['global_discharged'])
            counts[d['A_PC_research_status']] += 1
        self.assertEqual(counts, dict(closed=13, partial=6, not_activated=9))
        row = pc.debt_lifecycle(self.context, 'ATC7-DB-24')['rows'][0]
        self.assertTrue(row['payload']['admission_evidence'])
        self.assertIn('scoped_source_admission', {e['relation'] for e in row['edge_refs']})
        with self.assertRaises(KeyError):
            pc.debt_lifecycle(self.context, 'ATC7-DB-99')

    def test_recomputed_ledger_mutations_rejected(self):
        mutations = [
            lambda v:v.update(native_authority=True),
            lambda v:v.update(ATC2_closed=True),
            lambda v:v.update(ATC3_closed=True),
            lambda v:v['claims'][0].update(claim_class='normative'),
            lambda v:v['claims'][0].update(profile_scope=['A_CI']),
            lambda v:v['claims'][0].update(predecessor_claim_ids=['ATC-PC-DOMAIN-04']),
            lambda v:v['claims'][0]['source_ref'].update(json_pointer='/cases/0'),
            lambda v:v['debts'][0].update(global_discharged=True),
            lambda v:v['debts'][0].update(closure_requirement='weakened'),
            lambda v:v['debts'][0].update(successor_claim_ids=[]),
            lambda v:v['debts'][23].update(admission_evidence=False),
            lambda v:v['historical_controls'][0].update(selected_policy=True),
            lambda v:v.update(unaccepted_handles=[]),
            lambda v:v['claims'].pop(),
        ]
        for i, mutate in enumerate(mutations):
            value = copy.deepcopy(self.ledger)
            mutate(value)
            value['record_digest'] = record_digest(value, 'record_digest')
            with self.subTest(mutation=i), self.assertRaises(SourceAdmissionError):
                pc._validate_ledger(self.root, value)

    def test_recomputed_manifest_cannot_bypass_pin(self):
        value = copy.deepcopy(self.admission)
        value['scope'] = 'all families'
        value['record_digest'] = record_digest(value, 'record_digest')
        with patch.object(pc, 'load_json_object', return_value=value):
            with self.assertRaises(SourceAdmissionError):
                pc.pinned_admission(SIDE)

    def test_source_observation_and_fail_closed_rebuild(self):
        original = pc._inventory(self.root)
        with patch.object(pc, '_inventory', return_value=original + [pc.EVIDENCE+'/unreviewed.json']):
            self.assertEqual(pc.observe_sources(self.root, self.admission)['state'], 'new_unprocessed_source_available')
            with self.assertRaises(SourceAdmissionError):
                pc._build_context(self.root, SIDE, self.admission)
        value = copy.deepcopy(self.admission)
        value['evidence_files'][pc.LEDGER] = '0' * 64
        self.assertEqual(pc.observe_sources(self.root, value)['state'], 'admitted_source_identity_changed')
        value['evidence_files'][pc.EVIDENCE+'/missing.json'] = '0' * 64
        self.assertEqual(pc.observe_sources(self.root, value)['state'], 'admitted_source_missing')
        value = copy.deepcopy(self.admission)
        value['support_files'][0]['sha256'] = '0' * 64
        self.assertEqual(pc.observe_sources(self.root, value)['state'], 'admitted_source_identity_changed')

    def test_transitive_execution_source_drift_rejected(self):
        original = pc.file_sha256
        def altered(path):
            if path.name == 'atc_pc_reference.py':
                return '0' * 64
            return original(path)
        with patch.object(pc, 'file_sha256', side_effect=altered):
            self.assertEqual(pc.observe_sources(self.root, self.admission)['state'],
                             'admitted_source_identity_changed')
            with self.assertRaisesRegex(SourceAdmissionError, 'source set'):
                pc._build_context(self.root, SIDE, self.admission)

    def test_paths_are_repository_relative(self):
        for value in ('/outside.json', '../outside.json'):
            with self.assertRaises(SourceAdmissionError):
                pc._path(self.root, value)

    def test_cli_dispatch(self):
        runner = SIDE / 'tool/scripts/run.py'
        for args in [('audit',), ('discover',), ('debt', 'ATC7-DB-24'), ('claim', 'ATC-PC-DOMAIN-04')]:
            result = subprocess.run([sys.executable, str(runner), 'atc-pc-query', *args],
                                    capture_output=True, text=True, cwd=SIDE)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            if args[0] == 'audit':
                self.assertEqual(value['accepted_research_claims'], 5)
                self.assertFalse(value['native_authority'])
        invalid = subprocess.run([sys.executable, str(runner), 'atc-pc-query', 'audit', 'ignored'],
                                 capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
