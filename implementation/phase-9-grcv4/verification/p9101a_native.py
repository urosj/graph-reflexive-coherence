"""Small native basin checks. --check authenticates retained evidence, not a rerun."""

import argparse
from p9_aos_historical import references_match
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/tranche-10/"
SELF = "implementation/phase-9-grcv4/verification/p9101a_native.py"
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")
CLASSES = dict(
    zip(
        (*FAMILIES, "graph"),
        (
            "COSBasinTests",
            "CCIBasinTests",
            "ACIBasinTests",
            "APCBasinTests",
            "BasinGraphTests",
        ),
    )
)
AUTHORITY = "implementation/investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json"
AUTHORITY_DIGEST = "409e503e1ba880e2ab17a61f93f950e1a3e3116619561f19e70df9f0fc5eef28"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return {
        **body,
        "record_digest": sha(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ),
    }


def filename(family):
    if family not in CLASSES:
        raise ValueError("unselected native basin group")
    return BASE + "P9-10.1a-Native-" + family + ".json"


def references(root):
    # Bind native numerical dependencies as well as the changed facade. This is
    # a small source roster, not retained copies of the old trajectory campaigns.
    names = {
        SELF,
        AUTHORITY,
        BASE + "P9-10.1a-DesignAcceptance.json",
        "specs/grc-9-v4-basin-interface.md",
        "specs/grc-9-v4-basin-interface-schema.json",
    }
    for pattern in (
        "src/pygrc/**/*.py",
        "src/pygrc/models/grc_v4_assets/*.json",
        "tests/models/test_grc*.py",
    ):
        names.update(p.relative_to(root).as_posix() for p in root.glob(pattern))
    names.update(
        "implementation/phase-9-grcv4/tranche-9/P9-9.1b-" + f + ".json"
        for f in FAMILIES
    )
    return [dict(path=n, sha256=sha((root / n).read_bytes())) for n in sorted(names)]


def run(root, family):
    sys.path[:0] = [str(root), str(root / "src")]
    from tests.models import test_grc_9_v4_basin as tests
    import flint

    tests.EVIDENCE.clear()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        getattr(tests, CLASSES[family])
    )
    roster = [t.id() for t in suite]
    before = references(root)
    started = time.monotonic()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped or result.testsRun != len(roster):
        raise ValueError(
            "native basin conformance did not pass; no success record written"
        )
    if references(root) != before:
        raise ValueError("execution source changed during native tests")
    return seal(
        dict(
            schema="p9101a-native-basin-execution-v1",
            family=family,
            status="passed_bounded_native_execution",
            tests=roster,
            tests_run=result.testsRun,
            elapsed_seconds=round(time.monotonic() - started, 3),
            python_version=platform.python_version(),
            python_flint_version=flint.__version__,
            exact_backend="flint",
            numerical_policy="legacy_exact_v1",
            authority_record_digest=AUTHORITY_DIGEST,
            evidence=dict(tests.EVIDENCE),
            source_refs=before,
            user_accepted=False,
            P9_10_1a_closed=False,
            full_GRC9V4_conformance=False,
            new_support=[],
            other_six_native_execution=False,
        )
    )


def check(root=ROOT, family="C_OS"):
    root = Path(root).resolve()
    value = json.loads((root / filename(family)).read_bytes())
    if (
        value != seal(value)
        or value["schema"] != "p9101a-native-basin-execution-v1"
        or value["family"] != family
        or value["status"] != "passed_bounded_native_execution"
        or value["authority_record_digest"] != AUTHORITY_DIGEST
        or not references_match(root, value["source_refs"], references(root))
        or value["tests_run"] != 4
        or len(set(value["tests"])) != 4
        or any(
            value[k] is not False
            for k in (
                "user_accepted",
                "P9_10_1a_closed",
                "full_GRC9V4_conformance",
                "other_six_native_execution",
            )
        )
        or value["new_support"] != []
    ):
        raise ValueError("native basin evidence/source/scope mismatch")
    authority = json.loads((root / AUTHORITY).read_bytes())
    if authority["record_digest"] != AUTHORITY_DIGEST:
        raise ValueError("native basin authority drift")
    if family != "graph":
        e = value["evidence"]
        if (
            set(e) != {"capture", "lifecycle", "pressure", "compatibility"}
            or e["capture"]["family"] != family
        ):
            raise ValueError("incomplete native basin case coverage")
    return value


def status(root=ROOT):
    rows = [check(root, f) for f in CLASSES]
    return seal(
        dict(
            schema="p9101a-native-basin-status-v1",
            families=list(FAMILIES),
            check_mode="retained_integrity_not_native_rerun",
            tests_run=sum(r["tests_run"] for r in rows),
            native_execution_passed=True,
            user_accepted=False,
            P9_10_1a_closed=False,
            full_GRC9V4_conformance=False,
            authority_record_digest=AUTHORITY_DIGEST,
            records=[
                dict(
                    path=filename(r["family"]),
                    sha256=sha((Path(root) / filename(r["family"])).read_bytes()),
                    family=r["family"],
                    record_digest=r["record_digest"],
                    tests_run=r["tests_run"],
                )
                for r in rows
            ],
            scope="Four small native fixtures and graph/seed pressure; no support promotion or completed-spark claim.",
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=CLASSES)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.run and not args.family:
        parser.error("--run requires --family")
    value = (
        run(ROOT, args.family)
        if args.run
        else check(ROOT, args.family)
        if args.family
        else status(ROOT)
    )
    raw = json.dumps(value, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as out:
            out.write(raw)
    else:
        print(raw, end="")
