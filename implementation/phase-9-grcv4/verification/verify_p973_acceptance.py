"""Project P9-7.3 acceptance over the unchanged six-test and three-test runs."""

import json
import phase9_implementation_policy as p
from verify_p973_history_policy import check as baseline_check
from test_p973_sharp_regressions import check as sharp_check

REVIEW = p.PHASE + 'tranche-7/P9-7.3-Review.md'
ACCEPTANCE_SHA256 = '43dfc3b8be7c6183c6402eb2db9efa7378e0a0f1da684ebd614eac311977e7fb'
BASELINE_DIGEST = '3dd332471957d0adae6597842ec6f2c90dfa2baa8c55e642b52fe6a3d03ba653'
SHARP_DIGEST = 'b42ecf99e7168b97d91502bcdc2b68d3213e4c6527255f5a628cd30ac9ff3498'


def check():
    baseline, sharp = baseline_check(), sharp_check()
    p.require(baseline['record_digest'] == BASELINE_DIGEST and sharp['record_digest'] == SHARP_DIGEST,
              'P9-7.3 acceptance does not cover these executions')
    p.require(p.sha((p.ROOT/REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              'P9-7.3 acceptance record missing or changed')
    return dict(baseline, status='accepted', user_accepted=True, aggregate_closed=True,
                test_count=9, baseline_test_count=6, regression_test_count=3,
                regression_record_path=sharp['record_path'], regression_record_digest=SHARP_DIGEST,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256, numerical_tests_rerun=0)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
