"""Rehashed coupled-product pressure without native campaign reruns."""

from copy import deepcopy
import unittest
from unittest.mock import patch
import verify_p977_a_ci_pc_local as audit


class ACIPCLocalEvidenceTests(unittest.TestCase):
    def test_retained_product_and_rehashed_mutations(self):
        original=audit.review.read(audit.RECORD)
        audit.validate(original)
        def row(v,name):return next(r for r in v['fixture_results'] if r['fixture_id']==name)
        def change_branch(v,edit):
            for r in v['fixture_results']:
                if 'source_policy' in (r['observation'] or {}):edit(r['observation'])
        changes={
            'missing_cell':lambda v:v['fixture_results'].pop(),
            'duplicate_cell':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'borrowed_profile':lambda v:v['fixture_results'][0].update(complete_profile_id='A_CI'),
            'source_drift':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'authority_promotion':lambda v:v.update(authority={}),
            'G2':lambda v:v.update(G2_accepted=True),
            'acceptance':lambda v:v.update(user_accepted=True),
            'new_support':lambda v:v.update(new_G2_support=['A_CI_PC']),
            'invented_solver':lambda v:row(v,'CI-PC-SAME-SOURCE').update(solver_disposition='valid_root'),
            'receipt_delta':lambda v:row(v,'COMMON-VALID-ORDINARY-STEP').update(emitted_receipt_ids=[]),
            'later_source':lambda v:change_branch(v,lambda b:b.update(source_policy='post_continuity_source')),
            'double_Z':lambda v:change_branch(v,lambda b:b.update(carrier_writes=2)),
            'missing_W':lambda v:change_branch(v,lambda b:b.update(writer_count=0)),
            'gain_one':lambda v:change_branch(v,lambda b:b.update(composition_gain=1)),
            'immediate_off':lambda v:change_branch(v,lambda b:b.update(rho_inst=0)),
            'source_value':lambda v:change_branch(v,lambda b:b.update(source=[[0.]])),
            'carrier_value':lambda v:change_branch(v,lambda b:b.update(written_Z=[0.])),
            'self_consistent_wrong_current':lambda v:change_branch(v,lambda b:(b['observed'].update(current=[999.]),b['independent_oracle'].update(current=[999.]))),
            'shape_broadcast':lambda v:change_branch(v,lambda b:b['observed'].update(hodge=[1.])),
            'stale_reset':lambda v:change_branch(v,lambda b:b.update(reset_inputs_object=b['source_inputs_object'])),
            'uncertified_source':lambda v:change_branch(v,lambda b:b['certificate'].update(uniform_source_upper='99999')),
            'lost_companion':lambda v:v['companions'].pop(),
            'companion_source':lambda v:v['companions'][0].update(source=[[0.]]),
            'reset_not_release':lambda v:v['companions'][1].update(written_Z=[0.]),
            'companion_support':lambda v:v['companions'][1].update(scope='same_nomination_history_companion'),
            'companion_readmission':lambda v:v['companions'][0]['roles'].pop(),
            'stale_restart':lambda v:v['companions'][0]['roles'][1].update(current=v['companions'][0]['current']),
            'missing_rejection':lambda v:v['readmission_pressure'].pop(),
            'reset_writer_leak':lambda v:v['readmission_pressure'][0].update(carrier_writes_before_rejection=1),
            'rollback':lambda v:v['readmission_pressure'][1].update(whole_publication_unchanged=False),
            'reset_authority':lambda v:row(v,'RESET-AFTER-ORDINARY')['observation'].update(independent_reset_authority={}),
            'missing_parent':lambda v:row(v,'RECEIPT-OWNERSHIP')['observation'].update(coherent_missing_parent_rejected=False),
            'duplicate_alias':lambda v:row(v,'DUPLICATION-INDEPENDENCE')['observation'].update(exported_mutations_detached=False),
        }
        with patch.object(audit,'authority',return_value=original['authority']):
            for name,edit in changes.items():
                value=deepcopy(original);edit(value);value['record_digest']=audit.p.digest_record(value)
                with self.subTest(name=name),self.assertRaises((ValueError,KeyError,TypeError)):
                    audit.validate(value)


if __name__=='__main__':unittest.main()
