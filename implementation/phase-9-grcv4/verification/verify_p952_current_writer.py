#!/usr/bin/env python3
"""Capture bounded A current/writer tests or check their current publication."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import decimal
import importlib.metadata
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import verify_p951_initialization as previous

ROOT = p.ROOT
PRIOR_RECORD = p.PHASE + "tranche-5/P9-5.2-ExecutionRecord.json"
RECORD = p.PHASE + "tranche-5/P9-5.2-AuditFollowup.json"
SCRIPT = p.HERE + "verify_p952_current_writer.py"
TESTS = previous.TESTS
AUDIT_INPUTS = [
    p.PHASE + "tranche-5/P9-5.2-" + suffix
    for suffix in ("AuditReproducer.py", "AuditPressure.json")
]


def sources():
    return {
        **previous.source_bindings(),
        **{name: p.sha((ROOT / name).read_bytes()) for name in [SCRIPT, *AUDIT_INPUTS]},
    }


def capture():
    p.require(
        not (ROOT / RECORD).exists(),
        "preserve retained executions; use a new follow-up record",
    )
    suite = unittest.defaultTestLoader.loadTestsFromNames(TESTS)
    ids = [test.id() for test in previous.leaves(suite)]
    p.require(len(ids) == len(set(ids)) and len(ids) >= 65, "incomplete bounded roster")
    before = sources()
    for directory in ("src", "tests"):
        before.update(
            {
                path.relative_to(ROOT).as_posix(): p.sha(path.read_bytes())
                for path in (ROOT / directory).rglob("*.py")
            }
        )
    output = io.StringIO()
    start = time.monotonic()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    print(output.getvalue(), end="")
    p.require(
        result.wasSuccessful()
        and result.testsRun == len(ids)
        and not result.skipped
        and not result.expectedFailures,
        "bounded campaign did not pass every method",
    )
    bindings = sources()
    p.require(
        all(before.get(name) == digest for name, digest in bindings.items()),
        "execution source drift",
    )
    record = {
        "schema": "phase9_leaf_execution_record_v1",
        "iteration_id": "P9-5.2",
        "status": "audit_corrections_verified_pending_user_acceptance",
        "previous_execution": {
            "path": PRIOR_RECORD,
            "record_digest": p.read(ROOT / PRIOR_RECORD)["record_digest"],
            "scope": "Original 61-method execution remains historical; this fresh run includes the audit regressions.",
        },
        "release_id": p.ABUNDANCE_RELEASE_ID,
        "source_git_base": p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        "authority": "User requested P9-5.2 after accepting and committing P9-5.1 at c920376.",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "command": [".venv/bin/python", SCRIPT, "--capture"],
        "reconstruction_command": [".venv/bin/python", "-m", "unittest", "-v", *TESTS],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "libmpdec": decimal.__libmpdec_version__,
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "jsonschema", "rfc8785")
            },
        },
        "source_bindings": bindings,
        "runtime_result": {
            "tests_run": result.testsRun,
            "failures": 0,
            "errors": 0,
            "skips": 0,
            "expected_failures": 0,
            "executed_ids": ids,
            "output_sha256": p.sha(output.getvalue().encode()),
        },
        "reconstruction": "Use the Git revision matching source_bindings, provision root .venv from uv.lock and run reconstruction_command. No external inputs or source archive. Time and output digests are observations, not byte-reproduction promises.",
        "claim_ceiling": "Fixed-geometry A_OS current, typed Read-Back, structural source and provisional post-continuity log writer. No complete A_OS pass, lifecycle commit/readmission, authenticated initializer reference-current origin, native formation, A_OS G2 or G3 acceptance.",
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "G2_accepted": False,
        "existing_exact_C_OS_G2": "unchanged",
    }
    record["record_digest"] = p.digest_record(record)
    (ROOT / RECORD).write_text(json.dumps(record, indent=2) + "\n")
    print("P952_CURRENT_WRITER_CAPTURE_PASS tests=" + str(result.testsRun))


def check():
    record = p.read(ROOT / RECORD)
    p.require(
        record["record_digest"] == p.digest_record(record), "changed execution record"
    )
    prior = p.read(ROOT / PRIOR_RECORD)
    p.require(
        prior["record_digest"]
        == p.digest_record(prior)
        == record["previous_execution"]["record_digest"],
        "changed historical execution record",
    )
    for name, digest in record["source_bindings"].items():
        p.require(
            p.sha(p.safe_path(ROOT, name).read_bytes()) == digest,
            "changed scientific source: " + name,
        )
    suite = unittest.defaultTestLoader.loadTestsFromNames(TESTS)
    p.require(
        [t.id() for t in previous.leaves(suite)]
        == record["runtime_result"]["executed_ids"],
        "changed roster",
    )
    boundary = p.current_boundary(ROOT)
    ready, owners = p.leaf_permissions(ROOT)
    p.require(
        len(ready) == 32
        and "P9-5.2" in ready
        and "P9-5.3" not in ready
        and all("P9-5.2" in owners[name] for name in previous.RUNTIME),
        "wrong P9-5.2 entry",
    )
    controls = []
    work = p.read(ROOT / p.WORK)
    original_read = p.read
    for label, source, leaf, reason in (
        (
            "future_A_leaf",
            "src/pygrc/models/grc_v4_candidate_a.py",
            "P9-5.3",
            "entry dependencies",
        ),
        (
            "A_leaf_cannot_own_C",
            "src/pygrc/models/grc_v4_candidate_c.py",
            "P9-5.2",
            "different owning leaf",
        ),
    ):
        forged = deepcopy(work)
        next(row for row in forged["entries"] if row["path"] == source)[
            "iteration_id"
        ] = leaf
        forged["record_digest"] = p.digest_record(forged)
        with patch.object(
            p,
            "read",
            side_effect=lambda path: (
                forged if Path(path) == ROOT / p.WORK else original_read(path)
            ),
        ):
            try:
                p.work_entries(ROOT, p.acceptance(ROOT))
            except ValueError as exc:
                p.require(reason in str(exc), "wrong entry rejection: " + str(exc))
            else:
                raise ValueError("invalid entry mutation admitted")
        controls.append(label)
    with patch.object(
        p,
        "accepted_a_initialization",
        side_effect=ValueError("missing accepted P9-5.1"),
    ):
        try:
            p.leaf_permissions(ROOT)
        except ValueError as exc:
            p.require(str(exc) == "missing accepted P9-5.1", "wrong dependency guard")
        else:
            raise ValueError("ignored accepted initializer dependency")
    controls.append("missing_P9_5_1_dependency")
    import verify_p948b_review as review

    reuse = review.capture_reuse()
    p.require(
        set(reuse["additional_candidate_A_sources_not_used_for_C_OS_credit"])
        == previous.RUNTIME,
        "A work credited to C_OS",
    )
    changed = review.fixtures.source_hashes()
    changed["src/pygrc/models/grc_v4_candidate_c.py"] = "0" * 64
    try:
        review.capture_reuse(changed)
    except ValueError as exc:
        p.require("reused source changed" in str(exc), "wrong C scientific guard")
    else:
        raise ValueError("waived C source drift")
    controls.append("changed_C_OS_source")
    sys.path.insert(0, str(ROOT / p.SCRIPTS))
    from test_phase9_g1_surfaces import acceptance_status_check, status_only_check

    status_only_check(ROOT)
    acceptance_status_check(ROOT)
    notebook = subprocess.run(
        [
            sys.executable,
            str(ROOT / p.SCRIPTS / "run_phase9_notebook.py"),
            "--status-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    p.require(notebook.returncode == 0, notebook.stdout + notebook.stderr)
    p.require(p.current_boundary(ROOT) == boundary, "publication changed during checks")
    return {
        "status": "passed",
        "iteration_id": "P9-5.2",
        "reused_tests": record["runtime_result"]["tests_run"],
        "entry_controls": controls,
        "API_notebook_browser_status": "passed",
        "scientific_tests_rerun": 0,
        "A_OS_G2_accepted": False,
        "G3_accepted": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.capture:
        capture()
    else:
        print(json.dumps(check()))
