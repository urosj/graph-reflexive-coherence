"""User acceptance of bounded A_OS reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_a_os_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-A_OS-CrossingReview.md'
ACCEPTANCE_SHA256 = '980f8676b89c45e2d027b7c76f73324c5d759a3b6d161f66db6681709004e657'
EXECUTION_DIGEST = '2322b1a2f8b6b4904b38200f2f9018356db2698fbaafd53fe6c9ef8497afc351'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'A_OS acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'A_OS acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
