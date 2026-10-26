"""Focused fresh C_CI identity/role pressure without numerical reruns."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
import p984h_cci as run


class EventBinding(unittest.TestCase):
    def setUp(self):
        self.enterContext(run.exact_backend(run.ExactBackend.FLINT))
        self.enterContext(run.numerical_policy(run.NumericalPolicy.CERTIFIED_ARB_256))
        self.enterContext(run.matrix_operation())

    def test_actual_postbeat_and_distinct_reset(self):
        initial,_,_=run.seed();saved=run.accepted_source()['result']
        post=run.poststate(initial,saved);event=run.fresh(post)
        self.assertTrue(event['trigger']['eligible'])
        self.assertEqual(post.inputs.reset,initial.inputs.reset)
        self.assertNotEqual(post.inputs.current,post.inputs.reset)
        self.assertNotEqual(event['event_id'],event['prepared_event_id'])
        self.assertEqual(event['request']['source_state_digest'],post.scientific_digest)
        changed=replace(post,inputs=replace(post.inputs,current=post.inputs.reset))
        self.assertNotEqual(run.fresh(changed)['event_id'],event['event_id'])

    def test_source_poststate_corruption_rejected(self):
        initial,_,_=run.seed();saved=run.accepted_source()['result']
        for field in ('after_C','after_time','after_step_index'):
            bad=deepcopy(saved)
            if field=='after_C':bad[field][0]+=1e-6
            else:bad[field]+=1
            with self.assertRaises(ValueError):run.poststate(initial,bad)

    def test_historical_result_is_not_rebound_to_current_runtime(self):
        old=run.accepted_source()
        self.assertEqual(old['native_events'],0)
        with patch.object(run.hashlib,'sha256') as sha:
            sha.return_value.hexdigest.return_value='forged'
            with self.assertRaisesRegex(ValueError,'prerequisite seal'):run.accepted_source()


if __name__=='__main__':unittest.main()
