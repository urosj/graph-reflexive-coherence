"""User acceptance of bounded A_PC reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_a_pc_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-A_PC-CrossingReview.md'
ACCEPTANCE_SHA256 = '23a4cc11997d9035a6d3d89442be2b65b717cd522cb621ca2127d5164956e957'
EXECUTION_DIGEST = '4cf4b3405f775a790d7535891e32747378f3b4cac2e1cdf0d736f2225b619edc'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'A_PC acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'A_PC acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
