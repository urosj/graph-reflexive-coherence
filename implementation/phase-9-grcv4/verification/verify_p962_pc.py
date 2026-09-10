#!/usr/bin/env python3
"""One reconstructible PC a/b campaign; integrity checks never imply G2."""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import importlib.metadata
import io
import json
import platform
import sys
import time
import unittest

import phase9_implementation_policy as p
import verify_p961_ci as ci
from verify_p951_initialization import leaves

ROOT = p.ROOT
SCRIPT = p.HERE + "verify_p962_pc.py"
REVIEW = p.PHASE + "tranche-6/P9-6.2ab-Review.md"
RECORD = p.PHASE + "tranche-6/P9-6.2ab-ExecutionRecord.json"
FOLLOWUP = p.PHASE + "tranche-6/P9-6.2abc-AuditFollowup.json"
BASE = "d1ab4bb"
ACCEPTED_COMMIT = "affb214"
TESTS = ["tests.models.test_grc_v4_pc"]
REGRESSIONS = [
    "tests.models.test_grc_v4_candidate_a",
    "tests.models.test_grc_v4_ci.CandidateACITests",
    "tests.models.test_grc_v4_ci.CIStepTests",
    "tests.models.test_grc_v4_realizations.CandidateAOSIntegrationTests",
]
CONTRACTS = (
    "D10.2-EC-PARENT-REAL-PC",
    "D10.2-EC-PC-WRITER-COEFFICIENT",
    "D10.2-EC-PC-ZOH-WRITER",
    "D10.2-EC-PC-RELEASE",
    "D10.2-EC-PC-MATCHED-FORCING",
    "D11-C-EC-C-J0-REALIZATION-COVERAGE",
)
sys.path.insert(0, str(ROOT))


def source_contracts():
    side = ROOT / p.SIDE
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.abundance import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance

    context = load_current_forensic_context(ROOT, side)
    result = []
    for name in CONTRACTS:
        trace = contract_provenance(context, name)
        p.require(trace["row_count"] == 1, "missing PC source contract: " + name)
        row = trace["rows"][0]
        p.require(
            row["classification"] == "source_exact_contract_provenance",
            "changed PC contract classification",
        )
        contract = row["payload"]["contract"]
        result.append(
            dict(
                contract_id=name,
                classification=row["classification"],
                source_record_id=contract["source_record_id"],
                source_json_pointer=contract["source_json_pointer"],
                trace_digest=p.sha(p.canonical(trace)),
                blocked_overread=contract["attributes"].get("blocked_overread"),
            )
        )
    return result


def sources(subject=None):
    # Reuse the common model/test/asset/spec/paper/lock source inventory. Git
    # supplies source bytes; no source archive or external input is retained.
    return {
        **ci.sources(subject),
        **{name: p.sha(ci.source_bytes(name, subject)) for name in (SCRIPT, REVIEW)},
    }


def suite(names):
    value = unittest.defaultTestLoader.loadTestsFromNames(names)
    ids = [test.id() for test in leaves(value)]
    p.require(len(ids) == len(set(ids)), "duplicate methods")
    return value, ids


