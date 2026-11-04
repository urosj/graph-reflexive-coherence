"""Inspect retained native integration regressions without executing tests."""

from pathlib import Path
import json
import sys
from .canonical import digest

RECORD_DIGEST = "fe7bfcc6f5e6774bc5217cce85b06b017666d94269220ef9f39d8b0bdf8ceea5"
ACCEPTANCE_PATH = "implementation/phase-9-grcv4/tranche-10/P9-10.3-NativeSpark-Acceptance.json"
ACCEPTANCE_DIGEST = 'd54a2e2baa35139c1faaca1d28b2d277fc348be522e503c637ac1744da5f8343'


def accepted_decision(value, execution):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    if (
        value.get("record_digest") != digest(body)
        or value["record_digest"] != ACCEPTANCE_DIGEST
        or value["execution_record_digest"] != execution["record_digest"]
        or value["families"] != execution["reused_evidence"]["families"]
        or value["tests_run"] != execution["tests_run"]
    ):
        raise ValueError("changed native integration acceptance")
    return value


def native_spark_regressions(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import p9103_native_spark as checker

    if checker.ROOT != root:
        raise ValueError("regression checkout mismatch")
    value = checker.check()
    if value["record_digest"] != RECORD_DIGEST:
        raise ValueError("changed native integration record")
    acceptance = accepted_decision(json.loads((root / ACCEPTANCE_PATH).read_bytes()), value)
    body = {
        k: value[k]
        for k in (
            "schema",
            "status",
            "entry_commit",
            "tests_run",
            "regressions",
            "reused_evidence",
            "scope",
            "user_accepted",
            "full_GRC9V4_conformance",
            "G4_accepted",
            "hierarchy_tracking",
            "new_support",
            "source_to_completion_campaigns_rerun",
            "next_work",
            "record_digest",
        )
    }
    body["execution_status"] = value["status"]
    body["execution_user_accepted"] = value["user_accepted"]
    body["status"] = acceptance["status"]
    body["user_accepted"] = acceptance["user_accepted"]
    body["acceptance"] = dict(path=ACCEPTANCE_PATH, **acceptance)
    body["source_url"] = "/api/native-spark/regressions/source"
    return dict(body, projection_digest=digest(body))


def native_spark_regressions_source(root):
    native_spark_regressions(root)
    from p9103_native_spark import PATH

    return (Path(root) / PATH).read_bytes()
