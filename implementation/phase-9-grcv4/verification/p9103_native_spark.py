"""Focused native completion integration; retained checks never execute tests."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import platform
import subprocess
import time
import unittest

import p991a7_support as support

ROOT = support.ROOT
BASE = "implementation/phase-9-grcv4/"
SELF = BASE + "verification/p9103_native_spark.py"
TEST = BASE + "verification/test_p9103_native_spark_integration.py"
PATH = BASE + "tranche-10/P9-10.3-NativeSpark-Regressions.json"
ENTRY = "f41346da"
GROUPS = {
    "discovery_and_identities": (
        "tests.models.test_grc_9_v4_spark_support.NativeSparkSupportTests",
        "tests.models.test_grc_9_v4_contracts.PublicContractTests",
    ),
    "all_ten_persistence_and_branch_guards": (
        "test_p9103_native_spark_integration.NativeSparkIntegrationTests",
    ),
    "shared_completion_lifecycle": tuple(
        "tests.models.test_grc_9_v4_spark_completion.NativeSparkCompletionTests." + name
        for name in (
            "test_lawful_source_event_preserves_both_exact_roles",
            "test_wrong_role_pair_and_forced_requests_cannot_advance",
            "test_two_positive_beats_after_entry_and_atomic_child",
            "test_concurrent_duplicate_completion_is_one_atomic_claim",
            "test_late_failure_rolls_back_state_window_consumption_and_children",
            "test_zero_inspection_failure_reset_rebase_and_policy_replacement",
            "test_save_load_replay_and_stale_import_reconcile_occurrence",
            "test_cold_checkpoint_replay_actual_source_and_event",
        )
    ),
    "ordinary_v4_and_legacy_boundaries": (
        "tests.models.test_grc_9_v4_architecture.ArchitectureTests.test_execution_selection_is_independent",
        "tests.models.test_grc_9_v4_architecture.ArchitectureTests.test_all_ten_dispatch_preserves_closed_scientific_handlers",
        "tests.models.test_grc_9_v4.BoundaryPublic.test_publication_failure_and_typed_boundaries",
        "tests.models.test_grc_9_v4.COSPublic.test_public_branch_migrations_and_exact_disabled_projection",
        "tests.models.test_grc_9_v4_legacy.DelegateBoundaryTests",
    ),
}
need, seal = support.need, support.seal


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def ref(name):
    return {"path": name, "sha256": sha256((ROOT / name).read_bytes()).hexdigest()}


def inputs():
    """Pin unchanged numerical/runtime/test inputs and the new bounded test code."""
    names = (
        git("ls-tree", "-r", "--name-only", ENTRY, "src", "specs", "tests")
        .decode()
        .splitlines()
    )
    need(
        not git("diff", ENTRY, "--", "src", "specs", "tests").strip(),
        "runtime/spec/test change requires an explicit regression disposition",
    )
    # The entry commit pins the accepted fixture population, including ordinary
    # zero-site inputs; retain direct native input and reconciliation references.
    names += [support.RECORD, SELF, TEST, BASE + "verification/p991a7_support.py"]
    names += [support.prefix(tag) + "-inputs.jsonl.xz" for _, tag, _ in support.ROSTER]
    names += [
        BASE + "tranche-9/P9-9.1b-" + family + ".json"
        for family in ("C_OS", "C_CI", "A_CI", "A_PC")
    ]
    return [ref(name) for name in sorted(set(names))]


def retained():
    value = support.checked(ROOT)
    need(value["reconciliation_user_accepted"] is True, "P9-9.1a.7 acceptance required")
    # Historical numerical evidence keeps its original execution identities.
    return {
        "support": ref(support.RECORD),
        "record_digest": value["record_digest"],
        "families": [r["family"] for r in value["families"]],
        "campaigns": [r["campaign"] for r in value["evidence"]],
        "native_obligations": value["native_obligation_count"],
    }


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def roster(group):
    suite = unittest.defaultTestLoader.loadTestsFromNames(GROUPS[group])
    return suite, [t.id() for t in flatten(suite)]


def run_group(group):
    import flint
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend

    start = time.monotonic()
    output = io.StringIO()
    suite, ids = roster(group)
    with (
        redirect_stdout(output),
        redirect_stderr(output),
        exact_backend(ExactBackend.FLINT),
    ):
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    need(
        result.wasSuccessful()
        and not result.skipped
        and not result.expectedFailures
        and result.testsRun == len(ids) > 0,
        group + " failed:\n" + output.getvalue(),
    )
    return dict(
        group=group,
        tests=ids,
        tests_run=result.testsRun,
        status="passed",
        failures=0,
        errors=0,
        skips=0,
        expected_failures=0,
        elapsed_seconds=round(time.monotonic() - start, 3),
        python=platform.python_version(),
        python_flint=flint.__version__,
        exact_backend="flint",
    )


def check_value(value, subjects, reuse):
    need(
        value == seal(value) and value["schema"] == "p9103-native-spark-regressions-v1",
        "record identity",
    )
    need(
        value["entry_commit"] == git("rev-parse", ENTRY).decode().strip()
        and value["source_refs"] == subjects
        and value["reused_evidence"] == reuse,
        "source/evidence changed",
    )
    need(
        value["status"] == "passed_pending_acceptance"
        and all(
            value[k] is False
            for k in (
                "user_accepted",
                "G4_accepted",
                "full_GRC9V4_conformance",
                "hierarchy_tracking",
            )
        )
        and value["source_to_completion_campaigns_rerun"] == 0
        and value["new_support"] == [],
        "scope widened",
    )
    need(
        [r["group"] for r in value["regressions"]] == list(GROUPS),
        "missing regression group",
    )
    for row in value["regressions"]:
        _, ids = roster(row["group"])
        need(
            row["tests"] == ids
            and row["tests_run"] == len(ids) > 0
            and row["status"] == "passed"
            and all(
                row[k] == 0
                for k in ("failures", "errors", "skips", "expected_failures")
            ),
            "test roster/outcome drift",
        )
    need(
        value["tests_run"] == sum(r["tests_run"] for r in value["regressions"]),
        "test count drift",
    )
    return value


def check():
    return check_value(json.loads((ROOT / PATH).read_bytes()), inputs(), retained())


def run(workers):
    need(not (ROOT / PATH).exists(), "refuse to overwrite execution evidence")
    subjects, reuse = inputs(), retained()
    print(
        "Accepted evidence authenticated; four independent integration groups.",
        flush=True,
    )
    with ProcessPoolExecutor(max_workers=workers) as pool:
        completed = {}
        for future in as_completed([pool.submit(run_group, name) for name in GROUPS]):
            row = future.result()
            completed[row["group"]] = row
            print(
                f"{row['group']}: {row['tests_run']} passed in {row['elapsed_seconds']}s",
                flush=True,
            )
    need(subjects == inputs(), "execution inputs changed")
    rows = [completed[name] for name in GROUPS]
    value = seal(
        dict(
            schema="p9103-native-spark-regressions-v1",
            status="passed_pending_acceptance",
            entry_commit=git("rev-parse", ENTRY).decode().strip(),
            source_refs=subjects,
            reused_evidence=reuse,
            regressions=rows,
            workers=workers,
            tests_run=sum(r["tests_run"] for r in rows),
            user_accepted=False,
            G4_accepted=False,
            full_GRC9V4_conformance=False,
            hierarchy_tracking=False,
            source_to_completion_campaigns_rerun=0,
            new_support=[],
            scope="All-ten public identities/persistence; shared C_OS short-window lifecycle regressions; ordinary V4/legacy boundaries. Accepted family numerics and complete cold replay reused.",
            next_work=["P9-10.4-NATIVE-SPARK", "P9-10.5", "P9-10.6"],
        )
    )
    raw = json.dumps(value, indent=2) + "\n"
    need(len(raw.encode()) <= 1_000_000, "compress evidence above 1 MB")
    (ROOT / PATH).write_text(raw)
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    value = run(args.workers) if args.run else check()
    print(
        f"P9103_NATIVE_SPARK_PASS tests={value['tests_run']} families=10 campaign_reruns=0"
    )