def capture():
    p.require(not (ROOT / RECORD).exists(), "preserve the retained PC execution")
    before, contracts = sources(), source_contracts()
    runs = {}
    for name, names, count in (
        ("pc", TESTS, 32),
        ("affected_regressions", REGRESSIONS, 80),
    ):
        tests, ids = suite(names)
        p.require(len(ids) == count, "changed expected PC campaign roster")
        stream = io.StringIO()
        started = datetime.now(timezone.utc).isoformat()
        start = time.monotonic()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
        elapsed = round(time.monotonic() - start, 3)
        print(stream.getvalue(), end="", flush=True)
        p.require(
            result.wasSuccessful()
            and result.testsRun == count
            and not result.skipped
            and not result.expectedFailures,
            "PC campaign did not pass all methods",
        )
        p.require(before == sources(), "source drift during PC execution")
        runs[name] = dict(
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
    ids = runs["pc"]["executed_ids"]
    value = dict(
        schema="phase9_controlled_batch_execution_v1",
        iteration_ids=["P9-6.2a", "P9-6.2b"],
        status="implemented_verified_pending_combined_review",
        source_git_base=p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        release_id=p.current_abundance_release(ROOT),
        authority="User requested P9-6.2a and P9-6.2b together after accepting P9-6.1c; c and acceptance remain separate.",
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
        results=runs,
        children={
            leaf: dict(
                profile=candidate + "_PC",
                implementation_result="passed",
                review_disposition="pending_combined_review",
                candidate_test_ids=[
                    name
                    for name in ids
                    if ".Candidate" + candidate + "PCTests." in name
                ],
                shared_result_ref="#/shared_test_ids",
            )
            for leaf, candidate in (("P9-6.2a", "C"), ("P9-6.2b", "A"))
        },
        shared_test_ids=[name for name in ids if ".Candidate" not in name],
        reconstruction="Use Git source matching source_bindings; provision .venv from uv.lock and run the two recorded unittest commands from repository root. All inputs are repository-owned. Timings and output hashes are observations, not byte-reproduction promises. --check does not re-execute science.",
        domain_scope="Declared symmetric star-supported Frobenius carrier ball, nonnegative L2 resource ball and A positive weight interval. Uniform analytic source/current/geometry bounds, one whole-ball C selector stratum; actual stored state and final chart admission. Conservative sufficient conditions, not maximal or universal numerical radii.",
        claim_ceiling="Provisional local PC recipes only. Combined child review, c reconciliation, lifecycle authentication, reset/migration operations, formation, PC G2 and G3 remain pending. No matched-forcing contraction certificate or endpoint hysteresis. Public support remains the exact accepted C_OS singleton.",
        PC_G2_accepted=False,
        G3_accepted=False,
        accepted_generic_runtime_support=[],
        admitted_specialization_support_sets=[],
    )
    value["record_digest"] = p.digest_record(value)
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")


def execution_bytes(name, follow, subject=None):
    """Recover reviewed execution bytes after status-only acceptance edits."""
    raw = ci.source_bytes(name, subject)
    accepted = follow.get("acceptance")
    if accepted is None or name not in {SCRIPT, REVIEW}:
        return raw
    entry = accepted["source_maintenance"][name]
    p.require(p.sha(raw) == entry["current_sha256"], "changed acceptance source: " + name)
    lines = raw.decode().splitlines(keepends=True)
    end = len(lines)
    for span in reversed(entry["splices_to_execution"]):
        start, stop = span["start"], span["stop"]
        p.require(0 <= start <= stop <= end, "invalid acceptance reconstruction span")
        lines[start:stop] = span["old_lines"]
        end = start
    raw = "".join(lines).encode()
    p.require(
        p.sha(raw) == follow["source_bindings"][name],
        "changed reviewed execution source: " + name,
    )
    return raw


def reconstruct_prior(follow, subject=None):
    """Restore the original uncommitted subject using minimal old-line spans.

    Scientific execution records stay immutable. All unchanged bytes come
    from Git/current source; only otherwise unrecoverable pre-fix lines remain.
    This is reconstruction, never a second execution of the original campaign.
    """
    value = p.read(ROOT / RECORD)
    p.require(
        value["record_digest"] == p.digest_record(value)
        and value["record_digest"] == follow["original_execution_digest"]
        and p.sha((ROOT / RECORD).read_bytes()) == follow["original_execution_sha256"],
        "changed original PC execution",
    )
    allowed = {
        "src/pygrc/models/grc_v4_pc.py",
        "tests/models/test_grc_v4_pc.py",
        SCRIPT,
        REVIEW,
    }
    delta = follow["prior_source_delta"]
    p.require(
        set(delta) == allowed, "audit broadened the reconstructed scientific delta"
    )
    current = sources(subject)
    p.require(
        set(current) == set(value["source_bindings"]), "changed PC source inventory"
    )
    reconstructed = {}
    for name in value["source_bindings"]:
        raw = execution_bytes(name, follow, subject)
        if name in delta:
            entry = delta[name]
            p.require(
                p.sha(raw) == entry["current_sha256"], "changed audit source: " + name
            )
            lines = raw.decode().splitlines(keepends=True)
            end = len(lines)
            for span in reversed(entry["splices_to_original"]):
                start, stop = span["start"], span["stop"]
                p.require(0 <= start <= stop <= end, "invalid original-source span")
                lines[start:stop] = span["old_lines"]
                end = start
            raw = "".join(lines).encode()
        p.require(
            p.sha(raw) == value["source_bindings"][name],
            "changed original source: " + name,
        )
        reconstructed[name] = raw
    name = "tests/models/test_grc_v4_pc.py"
    before, after = (
        ast.parse(reconstructed[name]),
        ast.parse((ROOT / name).read_bytes()),
    )
    p.require(
        ast.dump(before)
        == ast.dump(ast.Module(body=after.body[: len(before.body)], type_ignores=[])),
        "changed pre-existing PC test or oracle",
    )
    _, all_ids = suite(TESTS)
    old_ids = value["results"]["pc"]["executed_ids"]
    p.require(
        len(old_ids) == 32 and set(old_ids) <= set(all_ids), "lost original PC roster"
    )
    _, regression_ids = suite(REGRESSIONS)
    p.require(
        value["results"]["affected_regressions"]["executed_ids"] == regression_ids
        and len(regression_ids) == 80,
        "changed reused regression roster",
    )
    p.require(
        value["source_contracts"] == source_contracts(), "changed PC source contracts"
    )
    for result in value["results"].values():
        p.require(
            result["failures"] == result["errors"] == result["skips"] == 0,
            "original campaign did not pass",
        )
    p.require(
        value["status"] == "implemented_verified_pending_combined_review"
        and set(value["children"]) == {"P9-6.2a", "P9-6.2b"}
        and value["accepted_generic_runtime_support"] == []
        and value["admitted_specialization_support_sets"] == []
        and value["PC_G2_accepted"] is False
        and value["G3_accepted"] is False,
        "original record changed its historical claim",
    )
    return value


def capture_reconciliation():
    follow = p.read(ROOT / FOLLOWUP)
    p.require(
        follow["status"] == "capture_prepared",
        "preserve completed audit/reconciliation",
    )
    prior = reconstruct_prior(follow)
    before, contracts = sources(), source_contracts()
    tests, ids = suite(TESTS)
    p.require(len(ids) == 48, "incomplete corrected PC roster")
    stream = io.StringIO()
    start_utc, start = datetime.now(timezone.utc).isoformat(), time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
    elapsed = round(time.monotonic() - start, 3)
    print(stream.getvalue(), end="", flush=True)
    p.require(
        result.wasSuccessful()
        and result.testsRun == len(ids)
        and not result.skipped
        and not result.expectedFailures,
        "corrected PC campaign did not pass every method",
    )
    p.require(before == sources(), "source drift during reconciliation")
    follow.update(
        status="reviewed_verified_pending_user_acceptance",
        source_git_base=p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        release_id=p.current_abundance_release(ROOT),
        source_bindings=before,
        source_contracts=contracts,
        command=[".venv/bin/python", SCRIPT, "--capture-reconciliation"],
        environment=dict(
            python=platform.python_version(),
            platform=platform.platform(),
            dependencies={
                n: importlib.metadata.version(n)
                for n in ("numpy", "jsonschema", "rfc8785")
            },
        ),
        result=dict(
            started_utc=start_utc,
            completed_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=elapsed,
            tests_run=len(ids),
            failures=0,
            errors=0,
            skips=0,
            executed_ids=ids,
            output_sha256=p.sha(stream.getvalue().encode()),
            reconstruction_command=[".venv/bin/python", "-m", "unittest", "-v", *TESTS],
        ),
        children={
            leaf: dict(
                profile=candidate + "_PC",
                scientific_verdict="PASS",
                review_status="corrected_and_reviewed_pending_user_acceptance",
                closed_findings=["F1", "selector_failure_provenance"]
                if candidate == "C"
                else ["F1", "F2"],
            )
            for leaf, candidate in (("P9-6.2a", "C"), ("P9-6.2b", "A"))
        },
        reconciliation=dict(
            iteration_id="P9-6.2c",
            profiles_reviewed=["A_PC", "C_PC"],
            scientific_verdict="PASS",
            status="completed_pending_user_acceptance",
            shared_contract_review=REVIEW,
            imported_audit_methods=[n for n in ids if ".PCAuditRegressionTests." in n],
            additional_pressure_methods=[
                n for n in ids if ".PCReconciliationTests." in n
            ],
            no_duplicate_audit_credit=True,
        ),
        reused_affected_regression=dict(
            record=RECORD,
            record_digest=prior["record_digest"],
            tests_run=80,
            new_execution=False,
            reason="A, C, CI, OS and resource runtime, their regression methods and oracles are byte-identical. The only runtime correction is the PC module, which these 80 named regressions do not consume. The original 32 PC methods are rerun in the fresh 48-method campaign.",
        ),
        user_accepted=False,
        open_blockers=[],
        PC_G2_accepted=False,
        G3_accepted=False,
        accepted_generic_runtime_support=[],
        admitted_specialization_support_sets=[],
        claim_ceiling="Provisional A_PC/C_PC numerical recipes and c reconciliation only; no live lifecycle/rollback, topology maps, formation provenance, matched-forcing contraction certificate, endpoint hysteresis, PC G2 or G3. Independent audit reviewed the original subject; post-fix PASS is the implementation/reconciliation review, not a claimed external re-audit.",
        reconstruction="Run the recorded 48-method unittest command from repository root with .venv provisioned from uv.lock. The 80 regressions are historical reuse, not re-execution. --check verifies current sources and restores original source hashes through minimal retained line spans. External isolated-pressure observations are attributed context, not a reproducible repository campaign or installed-dependency validation. No external files or source archive required.",
    )
    follow["record_digest"] = p.digest_record(follow)
    (ROOT / FOLLOWUP).write_text(json.dumps(follow, indent=2) + "\n")


def check():
    follow = p.read(ROOT / FOLLOWUP)
    p.require(
        follow["record_digest"] == p.digest_record(follow),
        "changed reconciliation record",
    )
    p.git(ROOT, "merge-base", "--is-ancestor", ACCEPTED_COMMIT, "HEAD")
    p.require((ROOT / FOLLOWUP).read_bytes() == ci.source_bytes(FOLLOWUP, ACCEPTED_COMMIT),
              "changed accepted PC evidence")
    reconstruct_prior(follow, ACCEPTED_COMMIT)
    current_sources = sources(ACCEPTED_COMMIT)
    accepted = follow.get("acceptance")
    if accepted is not None:
        p.require(
            accepted["status"] == "accepted_by_user"
            and accepted["accepted_iterations"] == ["P9-6.2a", "P9-6.2b", "P9-6.2c"]
            and accepted["profiles_reviewed"] == ["A_PC", "C_PC"]
            and accepted["scientific_verdict"] == "PASS"
            and accepted["open_leaf_blockers"] == []
            and accepted["new_runtime_iterations_authorized"] == []
            and accepted["PC_G2_accepted"] is False
            and accepted["G3_accepted"] is False
            and set(accepted["source_maintenance"]) == {SCRIPT, REVIEW},
            "invalid bounded PC acceptance",
        )
        for name in (SCRIPT, REVIEW):
            current_sources[name] = p.sha(execution_bytes(name, follow, ACCEPTED_COMMIT))
    p.require(follow["source_bindings"] == current_sources, "changed reconciliation sources")
    p.require(
        follow["source_contracts"] == source_contracts(),
        "changed reconciliation contracts",
    )
    _, ids = suite(TESTS)
    result = follow["result"]
    p.require(
        result["executed_ids"] == ids
        and result["tests_run"] == len(ids) == 48
        and result["failures"] == result["errors"] == result["skips"] == 0,
        "changed corrected PC result",
    )
    p.require(
        follow["status"] == "reviewed_verified_pending_user_acceptance"
        and follow["iteration_ids"] == ["P9-6.2a", "P9-6.2b", "P9-6.2c"]
        and set(follow["children"]) == {"P9-6.2a", "P9-6.2b"}
        and all(
            row["scientific_verdict"] == "PASS" for row in follow["children"].values()
        )
        and follow["reconciliation"]["profiles_reviewed"] == ["A_PC", "C_PC"]
        and follow["reconciliation"]["scientific_verdict"] == "PASS"
        and follow["user_accepted"] is False
        and follow["open_blockers"] == []
        and follow["accepted_generic_runtime_support"] == []
        and follow["admitted_specialization_support_sets"] == []
        and follow["PC_G2_accepted"] is False
        and follow["G3_accepted"] is False,
        "audit/reconciliation cannot grant user acceptance or support",
    )
    p.git(ROOT, "merge-base", "--is-ancestor", BASE, "HEAD")
    changed = set(
        p.git(ROOT, "diff", "--name-only", BASE, ACCEPTED_COMMIT, "--", "src", "tests")
        .decode()
        .splitlines()
    )
    p.require(
        changed == {"src/pygrc/models/grc_v4_candidate_a.py", *p.PC_BATCH_PATHS},
        "PC changed unrelated runtime/test owners",
    )
    ready, owners = p.leaf_permissions(ROOT)
    p.require(
        {"P9-6.2a", "P9-6.2b"} <= set(ready)
        and "P9-6.2c" in ready
        and "P9-6.2b" in owners["src/pygrc/models/grc_v4_candidate_a.py"],
        "PC batch changed dependent permission",
    )
    # CI is now historical: verify its exact accepted Git subjects, not today's
    # A source, and do not count the PC regression as its original execution.
    prior = ci.check_reconciliation()
    p.current_boundary(ROOT)
    return dict(
        status="passed",
        PC_methods=48,
        imported_audit_methods=8,
        additional_reconciliation_methods=8,
        affected_regression_methods_reused=80,
        source_contracts=len(CONTRACTS),
        scientific_tests_rerun=0,
        child_reviews="accepted_by_user" if accepted else "PASS_pending_user_acceptance",
        P9_6_2c="accepted_by_user" if accepted else "PASS_pending_user_acceptance",
        prior_CI_reconciliation=prior["P9_6_1c"],
        PC_G2_accepted=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--capture-reconciliation", action="store_true")
    args = parser.parse_args()
    if args.capture_reconciliation:
        capture_reconciliation()
    elif args.capture:
        capture()
    else:
        print(json.dumps(check()))
