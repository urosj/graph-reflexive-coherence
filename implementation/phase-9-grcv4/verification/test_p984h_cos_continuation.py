"""Continuation identity/scope pressure; no native trajectory reruns."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984h_cos_continuation as run


class ContinuationTests(unittest.TestCase):
    def test_paths_and_closed_scope(self):
        for role,step in (('foreign',1),('current',0),('reset',11),('current',True)):
            with self.assertRaises(ValueError):run.path(role,step)
        self.assertTrue(run.path('reset','final').endswith('.json.xz'))

    def test_retained_chains_and_resealed_pressure(self):
        if not (run.ROOT/run.path('current',1)).exists():self.skipTest('not executed')
        with run.native.oracle.exact_backend(run.native.oracle.ExactBackend.FLINT), run.native.oracle.numerical_policy(run.native.oracle.NumericalPolicy.CERTIFIED_ARB_256), patch.object(run.native,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')), patch.object(run,'CandidateCOSPass',side_effect=AssertionError('native rerun')):
            m=run.native.oracle.old.read(run.INPUTS)
            self.assertEqual(m,run.manifest())
            for role in run.ROLES:
                before,_,rows=run.checked_role(m,role)
                self.assertIn(len(rows),(1,10))
                if len(rows)==10:self.assertTrue((run.ROOT/run.path(role,'final')).exists())
            before=run.initial('current');value=run.read('current',1)
            for mutate in (
                lambda r:r.update(role='reset'),lambda r:r.update(predecessor_digest='foreign'),
                lambda r:r.update(native_events=1),lambda r:r.update(user_accepted=True),
                lambda r:r.update(elapsed_seconds=601),lambda r:r.update(step=2),
                lambda r:r['observation']['after_C'].__setitem__(0,-1.),
                lambda r:r['observation'].update(after_index=999),
                lambda r:r['next_inputs']['reset']['C'].__setitem__(0,123.),
                lambda r:r['observation'].update(split_admitted=False),
            ):
                bad=deepcopy(value);mutate(bad)
                with self.assertRaises(ValueError):run.validate(run.seal(bad),m,'current',1,before,m['event_record_digest'])
            if (run.ROOT/run.path('current','final')).exists():
                before,prev,_=run.checked_role(m,'current')
                final=run.read('current','final')
                for mutate in (lambda r:r.update(input_digest='stale'),lambda r:r.update(native_steps=1),lambda r:r.update(split_admitted=False)):
                    bad=deepcopy(final);mutate(bad)
                    with self.assertRaises(ValueError):run.validate(run.seal(bad),m,'current','final',before,prev)


if __name__=='__main__':unittest.main()
