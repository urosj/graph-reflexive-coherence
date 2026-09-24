#!/usr/bin/env python3
"""Scoped CIP admission/authority pressure; no numerical campaign reruns."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SIDE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer import atc, atc_pc as pc, atc_ci as ci, atc_cip as cip
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.paths import repository_root


class CIPResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=repository_root()
        cls.old=ci.load_current_forensic_context(cls.root,SIDE)
        cls.context=cip.load_current_forensic_context(cls.root,SIDE)
        cls.ledger=cls.context.documents_by_record[cip.RECORD_ID].data
        cls.admission=cip.pinned_admission(SIDE)

    def test_historical_ci_pc_and_aos_graph_preserved(self):
        for key,row in self.old.nodes.items():self.assertEqual(row,self.context.nodes[key])
        edges={e['edge_id']:e for e in self.context.propagation_edges}
        for edge in self.old.propagation_edges:self.assertEqual(edge,edges[edge['edge_id']])
        self.assertEqual(self.old.graph['annotation_edges'],self.context.graph['annotation_edges'])
        for debt in self.ledger['debts']:
            did=debt['origin_debt_id']
            self.assertEqual(pc.debt_lifecycle(self.old,did)['rows'],pc.debt_lifecycle(self.context,did)['rows'])
            self.assertEqual(ci.debt_lifecycle(self.old,did)['rows'],ci.debt_lifecycle(self.context,did)['rows'])
            old=atc.debt_lifecycle(self.old,did)['rows']
            new=atc.debt_lifecycle(self.context,did)['rows']
            for a,b in zip(old,new,strict=True):
                self.assertEqual({k:v for k,v in a.items() if k!='edge_refs'},
                                 {k:v for k,v in b.items() if k!='edge_refs'})

    def test_ci_complete_ancestry_and_ceiling(self):
        for cid in cip.CLAIMS:
            trace=cip.reconstruction_path(self.context,cid);row=trace['rows'][0]
            self.assertEqual(len(trace['trace_digest']),64)
            self.assertTrue(row['edge_refs']);self.assertTrue(row['source_ref'])
            value=row['payload']
            self.assertEqual(value['profile_scope'],['A_CI_PC'])
            self.assertEqual(value['claim_class'],'conditional')
            self.assertEqual(value['support_disposition'],'accepted_bounded_A_CI_PC_research')
            self.assertFalse(value['native_authority']);self.assertFalse(value['domain_widening_inferred'])
        nodes=cip.reconstruction_path(self.context,cip.CLAIMS[-1])['rows'][0]['payload']['nodes']
        expected=set(cip.CLAIMS)
        for cid in cip.INHERITED:
            trace=ci.reconstruction_path(self.old,cid)
            expected.update(n['identifier'] for n in trace['rows'][0]['payload']['nodes'])
        self.assertEqual({n['identifier'] for n in nodes},expected)
        self.assertNotIn('ATC-PC-CARRIER-02',expected)
        for n in nodes:
            if n['identifier'] in cip.INHERITED:
                self.assertEqual(n,self.old.nodes[n['node_id']])

    def test_all_debts_scoped_and_db05_db24_local(self):
        counts=dict(closed=0,partial=0,not_activated=0)
        for debt in self.ledger['debts']:
            row=cip.debt_lifecycle(self.context,debt['origin_debt_id'])['rows'][0]
            self.assertEqual(row['payload'],debt);self.assertTrue(row['source_ref']);self.assertTrue(row['edge_refs'])
            self.assertFalse(debt['global_discharged'])
            counts[debt['A_CI_PC_research_status']]+=1
        self.assertEqual(counts,dict(closed=14,partial=6,not_activated=8))
        row=cip.debt_lifecycle(self.context,'ATC7-DB-24')['rows'][0]
        self.assertIn('scoped_source_admission',{e['relation'] for e in row['edge_refs']})
        self.assertEqual(cip.debt_lifecycle(self.context,'ATC7-DB-05')['rows'][0]['payload']['A_CI_PC_research_status'],'closed')
        self.assertEqual(pc.debt_lifecycle(self.context,'ATC7-DB-05')['rows'][0]['payload']['A_PC_research_status'],'not_activated')

    def test_old_loader_proposals_controls_other_families_not_promoted(self):
        for cid in cip.CLAIMS:
            with self.assertRaises(KeyError):ci.reconstruction_path(self.old,cid)
        self.assertEqual(cip.reconstruction_path(self.context,'ATC7-CL-04')['rows'][0]['classification'],'proposed_origin_not_accepted')
        row=cip.reconstruction_path(self.context,'ATC-PC-CARRIER-02')['rows'][0]
        self.assertEqual(row['classification'],'superseded_selection_explicit_loss_control')
        self.assertFalse(row['payload']['selected_policy'])
        for cid in ('ATC-CI-PC-DOMAIN-01','ATC-CI-UNKNOWN','ATC-C-RG2B-01'):
            with self.assertRaises(KeyError):cip.reconstruction_path(self.context,cid)
        with self.assertRaises(KeyError):cip.debt_lifecycle(self.context,'ATC7-DB-99')

    def test_rehashed_ledger_mutations_reject(self):
        mutations=[lambda v:v.update(native_authority=True),lambda v:v.update(ATC2_closed=True),
            lambda v:v.update(ATC3_closed=True),lambda v:v['claims'][0].update(claim_class='normative'),
            lambda v:v['claims'][0].update(profile_scope=['A_PC']),
            lambda v:v['claims'][0].update(predecessor_claim_ids=[cip.CLAIMS[-1]]),
            lambda v:v['claims'][-1].update(predecessor_claim_ids=[]),
            lambda v:v['claims'][0]['source_ref'].update(json_pointer='/cases/1'),
            lambda v:v['debts'][0].update(global_discharged=True),
            lambda v:v['debts'][0].update(closure_requirement='weakened'),
            lambda v:v['debts'][0].update(successor_claim_ids=[]),
            lambda v:v['debts'][23].update(admission_evidence=False),
            lambda v:v['debts'][4].update(A_CI_PC_research_status='not_activated'),
            lambda v:v['claims'].pop(),
            lambda v:v['review_disposition'].update(independent_retained_record_comparison='PASS'),
            lambda v:v['claims'][0]['debt_ids'].remove('ATC7-DB-04'),
            lambda v:v['claims'][1].update(predecessor_claim_ids=[cip.CLAIMS[0],'ATC-PC-CARRIER-02']),
            lambda v:v['claims'][0]['debt_ids'].append('ATC7-DB-04'),
            lambda v:v['debts'][3]['successor_claim_ids'].append(cip.CLAIMS[0])]
        for i,mutate in enumerate(mutations):
            value=copy.deepcopy(self.ledger);mutate(value)
            value['record_digest']=record_digest(value,'record_digest')
            with self.subTest(mutation=i),self.assertRaises(SourceAdmissionError):cip._validate_ledger(self.root,value)

    def test_rehashed_manifest_cannot_bypass_pin(self):
        value=copy.deepcopy(self.admission);value['scope']='all families'
        value['record_digest']=record_digest(value,'record_digest')
        with patch.object(cip,'load_json_object',return_value=value):
            with self.assertRaises(SourceAdmissionError):cip.pinned_admission(SIDE)

    def test_source_discovery_and_rebuild_fail_closed(self):
        original=cip._inventory(self.root)
        with patch.object(cip,'_inventory',return_value=original+[cip.EVIDENCE+'/unreviewed.json']):
            self.assertEqual(cip.observe_sources(self.root,self.admission)['state'],'new_unprocessed_source_available')
            with self.assertRaises(SourceAdmissionError):cip._build_context(self.root,SIDE,self.admission)
        for key,path in (('changed',cip.LEDGER),('missing',cip.EVIDENCE+'/missing.json')):
            value=copy.deepcopy(self.admission);value['evidence_files'][path]='0'*64
            self.assertEqual(cip.observe_sources(self.root,value)['state'],
                'admitted_source_missing' if key=='missing' else 'admitted_source_identity_changed')

    def test_transitive_execution_drift_and_historical_pin_reject(self):
        original=cip.file_sha256
        def changed(path):return '0'*64 if path.name=='atc_cip_reference.py' else original(path)
        with patch.object(cip,'file_sha256',side_effect=changed):
            self.assertEqual(cip.observe_sources(self.root,self.admission)['state'],'admitted_source_identity_changed')
            with self.assertRaises(SourceAdmissionError):cip._build_context(self.root,SIDE,self.admission)
        value=copy.deepcopy(self.admission);value['historical_graph_digest']='0'*64
        with self.assertRaises(SourceAdmissionError):cip._build_context(self.root,SIDE,value)

    def test_portable_paths(self):
        for value in ('/outside.json','../outside.json'):
            with self.assertRaises(SourceAdmissionError):cip._path(self.root,value)

    def test_cli_dispatch(self):
        for args in [('audit',),('discover',),('claim',cip.CLAIMS[-1]),('debt','ATC7-DB-24')]:
            result=subprocess.run([sys.executable,str(SIDE/'tool/scripts/run.py'),'atc-cip-query',*args],
                cwd=SIDE,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            value=json.loads(result.stdout)
            if args[0]=='audit':self.assertEqual(value['accepted_research_claims'],3);self.assertFalse(value['native_authority'])
        bad=subprocess.run([sys.executable,str(SIDE/'tool/scripts/run.py'),'atc-cip-query','audit','ignored'],
            capture_output=True,text=True)
        self.assertEqual(bad.returncode,2)


    def test_reviewed_bytes_and_additive_db04_are_preserved(self):
        expected = {
            'atc-cip/ATCCIP0Certificate.json': '952a83c506882b97d26b8c146941a977b30ef0e159367d56782b5c032b6ff79e',
            'atc-cip/ATCCIP1Certificate.json': 'c3dc84d287ebd4f3c8317f644df1f7b92a87a3fc344037aefba35e1f0acea710',
            'atc-cip-successor/ATCCIP2Certificate.json': '6e7cf27c9303cc9c5b875a9c14aac621eeb2a8277278c422bdd636254bca3680',
        }
        for name,digest in expected.items():
            value=json.loads((self.root/atc.INV/'evidence'/name).read_text())
            self.assertEqual(value['record_digest'],digest)
            self.assertEqual(record_digest(value,'record_digest'),digest)
            self.assertFalse(value['graph_admitted'])
        value=json.loads((self.root/atc.INV/'evidence/atc-cip/ATCCIP0Certificate.json').read_text())
        self.assertNotIn('ATC7-DB-04',value['proposed_claims'][0]['debt_refs'])
        for cid in cip.CLAIMS:
            self.assertIn(cid,cip.debt_lifecycle(self.context,'ATC7-DB-04')['rows'][0]['payload']['successor_claim_ids'])
        self.assertEqual(self.ledger['review_disposition']['independent_retained_record_comparison'],
                         'not_supplied_not_claimed')

    def test_historical_authority_and_new_directory_discovery(self):
        self.assertEqual(self.old.graph_digest,
                         '8a72fed0586996146ef31b86affcaf5b2d34f08ba12ca28adc4338e13b35c1ed')
        self.assertEqual(pc.load_current_forensic_context(self.root,SIDE).graph_digest,
                         '34bf112649b30d38493a4cbc5f51cf323649ab24e679a2e481cf29c1e7afacba')
        original=cip._inventory(self.root)
        for directory in (cip.EVIDENCE,cip.SUCCESSOR,cip.REVIEW,cip.ADMISSION_EVIDENCE):
            with self.subTest(directory=directory),patch.object(cip,'_inventory',return_value=original+[directory+'/unreviewed.json']):
                self.assertEqual(cip.observe_sources(self.root,self.admission)['state'],'new_unprocessed_source_available')


if __name__=='__main__':unittest.main(verbosity=2)
