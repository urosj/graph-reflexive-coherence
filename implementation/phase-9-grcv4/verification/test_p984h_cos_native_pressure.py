"""Retained native event/role pressure without repeating numerical execution."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984h_cos_native as native
import p984h_cos_native_compact as driver


class NativeRecordPressure(unittest.TestCase):
    def test_removed_timeout_is_not_required_or_credited(self):
        import tranche8_evidence as index
        self.assertFalse((native.ROOT/native.path('event')).exists())
        row=index.larger_cos_native_view(index.Sources(index.ROOT))
        self.assertEqual(row['native_events'],0)
        self.assertEqual(row['source_steps'],2)
        self.assertFalse(row['current_tree_execution'])
        self.assertEqual(row['failures'],[])
        self.assertIn('removed at user request',row['timeout_note'])

    def test_event_ledger_and_role_binding(self):
        if not (native.ROOT/native.path('event')).exists(): self.skipTest('event not run')
        if native.read('event')['outcome']!='completed': self.skipTest('no successful event; successor still required')
        with native.oracle.exact_backend(native.oracle.ExactBackend.FLINT), native.oracle.numerical_policy(native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
            event=driver.check('event');cp=event['execution']['checkpoint']
            for mutate in (
                lambda p:p.update(lifecycle_digest='invalid'),
                lambda p:p['receipts'][0].update(commit_id='grcv4-commit-sha256:'+'0'*64),
                lambda p:p['state'].update(scientific_digest=p['initial']['scientific_digest']),
            ):
                bad=deepcopy(cp);mutate(bad)
                with self.assertRaises(ValueError):driver.checkpoint_identity(bad)
            m=native.manifest();original=native.read
            for role in ('current','reset'):
                if not (native.ROOT/native.path(role)).exists():continue
                value=driver.check(role)
                for mutate in (
                    lambda r:r['execution'].update(ten_step_campaign_complete=True),
                    lambda r:r['execution'].update(role='wrong'),
                    lambda r:r['execution']['steps'][0]['corrector']['current'].__setitem__(0,1.),
                ):
                    bad=deepcopy(value);mutate(bad)
                    def read(segment):return native.seal(bad) if segment==role else original(segment)
                    with patch.object(native,'manifest',return_value=m),patch.object(native,'read',side_effect=read), \
                         patch.object(native,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')), \
                         self.assertRaises(ValueError):driver.check(role)


if __name__=='__main__':unittest.main()
