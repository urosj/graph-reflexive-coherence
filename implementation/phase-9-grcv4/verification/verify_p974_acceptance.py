"""Project the user's bounded P9-7.4 acceptance over its unchanged execution."""

import json
import phase9_implementation_policy as p
from verify_p974_target_reference import check as execution_check

REVIEW = p.PHASE + 'tranche-7/P9-7.4-Review.md'
ACCEPTANCE_SHA256 = '40c38911b3a85a1863b2d1ee4a46ccc1a6daeda4d44f4bf97fa840a208c9b63f'
EXECUTION_DIGEST = '547e2c932a121189dcc6b5ea8b33d3d6524167a74a142c526d6898a2be597e51'


def check():
    value = execution_check()
    p.require(value['record_digest'] == EXECUTION_DIGEST,
              'P9-7.4 acceptance does not cover this execution')
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'P9-7.4 acceptance record missing or changed')
    return dict(value, status='accepted', user_accepted=True, aggregate_closed=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
