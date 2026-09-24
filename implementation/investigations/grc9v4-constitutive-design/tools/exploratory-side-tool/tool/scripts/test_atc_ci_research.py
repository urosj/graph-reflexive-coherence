#!/usr/bin/env python3
"""Scoped CI admission/authority pressure, without rerunning numerical campaigns."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SIDE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer import atc, atc_pc as pc, atc_ci as ci
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.paths import repository_root


class CIResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=repository_root()
        cls.old=pc.load_current_forensic_context(cls.root,SIDE)
        cls.context=ci.load_current_forensic_context(cls.root,SIDE)
        cls.ledger=cls.context.documents_by_record[ci.RECORD_ID].data
        cls.admission=ci.pinned_admission(SIDE)

    def test_historical_pc_and_aos_graph_preserved(self):
        for key,row in self.old.nodes.items():self.assertEqual(row,self.context.nodes[key])
        edges={e['edge_id']:e for e in self.context.propagation_edges}
        for edge in self.old.propagation_edges:self.assertEqual(edge,edges[edge['edge_id']])
        self.assertEqual(self.old.graph['annotation_edges'],self.context.graph['annotation_edges'])
        for debt in self.ledger['debts']:
            did=debt['origin_debt_id']
            self.assertEqual(pc.debt_lifecycle(self.old,did)['rows'],pc.debt_lifecycle(self.context,did)['rows'])
            old=atc.debt_lifecycle(self.old,did)['rows']
            new=atc.debt_lifecycle(self.context,did)['rows']
            for a,b in zip(old,new,strict=True):
                self.assertEqual({k:v for k,v in a.items() if k!='edge_refs'},
                                 {k:v for k,v in b.items() if k!='edge_refs'})

    def test_ci_complete_ancestry_and_ceiling(self):
        for cid in ci.CLAIMS:
            trace=ci.reconstruction_path(self.context,cid);row=trace['rows'][0]
            self.assertEqual(len(trace['trace_digest']),64)
            self.assertTrue(row['edge_refs']);self.assertTrue(row['source_ref'])
            value=row['payload']
            self.assertEqual(value['profile_scope'],['A_CI'])
            self.assertEqual(value['claim_class'],'conditional')
            self.assertEqual(value['support_disposition'],'accepted_bounded_A_CI_research')
            self.assertFalse(value['native_authority']);self.assertFalse(value['domain_widening_inferred'])
        nodes=ci.reconstruction_path(self.context,ci.CLAIMS[-1])['rows'][0]['payload']['nodes']
        self.assertEqual({n['identifier'] for n in nodes},set(ci.CLAIMS))

    def test_all_debts_scoped_and_db05_db24_local(self):
        counts=dict(closed=0,partial=0,not_activated=0)
        for debt in self.ledger['debts']:
            row=ci.debt_lifecycle(self.context,debt['origin_debt_id'])['rows'][0]
            self.assertEqual(row['payload'],debt);self.assertTrue(row['source_ref']);self.assertTrue(row['edge_refs'])
            self.assertFalse(debt['global_discharged'])
            counts[debt['A_CI_research_status']]+=1
        self.assertEqual(counts,dict(closed=14,partial=6,not_activated=8))
        row=ci.debt_lifecycle(self.context,'ATC7-DB-24')['rows'][0]
        self.assertIn('scoped_source_admission',{e['relation'] for e in row['edge_refs']})
        self.assertEqual(ci.debt_lifecycle(self.context,'ATC7-DB-05')['rows'][0]['payload']['A_CI_research_status'],'closed')
        self.assertEqual(pc.debt_lifecycle(self.context,'ATC7-DB-05')['rows'][0]['payload']['A_PC_research_status'],'not_activated')

    def test_old_loader_proposals_controls_other_families_not_promoted(self):
        for cid in ci.CLAIMS:
            with self.assertRaises(KeyError):pc.reconstruction_path(self.old,cid)
        self.assertEqual(ci.reconstruction_path(self.context,'ATC7-CL-04')['rows'][0]['classification'],'proposed_origin_not_accepted')
        row=ci.reconstruction_path(self.context,'ATC-PC-CARRIER-02')['rows'][0]
        self.assertEqual(row['classification'],'superseded_selection_explicit_loss_control')
        self.assertFalse(row['payload']['selected_policy'])
        for cid in ('ATC-CI-PC-DOMAIN-01','ATC-CI-UNKNOWN','ATC-C-RG2B-01'):
            with self.assertRaises(KeyError):ci.reconstruction_path(self.context,cid)
        with self.assertRaises(KeyError):ci.debt_lifecycle(self.context,'ATC7-DB-99')

    def test_rehashed_ledger_mutations_reject(self):
        mutations=[lambda v:v.update(native_authority=True),lambda v:v.update(ATC2_closed=True),
            lambda v:v.update(ATC3_closed=True),lambda v:v['claims'][0].update(claim_class='normative'),
            lambda v:v['claims'][0].update(profile_scope=['A_PC']),
            lambda v:v['claims'][0].update(predecessor_claim_ids=[ci.CLAIMS[-1]]),
            lambda v:v['claims'][-1].update(predecessor_claim_ids=[]),
            lambda v:v['claims'][0]['source_ref'].update(json_pointer='/cases/1'),
            lambda v:v['debts'][0].update(global_discharged=True),
            lambda v:v['debts'][0].update(closure_requirement='weakened'),
            lambda v:v['debts'][0].update(successor_claim_ids=[]),
            lambda v:v['debts'][23].update(admission_evidence=False),
            lambda v:v['debts'][4].update(A_CI_research_status='not_activated'),
            lambda v:v['claims'].pop()]
        for i,mutate in enumerate(mutations):
            value=copy.deepcopy(self.ledger);mutate(value)
            value['record_digest']=record_digest(value,'record_digest')
            with self.subTest(mutation=i),self.assertRaises(SourceAdmissionError):ci._validate_ledger(self.root,value)

    def test_rehashed_manifest_cannot_bypass_pin(self):
        value=copy.deepcopy(self.admission);value['scope']='all families'
        value['record_digest']=record_digest(value,'record_digest')
        with patch.object(ci,'load_json_object',return_value=value):
            with self.assertRaises(SourceAdmissionError):ci.pinned_admission(SIDE)

    def test_source_discovery_and_rebuild_fail_closed(self):
        original=ci._inventory(self.root)
        with patch.object(ci,'_inventory',return_value=original+[ci.EVIDENCE+'/unreviewed.json']):
            self.assertEqual(ci.observe_sources(self.root,self.admission)['state'],'new_unprocessed_source_available')
            with self.assertRaises(SourceAdmissionError):ci._build_context(self.root,SIDE,self.admission)
        for key,path in (('changed',ci.LEDGER),('missing',ci.EVIDENCE+'/missing.json')):
            value=copy.deepcopy(self.admission);value['evidence_files'][path]='0'*64
            self.assertEqual(ci.observe_sources(self.root,value)['state'],
                'admitted_source_missing' if key=='missing' else 'admitted_source_identity_changed')

    def test_transitive_execution_drift_and_historical_pin_reject(self):
        original=ci.file_sha256
        def changed(path):return '0'*64 if path.name=='atc_ci_state.py' else original(path)
        with patch.object(ci,'file_sha256',side_effect=changed):
            self.assertEqual(ci.observe_sources(self.root,self.admission)['state'],'admitted_source_identity_changed')
            with self.assertRaises(SourceAdmissionError):ci._build_context(self.root,SIDE,self.admission)
        value=copy.deepcopy(self.admission);value['historical_graph_digest']='0'*64
        with self.assertRaises(SourceAdmissionError):ci._build_context(self.root,SIDE,value)

    def test_portable_paths(self):
        for value in ('/outside.json','../outside.json'):
            with self.assertRaises(SourceAdmissionError):ci._path(self.root,value)

    def test_cli_dispatch(self):
        for args in [('audit',),('discover',),('claim',ci.CLAIMS[-1]),('debt','ATC7-DB-24')]:
            result=subprocess.run([sys.executable,str(SIDE/'tool/scripts/run.py'),'atc-ci-query',*args],
                cwd=SIDE,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            value=json.loads(result.stdout)
            if args[0]=='audit':self.assertEqual(value['accepted_research_claims'],4);self.assertFalse(value['native_authority'])
        bad=subprocess.run([sys.executable,str(SIDE/'tool/scripts/run.py'),'atc-ci-query','audit','ignored'],
            capture_output=True,text=True)
        self.assertEqual(bad.returncode,2)


if __name__=='__main__':unittest.main(verbosity=2)
