#!/usr/bin/env python3
"""CI+PC execution and c reconciliation; reuse unchanged scientific campaigns."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import io
import json
import platform
import time
import unittest

import phase9_implementation_policy as p
import verify_p961_ci as ci
import verify_p962_pc as pc

ROOT = p.ROOT
BASE = "affb214"
ACCEPTED_COMMIT = "ba45482"
SCRIPT = p.HERE + "verify_p963_cipc.py"
REVIEW = p.PHASE + "tranche-6/P9-6.3ab-Review.md"
RECORD = p.PHASE + "tranche-6/P9-6.3ab-ExecutionRecord.json"
FOLLOWUP = p.PHASE + "tranche-6/P9-6.3abc-AuditFollowup.json"
TESTS = ["tests.models.test_grc_v4_cipc"]
RECONCILIATION_TESTS = [
    TESTS[0] + ".CIPCAdditionalAuditPressure",
    TESTS[0] + ".CIPCReconciliationTests",
]
REGRESSIONS = [
    "tests.models.test_grc_v4_ci",
    "tests.models.test_grc_v4_pc",
    "tests.models.test_grc_v4_candidate_a.CandidateACurrentWriterTests",
    "tests.models.test_grc_v4_candidate_c.CandidateCCurrentTests",
]
CONTRACTS = tuple(
    "D10.2-EC-" + suffix
    for suffix in (
        "PARENT-REAL-CI-PC",
        "CI-PC-A-COMPOSITION",
        "CI-PC-A-ROOT",
        "CI-PC-C-COMPOSITION",
        "CI-PC-C-CONTRACTION",
        "CI-PC-C-ROOT-SELECTION",
        "CI-PC-ABLATIONS",
    )
)
RUNTIME = {
    "src/pygrc/models/grc_v4_ci.py",
    "src/pygrc/models/grc_v4_pc.py",
    "src/pygrc/models/grc_v4_candidate_a.py",
    "src/pygrc/models/grc_v4_candidate_c.py",
    "tests/models/test_grc_v4_cipc.py",
}


def sources(subject=None):
    names = {
        SCRIPT,
        REVIEW,
        pc.SCRIPT,
        p.INV
        + "decisions/GeometryTemporalRealizationHybridCoupledPersistentCarrier.md",
        p.INV
        + "decisions/GeometryTemporalRealizationHybridCoupledPersistentCarrier.json",
    }
    return {
        **ci.sources(subject),
        **{name: p.sha(ci.source_bytes(name, subject)) for name in sorted(names)},
    }


def source_contracts():
    # Current typed forensic context; no source search or historical fallback.
    import sys

    sys.path.insert(0, str(ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.abundance import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance

    context = load_current_forensic_context(ROOT, ROOT / p.SIDE)
    rows = []
    for name in CONTRACTS:
        trace = contract_provenance(context, name)
        p.require(trace["row_count"] == 1, "missing composition contract: " + name)
        row = trace["rows"][0]
        p.require(
            row["classification"] == "source_exact_contract_provenance",
            "changed composition authority",
        )
        contract = row["payload"]["contract"]
        rows.append(
            dict(
                contract_id=name,
                classification=row["classification"],
                source_record_id=contract["source_record_id"],
                source_json_pointer=contract["source_json_pointer"],
                trace_digest=p.sha(p.canonical(trace)),
                blocked_overread=contract["attributes"]["blocked_overread"],
            )
        )
    return rows


def capture():
    p.require(not (ROOT / RECORD).exists(), "preserve the retained composition run")
    before, contracts = sources(), source_contracts()
    results = {}
    for name, names, count in (
        ("composition", TESTS, 32),
        ("affected_regressions", REGRESSIONS, 143),
    ):
        tests, ids = pc.suite(names)
        p.require(len(ids) == count, "changed expected composition campaign roster")
        stream = io.StringIO()
        started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
        run = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
        elapsed = round(time.monotonic() - clock, 3)
        print(stream.getvalue(), end="", flush=True)
        p.require(
            run.wasSuccessful()
            and run.testsRun == count
            and not run.skipped
            and not run.expectedFailures,
            "composition campaign did not pass",
        )
        p.require(sources() == before, "source drift during composition execution")
        results[name] = dict(
            started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=elapsed,
            tests_run=count,
            failures=0,
            errors=0,
            skips=0,
            executed_ids=ids,
            output_sha256=p.sha(stream.getvalue().encode()),
            command=[".venv/bin/python", "-m", "unittest", "-v", *names],
        )
    value = dict(
        schema="phase9_controlled_batch_execution_v1",
        iteration_ids=["P9-6.3a", "P9-6.3b"],
        status="implemented_verified_pending_independent_review",
        authority="User requested P9-6.3a and P9-6.3b after accepting and committing P9-6.2. Shared c review, user acceptance and commit remain separate.",
        source_git_base=p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        release_id=p.current_abundance_release(ROOT),
        command=[".venv/bin/python", SCRIPT, "--capture"],
        environment=dict(
            python=platform.python_version(),
            platform=platform.platform(),
            dependencies={
                n: importlib.metadata.version(n)
                for n in ("numpy", "jsonschema", "rfc8785")
            },
        ),
        source_bindings=before,
        source_contracts=contracts,
        results=results,
        children={
            leaf: dict(
                profile=profile,
                implementation_result="passed",
                independent_review="pending",
                user_accepted=False,
            )
            for leaf, profile in (("P9-6.3a", "C_CI_PC"), ("P9-6.3b", "A_CI_PC"))
        },
        reused_predecessor_acceptance=dict(
            CI="d1ab4bb",
            PC=BASE,
            scope="Accepted scientific contracts and historical evidence. Their numerical suites were freshly rerun here against the extended shared runtime; no historical result is relabeled as current execution.",
        ),
        P9_6_3c="pending_unexecuted",
        user_accepted=False,
        composite_G2_accepted=False,
        G3_accepted=False,
        accepted_generic_runtime_support=[],
        admitted_specialization_support_sets=[],
        claim_ceiling="Provisional same-root unit-immediate/unit-retained A_CI_PC and C_CI_PC on the declared compact base chart, reference Hodge ball and carrier ball; one C selector stratum. No live lifecycle, authenticated initializer/formation provenance, topology maps, matched-forcing contraction, endpoint witness, G2/G3 or amplitude equivalence.",
        reconstruction="Provision root .venv from uv.lock and run the recorded commands from repository root with PYTHONPATH=src:. Source lives in Git; no external files or copied source archive. --check verifies current source identities/results and accepted CI/PC Git subjects without rerunning scientific tests. Timings and output digests are observations, not reproduction promises.",
    )
    value["record_digest"] = p.digest_record(value)
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")


def execution_bytes(name, follow, subject=None):
    """Recover the reviewed bytes after acceptance-only source maintenance."""
    raw = ci.source_bytes(name, subject)
    accepted = follow.get("acceptance")
    if accepted is None or name not in {SCRIPT, REVIEW}:
        return raw
    entry = accepted["source_maintenance"][name]
    p.require(p.sha(raw) == entry["current_sha256"], "changed acceptance source")
    lines = raw.decode().splitlines(keepends=True)
    end = len(lines)
    for span in reversed(entry["splices_to_execution"]):
        start, stop = span["start"], span["stop"]
        p.require(0 <= start <= stop <= end, "invalid acceptance source span")
        lines[start:stop] = span["old_lines"]
        end = start
    raw = "".join(lines).encode()
    p.require(
        p.sha(raw) == follow["source_bindings"][name],
        "changed reviewed execution source",
    )
    return raw


def execution_sources(follow, subject=None):
    current = sources(subject)
    for name in (SCRIPT, REVIEW):
        current[name] = p.sha(execution_bytes(name, follow, subject))
    return current


def original_sources(follow, subject=None):
    """Restore only the uncommitted review/runner and appended test prefix.

    Numerical sources and original test/oracle bytes must remain unchanged;
    these spans recover the original campaign, never constitute another run.
    """
    delta = follow["prior_source_delta"]
    test = "tests/models/test_grc_v4_cipc.py"
    p.require(set(delta) == {SCRIPT, REVIEW, test}, "changed reconciliation scope")
    current = execution_sources(follow, subject)
    for name, entry in delta.items():
        raw = execution_bytes(name, follow, subject)
        p.require(current[name] == entry["current_sha256"], "changed audit source")
        lines = raw.decode().splitlines(keepends=True)
        end = len(lines)
        for span in reversed(entry["splices_to_original"]):
            start, stop = span["start"], span["stop"]
            p.require(0 <= start <= stop <= end, "invalid original source span")
            lines[start:stop] = span["old_lines"]
            end = start
        original = "".join(lines).encode()
        if name == test:
            p.require(raw.startswith(original), "changed original test/oracle bytes")
        current[name] = p.sha(original)
    return current


def check_original(follow=None, subject=None):
    value = p.read(ROOT / RECORD)
    p.require(
        value["record_digest"] == p.digest_record(value), "changed composition record"
    )
    p.require(
        value["source_bindings"]
        == (sources(subject) if follow is None else original_sources(follow, subject)),
        "changed composition execution sources",
    )
    p.require(
        value["source_contracts"] == source_contracts(), "changed composition contracts"
    )
    for name, names, count in (
        ("composition", TESTS, 32),
        ("affected_regressions", REGRESSIONS, 143),
    ):
        _, ids = pc.suite(names)
        result = value["results"][name]
        if follow is not None and name == "composition":
            _, added = pc.suite(RECONCILIATION_TESTS)
            p.require(
                set(ids) == set(result["executed_ids"]) | set(added)
                and not set(result["executed_ids"]) & set(added),
                "changed original or additional composition roster",
            )
            ids = result["executed_ids"]
        p.require(
            result["executed_ids"] == ids
            and result["tests_run"] == len(ids) == count
            and result["failures"] == result["errors"] == result["skips"] == 0,
            "changed composition result/roster",
        )
    p.require(
        value["iteration_ids"] == ["P9-6.3a", "P9-6.3b"]
        and value["status"] == "implemented_verified_pending_independent_review"
        and value["P9_6_3c"] == "pending_unexecuted"
        and value["user_accepted"] is False
        and value["accepted_generic_runtime_support"] == []
        and value["admitted_specialization_support_sets"] == []
        and value["composite_G2_accepted"] is False
        and value["G3_accepted"] is False,
        "composition run cannot grant review/acceptance/support",
    )
    p.git(ROOT, "merge-base", "--is-ancestor", BASE, "HEAD")
    changed = set(
        p.git(
            ROOT, "diff", "--name-only", BASE, subject or "HEAD", "--", "src", "tests"
        )
        .decode()
        .splitlines()
    )
    if subject is None:
        changed.update(
            p.git(
                ROOT, "ls-files", "--others", "--exclude-standard", "--", "src", "tests"
            )
            .decode()
            .splitlines()
        )
    p.require(changed == RUNTIME, "composition changed unrelated numerical owners")
    ready, _ = p.leaf_permissions(ROOT)
    p.require(
        {"P9-6.3a", "P9-6.3b"} <= set(ready) and (follow is None or "P9-6.3c" in ready),
        "composition batch changed review authority",
    )
    if follow is not None:
        p.require(
            value["record_digest"] == follow["original_execution_digest"]
            and p.sha((ROOT / RECORD).read_bytes())
            == follow["original_execution_sha256"],
            "changed original composition run bytes",
        )
    return value


def capture_reconciliation():
    follow = p.read(ROOT / FOLLOWUP)
    p.require(
        follow["status"] == "prepared" and "result" not in follow,
        "preserve completed reconciliation",
    )
    prior = check_original(follow)
    before, contracts = sources(), source_contracts()
    tests, ids = pc.suite(RECONCILIATION_TESTS)
    p.require(len(ids) == 8, "changed reconciliation roster")
    stream = io.StringIO()
    started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
    run = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
    elapsed = round(time.monotonic() - clock, 3)
    print(stream.getvalue(), end="", flush=True)
    p.require(
        run.wasSuccessful()
        and run.testsRun == 8
        and not run.skipped
        and not run.expectedFailures,
        "reconciliation pressure did not pass",
    )
    p.require(before == sources(), "source drift during reconciliation")
    follow.update(
        status="reviewed_verified_pending_user_acceptance",
        source_bindings=before,
        source_contracts=contracts,
        environment=dict(
            python=platform.python_version(),
            platform=platform.platform(),
            dependencies={
                n: importlib.metadata.version(n)
                for n in ("numpy", "jsonschema", "rfc8785")
            },
        ),
        result=dict(
            started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=elapsed,
            tests_run=8,
            failures=0,
            errors=0,
            skips=0,
            executed_ids=ids,
            output_sha256=p.sha(stream.getvalue().encode()),
            command=[".venv/bin/python", "-m", "unittest", "-v", *RECONCILIATION_TESTS],
        ),
        reused_execution=dict(
            record=RECORD,
            record_digest=prior["record_digest"],
            composition_methods=32,
            affected_regressions=143,
            new_execution=False,
            reason="All numerical sources, original test/oracle bytes and dependency bindings are unchanged. Only eight methods were appended; the original 175 passes are reused, not rerun.",
        ),
        children={
            leaf: dict(
                profile=profile,
                scientific_verdict="PASS",
                independent_review="PASS_bounded_original_subject",
            )
            for leaf, profile in (("P9-6.3a", "C_CI_PC"), ("P9-6.3b", "A_CI_PC"))
        },
        reconciliation=dict(
            iteration_id="P9-6.3c",
            profiles_reviewed=["A_CI_PC", "C_CI_PC"],
            scientific_verdict="PASS",
            runtime_corrections=[],
            review=REVIEW,
        ),
    )
    follow["record_digest"] = p.digest_record(follow)
    (ROOT / FOLLOWUP).write_text(json.dumps(follow, indent=2) + "\n")


def check():
    follow = p.read(ROOT / FOLLOWUP)
    p.require(follow["record_digest"] == p.digest_record(follow), "changed followup")
    p.git(ROOT, "merge-base", "--is-ancestor", ACCEPTED_COMMIT, "HEAD")
    p.require(
        (ROOT / FOLLOWUP).read_bytes() == ci.source_bytes(FOLLOWUP, ACCEPTED_COMMIT),
        "changed accepted composition evidence",
    )
    check_original(follow, ACCEPTED_COMMIT)
    p.require(
        follow["source_bindings"] == execution_sources(follow, ACCEPTED_COMMIT)
        and follow["source_contracts"] == source_contracts(),
        "changed reconciliation sources/contracts",
    )
    _, ids = pc.suite(RECONCILIATION_TESTS)
    result = follow["result"]
    p.require(
        result["executed_ids"] == ids
        and result["tests_run"] == len(ids) == 8
        and result["failures"] == result["errors"] == result["skips"] == 0,
        "changed reconciliation result",
    )
    p.require(
        follow["status"] == "reviewed_verified_pending_user_acceptance"
        and follow["iteration_ids"] == ["P9-6.3a", "P9-6.3b", "P9-6.3c"]
        and set(follow["children"]) == {"P9-6.3a", "P9-6.3b"}
        and all(
            row["scientific_verdict"] == "PASS" for row in follow["children"].values()
        )
        and follow["reconciliation"]["scientific_verdict"] == "PASS"
        and follow["reconciliation"]["profiles_reviewed"] == ["A_CI_PC", "C_CI_PC"]
        and follow["reconciliation"]["runtime_corrections"] == []
        and follow["user_accepted"] is False
        and follow["open_blockers"] == []
        and follow["composite_G2_accepted"] is False
        and follow["G3_accepted"] is False
        and follow["accepted_generic_runtime_support"] == []
        and follow["admitted_specialization_support_sets"] == [],
        "reconciliation cannot grant user acceptance or support",
    )
    audit = follow["independent_audit"]
    original = p.read(ROOT / RECORD)
    p.require(
        audit["declared_execution_digest"] == original["record_digest"]
        and all(
            original["source_bindings"].get(name) == digest
            for name, digest in audit["audited_source_bindings"].items()
        ),
        "audit subject does not match original composition",
    )
    accepted = follow.get("acceptance")
    if accepted is not None:
        p.require(
            accepted["status"] == "accepted_by_user"
            and accepted["accepted_iterations"] == ["P9-6.3a", "P9-6.3b", "P9-6.3c"]
            and accepted["profiles_reviewed"] == ["A_CI_PC", "C_CI_PC"]
            and accepted["scientific_verdict"] == "PASS"
            and accepted["open_leaf_blockers"] == []
            and accepted["new_runtime_iterations_authorized"] == []
            and accepted["composite_G2_accepted"] is False
            and accepted["G3_accepted"] is False
            and set(accepted["source_maintenance"]) == {SCRIPT, REVIEW},
            "invalid bounded composition acceptance",
        )
    prior = pc.check()
    return dict(
        status="passed",
        reused_composition_methods=32,
        reused_affected_regression_methods=143,
        reconciliation_methods=8,
        scientific_tests_rerun=0,
        children="accepted_by_user" if accepted else "PASS_pending_user_acceptance",
        P9_6_3c="accepted_by_user" if accepted else "PASS_pending_user_acceptance",
        prior_PC=prior["P9_6_2c"],
        composite_G2_accepted=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--capture", action="store_true")
    action.add_argument("--capture-reconciliation", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.capture_reconciliation:
        capture_reconciliation()
    elif args.capture:
        capture()
    else:
        print(json.dumps(check()))
