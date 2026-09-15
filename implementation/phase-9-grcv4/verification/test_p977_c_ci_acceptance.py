"""Bounded acceptance projection checks; no numerical reruns."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import verify_p977_c_ci_acceptance as acceptance
import verify_p977_c_ci_crossings as crossing
import verify_p977_c_ci_local as local
import verify_p977_profile_review as review


class AcceptanceTests(unittest.TestCase):
    def test_acceptance_preserves_execution_and_gate_boundaries(self):
        predecessor = {'record_digest': review.read(local.RECORD)['record_digest']}
        original = crossing.check(local_product=predecessor)
        with patch.object(acceptance, 'execution_check', return_value=original):
            accepted = acceptance.check(local_product=predecessor)
        self.assertTrue(accepted['user_accepted'])
        self.assertFalse(original['user_accepted'])
        self.assertEqual(accepted['status'], 'accepted_bounded_reconciliation')
        for flag in ('aggregate_closed', 'G2_accepted', 'G3_accepted', 'all_ordered_pairs_verified'):
            self.assertFalse(accepted[flag])
        self.assertEqual(accepted['new_G2_support'], [])
        self.assertFalse(review.read(crossing.RECORD)['user_accepted'])
        for changed in ('subject', 'acceptance'):
            bad = deepcopy(original)
            if changed == 'subject': bad['record_digest'] = '0' * 64
            with self.subTest(changed=changed), patch.object(acceptance, 'execution_check', return_value=bad), \
                 patch.object(acceptance, 'ACCEPTANCE_SHA256', '0' * 64 if changed == 'acceptance' else acceptance.ACCEPTANCE_SHA256):
                with self.assertRaises(ValueError): acceptance.check(local_product=predecessor)


if __name__ == '__main__':
    unittest.main()
