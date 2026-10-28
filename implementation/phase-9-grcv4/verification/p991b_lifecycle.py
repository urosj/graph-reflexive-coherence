"""Four-family mandatory lifecycle: native --run, read-only retained --check."""

import argparse
import hashlib
import json
import lzma
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/tranche-9/"
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")
CLASSES = dict(
    zip(FAMILIES, ("COSLifecycle", "CCILifecycle", "ACILifecycle", "APCLifecycle"))
)
ACCEPTANCE = (
    "implementation/phase-9-grcv4/tranche-8/P9-Tranche8-FirstGroupAcceptance.json"
)
PREDECESSOR = "9b177f90bc5c38deea9769aca98fc16d9f6c0c10dc6ccc3b92583a3faa8f697c"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    value = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        value,
        record_digest=sha(
            json.dumps(
                value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ),
    )


def filename(family):
    if family not in FAMILIES:
        raise ValueError("unselected family")
    return BASE + "P9-9.1b-" + family + ".json"


def prerequisite(root):
    value = json.loads((root / ACCEPTANCE).read_bytes())
    # Execution depends on the accepted predecessor, not on evolving metadata
    # policy modules. The separate current-boundary check owns work permission.
    from pygrc.models.grc_v4_codec import canonical_json_bytes

    body = {k: v for k, v in value.items() if k != "record_digest"}
    if (
        value["record_digest"] != PREDECESSOR
        or sha(canonical_json_bytes(body)) != PREDECESSOR
        or not value["user_accepted"]
        or not value["first_group_closed"]
        or set(value["families"]) != set(FAMILIES)
    ):
        raise ValueError("unaccepted Tranche 8 predecessor")
    return dict(
        path=ACCEPTANCE,
        sha256=sha((root / ACCEPTANCE).read_bytes()),
        record_digest=PREDECESSOR,
    )


def run(root, family):
    sys.path[:0] = [str(root), str(root / "src")]
    prior = prerequisite(root)
    from tests.models import test_grc_9_v4_owner as test

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        getattr(test, CLASSES[family])
    )
    roster = [case.id() for case in suite]
    started = time.monotonic()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError("native lifecycle suite did not pass")
    source_paths = {Path(__file__).resolve()}
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name:
            path = Path(name).resolve()
            if (
                path.is_relative_to(root)
                and path.suffix == ".py"
                and ".venv" not in path.parts
            ):
                source_paths.add(path)
    # Numerical declarations and fixed oracle inputs are explicit, portable
    # inputs, not inferred from imported Python modules alone.
    input_paths = [root / "specs/grc-v4-conformance-vectors.json"]
    if family in ("A_CI", "A_PC"):
        module = sys.modules[
            "tests.models.test_grc_9_v4_" + ("aci" if family == "A_CI" else "apc")
        ]
        input_paths.append(module.RECORD)
    source_paths.update((root / "src/pygrc/models/grc_v4_assets").glob("*.json"))
    import flint
    import numpy

    return seal(
        dict(
            schema="p991b-enabled-lifecycle-execution-v1",
            family=family,
            predecessor=prior,
            outcome="passed",
            tests=roster,
            tests_run=result.testsRun,
            errors=0,
            failures=0,
            skips=0,
            elapsed_seconds=time.monotonic() - started,
            execution=dict(
                exact_backend="flint",
                numerical_policy="legacy_exact_v1",
                python=sys.version.split()[0],
                python_flint=flint.__version__,
                numpy=numpy.__version__,
            ),
            source_refs=[
                dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
                for p in sorted(source_paths)
            ],
            input_refs=[
                dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
                for p in sorted(input_paths)
            ],
            evidence=test.OBSERVATIONS[family],
            user_accepted=False,
            aggregate_closed=False,
            full_GRC9V4_conformance=False,
            disabled_compatibility_executed=False,
            completion_hierarchy_executed=False,
            large_graph_campaign_repeated=False,
        )
    )


def check(root, family):
    if (root / BASE / "P9-9.1b-Acceptance.json").is_file():
        from p994a_owner_successor import check as accepted_check

        return accepted_check(root, family)
    path = root / filename(family)
    compressed = path.with_suffix(".json.xz")
    if path.exists() and compressed.exists():
        raise ValueError("ambiguous evidence representation")
    raw = (
        path.read_bytes() if path.exists() else lzma.decompress(compressed.read_bytes())
    )
    value = json.loads(raw)
    if (
        value != seal(value)
        or value["family"] != family
        or value["outcome"] != "passed"
        or value["tests_run"] != 6
        or len(value["tests"]) != 6
        or value["errors"]
        or value["failures"]
        or value["skips"]
        or not value["evidence"]["source_beat_then_bound_event"]
        or value["predecessor"] != prerequisite(root)
    ):
        raise ValueError("execution record mismatch")
    for row in value["source_refs"] + value["input_refs"]:
        p = (root / row["path"]).resolve()
        if (
            not p.is_relative_to(root)
            or Path(row["path"]).is_absolute()
            or sha(p.read_bytes()) != row["sha256"]
        ):
            raise ValueError("current execution input drift: " + row["path"])
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FAMILIES, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.run:
        path = ROOT / filename(args.family)
        if path.exists() or path.with_suffix(".json.xz").exists():
            raise FileExistsError("retained run already exists")
        value = run(ROOT, args.family)
        raw = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
        path.parent.mkdir(parents=True, exist_ok=True)
        if len(raw) > 1_000_000:
            path = path.with_suffix(".json.xz")
            raw = lzma.compress(raw)
        path.write_bytes(raw)
    else:
        value = check(ROOT, args.family)
    print(
        json.dumps(
            dict(
                family=args.family,
                mode="native_execution" if args.run else "retained_integrity_only",
                tests=value["tests_run"],
                outcome=value["outcome"],
                record_digest=value["record_digest"],
            )
        )
    )


if __name__ == "__main__":
    main()
