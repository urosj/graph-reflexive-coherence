"""One CI batch capture/check with separate a/b results and shared evidence."""

import argparse
import ast
from datetime import datetime, timezone
import importlib.metadata
import importlib.util
import io
import json
import platform
import sys
import time
import unittest

import phase9_implementation_policy as p
from verify_p951_initialization import leaves

ROOT = p.ROOT
SCRIPT = p.HERE + "verify_p961_ci.py"
RECORD = p.PHASE + "tranche-6/P9-6.1ab-ExecutionRecord.json"
FOLLOWUP = p.PHASE + "tranche-6/P9-6.1ab-AuditFollowup.json"
AUDIT = p.PHASE + "tranche-6/P9-6.1ab-AuditReproducer.py"
PRESSURE = p.PHASE + "tranche-6/P9-6.1ab-AuditPressure.json"
REVIEW = p.PHASE + "tranche-6/P9-6.1ab-Review.md"
BASE = "c55960b"
CHILD_COMMIT = "6d3c0b2"
RECONCILIATION_COMMIT = "d1ab4bb"
RECONCILIATION = p.PHASE + "tranche-6/P9-6.1c-ExecutionRecord.json"
RECONCILIATION_REVIEW = p.PHASE + "tranche-6/P9-6.1c-Review.md"
RECONCILIATION_TESTS = ["tests.models.test_grc_v4_ci.CIReconciliationTests"]
TESTS = ["tests.models.test_grc_v4_ci"]
REGRESSIONS = [
    "tests.models.test_grc_v4_candidate_a",
    "tests.models.test_grc_v4_candidate_c.CandidateCCurrentTests",
    "tests.models.test_grc_v4_realizations.CandidateCOSPassTests",
    "tests.models.test_grc_v4_realizations.CandidateCOSStepTests",
    "tests.models.test_grc_v4_realizations.CandidateAOSIntegrationTests",
]
SMOKE = [
    "tests.models.test_grc_v4_candidate_a.CandidateACurrentWriterTests.test_writer_rejects_wrong_current_stage_operation_and_duration",
    "tests.models.test_grc_v4_candidate_a.CandidateACurrentWriterTests.test_writer_preserves_subnormal_below_floor_history_and_checks_policy",
    "tests.models.test_grc_v4_realizations.CandidateAOSIntegrationTests.test_zero_duration_admits_current_and_reset_without_advancement",
    "tests.models.test_grc_v4_realizations.CandidateCOSStepTests.test_zero_duration_admits_current_and_reset_without_pass_or_writer",
]
CONTRACTS = (
    "D10.2-EC-CI-A-ROOT",
    "D10.2-EC-CI-A-CONTRACTION",
    "D10.2-EC-CI-C-ROOT",
    "D10.2-EC-CI-C-CONTRACTION",
    "D10.2-EC-CI-C-ROOT-SELECTION",
    "D11-C-EC-C-J0-REALIZATION-COVERAGE",
)
RUNTIME = {
    "src/pygrc/models/grc_v4_candidate_a.py",
    "src/pygrc/models/grc_v4_candidate_c.py",
    "src/pygrc/models/grc_v4_ci.py",
    "tests/models/test_grc_v4_ci.py",
}
sys.path.insert(0, str(ROOT))


def source_contracts():
    side = ROOT / p.SIDE
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.abundance import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance

    context = load_current_forensic_context(ROOT, side)
    results = []
    for name in CONTRACTS:
        trace = contract_provenance(context, name)
        p.require(trace["row_count"] == 1, "missing CI source contract: " + name)
        row = trace["rows"][0]
        p.require(
            row["classification"] == "source_exact_contract_provenance",
            "CI source classification changed",
        )
        contract = row["payload"]["contract"]
        results.append(
            {
                "contract_id": name,
                "classification": row["classification"],
                "trace_digest": p.sha(p.canonical(trace)),
                "source_record_id": contract["source_record_id"],
                "source_json_pointer": contract["source_json_pointer"],
            }
        )
    return results


def source_bytes(name, subject=None):
    return (
        (ROOT / name).read_bytes()
        if subject is None
        else p.git(ROOT, "show", subject + ":" + name)
    )


