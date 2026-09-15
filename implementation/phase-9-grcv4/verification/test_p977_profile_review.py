"""Read-only pressure on P9-7.7 reconciliation; no numerical reruns."""

from copy import deepcopy
import unittest

import verify_p977_profile_review as review


class ProfileReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = review.read(review.RECORD)

    def test_full_catalog_product_and_existing_positive_alias(self):
        actual = review.reconcile()
        self.assertEqual(actual, {k: self.value[k] for k in actual})
        self.assertEqual(actual['summary']['required_cells'], 305)
        self.assertEqual(len(actual['profiles']), 10)
        for row in actual['profiles']:
            self.assertEqual([c['fixture_id'] for c in row['cells']], review.required_cases(row['profile_family']))
            self.assertEqual(row['required_case_count'], len(row['cells']))
            self.assertTrue(row['cells'])
        accepted = [r for r in actual['profiles'] if r['verdict'] == 'ACCEPTED_ALIAS']
        self.assertEqual([r['profile_family'] for r in accepted], ['C_OS'])
        self.assertTrue(all(c['disposition'] == 'accepted_alias' for c in accepted[0]['cells']))
        self.assertNotEqual(accepted[0]['complete_profile_id'], accepted[0]['lifecycle_seed_profile_id'])
        self.assertEqual(actual['summary']['new_execution_credit'], 0)

    def test_nominations_and_crossing_identities_are_not_family_joins(self):
        from pygrc.models.grc_v4_profile import resolve_profile
        for row in self.value['profiles']:
            profile = row['nomination']
            self.assertEqual(resolve_profile(profile['params_resolved'], profile['identity_payload']).complete_profile_id,
                             row['complete_profile_id'])
            self.assertEqual(row['event_target_matches_nomination'], row['event_target_profile_id'] == row['complete_profile_id'])
            for cell in row['cells']:
                self.assertTrue(cell['evidence'])
                for source in cell['evidence']:
                    self.assertIsNotNone(review.resolve(source))
        mismatches = {r['profile_family'] for r in self.value['profiles'] if not r['event_target_matches_nomination']}
        self.assertEqual(mismatches, {'C_OS', 'C_RG2b', 'A_OS', 'A_CI', 'A_PC', 'A_CI_PC', 'A_RG2b'})
        self.assertEqual(len(self.value['ordered_migration_witnesses']), 18)
        self.assertEqual(len(self.value['migration_classes']), 7)

    def test_rehashed_scope_coverage_and_acceptance_mutations_reject(self):
        mutations = {
            'missing_profile': lambda v: v['profiles'].pop(),
            'duplicate_profile': lambda v: v['profiles'].append(deepcopy(v['profiles'][0])),
            'missing_case': lambda v: v['profiles'][0]['cells'].pop(),
            'duplicate_case': lambda v: v['profiles'][0]['cells'].append(deepcopy(v['profiles'][0]['cells'][0])),
            'family_as_identity': lambda v: v['profiles'][0].update(complete_profile_id='A_CI'),
            'borrowed_event_identity': lambda v: v['profiles'][0].update(complete_profile_id=v['profiles'][0]['event_target_profile_id']),
            'invented_credit': lambda v: v['profiles'][0]['cells'][0].update(disposition='accepted_alias'),
            'false_gate_pass': lambda v: v['profiles'][0].update(verdict='PASS'),
            'user_acceptance': lambda v: v.update(user_accepted=True),
            'support_expansion': lambda v: v.update(new_G2_support=['A_OS']),
            'G3_expansion': lambda v: v.update(G3_accepted=True),
            'missing_migration_class': lambda v: v['migration_classes'].pop(),
            'symbolic_as_native': lambda v: v['summary'].update(new_execution_credit=16),
            'source_drift': lambda v: v['source_bindings'].update({review.CATALOG: '0'*64}),
        }
        review.validate(self.value, self.value)
        for name, mutate in mutations.items():
            value = deepcopy(self.value)
            mutate(value)
            value['record_digest'] = review.p.digest_record(value)
            with self.subTest(name=name), self.assertRaises(ValueError):
                review.validate(value, self.value)


if __name__ == '__main__':
    unittest.main()
