"""Read-only pressure on the A_CI local execution record."""

from copy import deepcopy
import unittest

import verify_p977_a_ci_local as audit


class ACILocalEvidenceTests(unittest.TestCase):
    def test_retained_product_and_rehashed_mutations(self):
        original=audit.review.read(audit.RECORD)
        audit.validate(original)
        def row(v,case):
            return next(r for r in v['fixture_results'] if r['fixture_id']==case)
        changes={
            'missing_row':lambda v:v['fixture_results'].pop(),
            'duplicate_row':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'missing_result_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'borrowed_profile':lambda v:v['fixture_results'][0].update(complete_profile_id='A_CI'),
            'source_drift':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'G2_promotion':lambda v:v.update(G2_accepted=True),
            'new_support':lambda v:v.update(new_G2_support=['A_CI']),
            'unearned_acceptance':lambda v:v.update(user_accepted=True),
            'invented_solver':lambda v:row(v,'A-LOG-WRITER').update(solver_disposition='valid_root'),
            'wrong_delta':lambda v:row(v,'COMMON-VALID-ORDINARY-STEP').update(emitted_receipt_ids=[]),
            'wrong_failure':lambda v:row(v,'COMMON-CHARGE-MISMATCH').update(failure_code='domain_failure'),
            'wrong_control':lambda v:row(v,'A-CHI-ZERO').update(complete_profile_id=v['nomination']['complete_profile_id']),
            'CI_contraction':lambda v:row(v,'CI-BRANCH')['observation']['certificate'].update(contraction_upper='1'),
            'CI_residual':lambda v:row(v,'CI-BRANCH')['observation'].update(residual_squared='1'),
            'CI_writer_count':lambda v:row(v,'CI-BRANCH')['observation'].update(writer_count=2),
            'CI_global_branch':lambda v:row(v,'CI-BRANCH')['observation'].update(branch_scope='global_unique'),
            'CI_borrowed_OS_stage':lambda v:row(v,'CI-BRANCH')['observation'].update(current_stage_roster=['os_corrector']),
            'CI_bad_current':lambda v:row(v,'CI-BRANCH')['observation']['observed'].update(current=[999]),
            'CI_fallback':lambda v:row(v,'CI-BRANCH')['observation']['budget_control'].update(fallback_used=True),
            'CI_authority':lambda v:v.update(authority={}),
        }
        for name,change in changes.items():
            value=deepcopy(original); change(value); value['record_digest']=audit.p.digest_record(value)
            with self.subTest(name=name), self.assertRaises((ValueError,KeyError)):
                audit.validate(value)


if __name__=='__main__':
    unittest.main()