def sources(subject=None):
    # Whole local model/test inputs are cheap to identify and avoid losing a
    # lazily imported oracle. Git supplies their bytes; no archive is created.
    paths = {
        "uv.lock",
        "pyproject.toml",
        SCRIPT,
        p.HERE + "verify_p951_initialization.py",
        "specs/grc-v4-spec.md",
        "specs/grc-v4-conformance-vectors.json",
        p.INV + "drafts/2026-09-GRC-V4.md",
        p.INV + "drafts/GRCV4-proposal.md",
    }
    if subject is None:
        for folder in ("src/pygrc/models", "tests/models"):
            paths.update(path.relative_to(ROOT).as_posix()
                         for path in (ROOT / folder).rglob("*.py"))
        paths.update(path.relative_to(ROOT).as_posix()
                     for path in (ROOT / "src/pygrc/models/grc_v4_assets").iterdir()
                     if path.is_file())
    else:
        # Enumerate the historical tree itself. A new successor file must not
        # become a purported dependency of an earlier scientific execution.
        paths.update(name for name in p.git(ROOT, "ls-tree", "-r", "--name-only",
                     subject, "--", "src/pygrc/models", "tests/models").decode().splitlines()
                     if name.endswith(".py") or name.startswith("src/pygrc/models/grc_v4_assets/"))
    return {name: p.sha(source_bytes(name, subject)) for name in sorted(paths)}


def capture():
    p.require(not (ROOT / RECORD).exists(), "preserve the retained batch execution")
    suite = unittest.defaultTestLoader.loadTestsFromNames(TESTS)
    ids = [test.id() for test in leaves(suite)]
    p.require(len(ids) == 30 and len(set(ids)) == len(ids), "incomplete CI roster")
    before, contracts = sources(), source_contracts()
    stream = io.StringIO()
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    elapsed = round(time.monotonic() - start, 3)
    print(stream.getvalue(), end="")
    p.require(
        result.wasSuccessful()
        and result.testsRun == len(ids)
        and not result.skipped
        and not result.expectedFailures,
        "CI campaign did not pass every method",
    )
    p.require(before == sources(), "source drift during CI execution")
    common = [
        name for name in ids if ".CISharedTests." in name or ".CIStepTests." in name
    ]
    children = {
        child: {
            "profile": candidate + "_CI",
            "implementation_result": "passed",
            "review_disposition": "pending_combined_review",
            "candidate_test_ids": [
                name for name in ids if ".Candidate" + candidate + "CITests." in name
            ],
            "shared_result_ref": "#/shared_test_ids",
        }
        for child, candidate in (("P9-6.1a", "C"), ("P9-6.1b", "A"))
    }
    regression_ids = [
        test.id()
        for test in leaves(unittest.defaultTestLoader.loadTestsFromNames(REGRESSIONS))
    ]
    p.require(len(regression_ids) == 112, "changed recorded regression roster")
    value = {
        "schema": "phase9_controlled_batch_execution_v1",
        "iteration_ids": ["P9-6.1a", "P9-6.1b"],
        "status": "implemented_verified_pending_combined_review",
        "source_git_base": p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        "release_id": p.current_abundance_release(ROOT),
        "authority": "User approved a/b implementation as one batch on the new Tranche 6 branch after c55960b, followed by combined review with separate verdicts, then c reconciliation.",
        "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "command": [".venv/bin/python", SCRIPT, "--capture"],
        "reconstruction_command": [".venv/bin/python", "-m", "unittest", "-v", *TESTS],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "jsonschema", "rfc8785")
            },
        },
        "source_bindings": before,
        "source_contracts": contracts,
        "result": {
            "tests_run": result.testsRun,
            "failures": 0,
            "errors": 0,
            "skips": 0,
            "executed_ids": ids,
            "output_sha256": p.sha(stream.getvalue().encode()),
        },
        "children": children,
        "shared_test_ids": common,
        "affected_regression": {
            "status": "passed",
            "tests_run": 112,
            "elapsed_seconds": 312.156,
            "command": [".venv/bin/python", "-m", "unittest", "-v", *REGRESSIONS],
            "executed_ids": regression_ids,
            "recording": "Executed once immediately before CI capture, observed from unittest output. Existing candidate/OS sources and tests were unchanged between that run and this capture. This capture does not repeat or relabel that separate run.",
        },
        "reconstruction": "Use Git source matching source_bindings, provision .venv from uv.lock, and run the two reconstruction commands. No external inputs or source archive; output digests and elapsed times are observations, not byte-reproduction promises.",
        "domain_scope": "Declared reference-centred symmetric Frobenius ball, nonempty edge space, certified SPD/current/floor/selector bounds, strict contraction. C covers one whole-ball stratum; arbitrary multi-stratum searches are unsupported.",
        "claim_ceiling": "Provisional local CI roots and numerical transitions only. Both child reviews, c reconciliation, lifecycle authentication, formation, CI G2 and G3 remain pending. Exact accepted C_OS support is unchanged.",
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
    }
    value["record_digest"] = p.digest_record(value)
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")


