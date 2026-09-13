"""Cheap rehashed evidence pressure; no numerical execution."""

from copy import deepcopy
import unittest

import phase9_implementation_policy as p
import verify_p977_a_os_crossings as crossing
import verify_p977_profile_review as review


class CrossingEvidenceTests(unittest.TestCase):
    def test_rehashed_scope_endpoint_result_and_preimage_mutations(self):
        original = review.read(crossing.RECORD)
        crossing.validate(original)
        mutations = {
            'missing_case': lambda v: v['fixture_results'].pop(),
            'duplicate_case': lambda v: v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'source_drift': lambda v: v['source_bindings'].update({crossing.TEST: '0'*64}),
            'borrowed_source': lambda v: v['fixture_results'][0].update(complete_profile_id='A_OS'),
            'missing_result_field': lambda v: v['fixture_results'][0].pop('solver_disposition'),
            'invented_solver': lambda v: v['fixture_results'][0].update(solver_disposition='valid_root'),
            'wrong_delta': lambda v: v['fixture_results'][0]['emitted_receipt_ids'].pop(),
            'missing_matrix_class': lambda v: v['ordered_migration_matrix'].pop(),
            'negative_as_positive': lambda v: v['ordered_migration_matrix'][-1].update(disposition='positive'),
            'borrowed_alias': lambda v: v['retained_aliases'][-1].update(target_active_model_identity=crossing.NOMINATED),
            'G2_promotion': lambda v: v.update(G2_accepted=True),
            'user_acceptance': lambda v: v.update(user_accepted=True),
            'all_pairs': lambda v: v.update(all_ordered_pairs_verified=True),
            'new_support': lambda v: v.update(new_G2_support=['A_OS']),
            'catalog_omission': lambda v: v['catalog_cells'].pop('HISTORY-DISPOSITION'),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                bad = deepcopy(original)
                mutate(bad)
                bad['record_digest'] = p.digest_record(bad)
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    crossing.validate(bad)


if __name__ == '__main__':
    unittest.main()
