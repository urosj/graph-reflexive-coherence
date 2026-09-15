"""Cheap rehashed evidence pressure; no numerical execution."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import verify_p977_c_ci_crossings as crossing
import verify_p977_profile_review as review


class CrossingEvidenceTests(unittest.TestCase):
    def test_rehashed_scope_endpoint_result_and_preimage_mutations(self):
        original = review.read(crossing.RECORD)
        crossing.validate(original)
        def row(v, name):
            return next(r for r in v['fixture_results'] if r['fixture_id'] == name)
        mutations = {
            'missing_case': lambda v: v['fixture_results'].pop(),
            'duplicate_case': lambda v: v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'source_drift': lambda v: v['source_bindings'].update({crossing.TEST: '0'*64}),
            'borrowed_source': lambda v: v['fixture_results'][0].update(complete_profile_id='C_CI'),
            'missing_result_field': lambda v: v['fixture_results'][0].pop('solver_disposition'),
            'invented_solver': lambda v: v['fixture_results'][0].update(solver_disposition='valid_root'),
            'wrong_delta': lambda v: v['fixture_results'][0]['emitted_receipt_ids'].pop(),
            'missing_matrix_class': lambda v: v['ordered_migration_matrix'].pop(),
            'all_pairs_matrix': lambda v: v['ordered_migration_matrix'][-1].update(disposition='all_pairs'),
            'borrowed_alias': lambda v: v['retained_aliases'][2].update(target_active_model_identity=crossing.NOMINATED),
            'G2_promotion': lambda v: v.update(G2_accepted=True),
            'user_acceptance': lambda v: v.update(user_accepted=True),
            'all_pairs': lambda v: v.update(all_ordered_pairs_verified=True),
            'new_support': lambda v: v.update(new_G2_support=['C_CI']),
            'missing_authority': lambda v:v.update(authority={}),
            'lost_carrier_loss': lambda v:row(v,'persistent_C_PC')['observation'].update(expected_losses=[]),
            'invented_initializer_loss': lambda v:row(v,'C_to_A')['observation'].update(expected_losses=['candidate_history_loss']),
            'event_charge': lambda v:row(v,'mapped_event')['observation'].update(expected_Q_target=4),
            'event_archive': lambda v:row(v,'mapped_event')['observation'].update(missing_archive_rejected=False),
            'initializer_role': lambda v:row(v,'C_to_A')['observation']['expectations']['reset'].update(W_A=[999]),
            'reference_equations': lambda v:row(v,'mapped_event')['observation']['target_readmission_points'][0]['observed'].update(j0=[999]),
            'reference_scope': lambda v:row(v,'mapped_event')['observation'].update(map_scope='all_graphs'),
            'publication_order': lambda v:row(v,'mapped_event')['observation'].update(both_roles_admitted_before_publication=False),
            'reset_role': lambda v:row(v,'persistent_C_PC')['observation'].update(after_reset_object=row(v,'persistent_C_PC')['poststate_object']),
            'catalog_omission': lambda v: v['catalog_cells'].pop('HISTORY-DISPOSITION'),
        }
        # Actual authority and retained aliases were validated once above.
        with patch.object(crossing,'authority',return_value=original['authority']), patch.object(crossing,'retained',return_value=original['retained_aliases']):
            for label, mutate in mutations.items():
                with self.subTest(label=label):
                    bad = deepcopy(original)
                    mutate(bad)
                    bad['record_digest'] = p.digest_record(bad)
                    with self.assertRaises((ValueError, KeyError, TypeError)):
                        crossing.validate(bad)


if __name__ == '__main__':
    unittest.main()