def audit_sources(subject=None):
    return {
        **sources(subject),
        **{name: p.sha(source_bytes(name, subject)) for name in (AUDIT, PRESSURE)},
    }


def execution_verifier(value, subject=None):
    """Recover the verifier used by the retained run after acceptance maintenance."""
    raw = source_bytes(SCRIPT, subject)
    acceptance = value.get("acceptance")
    if acceptance is not None:
        maintenance = acceptance["verifier_maintenance"]
        p.require(
            p.sha(raw) == maintenance["current_sha256"], "changed acceptance verifier"
        )
        lines = raw.decode().splitlines(keepends=True)
        end = len(lines)
        for span in reversed(maintenance["splices_to_execution"]):
            start, stop = span["start"], span["stop"]
            p.require(0 <= start <= stop <= end, "invalid verifier reconstruction span")
            lines[start:stop] = span["old_lines"]
            end = start
        raw = "".join(lines).encode()
    p.require(
        p.sha(raw) == value["source_bindings"][SCRIPT], "changed execution verifier"
    )
    return raw


def reconstruct_prior(value, subject=None):
    """Reverse changed line spans; retain old bytes only, never a source archive.

    The pre-audit implementation was uncommitted. Git alone cannot recover its
    new module. Hash-checked splices retain the few removed/replaced old lines;
    all unchanged lines and all current source remain repository/Git owned.
    """
    prior = p.read(ROOT / RECORD)
    p.require(
        prior["record_digest"]
        == p.digest_record(prior)
        == value["previous_execution"]["record_digest"],
        "changed pre-audit execution",
    )
    delta = value["prior_source_delta"]
    for name, digest in prior["source_bindings"].items():
        raw = (
            execution_verifier(value, subject)
            if name == SCRIPT and "acceptance" in value
            else source_bytes(name, subject)
        )
        if name in delta:
            entry = delta[name]
            p.require(
                p.sha(raw) == entry["after_sha256"], "changed corrected source: " + name
            )
            lines = raw.decode().splitlines(keepends=True)
            end = len(lines)
            for change in reversed(entry["splices"]):
                start, stop = change["start"], change["stop"]
                p.require(0 <= start <= stop <= end, "invalid reconstruction span")
                lines[start:stop] = change["old_lines"]
                end = start
            raw = "".join(lines).encode()
        p.require(p.sha(raw) == digest, "pre-audit reconstruction mismatch: " + name)
    p.require(set(delta) <= set(prior["source_bindings"]), "foreign source delta")
    for row in p.read(ROOT / PRESSURE)["source_checks"]:
        p.require(
            prior["source_bindings"][row["bound_path"]] == row["sha256"],
            "audit addressed a different source subject",
        )
    return prior


