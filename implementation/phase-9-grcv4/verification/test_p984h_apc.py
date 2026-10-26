"""A_PC operand preparation pressure; no large native campaign."""
from copy import deepcopy
from dataclasses import replace
from contextlib import ExitStack
import unittest
from unittest.mock import patch
import p984h_apc as p


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.stack.enter_context(p.exact_backend(p.ExactBackend.FLINT))
        self.stack.enter_context(p.numerical_policy(p.NumericalPolicy.CERTIFIED_ARB_256))
        self.stack.enter_context(p.matrix_operation())

    @classmethod
    def setUpClass(cls):
        cls.old,cls.oracle=p.accepted();cls.seed,_=p.seed()
        cls.post=p.poststate(cls.seed,cls.old['result'])

    def test_full_persistent_roundtrip_and_fresh_request(self):
        value=p.preflight()
        self.assertTrue(value['full_C_W_Z_roundtrip'] and value['distinct_reset'] and value['fresh_history_binding'])
        self.assertEqual((value['source_nodes'],value['source_edges'],value['target_nodes'],value['target_edges']),(100,400,107,407))

    def test_poststate_keeps_reset_and_rebuilds_carrier_geometry(self):
        post=self.post
        self.assertEqual(post.inputs.reset,self.seed.inputs.reset)
        self.assertNotEqual(post.inputs.current.Z_4,self.seed.inputs.current.Z_4)
        self.assertEqual(post.inputs.geometry,p.carrier_geometry(post.inputs,post.inputs.current))
        self.assertEqual(post.inputs.current.W_A,tuple(self.old['result']['after_W_A']))
        bad=deepcopy(self.old['result']);bad['after_time']+=1
        with self.assertRaises(ValueError):p.poststate(self.seed,bad)

    def test_both_history_channels_are_content_bound(self):
        post=self.post;req=p.request(post)
        authority=post.inputs.reset;z=list(authority.Z_4);z[0]+=2**-20
        changed=replace(post,inputs=replace(post.inputs,reset=replace(authority,Z_4=tuple(z))))
        other=p.request(changed)
        self.assertNotEqual(other['history_policy']['carrier_history_policy_digest'],req['history_policy']['carrier_history_policy_digest'])
        w=list(authority.W_A);w[0]*=.99
        changed=replace(post,inputs=replace(post.inputs,reset=replace(authority,W_A=tuple(w))))
        self.assertNotEqual(p.request(changed)['history_policy']['candidate_history_policy_digest'],req['history_policy']['candidate_history_policy_digest'])

    def test_preparation_never_calls_native_step_or_event(self):
        with patch.object(p.native,'GRC9V4APCOperation',side_effect=AssertionError('event forbidden')), \
             patch('pygrc.models.grc_v4_pc.ProvisionalCandidatePCStep',side_effect=AssertionError('step forbidden')):
            p.preflight()


if __name__=='__main__':unittest.main()
