"""Retained A_PC crossing pressure; no lifecycle reruns."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import verify_p977_a_pc_crossings as crossing
import verify_p977_profile_review as review


class CrossingEvidenceTests(unittest.TestCase):
    def test_rehashed_scope_map_history_and_endpoint_mutations(self):
        original=review.read(crossing.RECORD)
        crossing.validate(original)
        def row(v,name):
            return next(r for r in v['fixture_results'] if r['fixture_id']==name)
        def event(v):
            return row(v,'mapped_event')['observation']
        mutations={
            'missing_case':lambda v:v['fixture_results'].pop(),
            'duplicate_case':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'source_drift':lambda v:v['source_bindings'].update({crossing.TEST:'0'*64}),
            'borrowed_source':lambda v:row(v,'mapped_event').update(complete_profile_id='A_PC'),
            'missing_result_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'invented_solver':lambda v:v['fixture_results'][0].update(solver_disposition='valid_root'),
            'wrong_delta':lambda v:v['fixture_results'][0]['emitted_receipt_ids'].pop(),
            'missing_class':lambda v:v['ordered_migration_matrix'].pop(),
            'PC_pair_not_applicable':lambda v:v['ordered_migration_matrix'][3].update(disposition='not_applicable'),
            'incoming_promoted':lambda v:v['ordered_migration_matrix'][-1].update(disposition='positive_exact_nomination_target'),
            'borrowed_initializer':lambda v:v['retained_aliases'][-1].update(target_active_model_identity=crossing.NOMINATED),
            'G2_promotion':lambda v:v.update(G2_accepted=True),
            'acceptance':lambda v:v.update(user_accepted=True),
            'all_pairs':lambda v:v.update(all_ordered_pairs_verified=True),
            'new_support':lambda v:v.update(new_G2_support=['A_PC']),
            'authority':lambda v:v.update(authority={}),
            'carrier_loss_erased':lambda v:event(v).update(expected_losses=['candidate_history_loss']),
            'candidate_loss_erased':lambda v:event(v).update(expected_losses=['carrier_history_loss']),
            'reset_as_release':lambda v:event(v).update(source_history_removal_is_not_native_release=False),
            'event_charge':lambda v:event(v).update(expected_Q_target=4.),
            'event_archive':lambda v:event(v).update(missing_archive_rejected=False),
            'event_W':lambda v:event(v)['expectations']['current'].update(W_A=[2.]),
            'event_current':lambda v:event(v)['expectations']['reset'].update(current=[0.]),
            'collapsed_readmission_roles':lambda v:event(v)['expectations']['reset'].update(
                readmission_inputs_object=event(v)['expectations']['current']['readmission_inputs_object']),
            'initializer_identity':lambda v:row(v,'incoming_C_rejection')['observation'].update(selected_initializer_profile_id=crossing.NOMINATED),
            'reset_role':lambda v:event(v).update(after_reset_object=row(v,'mapped_event')['poststate_object']),
            'reset_chart':lambda v:row(v,'readmission_rejection')['observation'].update(target_resource_radius=4.),
            'reset_norm':lambda v:row(v,'readmission_rejection')['observation'].update(source_reset_norm_squared=8.),
            'silent_carrier_reset':lambda v:row(v,'carrier_contract_rejection')['observation'].update(unchanged_history_not_silently_reset=False),
            'catalog_omission':lambda v:v['catalog_cells'].pop('HISTORY-DISPOSITION'),
        }
        # Authority is validated once above; mutations still compare against
        # that exact trace. Avoid repeatedly loading the forensic graph.
        with patch.object(crossing,'authority',return_value=original['authority']):
            for label,mutate in mutations.items():
                with self.subTest(label=label):
                    bad=deepcopy(original); mutate(bad)
                    bad['record_digest']=p.digest_record(bad)
                    with self.assertRaises((ValueError,KeyError,TypeError)):
                        crossing.validate(bad)


if __name__=='__main__':
    unittest.main()