def audit_suite():
    spec = importlib.util.spec_from_file_location(
        "p961_independent_audit", ROOT / AUDIT
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    suite = unittest.TestSuite(
        [
            unittest.defaultTestLoader.loadTestsFromNames(TESTS + SMOKE),
            unittest.defaultTestLoader.loadTestsFromModule(module),
        ]
    )
    # Reconciliation is a separate four-method run; never recount it as a/b.
    return unittest.TestSuite(
        test for test in leaves(suite) if ".CIReconciliationTests." not in test.id()
    )


def preserved_children(subject=None):
    """Verify a/b reuse at the stated subject; successor code is separate."""
    p.git(ROOT, "merge-base", "--is-ancestor", CHILD_COMMIT, "HEAD")
    for name in (RECORD, FOLLOWUP, REVIEW, AUDIT, PRESSURE):
        p.require(
            source_bytes(name) == source_bytes(name, CHILD_COMMIT),
            "changed accepted child evidence: " + name,
        )
    old = sources(CHILD_COMMIT)
    for name, digest in old.items():
        if name not in {SCRIPT, "tests/models/test_grc_v4_ci.py"}:
            p.require(
                p.sha(source_bytes(name, subject)) == digest,
                "changed reused scientific source: " + name,
            )
    name = "tests/models/test_grc_v4_ci.py"
    before, after = (
        ast.parse(source_bytes(name, CHILD_COMMIT)),
        ast.parse(source_bytes(name, subject)),
    )
    # Only the new reconciliation class and its additional interval adapter
    # import are permitted; every existing helper and oracle stays unchanged.
    after.body = [
        node
        for node in after.body
        if not (isinstance(node, ast.ClassDef) and node.name == "CIReconciliationTests")
    ]
    for node in after.body:
        if isinstance(node, ast.ImportFrom) and node.module == "pygrc.models.grc_v4_ci":
            node.names = [alias for alias in node.names if alias.name != "_im"]
    p.require(ast.dump(before) == ast.dump(after), "changed accepted CI oracle or test")
    return old


def capture_audit():
    value = p.read(ROOT / FOLLOWUP)
    p.require(
        value["status"] == "capture_prepared", "preserve completed audit followup"
    )
    prior = reconstruct_prior(value)
    # All existing candidate/OS regression implementations are byte-identical.
    # CI is a new module, not imported by those existing OS execution paths.
    p.require(
        set(value["prior_source_delta"])
        <= {SCRIPT, "src/pygrc/models/grc_v4_ci.py", "tests/models/test_grc_v4_ci.py"},
        "broaden regression selection after another source changes",
    )
    suite = audit_suite()
    ids = [test.id() for test in leaves(suite)]
    p.require(len(ids) == 48 and len(set(ids)) == 48, "incomplete audit roster")
    before, contracts = audit_sources(), source_contracts()
    started = datetime.now(timezone.utc).isoformat()
    stream = io.StringIO()
    start = time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    elapsed = round(time.monotonic() - start, 3)
    print(stream.getvalue(), end="")
    p.require(
        result.wasSuccessful()
        and result.testsRun == len(ids)
        and not result.skipped
        and not result.expectedFailures,
        "audit campaign failed",
    )
    p.require(before == audit_sources(), "source drift during audit execution")
    value.update(
        status="corrected_verified_pending_child_review",
        source_git_base=p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        release_id=p.current_abundance_release(ROOT),
        started_utc=started,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=elapsed,
        command=[".venv/bin/python", SCRIPT, "--capture-audit"],
        reconstruction_commands=[
            [".venv/bin/python", "-m", "unittest", "-v", *TESTS, *SMOKE],
            [".venv/bin/python", AUDIT],
        ],
        reconstruction="Run from repository root with PYTHONPATH=src:. and .venv provisioned from uv.lock. The retained prior_source_delta reconstructs the original source by reversing zero-based line spans in descending order; --check verifies every original hash. Timing and output hashes are observations, not reproduction promises.",
        environment={
            "python": platform.python_version(),
            "platform": platform.platform(),
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "jsonschema", "rfc8785")
            },
        },
        source_bindings=before,
        source_contracts=contracts,
        result={
            "tests_run": result.testsRun,
            "failures": 0,
            "errors": 0,
            "skips": 0,
            "executed_ids": ids,
            "output_sha256": p.sha(stream.getvalue().encode()),
        },
        children={
            leaf: {
                "profile": candidate + "_CI",
                "correction_result": "passed",
                "review_disposition": "pending_review_of_corrections",
                "candidate_test_ids": [
                    name
                    for name in ids
                    if ".Candidate" + candidate + "CITests." in name
                ],
                "shared_result_ref": "#/result/executed_ids",
            }
            for leaf, candidate in (("P9-6.1a", "C"), ("P9-6.1b", "A"))
        },
        affected_regression={
            "fresh_test_ids": SMOKE,
            "prior_112_method_run_reused": RECORD,
            "prior_result": prior["affected_regression"]["status"],
            "reason": "Existing candidate/OS sources unchanged; four writer/zero-duration boundary regressions rerun. The 112-method predecessor run is not recounted as fresh execution.",
        },
        accepted_generic_runtime_support=[],
        admitted_specialization_support_sets=[],
        claim_ceiling="Provisional analytic-residual-certified CI approximations on the declared local ball. Child review/acceptance, P9-6.1c, lifecycle, CI G2 and G3 remain pending.",
    )
    value["record_digest"] = p.digest_record(value)
    (ROOT / FOLLOWUP).write_text(json.dumps(value, indent=2) + "\n")


