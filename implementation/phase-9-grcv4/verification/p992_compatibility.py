"""Execute or authenticate independent disabled-delegate cells; no migration grant."""

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
SURFACES = ("transition", "state", "observable", "lifecycle")
CLASSES = dict(
    zip(
        FAMILIES,
        (
            "COSCompatibility",
            "CCICompatibility",
            "ACICompatibility",
            "APCCompatibility",
        ),
    )
)
RECORDS = (*FAMILIES, "boundary")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha(
            json.dumps(
                body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ),
    )


def filename(family):
    if family not in RECORDS:
        raise ValueError("unselected family")
    return BASE + "P9-9.2-" + family + ".json"


def predecessor(root):
    from p991b_acceptance import decision, PATH

    v = decision(root)
    return dict(
        path=PATH,
        sha256=sha((root / PATH).read_bytes()),
        record_digest=v["record_digest"],
    )


def run(root, family):
    sys.path[:0] = [str(root), str(root / "src")]
    prior = predecessor(root)
    from tests.models import test_grc_9_v4_legacy as tests

    cls = (
        tests.DelegateBoundaryTests
        if family == "boundary"
        else getattr(tests, CLASSES[family])
    )
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    roster = [t.id() for t in suite]
    started = time.monotonic()
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    if not outcome.wasSuccessful() or outcome.skipped:
        raise RuntimeError("compatibility suite failed")
    sources = {Path(__file__).resolve()}
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path:
            p = Path(path).resolve()
            if p.is_relative_to(root) and ".venv" not in p.parts and p.suffix == ".py":
                sources.add(p)
    sources.update((root / "src/pygrc/models/grc_v4_assets").glob("*.json"))
    inputs = [
        root / "specs/grc-9-v3-spec.md",
        root / "specs/grc-9-v4-spec.md",
        root / "specs/grc-v4-conformance-fixtures.json",
    ]
    selected = FAMILIES if family == "boundary" else (family,)
    inputs += [root / BASE / ("P9-9.1b-" + f + ".json") for f in selected]
    evidence = {} if family == "boundary" else tests.EVIDENCE
    if family != "boundary" and set(evidence) != set(SURFACES):
        raise ValueError("missing independent surface")
    return seal(
        dict(
            schema="p992-disabled-delegate-execution-v1",
            family=family,
            outcome="passed",
            tests=roster,
            tests_run=outcome.testsRun,
            failures=0,
            errors=0,
            skips=0,
            predecessor=prior,
            elapsed_seconds=time.monotonic() - started,
            execution=dict(
                python=sys.version.split()[0],
                engine="unchanged_native_GRC9V3",
                comparison="exact_no_tolerance",
                workers_per_record=1,
            ),
            source_refs=[
                dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
                for p in sorted(sources)
            ],
            input_refs=[
                dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
                for p in inputs
            ],
            cells={
                s: dict(
                    iteration_id=f"P9-9.2-{family}-{s}",
                    vector_id=f"DISABLED-{family}-{s.upper()}",
                    **evidence[s],
                )
                for s in SURFACES
            }
            if evidence
            else {},
            domain_control="saturated_candidate_rejection_on_private_copy"
            if family == "boundary"
            else None,
            user_accepted=False,
            enabled_disabled_crossing_executed=False,
            full_GRC9V4_conformance=False,
            aggregate_closed=False,
            legacy_source_modified=False,
        )
    )


def read(root, family):
    p = root / filename(family)
    q = p.with_suffix(".json.xz")
    if p.exists() and q.exists():
        raise ValueError("ambiguous retained representation")
    raw = p.read_bytes() if p.exists() else lzma.decompress(q.read_bytes())
    return json.loads(raw)


def check(root, family):
    from p994b_source_compatibility import execution_sha
    root = Path(root).resolve()
    v = read(root, family)
    count = 2 if family == "boundary" else 4
    if (
        v != seal(v)
        or v["schema"] != "p992-disabled-delegate-execution-v1"
        or v["family"] != family
        or v["outcome"] != "passed"
        or v["tests_run"] != count
        or len(v["tests"]) != count
        or any(
            v[k]
            for k in (
                "failures",
                "errors",
                "skips",
                "user_accepted",
                "enabled_disabled_crossing_executed",
                "full_GRC9V4_conformance",
                "aggregate_closed",
                "legacy_source_modified",
            )
        )
        or v["predecessor"] != predecessor(root)
    ):
        raise ValueError("invalid retained compatibility record")
    if family != "boundary":
        if set(v["cells"]) != set(SURFACES):
            raise ValueError("missing compatibility cell")
        for s, row in v["cells"].items():
            if (
                row["iteration_id"] != f"P9-9.2-{family}-{s}"
                or row["contract_id"] != f"D10.2-EC-DISABLED-{family}-{s.upper()}"
                or row["outcome"] != "passed"
            ):
                raise ValueError("cell authority/disposition drift")
    for ref in v["source_refs"] + v["input_refs"]:
        path = (root / ref["path"]).resolve()
        if (
            Path(ref["path"]).is_absolute()
            or not path.is_relative_to(root)
            or execution_sha(root, ref["path"], ref["sha256"]) != ref["sha256"]
        ):
            raise ValueError("execution input drift: " + ref["path"])
    return v


def status(root):
    records = {f: check(root, f) for f in RECORDS}
    rows = []
    for candidate in ("A", "C"):
        for realization in ("OS", "CI", "PC", "CI_PC", "RG2b"):
            family = candidate + "_" + realization
            for surface in SURFACES:
                rows.append(
                    dict(
                        family=family,
                        surface=surface,
                        iteration_id=f"P9-9.2-{family}-{surface}",
                        state="executed_pending_acceptance"
                        if family in FAMILIES
                        else "unselected",
                        record_digest=records[family]["record_digest"]
                        if family in FAMILIES
                        else None,
                    )
                )
    paths = [filename(f) for f in RECORDS] + [
        BASE + "P9-9.2-Review.md",
        BASE + "P9-9.2-Authority.json",
    ]
    refs = []
    for name in paths:
        p = Path(root) / name
        if not p.exists():
            p = p.with_suffix(".json.xz")
        refs.append(
            dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
        )
    return dict(
        schema="p992-compatibility-status-v1",
        families=list(FAMILIES),
        cells=rows,
        selected_cells=16,
        passed_cells=16,
        unselected_cells=24,
        user_accepted=False,
        full_GRC9V4_conformance=False,
        aggregate_closed=False,
        crossings_executed=False,
        check_level="retained_integrity_only_no_native_rerun",
        source_refs=refs,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=RECORDS, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.run:
        p = ROOT / filename(args.family)
        if p.exists() or p.with_suffix(".json.xz").exists():
            raise FileExistsError("retained record already exists")
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
                tests=v["tests_run"],
                outcome=v["outcome"],
                record_digest=v["record_digest"],
            )
        )
    )


if __name__ == "__main__":
    main()
