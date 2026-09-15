"""Project the user's bounded P9-7.6 acceptance over its unchanged execution."""

import json
import phase9_implementation_policy as p
from verify_p976_lineage_ownership import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.6-Review.md'
ACCEPTANCE_SHA256 = '2368d43b5fb7e4548dceffdb9b9fac92441170cf2730934fdf61a5ca0033e512'
EXECUTION_DIGEST = '1321caf7fd2b532375b08e219285805475e77ce377785ca47a32b1cfa7a99354'


def check():
    value = execution_check()
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'P9-7.6 acceptance does not cover this execution')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'P9-7.6 acceptance record missing or changed')
    return dict(value, status='accepted', user_accepted=True, aggregate_closed=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