def check():
    preserved_children(RECONCILIATION_COMMIT)
    follow = p.read(ROOT / FOLLOWUP)
    p.require(
        follow["record_digest"] == p.digest_record(follow), "changed audit record"
    )
    reconstruct_prior(follow, CHILD_COMMIT)
    current_sources = audit_sources(CHILD_COMMIT)
    current_sources[SCRIPT] = p.sha(execution_verifier(follow, CHILD_COMMIT))
    p.require(follow["source_bindings"] == current_sources, "changed audit sources")
    p.require(
        follow["source_contracts"] == source_contracts(),
        "changed audit source authority",
    )
    p.require(
        follow["result"]["executed_ids"]
        == [test.id() for test in leaves(audit_suite())],
        "changed audit roster",
    )
    p.require(
        follow["status"] == "corrected_verified_pending_child_review"
        and all(
            child["review_disposition"] == "pending_review_of_corrections"
            for child in follow["children"].values()
        ),
        "unreviewed CI acceptance",
    )
    accepted = follow.get("acceptance")
    if accepted is not None:
        p.require(
            accepted["status"] == "accepted_by_user"
            and accepted["accepted_iterations"] == ["P9-6.1a", "P9-6.1b"]
            and accepted["child_verdicts"] == {"P9-6.1a": "PASS", "P9-6.1b": "PASS"}
            and accepted["open_leaf_blockers"] == []
            and accepted["new_runtime_iterations_authorized"] == []
            and accepted["P9_6_1c"] == "pending_unexecuted"
            and accepted["CI_G2_accepted"] is False,
            "invalid bounded CI child acceptance",
        )
    p.require(
        follow["accepted_generic_runtime_support"] == []
        and follow["admitted_specialization_support_sets"] == [],
        "audit cannot grant CI support",
    )
    value = p.read(ROOT / RECORD)
    p.require(
        value["record_digest"] == p.digest_record(value), "changed CI execution record"
    )
    p.require(
        value["source_contracts"] == source_contracts(), "changed CI source authority"
    )
    p.require(
        set(value["children"]) == {"P9-6.1a", "P9-6.1b"}, "combined result lost a child"
    )
    p.require(
        value["accepted_generic_runtime_support"] == []
        and value["admitted_specialization_support_sets"] == [],
        "CI execution cannot grant support",
    )
    changed = set(
        p.git(ROOT, "diff", "--name-only", BASE, CHILD_COMMIT, "--", "src", "tests")
        .decode()
        .splitlines()
    )
    p.require(changed == RUNTIME, "CI batch changed unrelated runtime/tests")
    for leaf in range(1, 5):
        for suffix in ("Review.md", "ExecutionRecord.json", "AuditFollowup.json"):
            name = p.PHASE + f"tranche-5/P9-5.{leaf}-" + suffix
            p.require(
                (ROOT / name).read_bytes() == p.git(ROOT, "show", BASE + ":" + name),
                "changed accepted Tranche 5 record",
            )
    boundary = p.current_boundary(ROOT)
    ready, owners = p.leaf_permissions(ROOT)
    p.require(
        {"P9-6.1a", "P9-6.1b"} <= set(ready)
        and "P9-6.1c" in ready
        and "P9-7.1-A_OS" not in ready,
        "CI batch changed dependent permission",
    )
    p.require(
        "P9-6.1a" in owners["src/pygrc/models/grc_v4_candidate_c.py"]
        and "P9-6.1b" in owners["src/pygrc/models/grc_v4_candidate_a.py"],
        "candidate ownership mismatch",
    )
    sys.path.insert(0, str(ROOT / p.SCRIPTS))
    from test_phase9_g1_surfaces import status_only_check, acceptance_status_check

    status_only_check(ROOT)
    acceptance_status_check(ROOT)
    p.require(p.current_boundary(ROOT) == boundary, "publication changed during check")
    return {
        "status": "passed",
        "CI_methods": 40,
        "native_audit_methods": 4,
        "fresh_OS_regression_methods": 4,
        "prior_regression_methods_reused": 112,
        "source_contracts": len(CONTRACTS),
        "permitted_leaves": len(ready),
        "CI_child_reviews": "accepted_by_user" if accepted else "pending",
        "P9_6_1c": "authorized_reconciliation",
        "scientific_tests_rerun": 0,
        "CI_G2_accepted": False,
    }


