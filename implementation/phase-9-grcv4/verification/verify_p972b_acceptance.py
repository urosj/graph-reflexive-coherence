"""Project the user's P9-7.2b acceptance without relabeling execution evidence."""

import json
import phase9_implementation_policy as p
from verify_p972b_runtime import check as execution_check

REVIEW = p.PHASE + "tranche-7/P9-7.2b-RuntimeReview.md"
ACCEPTANCE_SHA256 = "9ac06f87275fe656a2650334517be319b9eb7c98c2b9710dae263a349237120d"
EXECUTION_DIGEST = "420c4a6ed565edf48e61398f6dca8680b0b190915881e738085d410993bbd7db"


def check():
    evidence = execution_check()
    p.require(evidence["record_digest"] == EXECUTION_DIGEST,
              "P9-7.2b acceptance does not cover this execution")
    p.require(p.sha((p.ROOT / REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              "P9-7.2b acceptance record missing or changed")
    return dict(evidence, status="accepted", user_accepted=True, aggregate_closed=True,
                acceptance_path=REVIEW, acceptance_sha256=ACCEPTANCE_SHA256,
                numerical_tests_rerun=0)


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
