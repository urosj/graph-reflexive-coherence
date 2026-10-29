"""Retained independent basin pressure. --check does not rerun native reads."""

import argparse
from p9_aos_historical import references_match
import json
import lzma
from pathlib import Path
import platform
import sys
import time
import unittest

import p9101a_native as predecessor

ROOT, BASE = predecessor.ROOT, predecessor.BASE
GROUPS = dict(
    zip(
        (*predecessor.FAMILIES, "graph"),
        (
            "COSPressure",
            "CCIPressure",
            "ACIPressure",
            "APCPressure",
            "GraphOraclePressure",
        ),
    )
)
FILES = (
    "p9101a_basin_pressure.py",
    "p9101a_basin_oracle.py",
    "test_p9101a_basin_pressure.py",
    "test_p980_os_effect_witness.py",
    "test_p980_os_numerical_feasibility.py",
    "test_p980_fixed_row_bounds.py",
    "test_p980_boundary_continuation.py",
    "test_p980_feasibility.py",
)


def references(root):
    refs = {r["path"]: r for r in predecessor.references(root)}
    for name in FILES:
        path = "implementation/phase-9-grcv4/verification/" + name
        refs[path] = dict(path=path, sha256=predecessor.sha((root / path).read_bytes()))
    return [refs[k] for k in sorted(refs)]


def stem(group):
    if group not in GROUPS:
        raise ValueError("unselected pressure group")
    return BASE + "P9-10.1a-Pressure-" + group + ".json"


def run(root, group):
    sys.path[:0] = [str(root), str(root / "src")]
    import test_p9101a_basin_pressure as tests
    import flint

    tests.EVIDENCE.clear()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        getattr(tests, GROUPS[group])
    )
    roster = [t.id() for t in suite]
    refs = references(root)
    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped or result.testsRun != len(roster):
        raise ValueError("pressure failed; no success record written")
    if refs != references(root):
        raise ValueError("pressure source changed during execution")
    return predecessor.seal(
        dict(
            schema="p9101a-basin-pressure-v1",
            group=group,
            status="passed_bounded_end_to_end_pressure",
            tests=roster,
            tests_run=result.testsRun,
            elapsed_seconds=round(time.monotonic() - start, 3),
            python_version=platform.python_version(),
            python_flint_version=flint.__version__,
            exact_backend="flint",
            authority_record_digest=predecessor.AUTHORITY_DIGEST,
            evidence=tests.EVIDENCE,
            source_refs=refs,
            user_accepted=False,
            P9_10_1a_closed=False,
            new_support=[],
        )
    )


def load(root, group):
    choices = [root / stem(group), root / (stem(group) + ".xz")]
    existing = [p for p in choices if p.exists()]
    if len(existing) != 1:
        raise ValueError("exactly one pressure record required")
    p = existing[0]
    raw = p.read_bytes()
    value = json.loads(lzma.decompress(raw) if p.suffix == ".xz" else raw)
    return value, dict(
        path=p.relative_to(root).as_posix(),
        sha256=predecessor.sha(raw),
        record_digest=value["record_digest"],
        family=group,
        tests_run=value["tests_run"],
    )


def check(root=ROOT, group="C_OS"):
    root = Path(root).resolve()
    value, ref = load(root, group)
    count = 1 if group == "graph" else 4
    if (
        value != predecessor.seal(value)
        or value["schema"] != "p9101a-basin-pressure-v1"
        or value["group"] != group
        or value["tests_run"] != count
        or len(set(value["tests"])) != count
        or not references_match(root, value["source_refs"], references(root))
        or value["authority_record_digest"] != predecessor.AUTHORITY_DIGEST
        or value["status"] != "passed_bounded_end_to_end_pressure"
        or value["user_accepted"] is not False
        or value["P9_10_1a_closed"] is not False
        or value["new_support"] != []
    ):
        raise ValueError("pressure evidence/source/scope mismatch")
    import p9101a_basin_oracle as oracle

    if group != "graph":
        if set(value["evidence"]) != {
            "observations",
            "freshness",
            "occurrence",
            "lifecycle",
            "faults",
        }:
            raise ValueError("incomplete end-to-end coverage")
        for case in value["evidence"]["observations"]:
            if case["fixture_identity"] != oracle.digest(case["saved_native_state"]):
                raise ValueError("saved-state digest mismatch")
            for role in ("current", "reset"):
                observed = case["observations"][role + "_observation"]
                selected = case["selected_roots"][role]
                if observed["binding"][
                    "read_identity"
                ] != "grc9v4-basin-read-sha256:" + oracle.digest(selected) or selected[
                    "current"
                ] != [e["current"] for e in observed["witness"]["edges"]]:
                    raise ValueError("retained selected-root/operand mismatch")
                oracle.compare_classification(observed)
                if case["expected_classification"][role] != oracle.classification(
                    observed["witness"], observed["binding"]["graph_digest"]
                ):
                    raise ValueError("independent expected classification drift")
    return value, ref


def status(root=ROOT):
    root = Path(root).resolve()
    old = predecessor.status(root)
    rows = [check(root, f) for f in GROUPS]
    return predecessor.seal(
        dict(
            schema="p9101a-native-basin-status-v2",
            families=list(predecessor.FAMILIES),
            check_mode="retained_integrity_and_classification_not_native_rerun",
            tests_run=old["tests_run"] + sum(v["tests_run"] for v, _ in rows),
            original_tests_run=old["tests_run"],
            pressure_tests_run=sum(v["tests_run"] for v, _ in rows),
            native_execution_passed=True,
            user_accepted=False,
            P9_10_1a_closed=False,
            full_GRC9V4_conformance=False,
            authority_record_digest=predecessor.AUTHORITY_DIGEST,
            records=old["records"] + [r for _, r in rows],
            scope="Four bounded families: saved-state equation/row/capture oracle, full classification and lifecycle pressure. Seed-positive excluded by pinned thresholds; cycles synthetic only; no stable-attractor claim.",
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=GROUPS)
    parser.add_argument(
        "--output",
        type=Path,
        help="fresh run destination; existing files never overwritten",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.run:
        if not args.family:
            parser.error("--run requires --family")
        destination = args.output or ROOT / stem(args.family)
        if any(Path(str(destination) + suffix).exists() for suffix in ("", ".xz")):
            parser.error(
                "pressure evidence already exists; select a reviewed successor"
            )
        value = run(ROOT, args.family)
        raw = (json.dumps(value, indent=2) + "\n").encode()
        compressed = len(raw) > 1_000_000
        path = Path(str(destination) + (".xz" if compressed else ""))
        with path.open("xb") as out:
            out.write(lzma.compress(raw) if compressed else raw)
        print(
            json.dumps(
                dict(
                    filename=path.name,
                    tests_run=value["tests_run"],
                    elapsed_seconds=value["elapsed_seconds"],
                    bytes=path.stat().st_size,
                )
            )
        )
    else:
        value = check(ROOT, args.family)[0] if args.family else status(ROOT)
        print(
            json.dumps(
                {
                    k: v
                    for k, v in value.items()
                    if k not in {"evidence", "source_refs"}
                },
                indent=2,
            )
        )