def reconciliation_sources(subject=None):
    return {
        **audit_sources(subject),
        RECONCILIATION_REVIEW: p.sha(source_bytes(RECONCILIATION_REVIEW, subject)),
    }


def capture_reconciliation():
    p.require(not (ROOT / RECONCILIATION).exists(), "preserve reconciliation execution")
    preserved_children()
    before, contracts = reconciliation_sources(), source_contracts()
    suite = unittest.defaultTestLoader.loadTestsFromNames(RECONCILIATION_TESTS)
    ids = [test.id() for test in leaves(suite)]
    p.require(len(ids) == len(set(ids)) == 4, "incomplete reconciliation pressure")
    stream = io.StringIO()
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    elapsed = round(time.monotonic() - start, 3)
    print(stream.getvalue(), end="")
    p.require(
        result.wasSuccessful()
        and result.testsRun == 4
        and not result.skipped
        and not result.expectedFailures,
        "reconciliation pressure failed",
    )
    p.require(before == reconciliation_sources(), "source drift during reconciliation")
    child = p.read(ROOT / FOLLOWUP)
    value = {
        "schema": "phase9_ci_reconciliation_v1",
        "iteration_id": "P9-6.1c",
        "status": "reviewed_verified_pending_user_acceptance",
        "scientific_verdict": "PASS",
        "open_blockers": [],
        "profiles_reviewed": ["A_CI", "C_CI"],
        "authority": "User requested the remaining shared-contract reconciliation and review of corrected enclosures, reusing the accepted a/b audit and run.",
        "source_git_base": p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        "release_id": p.current_abundance_release(ROOT),
        "review": RECONCILIATION_REVIEW,
        "source_bindings": before,
        "source_contracts": contracts,
        "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "command": [".venv/bin/python", SCRIPT, "--capture-reconciliation"],
        "reconstruction_command": [
            ".venv/bin/python",
            "-m",
            "unittest",
            "-v",
            *RECONCILIATION_TESTS,
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "jsonschema", "rfc8785")
            },
        },
        "fresh_result": {
            "tests_run": 4,
            "failures": 0,
            "errors": 0,
            "skips": 0,
            "executed_ids": ids,
            "output_sha256": p.sha(stream.getvalue().encode()),
        },
        "reused_execution": {
            "path": FOLLOWUP,
            "record_digest": child["record_digest"],
            "git_subject": CHILD_COMMIT,
            "tests_run": 48,
            "rerun": False,
            "verification": "Accepted evidence bytes and numerical sources match Git; pre-existing CI test/helper ASTs are unchanged.",
        },
        "disposition": "The enclosure derivation, operator-coordinate ordering, domain-local theorem and numerical residual contract are consistent. Four added pressure methods expose no new numerical defect. No runtime correction was needed.",
        "claim_ceiling": "Bounded provisional A_CI and C_CI on the declared reference ball; C covers one whole-ball strict-gap stratum. This is not generic profile publication, live lifecycle, a global branch or stability result.",
        "user_accepted": False,
        "CI_G2_accepted": False,
        "G3_accepted": False,
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "reconstruction": "Use the Git/file subject matching source_bindings, provision .venv from uv.lock and run from repository root with PYTHONPATH=src:. The existing verifier checks the two historical a/b subjects through Git and their retained line spans. No source archive or external file is needed. Timings/output hashes are observations, not reproduction promises.",
    }
    value["record_digest"] = p.digest_record(value)
    (ROOT / RECONCILIATION).write_text(json.dumps(value, indent=2) + "\n")


