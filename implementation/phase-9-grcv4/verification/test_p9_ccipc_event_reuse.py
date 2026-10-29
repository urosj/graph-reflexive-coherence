"""Exact initial-owner reuse never bypasses publication or operand checks."""
from dataclasses import replace
import unittest
from unittest.mock import patch

import p9_ccipc_event_reuse as p


class InitialOwnerReuseTests(unittest.TestCase):
    def test_retained_full_event_parity_keeps_fresh_replay(self):
        record=p.checked();before,after=record['measurements']
        self.assertEqual(before['execution_digest'],after['execution_digest'])
        self.assertEqual((before['native_roots'],after['native_roots']),(14,12))
        self.assertEqual(after['observations']['fresh_replays'],1)
        self.assertFalse(after['observations']['root_results_reused'])

    def test_changed_pointer_wrong_operand_and_third_use_fail(self):
        native=p.n.native;original=native.GRC9V4CCIPCOperation
        with p.n.compute_worker():
            seed=p.n.r.state(p.n.storage.read(p.n.r.INPUTS)['expected_source'])
            with p.initial_owner(seed):
                owner=native.GRC9V4CCIPCOperation(seed)
                with self.assertRaisesRegex(ValueError,'operand identity'):
                    native.GRC9V4CCIPCOperation(replace(seed))
                with patch.object(owner,'_published',object()):
                    with self.assertRaisesRegex(ValueError,'publication changed'):
                        native.GRC9V4CCIPCOperation(seed)
                with self.assertRaisesRegex(ValueError,'publication changed'):
                    native.GRC9V4CCIPCOperation(seed)
        self.assertIs(native.GRC9V4CCIPCOperation,original)


if __name__=='__main__':unittest.main()
