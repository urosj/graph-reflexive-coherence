"""User acceptance of bounded C_PC reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_c_pc_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-C_PC-CrossingReview.md'
ACCEPTANCE_SHA256 = '442d9417d01b362a5531817b68f2c1d57343cc88d6b76055659535f0a18edbcd'
EXECUTION_DIGEST = 'd18e5fe2a2bba6b2a11992ab8f22edda423cb3c2f8934937e22ab77df3acad49'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'C_PC acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'C_PC acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