def check_reconciliation():
    value = p.read(ROOT / RECONCILIATION)
    p.require(
        value["record_digest"] == p.digest_record(value),
        "changed reconciliation record",
    )
    p.git(ROOT, "merge-base", "--is-ancestor", RECONCILIATION_COMMIT, "HEAD")
    p.require(source_bytes(RECONCILIATION) == source_bytes(RECONCILIATION, RECONCILIATION_COMMIT),
              "changed accepted reconciliation evidence")
    current_sources = reconciliation_sources(RECONCILIATION_COMMIT)
    accepted = value.get("acceptance")
    if accepted is not None:
        p.require(
            accepted["status"] == "accepted_by_user"
            and accepted["accepted_iterations"] == ["P9-6.1c"]
            and accepted["profiles_reviewed"] == ["A_CI", "C_CI"]
            and accepted["open_leaf_blockers"] == []
            and accepted["new_runtime_iterations_authorized"] == []
            and accepted["CI_G2_accepted"] is False
            and accepted["G3_accepted"] is False,
            "invalid shared CI acceptance",
        )
        maintenance = accepted["source_maintenance"]
        p.require(
            set(maintenance) == {SCRIPT, RECONCILIATION_REVIEW},
            "acceptance cannot change scientific execution sources",
        )
        for name, entry in maintenance.items():
            raw = source_bytes(name, RECONCILIATION_COMMIT)
            p.require(
                p.sha(raw) == entry["current_sha256"],
                "changed acceptance source: " + name,
            )
            lines = raw.decode().splitlines(keepends=True)
            end = len(lines)
            for span in reversed(entry["splices_to_execution"]):
                start, stop = span["start"], span["stop"]
                p.require(
                    0 <= start <= stop <= end, "invalid acceptance reconstruction span"
                )
                lines[start:stop] = span["old_lines"]
                end = start
            current_sources[name] = p.sha("".join(lines).encode())
    p.require(
        value["source_bindings"] == current_sources, "changed reconciliation sources"
    )
    p.require(
        value["source_contracts"] == source_contracts(),
        "changed reconciliation source authority",
    )
    ids = [
        test.id()
        for test in leaves(
            unittest.defaultTestLoader.loadTestsFromNames(RECONCILIATION_TESTS)
        )
    ]
    p.require(
        value["fresh_result"]["executed_ids"] == ids and len(ids) == 4,
        "changed reconciliation roster",
    )
    p.require(
        value["profiles_reviewed"] == ["A_CI", "C_CI"]
        and value["scientific_verdict"] == "PASS"
        and value["open_blockers"] == []
        and value["user_accepted"] is False
        and value["CI_G2_accepted"] is False
        and value["G3_accepted"] is False
        and value["accepted_generic_runtime_support"] == []
        and value["admitted_specialization_support_sets"] == [],
        "invalid reconciliation claim",
    )
    p.require(
        value["reused_execution"]["record_digest"]
        == p.read(ROOT / FOLLOWUP)["record_digest"],
        "changed reused child result",
    )
    result = check()
    result.update(
        P9_6_1c="accepted_by_user"
        if accepted
        else "reviewed_verified_pending_user_acceptance",
        reconciliation_verdict="PASS",
        fresh_reconciliation_methods=4,
        reused_child_methods=48,
        scientific_tests_rerun=0,
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true")
    group.add_argument("--capture-audit", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--capture-reconciliation", action="store_true")
    group.add_argument("--check-reconciliation", action="store_true")
    args = parser.parse_args()
    if args.capture_reconciliation:
        capture_reconciliation()
    elif args.check_reconciliation:
        print(json.dumps(check_reconciliation()))
    elif args.capture_audit:
        capture_audit()
    elif args.capture:
        capture()
    else:
        print(json.dumps(check()))
