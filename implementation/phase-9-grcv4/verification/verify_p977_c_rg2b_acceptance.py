"""User acceptance of bounded C_RG2b reconciliation, not G2 or all-pairs support."""

import json
import phase9_implementation_policy as p
from verify_p977_c_rg2b_crossings import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.7-C_RG2b-CrossingReview.md'
ACCEPTANCE_SHA256 = '3a8bda111dd99b55c7c99dadd11f9c9ce789a4ab1303e1945fc4216bc9e6b5a5'
EXECUTION_DIGEST = 'f6b717563826c8af1d333390b22cfaf7c6967ff01e5636a7b9b90dc7aff6feaf'


def check(local_product=None):
    value = execution_check(local_product=local_product)
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'C_RG2b acceptance does not cover this reconciliation')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'C_RG2b acceptance record missing or changed')
    return dict(value, status='accepted_bounded_reconciliation', user_accepted=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
