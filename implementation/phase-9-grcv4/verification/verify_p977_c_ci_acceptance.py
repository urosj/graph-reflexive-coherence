"""User acceptance of bounded C_CI reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_c_ci_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-C_CI-CrossingReview.md'
ACCEPTANCE_SHA256 = '6855f835006f1502acae874189b0476cb307ce4bc1dec0e8467ebf2fa3e2ab5c'
EXECUTION_DIGEST = '0bb8587f208e05121d517670468611c5f0c82f8935886f6e0b2c3b0976beec21'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'C_CI acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'C_CI acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
