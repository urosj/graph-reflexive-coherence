"""Exact A_OS G2 acceptance over preserved review and execution subjects."""

import json
import phase9_implementation_policy as p
import verify_p977_a_os_g2 as proposal

RECORD = p.PHASE + 'tranche-7/P9-7.7-A_OS-G2Acceptance.json'


def check(bounded_acceptance=None):
    reviewed = proposal.check(bounded_acceptance)
    accepted = p.accepted_a_os_g2(p.ROOT)
    p.require(reviewed['record_digest'] == accepted['review']['record_digest'], 'A_OS acceptance subject differs')
    return dict(reviewed, status='accepted', user_accepted=True, G2_accepted=True,
        acceptance_path=RECORD, acceptance_digest=accepted['record_digest'],
        accepted_generic_runtime_support=p.accepted_generic_support(p.ROOT),
        source_reuse_record=accepted['source_reuse'], new_G2_support=[proposal.NOMINATED])


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
