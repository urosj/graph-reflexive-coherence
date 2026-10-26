"""Receipt/checkpoint corruption fails without replaying a native event."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984h_aci_closeout as m


class CheckpointTests(unittest.TestCase):
    def test_actual_checkpoint_and_mutations(self):
        original=m.c.read('event')['execution']
        with patch.object(m.c.p.native,'GRC9V4ACIOperation',side_effect=AssertionError('native replay forbidden')):
            self.assertEqual(m.checkpoint(original)['receipts'],4)
            for field in ('state','receipt','reference_current'):
                with self.subTest(field=field):
                    bad=deepcopy(original)
                    if field=='state':bad['checkpoint']['state']['scientific_digest']='grcv4-state-sha256:'+'0'*64
                    elif field=='receipt':bad['checkpoint']['receipts'][0]['commit_id']='grc-commit-sha256:'+'0'*64
                    else:bad['checkpoint']['reference_currents'][0]['roles']['reset']['target'][0]+=1
                    with self.assertRaises(ValueError):m.checkpoint(bad)


if __name__=='__main__':unittest.main()
