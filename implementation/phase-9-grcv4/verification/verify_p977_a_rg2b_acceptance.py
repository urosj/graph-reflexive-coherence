"""User acceptance of bounded A_RG2b reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_a_rg2b_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-A_RG2b-CrossingReview.md'
ACCEPTANCE_SHA256 = 'a9bc7038055e03f836b4b5d9c538e1eb23d2fbc4f25bde21471d1379902de41a'
EXECUTION_DIGEST = '73d4c7823d18e71464e61f377a1cb8a93c9654c47cd5b2ff4727d20b0b7093a2'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'A_RG2b acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'A_RG2b acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
