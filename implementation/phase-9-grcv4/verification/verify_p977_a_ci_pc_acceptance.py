"""User acceptance of bounded A_CI_PC reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_a_ci_pc_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-A_CI_PC-CrossingReview.md'
ACCEPTANCE_SHA256 = 'b4fde37466d1c222e02d7e4352e431fb569142e6d7658d7181455bc337875275'
EXECUTION_DIGEST = '484beef4f47d73f0c255c50c5299fcb79179dfa59813a2dde1a2a868e461b4e5'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'A_CI_PC acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'A_CI_PC acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
