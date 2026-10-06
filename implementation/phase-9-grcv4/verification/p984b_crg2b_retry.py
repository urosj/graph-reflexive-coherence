"""Preserve the timed-out attempt and retry with no competing recheck workers.

The frozen inputs, native owner, 900-second budget and tolerances are unchanged.
This is a recorded execution retry, not numerical or acceptance credit for the
incomplete attempt.
"""

import hashlib
import json
import os

import p984b_crg2b_resume as recovery

r, b = recovery.r, recovery.b
SELF = b.HERE + "p984b_crg2b_retry.py"
TEST = b.HERE + "test_p984b_crg2b_retry.py"
TIMEOUT = b.BASE + "P9-8.4b-CRG2bTimeout.jsonl"
RECORD = b.BASE + "P9-8.4b-CRG2bRetry.json"
ATTEMPT_SHA = "672e26fa339ba75b9e503d5504105bc9179c377b131dc8f59864ea83b0763ee7"


def failed_attempt(raw, manifest, expected_sha=ATTEMPT_SHA):
    b.require(hashlib.sha256(raw).hexdigest() == expected_sha, "timeout evidence drift")
    lines = raw.splitlines(keepends=True)
    b.require(
        len(lines) == 16 and all(x.endswith(b"\n") for x in lines),
        "incomplete attempt framing",
    )
    prefix = b"".join(lines[:-1])
    recovery.decode_journal(prefix, manifest)
    failure = json.loads(lines[-1])
    b.check_digest(failure)
    case = manifest["cases"][14]
    b.require(
        failure["case_id"] == case["case_id"]
        and failure["input_digest"] == b.digest(case)
        and failure["case_passed"] is False
        and failure["outcome"] == "incomplete_case"
        and failure["first_failure"]["kind"] == "BudgetExpired",
        "not the declared operational timeout",
    )
    return prefix, failure


def main():
    manifest = b.read(r.INPUTS)
    r.check_manifest(manifest)
    journal = b.ROOT / (r.RESULTS + ".progress.jsonl")
    b.require(not (b.ROOT / r.RESULTS).exists(), "native result already exists")
    b.require(
        not (b.ROOT / TIMEOUT).exists(),
        "retry already prepared; explicit recovery required",
    )
    raw = journal.read_bytes()
    prefix, failure = failed_attempt(raw, manifest)
    b.require(
        hashlib.sha256(prefix).hexdigest() == recovery.JOURNAL_SHA,
        "original cases changed",
    )
    journal.rename(b.ROOT / TIMEOUT)
    with journal.open("xb") as out:
        out.write(prefix)
        out.flush()
        os.fsync(out.fileno())
    print("CRG2b_TIMEOUT_PRESERVED retry_budget_seconds=900", flush=True)
    # Native execution already uses FLINT. Select that same accepted exact
    # backend for the otherwise expensive retained-prefix/final validation.
    with b.exact_backend(b.ExactBackend.FLINT):
        recovery.main()
    result = b.read(r.RESULTS)
    b.check_digest(result)
    passed = result["cases"][14]
    b.require(
        passed["case_id"] == failure["case_id"] and passed["case_passed"] is True,
        "timed-out case not completed",
    )
    record = b.seal(
        {
            "schema": "p984b-crg2b-operational-retry-v1",
            "manifest_digest": manifest["record_digest"],
            "runtime_digest": result["record_digest"],
            "timeout_evidence": TIMEOUT,
            "timeout_sha256": ATTEMPT_SHA,
            "failed_case_id": failure["case_id"],
            "first_failure": failure["first_failure"],
            "completed_beats_before_timeout": len(failure["continuation"]),
            "case_budget_seconds": 900,
            "numerical_thresholds_changed": False,
            "retained_validation_backend": "flint",
            "incomplete_attempt_credited": False,
            "retry_scheduling": "native_cases_without_concurrent_recheck_workers",
            "source_bindings": b.bind(
                [SELF, TEST, TIMEOUT, r.INPUTS, r.RESULTS, recovery.SELF]
            ),
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )
    recovery.publish(b.ROOT / RECORD, record)
    print("CRG2b_OPERATIONAL_RETRY_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
