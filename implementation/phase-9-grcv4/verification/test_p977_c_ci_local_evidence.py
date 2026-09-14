"""Retained C_CI evidence pressure; never reruns the numerical campaign."""

from copy import deepcopy
import unittest
from unittest.mock import patch
import verify_p977_c_ci_local as audit


class CCILocalEvidenceTests(unittest.TestCase):
    def test_retained_product_and_rehashed_mutations(self):
        original=audit.review.read(audit.RECORD)
        audit.validate(original)
        def row(value,case):
            return next(r for r in value['fixture_results'] if r['fixture_id']==case)
        changes={
            'missing_row':lambda v:v['fixture_results'].pop(),
            'duplicate_row':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'missing_result_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'borrowed_profile':lambda v:v['fixture_results'][0].update(complete_profile_id='C_CI'),
            'source_drift':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'G2_promotion':lambda v:v.update(G2_accepted=True),
            'new_support':lambda v:v.update(new_G2_support=['C_CI']),
            'unearned_acceptance':lambda v:v.update(user_accepted=True),
            'invented_solver':lambda v:row(v,'C-BASELINE-EXACT').update(solver_disposition='valid_root'),
            'wrong_delta':lambda v:row(v,'COMMON-VALID-ORDINARY-STEP').update(emitted_receipt_ids=[]),
            'wrong_failure':lambda v:row(v,'COMMON-CHARGE-MISMATCH').update(failure_code='domain_failure'),
            'wrong_control':lambda v:row(v,'C-CHI-ZERO')['observation'].update(control_complete_profile_id=v['nomination']['complete_profile_id']),
            'CI_contraction':lambda v:row(v,'CI-BRANCH')['observation']['certificate'].update(contraction_upper='1'),
            'CI_residual':lambda v:row(v,'CI-BRANCH')['observation'].update(residual_squared='1'),
            'CI_writer_leak':lambda v:row(v,'CI-BRANCH')['observation'].update(writer_count=1),
            'CI_global_branch':lambda v:row(v,'CI-BRANCH')['observation'].update(branch_scope='global_unique'),
            'CI_bad_current':lambda v:row(v,'CI-BRANCH')['observation']['observed'].update(current=[999]),
            'CI_fallback':lambda v:row(v,'CI-BRANCH')['observation']['budget_control'].update(fallback_used=True),
            'CI_authority':lambda v:v.update(authority={}),
            'C_stale_restart':lambda v:row(v,'CI-BRANCH')['observation']['observed'].update(restart_current=row(v,'CI-BRANCH')['observation']['observed']['current']),
            'C_bad_derivative':lambda v:row(v,'C-BASELINE-DERIVATIVE-COVARIANCE')['observation']['derivatives'][0]['finite'].update(j0=[999]),
            'C_dense_scope':lambda v:row(v,'C-BASELINE-DERIVATIVE-COVARIANCE')['observation'].update(dense_control_not_nominated=False),
            'C_conditioning_scope':lambda v:row(v,'C-RETAINED-VS-PHYSICAL-CONDITIONING')['observation'].update(scope='nomination_dense_runtime'),
            'C_double_chi':lambda v:row(v,'C-ONE-CHI-GATE')['observation'].update(fixed_J_chi_ratio=4),
            'C_history':lambda v:row(v,'C-C-ONLY-AUTHORITY')['observation'].update(W_A=[1]),
        }
        # The actual authority was checked above. Reuse that one immutable result
        # only while mutating the retained record; no repeated graph loading.
        with patch.object(audit,'authority',return_value=original['authority']):
            for name,change in changes.items():
                value=deepcopy(original); change(value); value['record_digest']=audit.p.digest_record(value)
                with self.subTest(name=name), self.assertRaises((ValueError,KeyError)):
                    audit.validate(value)


if __name__=='__main__':
    unittest.main()
