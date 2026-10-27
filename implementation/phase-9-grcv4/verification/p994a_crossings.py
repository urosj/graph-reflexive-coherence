"""Execute four bounded branch-crossing suites or authenticate retained records."""

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
    zip(FAMILIES, ("COSCrossing", "CCICrossing", "ACICrossing", "APCCrossing"))
)
CASES = ("roundtrip", "rollback", "replay_pressure", "excluded_domain")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(v):
    body = {k: x for k, x in v.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha(
            json.dumps(
                body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ),
    )


def filename(f):
    if f not in FAMILIES:
        raise ValueError("unselected family")
    return BASE + "P9-9.4a-" + f + ".json"


def predecessor(root):
    from p993_acceptance import decision, PATH

    d = decision(root)
    return dict(
        path=PATH,
        sha256=sha((root / PATH).read_bytes()),
        record_digest=d["record_digest"],
    )


def run(root, f):
    sys.path[:0] = [str(root), str(root / "src")]
    from tests.models import test_grc_9_v4_crossing as tests

    tests.EVIDENCE.clear()
    cls = getattr(tests, CLASSES[f])
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    roster = [t.id() for t in suite]
    # Capture input bytes before execution; reject a concurrent source edit.
    sources = [p for p in (root / "src").rglob("*.py")]
    sources += [
        root / "tests/models/test_grc_9_v4_crossing.py",
        root / "tests/models/test_grc_9_v4_legacy.py",
        Path(__file__).resolve(),
    ]
    sources += list((root / "src/pygrc/models/grc_v4_assets").glob("*.json"))
    inputs = [
        root / BASE / ("P9-9.1b-" + f + ".json"),
        root / "specs/grc-9-v4-spec.md",
        root / "specs/grc-common-interface-v4-ext.md",
        root / BASE / "P9-9.4a-Authority.json",
    ]

    def refs(paths):
        return [
            dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
            for p in sorted(set(paths))
        ]

    before = refs(sources + inputs)
    prior = predecessor(root)
    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError("crossing suite failed")
    if refs(sources + inputs) != before:
        raise ValueError("execution source changed during run")
    if set(tests.EVIDENCE) != set(CASES):
        raise ValueError("incomplete evidence")
    # Retain imported source dependencies, not unrelated runtime modules.
    imported = {
        Path(m.__file__).resolve()
        for m in list(sys.modules.values())
        if getattr(m, "__file__", None)
    }
    used = [p for p in sources if p in imported or p.suffix == ".json"]
    return seal(
        dict(
            schema="p994a-crossing-execution-v1",
            family=f,
            outcome="passed",
            tests=roster,
            tests_run=result.testsRun,
            failures=0,
            errors=0,
            skips=0,
            predecessor=prior,
            elapsed_seconds=time.monotonic() - start,
            source_refs=refs(used),
            input_refs=refs(inputs),
            execution=dict(
                python=sys.version.split()[0],
                exact_backend="flint",
                numerical_policy="legacy_exact_v1",
                workers_per_record=1,
            ),
            evidence=tests.EVIDENCE,
            user_accepted=False,
            public_api=False,
            full_GRC9V4_conformance=False,
            aggregate_closed=False,
            scope="same_graph_explicit_stage_roundtrip_no_optional_completion",
        )
    )


def read(root, f):
    p = root / filename(f)
    q = p.with_suffix(".json.xz")
    if p.exists() and q.exists():
        raise ValueError("ambiguous evidence representation")
    return json.loads(p.read_bytes() if p.exists() else lzma.decompress(q.read_bytes()))


def check(root, f):
    root = Path(root).resolve()
    v = read(root, f)
    names = (
        "test_excluded_legacy_timestep_returns_honest_failure",
        "test_rejection_and_whole_publication_rollback",
        "test_replay_tamper_and_wire_pressure",
        "test_roundtrip_both_roles_native_parity_and_continuation",
    )
    if (
        v != seal(v)
        or v["schema"] != "p994a-crossing-execution-v1"
        or v["family"] != f
        or v["outcome"] != "passed"
        or v["tests_run"] != 4
        or v["tests"]
        != [
            "tests.models.test_grc_9_v4_crossing." + CLASSES[f] + "." + n for n in names
        ]
        or any(
            v[k]
            for k in (
                "failures",
                "errors",
                "skips",
                "user_accepted",
                "public_api",
                "full_GRC9V4_conformance",
                "aggregate_closed",
            )
        )
        or v["predecessor"] != predecessor(root)
        or set(v["evidence"]) != set(CASES)
        or v["scope"] != "same_graph_explicit_stage_roundtrip_no_optional_completion"
    ):
        raise ValueError("invalid bounded crossing evidence")
    r = v["evidence"]["roundtrip"]
    if (
        not all(
            r[k] is True
            for k in (
                "exact_native_step_and_snapshot",
                "current_reset_independently_admitted",
                "enabled_positive_step",
            )
        )
        or r["independent_initializer"] != f.startswith("A_")
        or r["commits"] != 8
        or r["disabled_checkpoint"]["branch"] != "disabled_grc9v3"
        or r["final_checkpoint"]["branch"] != "enabled_v4"
    ):
        raise ValueError("crossing coverage mismatch")
    for ref in v["source_refs"] + v["input_refs"]:
        p = (root / ref["path"]).resolve()
        if (
            Path(ref["path"]).is_absolute()
            or not p.is_relative_to(root)
            or sha(p.read_bytes()) != ref["sha256"]
        ):
            raise ValueError("crossing input drift: " + ref["path"])
    return v


def status(root):
    root = Path(root).resolve()
    records = [check(root, f) for f in FAMILIES]
    names = [filename(f) for f in FAMILIES] + [
        BASE + "P9-9.4a-Review.md",
        BASE + "P9-9.4a-Authority.json",
    ]
    refs = []
    for name in names:
        p = root / name
        if not p.exists():
            p = p.with_suffix(".json.xz")
        refs.append(
            dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
        )
    return dict(
        schema="p994a-crossing-status-v1",
        iteration="P9-9.4a",
        families=list(FAMILIES),
        records=[
            dict(
                family=v["family"],
                tests=v["tests_run"],
                outcome=v["outcome"],
                record_digest=v["record_digest"],
                elapsed_seconds=v["elapsed_seconds"],
            )
            for v in records
        ],
        user_accepted=False,
        public_api=False,
        aggregate_closed=False,
        full_GRC9V4_conformance=False,
        state="executed_pending_review",
        check_level="retained_integrity_only_no_native_rerun",
        source_refs=refs,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FAMILIES, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.run:
        p = ROOT / filename(args.family)
        if p.exists() or p.with_suffix(".json.xz").exists():
            raise FileExistsError("retained record exists")
        v = run(ROOT, args.family)
        raw = (json.dumps(v, indent=2) + "\n").encode()
        if len(raw) > 1_000_000:
            p = p.with_suffix(".json.xz")
            raw = lzma.compress(raw)
        p.write_bytes(raw)
    else:
        v = check(ROOT, args.family)
    print(
        json.dumps(
            dict(
                family=args.family,
                mode="native_execution" if args.run else "retained_integrity_only",
                outcome=v["outcome"],
                record_digest=v["record_digest"],
            )
        )
    )


if __name__ == "__main__":
    main()
