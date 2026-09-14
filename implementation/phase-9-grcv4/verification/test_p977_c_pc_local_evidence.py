"""Retained C_PC evidence pressure; no numerical campaign reruns."""

from copy import deepcopy
import unittest
from unittest.mock import patch
import verify_p977_c_pc_local as audit


class CPCLocalEvidenceTests(unittest.TestCase):
    def test_retained_product_and_rehashed_mutations(self):
        original=audit.review.read(audit.RECORD)
        audit.validate(original)
        def row(value,case):return next(r for r in value['fixture_results'] if r['fixture_id']==case)
        def obs(value,case):return row(value,case)['observation']
        def pc(value,change):
            # Mutate both shared catalog references consistently so the
            # scientific check, not just their equality, must reject it.
            for case in ('PC-ZOH','C-POST-CONTINUITY-REDERIVATION'):change(obs(value,case))
        changes={
            'missing_row':lambda v:v['fixture_results'].pop(),
            'duplicate_row':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'missing_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'borrowed_profile':lambda v:v['fixture_results'][0].update(complete_profile_id='C_PC'),
            'source_drift':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'G2_promotion':lambda v:v.update(G2_accepted=True),
            'new_support':lambda v:v.update(new_G2_support=['C_PC']),
            'acceptance':lambda v:v.update(user_accepted=True),
            'authority':lambda v:v.update(authority={}),
            'invented_solver':lambda v:row(v,'C-BASELINE-EXACT').update(solver_disposition='valid_root'),
            'wrong_delta':lambda v:row(v,'COMMON-VALID-ORDINARY-STEP').update(emitted_receipt_ids=[]),
            'wrong_failure':lambda v:row(v,'COMMON-CHARGE-MISMATCH').update(failure_code='domain_failure'),
            'control_identity':lambda v:obs(v,'C-CHI-ZERO').update(control_complete_profile_id=v['nomination']['complete_profile_id']),
            'extra_W_writer':lambda v:pc(v,lambda b:b['stages'][0].update(writer_count=1)),
            'double_Z_writer':lambda v:pc(v,lambda b:b['stages'][0].update(carrier_writes=2)),
            'new_source_refresh':lambda v:pc(v,lambda b:b.update(source_policy='post_continuity_source')),
            'matched_forcing_overclaim':lambda v:pc(v,lambda b:b.update(matched_forcing_contraction_claimed=True)),
            'base_invariance_overclaim':lambda v:pc(v,lambda b:b.update(indefinite_base_chart_invariance_claimed=True)),
            'old_h_geometry':lambda v:pc(v,lambda b:b['stages'][1]['observed'].update(h=[[2.]])),
            'C_baseline_drift':lambda v:pc(v,lambda b:b['stages'][0]['chains'][0]['observed'].update(j0=[999.])),
            'C_stale_reset':lambda v:pc(v,lambda b:b['stages'][0]['chains'][1].update(inputs_object=b['stages'][0]['chains'][0]['inputs_object'])),
            'C_stale_restart':lambda v:pc(v,lambda b:b['stages'][0]['chains'][2]['observed'].update(current=b['stages'][0]['chains'][0]['observed']['current'])),
            'carrier_endpoint':lambda v:pc(v,lambda b:b['stages'][0]['observed'].update(written_Z=[0.])),
            'source_envelope':lambda v:pc(v,lambda b:b['stages'][0]['certificate'].update(source_norm_upper='9999999')),
            'derivative':lambda v:obs(v,'C-BASELINE-DERIVATIVE-COVARIANCE')['derivatives'][0]['finite'].update(j0=[999]),
            'dense_scope':lambda v:obs(v,'C-BASELINE-DERIVATIVE-COVARIANCE').update(dense_control_not_nominated=False),
            'conditioning_scope':lambda v:obs(v,'C-RETAINED-VS-PHYSICAL-CONDITIONING').update(scope='dense_nomination_runtime'),
            'double_chi':lambda v:obs(v,'C-ONE-CHI-GATE').update(fixed_J_chi_ratio=4),
            'candidate_history':lambda v:obs(v,'C-C-ONLY-AUTHORITY').update(W_A=[1]),
            'drop_PC_authority':lambda v:obs(v,'C-C-ONLY-AUTHORITY').update(Z_4=None),
            'reset_as_release':lambda v:obs(v,'C-ZETA-ZERO').update(zero_source_release_not_reset=False),
            'missing_rejection':lambda v:v['readmission_pressure'].pop(),
            'reset_writer_leak':lambda v:v['readmission_pressure'][0].update(carrier_writes_before_rejection=1),
            'rollback':lambda v:v['readmission_pressure'][1].update(whole_publication_unchanged=False),
            'reset_authority':lambda v:obs(v,'RESET-AFTER-ORDINARY').update(independent_reset_authority={}),
            'lost_parent':lambda v:obs(v,'RECEIPT-OWNERSHIP').update(coherent_missing_parent_rejected=False),
            'duplicate_alias':lambda v:obs(v,'DUPLICATION-INDEPENDENCE').update(exported_mutations_detached=False),
        }
        with patch.object(audit,'authority',return_value=original['authority']):
            for name,change in changes.items():
                value=deepcopy(original);change(value);value['record_digest']=audit.p.digest_record(value)
                with self.subTest(name=name),self.assertRaises((ValueError,KeyError,TypeError)):
                    audit.validate(value)


if __name__=='__main__':
    unittest.main()
