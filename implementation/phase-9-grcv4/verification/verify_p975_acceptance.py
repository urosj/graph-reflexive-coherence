"""Project the user's bounded P9-7.5 acceptance over its unchanged execution."""

import json
import phase9_implementation_policy as p
from verify_p975_failure_sequences import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.5-Review.md'
ACCEPTANCE_SHA256 = 'cfd83f4b1c5e9ae04f5deb04ca79788af04327660b82415f3d45306deb64a647'
EXECUTION_DIGEST = '8563c051871a681654da4767031916357840a55e50f3cdb4b39e07089b843329'


def check():
    value = execution_check()
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'P9-7.5 acceptance does not cover this execution')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'P9-7.5 acceptance record missing or changed')
    return dict(value, status='accepted', user_accepted=True, aggregate_closed=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
