"""Small actual APC checkpoint pressure; no large-graph event reruns."""
from copy import deepcopy
from dataclasses import replace
import json
import unittest
from unittest.mock import patch
import p984h_apc_closeout as m
from tests.models import test_grc_9_v4_apc as fixture


class CheckpointTests(unittest.TestCase):
    def test_checkpoint_receipts_lineage_and_complete_archive(self):
        record=json.loads(fixture.RECORD.read_text())
        with m.c.prep.validation_reuse(),m.c.prep.exact_backend(m.c.prep.ExactBackend.FLINT),m.c.prep.numerical_policy(m.c.prep.NumericalPolicy.CERTIFIED_ARB_256):
            seed=fixture.fixture(record)[0];owner=fixture.GRC9V4APCOperation(seed)
            admissions={r:{'actual':{'current':list(m.c.pc.CandidatePCRead(
                replace(seed.inputs,current=getattr(seed.inputs,r),geometry=m.c.pc.carrier_geometry(seed.inputs,getattr(seed.inputs,r))),
                m.c.backend(seed.inputs)).point.current.values)}} for r in m.c.ROLES}
            result=owner.expand(fixture.GRC9V4ExpansionRequestInput.from_payload(record['request']))
        self.assertTrue(result.committed)
        original=dict(checkpoint=json.loads(owner.checkpoint()),request=record['request'],event_id=record['event_id'],
            carrier_archive=record['carrier_archive'],admissions=[admissions])
        with patch.object(m.c.prep.native,'GRC9V4APCOperation',side_effect=AssertionError('native replay forbidden')):
            self.assertEqual(m.checkpoint(original)['receipts'],4)
            for field in ('state','receipt','reference_current','archive','loss'):
                with self.subTest(field=field):
                    bad=deepcopy(original)
                    if field=='state':bad['checkpoint']['state']['scientific_digest']='grcv4-state-sha256:'+'0'*64
                    elif field=='receipt':bad['checkpoint']['receipts'][0]['commit_id']='grc-commit-sha256:'+'0'*64
                    elif field=='reference_current':bad['checkpoint']['reference_currents'][0]['roles']['reset']['target'][0]+=1
                    elif field=='archive':bad['checkpoint']['carrier_archives']=[]
                    else:bad['checkpoint']['receipts'][0]['identity_payload']['core']['information_losses']=[]
                    with self.assertRaises(ValueError):m.checkpoint(bad)


if __name__=='__main__':unittest.main()
