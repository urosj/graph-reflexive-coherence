"""Coverage, authority scope, portable sources and first-group surface pressure."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import p984i_first_group as h


class FirstGroupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshots=[json.loads(h.git_bytes(h.ROOT,p).decode().split(' = ',1)[1].rstrip(';\n')) for p in h.SNAPSHOTS]

    def test_retained_handoff_and_bounds(self):
        value=h.check()
        self.assertEqual(value['counts'],dict(families=4,source_steps=5,events=36,target_steps=144,final_reads=8))
        self.assertTrue(value['first_group_i_accepted']);self.assertTrue(value['first_group_8_4_closed']);self.assertFalse(value['all_ten_8_4_closed'])
        self.assertEqual(len(value['atomic_failure_vectors']),5)
        self.assertEqual(len(value['authority_traces']),6)

    def test_omitted_or_promoted_family_cannot_close(self):
        for mutation in ('omit','duplicate','unaccepted','cells','steps','reset'):
            a,b=deepcopy(self.snapshots)
            if mutation=='omit':a['coverage']['families']=[r for r in a['coverage']['families'] if r['family']!='C_OS']
            elif mutation=='duplicate':a['coverage']['families'].append(h.one(a['coverage']['families'],'C_OS'))
            elif mutation=='unaccepted':b['runtime']['user_accepted']=False
            elif mutation=='cells':h.one(a['coverage']['chart_covariance']['family_results'],'A_PC')['accepted_cells']=23
            elif mutation=='steps':b['runtime']['covariance']['target_steps']=15
            else:b['runtime']['continuation']['baseline_complete']=False
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):h.project(a,b)

    def test_source_drift_and_missing_history_reject(self):
        ref=h.reference(h.ROOT,h.AUTHORITY)
        with patch.object(Path,'read_bytes',return_value=b'changed'),self.assertRaisesRegex(ValueError,'source drift'):
            h.authenticate(h.ROOT,ref)
        with patch.object(h,'git_bytes',side_effect=ValueError('missing history')),self.assertRaisesRegex(ValueError,'missing history'):
            h.build()
        for name in ('/tmp/no','../no','a/../no'):
            with self.assertRaises(ValueError):h.safe(h.ROOT,name)

    def test_archive_only_source_is_retrievable(self):
        from scripts.evidence_storage import entries
        row=next(r for r in entries(h.ROOT) if r['path'].endswith('P9-8.4c-ACIResults.json'))
        target=h.ROOT/row['path'];original=Path.exists
        with patch.object(Path,'exists',lambda p:False if p==target else original(p)):
            raw=h.authenticate(h.ROOT,dict(path=row['path'],sha256=row['sha256'],revision=None))
        self.assertEqual(h.sha(raw),row['sha256'])

    def test_api_and_sources_do_not_run_numerics(self):
        sys.path.insert(0,str(h.ROOT/h.SIDE/'tool/src'))
        from grcv4_explorer.tranche8 import tranche8_status,tranche8_source
        import p984h_apc_campaign as numerical
        with patch.object(numerical,'state',side_effect=AssertionError('native construction forbidden')):
            value=tranche8_status(h.ROOT,family='first_group',checkpoint='8.4i')
            raw,ref=tranche8_source(h.ROOT,h.RESULT,family='first_group',checkpoint='8.4i')
        self.assertEqual(value['handoff'],json.loads(raw));self.assertEqual(h.sha(raw),ref['sha256'])
        with self.assertRaises(ValueError):tranche8_status(h.ROOT,family='A_PC',checkpoint='8.4i')
        with self.assertRaises(KeyError):tranche8_source(h.ROOT,'specs/not-indexed.md',family='first_group',checkpoint='8.4i')


if __name__=='__main__':unittest.main()
