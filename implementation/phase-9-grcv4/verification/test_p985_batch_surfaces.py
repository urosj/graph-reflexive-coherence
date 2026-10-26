"""Family coverage, historical acceptance and read-only parallel API pressure."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import p985_batch as h
import p985_status as status


class FamilySurfaceTests(unittest.TestCase):
    def test_retained_family_coverage(self):
        for family in h.FAMILIES:
            with self.subTest(family=family):
                m,r=status.checked_batch(h.ROOT,family)
                self.assertEqual(r['small']['observations']['tests'],6)
                self.assertEqual(r['large']['observations']['occupied_ports'],814)
                self.assertFalse(r['large']['user_accepted'])

    def test_resealed_family_root_archive_and_scope_mutations_fail(self):
        original=Path.read_text
        for family,kind in (('C_CI','role'),('A_CI','root'),('A_PC','archive'),
                            ('A_PC','reset'),('A_CI','methods'),('C_CI','promotion')):
            segment='small' if kind in ('reset','methods') else 'large'
            name=h.path(family,segment);v=json.loads((h.ROOT/name).read_text())
            if kind=='role':v['observations']['selected_points'][2].pop('reset')
            elif kind=='root':v['observations']['selected_points'][2]['reset'].pop('H_digest')
            elif kind=='archive':v['observations']['archive_count']=0
            elif kind=='reset':v['observations']['cases']['continuation_reset']['full_authority_restored']=False
            elif kind=='methods':v['observations']['cases']['domain_and_history']['methods'].pop()
            else:v['user_accepted']=True
            raw=json.dumps(h.seal(v))
            def read(path,*a,**kw):return raw if path==h.ROOT/name else original(path,*a,**kw)
            with self.subTest(family=family,kind=kind),patch.object(Path,'read_text',read),self.assertRaises((ValueError,KeyError)):
                status.checked_batch(h.ROOT,family)

    def test_source_drift_and_missing_execution_roster_fail(self):
        original=Path.read_bytes
        def read(path):return b'changed' if path==h.ROOT/'src/pygrc/models/grc_v4_lifecycle.py' else original(path)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'source drift'):status.checked_batch(h.ROOT,'A_CI')
        def snapshot_read(path):return b'changed' if path==h.ROOT/status.POLICY_SNAPSHOT else original(path)
        with patch.object(Path,'read_bytes',snapshot_read),self.assertRaisesRegex(ValueError,'maintenance source'):status.checked_batch(h.ROOT,'A_CI')
        family='C_CI';name=h.path(family,'inputs');v=json.loads((h.ROOT/name).read_text())
        v['source_bindings'].pop(h.SELF);raw=json.dumps(h.seal(v));original_text=Path.read_text
        def text(path,*a,**kw):return raw if path==h.ROOT/name else original_text(path,*a,**kw)
        with patch.object(Path,'read_text',text),self.assertRaisesRegex(ValueError,'source roster'):status.checked_batch(h.ROOT,family)

    def test_parallel_api_and_original_cos_source(self):
        sys.path.insert(0,str(h.ROOT/h.SIDE/'tool/src'))
        from grcv4_explorer.tranche8 import tranche8_status,tranche8_source
        with patch.object(h,'large',side_effect=AssertionError('no native execution')):
            with ThreadPoolExecutor(max_workers=4) as pool:
                results=list(pool.map(lambda f:tranche8_status(h.ROOT,family=f,checkpoint='8.5'),('C_OS',*h.FAMILIES)))
        self.assertEqual([r['user_accepted'] for r in results],[True,True,True,True])
        for v in results:
            self.assertTrue(v['first_group_closed']);self.assertFalse(v['aggregate_closed']);self.assertFalse(v['native_trajectories_rerun'])
        raw,ref=tranche8_source(h.ROOT,status.LIFECYCLE,family='C_OS',checkpoint='8.5')
        self.assertEqual(ref['revision'],status.COS_REVISION)
        self.assertEqual(h.sha(raw),ref['sha256'])
        self.assertNotEqual(raw,(h.ROOT/status.LIFECYCLE).read_bytes())
        for family in ('A_CI','A_PC'):
            raw,ref=tranche8_source(h.ROOT,status.POLICY_SNAPSHOT,family=family,checkpoint='8.5')
            self.assertEqual(h.sha(raw),status.POLICY_DIGEST)
        for family in h.FAMILIES:
            raw,ref=tranche8_source(h.ROOT,h.path(family,'large'),family=family,checkpoint='8.5')
            self.assertEqual(h.sha(raw),ref['sha256']);self.assertEqual(json.loads(raw)['family'],family)
        with self.assertRaises(ValueError):tranche8_status(h.ROOT,family='C_PC',checkpoint='8.5')
        with self.assertRaises(KeyError):tranche8_source(h.ROOT,'../outside',family='A_CI',checkpoint='8.5')

    def test_acceptance_does_not_follow_execution_flags_or_changed_review(self):
        name=status.ACCEPTANCE;v=json.loads((h.ROOT/name).read_text());v['family']='A_CI'
        raw=json.dumps(h.seal(v));original=Path.read_text
        def read(path,*a,**kw):return raw if path==h.ROOT/name else original(path,*a,**kw)
        with patch.object(Path,'read_text',read),self.assertRaisesRegex(ValueError,'acceptance'):
            status._view(h.ROOT,'C_OS')


if __name__=='__main__':unittest.main()
