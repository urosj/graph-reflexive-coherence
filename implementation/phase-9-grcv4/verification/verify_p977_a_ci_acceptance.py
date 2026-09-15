"""User acceptance of bounded A_CI reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_a_ci_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-A_CI-CrossingReview.md'
ACCEPTANCE_SHA256 = 'f08c2d2017702d2d36cf1c3e2bf8ed90dae0a7003e809395c23a03e082a25a0c'
EXECUTION_DIGEST = 'a5d8a9ea17843359b57e094cacb7f8d0dde1fa9ab46480f1eae6632acd2aba80'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'A_CI acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'A_CI acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
