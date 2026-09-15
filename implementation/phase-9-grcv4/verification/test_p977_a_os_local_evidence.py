"""Read-only pressure on the A_OS local execution record."""

from copy import deepcopy
import unittest

import verify_p977_a_os_local as audit


class AOSLocalEvidenceTests(unittest.TestCase):
    def test_retained_product_and_rehashed_mutations(self):
        original=audit.review.read(audit.RECORD)
        audit.validate(original)
        def row(v,case):
            return next(r for r in v['fixture_results'] if r['fixture_id']==case)
        changes={
            'missing_row':lambda v:v['fixture_results'].pop(),
            'duplicate_row':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'missing_result_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'borrowed_profile':lambda v:v['fixture_results'][0].update(complete_profile_id='A_OS'),
            'source_drift':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'G2_promotion':lambda v:v.update(G2_accepted=True),
            'new_support':lambda v:v.update(new_G2_support=['A_OS']),
            'unearned_acceptance':lambda v:v.update(user_accepted=True),
            'invented_solver':lambda v:row(v,'A-LOG-WRITER').update(solver_disposition='valid_root'),
            'wrong_delta':lambda v:row(v,'COMMON-VALID-ORDINARY-STEP').update(emitted_receipt_ids=[]),
            'wrong_failure':lambda v:row(v,'COMMON-CHARGE-MISMATCH').update(failure_code='domain_failure'),
            'wrong_control':lambda v:row(v,'A-CHI-ZERO').update(complete_profile_id=v['nomination']['complete_profile_id']),
        }
        for name,change in changes.items():
            value=deepcopy(original); change(value); value['record_digest']=audit.p.digest_record(value)
            with self.subTest(name=name), self.assertRaises((ValueError,KeyError)):
                audit.validate(value)


if __name__=='__main__':
    unittest.main()
