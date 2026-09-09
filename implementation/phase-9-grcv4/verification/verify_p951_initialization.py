#!/usr/bin/env python3
"""Capture bounded A initialization tests, or check evidence and entry surfaces."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
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

ROOT = p.ROOT
sys.path.insert(0, str(ROOT))
PRIOR_RECORD = p.PHASE + "tranche-5/P9-5.1-ExecutionRecord.json"
RECORD = p.PHASE + "tranche-5/P9-5.1-AuditFollowup.json"
TESTS = [
    "tests.models.test_grc_v4_candidate_a",
    "tests.models.test_grc_v4_transport.MobilityTests",
]
RUNTIME = {
    "src/pygrc/models/grc_v4_candidate_a.py",
    "tests/models/test_grc_v4_candidate_a.py",
}


def leaves(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from leaves(item)
        else:
            yield item


def source_bindings():
    paths = {
        "uv.lock",
        "pyproject.toml",
        "specs/grc-v4-conformance-vectors.json",
        p.HERE + "verify_p951_initialization.py",
    }
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            try:
                name = Path(filename).resolve().relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if name.startswith(("src/", "tests/")) and name.endswith(".py"):
                paths.add(name)
    paths.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "src/pygrc/models/grc_v4_assets").iterdir()
        if path.is_file()
    )
    return {name: p.sha((ROOT / name).read_bytes()) for name in sorted(paths)}


def capture():
    p.require(
        not (ROOT / RECORD).exists(),
        "preserve published execution; use a separate follow-up capture",
    )
    suite = unittest.defaultTestLoader.loadTestsFromNames(TESTS)
    ids = [test.id() for test in leaves(suite)]
    p.require(
        len(ids) == len(set(ids)) and len(ids) >= 21, "invalid bounded test roster"
    )
    sources = source_bindings()
    # Numerical validation loads some optional V4 modules lazily. Snapshot
    # candidate source bytes before execution, then retain only the modules
    # actually used. A late import is not source drift; a changed byte is.
    before = dict(sources)
    for directory in ("src", "tests"):
        before.update(
            {
                path.relative_to(ROOT).as_posix(): p.sha(path.read_bytes())
                for path in (ROOT / directory).rglob("*.py")
            }
        )
    start = time.monotonic()
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    print(output.getvalue(), end="")
    p.require(
        result.wasSuccessful()
        and result.testsRun == len(ids)
        and not result.skipped
        and not result.expectedFailures,
        "A initialization campaign did not execute every assertion successfully",
    )
    sources = source_bindings()
    p.require(
        all(before.get(name) == digest for name, digest in sources.items()),
        "scientific execution sources changed",
    )
    record = {
        "schema": "phase9_leaf_execution_record_v1",
        "iteration_id": "P9-5.1",
        "status": "audit_corrections_verified_pending_user_acceptance",
        "previous_execution": {
            "path": PRIOR_RECORD,
            "record_digest": p.read(ROOT / PRIOR_RECORD)["record_digest"],
            "scope": "Original 38-method execution remains historical; this is a fresh run including audit regressions.",
        },
        "release_id": p.ABUNDANCE_RELEASE_ID,
        "authority": {
            "request": "ok, let's implement p9-5.1",
            "base_commit": p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
            "accepted_entry_gate": "P9-G2[C_OS]",
            "acceptance_path": p.G2_ACCEPTANCE,
        },
        "command": [
            ".venv/bin/python",
            p.HERE + "verify_p951_initialization.py",
            "--capture",
        ],
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ["numpy", "jsonschema", "rfc8785"]
            },
        },
        "source_bindings": sources,
        "runtime_result": {
            "tests_run": result.testsRun,
            "failures": 0,
            "errors": 0,
            "skips": 0,
            "expected_failures": 0,
            "executed_ids": ids,
            "stdout_sha256": p.sha(output.getvalue().encode()),
        },
        "reconstruction": "Use the repository version whose files match source_bindings, provision its root .venv from uv.lock, then run .venv/bin/python -m unittest -v "
        + " ".join(TESTS)
        + ". Source is retained in Git; no machine-local inputs or source archive are needed. Timings and output digests are observations, not byte-reproduction promises.",
        "current_read_only_check": [
            ".venv/bin/python",
            p.HERE + "verify_p951_initialization.py",
            "--check",
        ],
        "claim_ceiling": "Fresh declared target-reference G_W construction and positive retained A mobility only. This is not native formation, source-history preservation, a solved A current, whole-target lifecycle admission, or A_OS G2 acceptance. A target reference flux is an explicit operand, not a fabricated seed or authenticated solver result.",
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "G2_accepted": False,
        "existing_C_OS_G2": "unchanged exact singleton; no new support is granted by this leaf",
    }
    record["record_digest"] = p.digest_record(record)
    (ROOT / RECORD).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / RECORD).write_text(json.dumps(record, indent=2) + "\n")
    print("P951_INITIALIZATION_CAPTURE_PASS tests=" + str(result.testsRun))


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
        [t.id() for t in leaves(suite)] == record["runtime_result"]["executed_ids"],
        "changed test roster",
    )
    boundary = p.current_boundary(ROOT)
    ready, owners = p.leaf_permissions(ROOT)
    p.require(
        len(ready) == 31
        and "P9-5.1" in ready
        and "P9-5.2" not in ready
        and all("P9-5.1" in owners[name] for name in RUNTIME),
        "wrong A entry scope",
    )
    approval = p.acceptance(ROOT)
    work = p.read(ROOT / p.WORK)
    original_read = p.read
    controls = []
    for label, path, leaf, reason in [
        (
            "future_A_leaf",
            "src/pygrc/models/grc_v4_candidate_a.py",
            "P9-5.2",
            "entry dependencies",
        ),
        (
            "A_leaf_cannot_own_C",
            "src/pygrc/models/grc_v4_candidate_c.py",
            "P9-5.1",
            "different owning leaf",
        ),
    ]:
        forged = deepcopy(work)
        next(r for r in forged["entries"] if r["path"] == path)["iteration_id"] = leaf
        forged["record_digest"] = p.digest_record(forged)
        with patch.object(
            p,
            "read",
            side_effect=lambda target: (
                forged if Path(target) == ROOT / p.WORK else original_read(target)
            ),
        ):
            try:
                p.work_entries(ROOT, approval)
            except ValueError as exc:
                p.require(
                    reason in str(exc),
                    "entry pressure failed at another guard: " + str(exc),
                )
            else:
                raise ValueError("invalid entry mutation passed")
        controls.append(label)
    with patch.object(
        p, "accepted_g2", side_effect=ValueError("missing accepted C_OS G2")
    ):
        try:
            p.leaf_permissions(ROOT)
        except ValueError as exc:
            p.require(str(exc) == "missing accepted C_OS G2", "wrong missing-G2 guard")
        else:
            raise ValueError("A entry ignored its G2 dependency")
    controls.append("missing_G2_dependency")
    import verify_p948b_review as review

    reuse = review.capture_reuse()
    p.require(
        set(reuse["additional_candidate_A_sources_not_used_for_C_OS_credit"])
        == RUNTIME,
        "A implementation credited to old C_OS capture",
    )
    changed = review.fixtures.source_hashes()
    changed["src/pygrc/models/grc_v4_lifecycle.py"] = "0" * 64
    try:
        review.capture_reuse(changed)
    except ValueError as exc:
        p.require("reused source changed" in str(exc), "wrong scientific reuse guard")
    else:
        raise ValueError("A entry waived C_OS scientific source drift")
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
    p.require(
        p.current_boundary(ROOT) == boundary, "publication inputs changed during checks"
    )
    return {
        "status": "passed",
        "iteration_id": "P9-5.1",
        "reused_tests": record["runtime_result"]["tests_run"],
        "entry_controls": controls,
        "API_notebook_browser_status": "passed",
        "scientific_tests_rerun": 0,
        "G2_A_OS_accepted": False,
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
