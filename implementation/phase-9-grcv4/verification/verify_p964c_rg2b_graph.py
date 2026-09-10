#!/usr/bin/env python3
"""Preserve the graph RG2b campaign and capture/check its bounded d review."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import io
import json
import platform
import sys
import time
import unittest

import phase9_implementation_policy as p
import verify_p964_rg2b as original
import verify_p962_pc as pc

ROOT = p.ROOT
SCRIPT = p.HERE + "verify_p964c_rg2b_graph.py"
REVIEW = p.PHASE + "tranche-6/P9-6.4c-Review.md"
RECORD = p.PHASE + "tranche-6/P9-6.4c-ExecutionRecord.json"
FOLLOWUP = p.PHASE + "tranche-6/P9-6.4d-AuditFollowup.json"
RECONCILIATION_TESTS = ["tests.models.test_grc_v4_rg2b_graph.GraphRG2bReconciliation"]
RECONCILIATION_SOURCES = {
    SCRIPT,
    REVIEW,
    original.SCRIPT,
    "tests/models/test_grc_v4_rg2b_graph.py",
}
TESTS = ["tests.models.test_grc_v4_rg2b", "tests.models.test_grc_v4_rg2b_graph"]
OPTIONAL = (
    "tests.models.test_grc_v4_rg2b_graph.GraphRG2bLargerExecution."
    "test_32_vertex_cycle_native_step_and_independent_current"
)


def permitted_skips(run):
    return [test.id() for test, _ in run.skipped] in ([], [OPTIONAL])


def sources():
    return {
        **original.sources(),
        **{name: p.sha((ROOT / name).read_bytes()) for name in (SCRIPT, REVIEW)},
    }


def capture():
    # The initialized record contains only essential external audit context and
    # reverse source spans; execution fields are written only after real success.
    record = p.read(ROOT / RECORD)
    p.require("result" not in record, "preserve completed RG2b execution")
    before = sources()
    suite, ids = pc.suite(TESTS)
    output = io.StringIO()

    class Tee:
        def write(self, text):
            output.write(text)
            sys.stdout.write(text)
            sys.stdout.flush()

        def flush(self):
            sys.stdout.flush()

    started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
    run = unittest.TextTestRunner(stream=Tee(), verbosity=2).run(suite)
    elapsed = round(time.monotonic() - clock, 3)
    p.require(
        run.wasSuccessful()
        and run.testsRun == len(ids)
        and permitted_skips(run)
        and not run.expectedFailures,
        "RG2b graph campaign failed",
    )
    p.require(sources() == before, "source drift during RG2b campaign")
    record.update(
        status="implemented_verified_pending_P9_6_4d_and_user_acceptance",
        source_git_base=p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        source_bindings=before,
        source_contracts=original.source_contracts(),
        environment=dict(
            python=platform.python_version(),
            platform=platform.platform(),
            dependencies={
                name: importlib.metadata.version(name)
                for name in ("numpy", "jsonschema", "rfc8785")
            },
        ),
        result=dict(
            started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=elapsed,
            tests_run=run.testsRun,
            failures=0,
            errors=0,
            skips=len(run.skipped),
            skipped_ids=[test.id() for test, _ in run.skipped],
            passed=run.testsRun - len(run.skipped),
            roster_ids=ids,
            executed_ids=[
                name
                for name in ids
                if name not in {test.id() for test, _ in run.skipped}
            ],
            output_sha256=p.sha(output.getvalue().encode()),
            command=[".venv/bin/python", "-m", "unittest", "-v", *TESTS],
        ),
        reconstruction="From repository root, provision .venv with uv sync --frozen --extra v4 --extra dev, then use PYTHONPATH=src:. with the recorded unittest command. The 32-vertex campaign is optional and skipped unless GRCV4_RUN_SLOW_RG2B=1 is explicitly set; a skip does not establish its result. The fixture and oracle source is in Git; reverse spans recover the original uncommitted a/b subject. --check verifies source/record bindings without repeating numerical tests. No external files are needed. Output hashes and timings are observations.",
    )
    record["record_digest"] = p.digest_record(record)
    (ROOT / RECORD).write_text(json.dumps(record, indent=2) + "\n")


def capture_reconciliation():
    follow = p.read(ROOT / FOLLOWUP)
    p.require("result" not in follow, "preserve completed RG2b reconciliation")
    before = sources()
    suite, ids = pc.suite(RECONCILIATION_TESTS)
    stream = io.StringIO()
    started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
    run = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    elapsed = round(time.monotonic() - clock, 3)
    print(stream.getvalue(), end="", flush=True)
    p.require(
        run.wasSuccessful()
        and run.testsRun == len(ids) == 3
        and not run.skipped
        and not run.expectedFailures,
        "RG2b reconciliation pressure failed",
    )
    p.require(sources() == before, "source drift during RG2b reconciliation")
    follow.update(
        status="reviewed_verified_pending_user_acceptance",
        source_bindings={name: before[name] for name in sorted(RECONCILIATION_SOURCES)},
        source_inventory_digest=p.sha(p.canonical(before)),
        environment=dict(
            python=platform.python_version(),
            dependencies={
                name: importlib.metadata.version(name)
                for name in ("numpy", "jsonschema", "rfc8785")
            },
        ),
        result=dict(
            started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=elapsed,
            tests_run=run.testsRun,
            failures=0,
            errors=0,
            skips=0,
            executed_ids=ids,
            output_sha256=p.sha(stream.getvalue().encode()),
            command=[".venv/bin/python", "-m", "unittest", "-v", *RECONCILIATION_TESTS],
        ),
    )
    follow["record_digest"] = p.digest_record(follow)
    (ROOT / FOLLOWUP).write_text(json.dumps(follow, indent=2) + "\n")


def check_reconciliation(follow, record):
    current = sources()
    accepted = follow.get("acceptance")
    if accepted is not None:
        p.require(
            accepted["status"] == "accepted_by_user"
            and accepted["accepted_iterations"]
            == ["P9-6.4a", "P9-6.4b", "P9-6.4c", "P9-6.4d"]
            and accepted["profiles_reviewed"] == ["A_RG2b", "C_RG2b"]
            and accepted["scientific_verdict"] == "PASS"
            and accepted["open_leaf_blockers"] == []
            and accepted["new_runtime_iterations_authorized"] == []
            and accepted["RG2b_G2_accepted"] is False
            and accepted["G3_accepted"] is False
            and accepted["reviewed_record_digest"]
            == p.digest_record({k: v for k, v in follow.items() if k != "acceptance"})
            and set(accepted["source_maintenance"]) == {SCRIPT, REVIEW},
            "invalid bounded RG2b acceptance",
        )
        current = original.historical_sources(
            {"source_bindings": current},
            {"prior_source_delta": accepted["source_maintenance"]},
        )
    p.require(
        follow["record_digest"] == p.digest_record(follow), "changed RG2b d record"
    )
    p.require(
        set(follow["prior_source_delta"]) == RECONCILIATION_SOURCES,
        "RG2b reconciliation cannot alter numerical owners",
    )
    p.require(
        follow["original_execution_digest"] == record["record_digest"]
        and follow["original_execution_sha256"] == p.sha((ROOT / RECORD).read_bytes()),
        "changed retained graph execution",
    )
    p.require(
        follow["source_bindings"]
        == {name: current[name] for name in RECONCILIATION_SOURCES}
        and follow["source_inventory_digest"] == p.sha(p.canonical(current)),
        "changed RG2b reconciliation sources",
    )
    # The original graph test bytes are a literal prefix, not rewritten tests.
    test = "tests/models/test_grc_v4_rg2b_graph.py"
    prefix = (ROOT / test).read_bytes()[: follow["preserved_graph_test_prefix_bytes"]]
    p.require(
        p.sha(prefix) == record["source_bindings"][test], "changed reused graph tests"
    )
    audited_prefix = (
        prefix.decode()
        .replace("import os\n", "")
        .replace(
            "    @unittest.skipUnless(\n"
            '        os.environ.get("GRCV4_RUN_SLOW_RG2B") == "1",\n'
            '        "optional slow campaign; set GRCV4_RUN_SLOW_RG2B=1 explicitly",\n'
            "    )\n",
            "",
        )
    )
    audit = follow["independent_audit"]
    p.require(
        p.sha(audited_prefix.encode()) == audit["audited_graph_test_sha256"]
        and all(
            current[name] == digest
            for name, digest in audit["audited_source_bindings"].items()
        ),
        "changed reviewed RG2b numerical subject",
    )
    _, ids = pc.suite(RECONCILIATION_TESTS)
    run = follow["result"]
    p.require(
        run["executed_ids"] == ids
        and run["tests_run"] == len(ids) == 3
        and run["failures"] == run["errors"] == run["skips"] == 0,
        "changed reconciliation roster/result",
    )
    p.require(
        follow["status"] == "reviewed_verified_pending_user_acceptance"
        and follow["iteration_ids"] == ["P9-6.4a", "P9-6.4b", "P9-6.4c", "P9-6.4d"]
        and set(follow["children"]) == {"A_RG2b", "C_RG2b"}
        and all(
            row["scientific_verdict"] == "PASS" for row in follow["children"].values()
        )
        and follow["reconciliation"]["scientific_verdict"] == "PASS"
        and follow["runtime_corrections"] == follow["open_leaf_blockers"] == []
        and follow["user_accepted"] is False
        and follow["RG2b_G2_accepted"] is False
        and follow["G3_accepted"] is False,
        "RG2b reconciliation cannot grant acceptance or lifecycle support",
    )


def check():
    record = p.read(ROOT / RECORD)
    p.require(
        record["record_digest"] == p.digest_record(record), "changed graph RG2b record"
    )
    follow_path = ROOT / FOLLOWUP
    follow = p.read(follow_path) if follow_path.exists() else None
    if follow:
        check_reconciliation(follow, record)
    p.require(
        record["source_bindings"]
        == (
            original.historical_sources(
                record,
                follow,
                {"prior_source_delta": follow["acceptance"]["source_maintenance"]}
                if follow.get("acceptance")
                else None,
            )
            if follow
            else sources()
        ),
        "changed graph RG2b sources",
    )
    p.require(
        record["source_contracts"] == original.source_contracts(),
        "changed graph RG2b source contracts",
    )
    _, ids = pc.suite(TESTS)
    run = record["result"]
    if follow:
        _, added = pc.suite(RECONCILIATION_TESTS)
        p.require(
            set(ids) == set(run["roster_ids"]) | set(added)
            and not set(run["roster_ids"]) & set(added),
            "changed inherited RG2b roster",
        )
        ids = run["roster_ids"]
    p.require(
        run["roster_ids"] == ids
        and run["executed_ids"]
        == [name for name in ids if name not in run["skipped_ids"]]
        and run["tests_run"] == len(ids)
        and run["failures"] == run["errors"] == 0
        and run["skipped_ids"] in ([], [OPTIONAL])
        and run["skips"] == len(run["skipped_ids"])
        and run["passed"] == len(ids) - run["skips"],
        "changed graph RG2b execution",
    )
    p.require(
        record["iteration_ids"] == ["P9-6.4a", "P9-6.4b", "P9-6.4c"]
        and record["P9_6_4d"] == "pending_unexecuted"
        and record["user_accepted"] is False
        and record["RG2b_G2_accepted"] is False
        and record["G3_accepted"] is False,
        "RG2b implementation cannot grant audit/acceptance/support",
    )
    prior = original.check()
    p.current_boundary(ROOT)
    return dict(
        status="passed",
        methods=len(ids),
        passed=run["passed"],
        optional_skipped=run["skips"],
        scientific_tests_rerun=0,
        P9_6_4d=(
            "accepted_by_user"
            if follow.get("acceptance")
            else "PASS_pending_user_acceptance"
        )
        if follow
        else "pending_unexecuted",
        reconciliation_methods=follow["result"]["tests_run"] if follow else 0,
        user_accepted=bool(follow and follow.get("acceptance")),
        historical=prior,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--capture-reconciliation", action="store_true")
    args = parser.parse_args()
    if args.capture:
        capture()
    elif args.capture_reconciliation:
        capture_reconciliation()
    else:
        print(json.dumps(check()))
