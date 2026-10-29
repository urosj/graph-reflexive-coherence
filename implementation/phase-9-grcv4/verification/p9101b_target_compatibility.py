"""P9-10.1b. --run executes native tests; --check authenticates retained records only."""

import argparse
from p9_aos_historical import references_match
import json
import lzma
from pathlib import Path
import platform
import sys
import time
import unittest

from p9101a_native import ROOT, BASE, FAMILIES, seal, sha

VERIFY = "implementation/phase-9-grcv4/verification/"
PREDECESSORS = {
    "implementation/phase-9-grcv4/tranche-9/P9-9.6-SupportReview.json": "1c30d49b1b7d011632eb307a358c7870e78ac3f81b3b4139c67c3ac1f64ccd00",
    BASE
    + "P9-10.1a-NativeAcceptance.json": "07ab5fae7e2cb15fe72ec8dd48842633666bf032c5cd70ca03b086a151e8dd01",
}
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
METHODS = (
    "test_exact_accepted_target_four_surfaces",
    "test_excluded_domain_replay_tampering_and_late_failure",
    "test_explicit_basin_successor_four_surfaces",
)
SURFACES = ("transition", "state", "observable", "lifecycle")


def references(root):
    names = set(PREDECESSORS) | {
        VERIFY + p
        for p in (
            "p9101b_target_compatibility.py",
            "test_p9101b_target_compatibility.py",
            "p9101a_native.py",
        )
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
    names.update(("specs/grc-9-v4-spec.md", "specs/grc-9-v4-basin-interface.md"))
    return [dict(path=n, sha256=sha((root / n).read_bytes())) for n in sorted(names)]


def predecessors(root):
    rows = {}
    for path, expected in PREDECESSORS.items():
        value = json.loads((root / path).read_bytes())
        if value != seal(value) or value["record_digest"] != expected:
            raise ValueError("accepted prerequisite changed: " + path)
        rows[path] = value
    return rows


def run(root, family):
    sys.path[:0] = [str(root), str(root / "src")]
    import test_p9101b_target_compatibility as tests
    import flint

    predecessors(root)
    refs = references(root)
    tests.EVIDENCE.clear()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        getattr(tests, CLASSES[family])
    )
    roster = [t.id() for t in suite]
    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped or result.testsRun != len(METHODS):
        raise ValueError("expanded-target checks failed; no success record written")
    if refs != references(root):
        raise ValueError("execution sources changed during run")
    return seal(
        dict(
            schema="p9101b-expanded-target-compatibility-v1",
            family=family,
            status="passed_bounded_target_execution",
            tests=roster,
            tests_run=result.testsRun,
            elapsed_seconds=round(time.monotonic() - start, 3),
            python_version=platform.python_version(),
            python_flint_version=flint.__version__,
            exact_backend="flint",
            numerical_policy="legacy_exact_v1",
            # Native snapshots include integer-indexed maps. Normalize to the
            # actual JSON wire object before hashing, so numeric versus lexical
            # key ordering cannot change the digest on reload.
            evidence=json.loads(json.dumps(tests.EVIDENCE, allow_nan=False)),
            source_refs=refs,
            user_accepted=False,
            P9_10_1b_closed=False,
            full_GRC9V4_conformance=False,
            new_support=[],
            other_six_native_execution=False,
        )
    )


def stem(family):
    if family not in FAMILIES:
        raise ValueError("unselected target family")
    return BASE + "P9-10.1b-" + family + ".json"


def load(root, family):
    paths = [root / stem(family), root / (stem(family) + ".xz")]
    found = [p for p in paths if p.exists()]
    if len(found) != 1:
        raise ValueError("one unambiguous target evidence record required")
    p = found[0]
    raw = p.read_bytes()
    value = json.loads(lzma.decompress(raw) if p.suffix == ".xz" else raw)
    return value, dict(
        path=p.relative_to(root).as_posix(),
        sha256=sha(raw),
        record_digest=value["record_digest"],
        family=family,
    )


def check(root=ROOT, family="C_OS"):
    root = Path(root).resolve()
    prior = predecessors(root)
    value, ref = load(root, family)
    roster = [
        "test_p9101b_target_compatibility." + CLASSES[family] + "." + m for m in METHODS
    ]
    if (
        value != seal(value)
        or value["schema"] != "p9101b-expanded-target-compatibility-v1"
        or value["family"] != family
        or value["status"] != "passed_bounded_target_execution"
        or value["tests"] != roster
        or value["tests_run"] != 3
        or not references_match(root, value["source_refs"], references(root))
        or any(
            value[k] is not False
            for k in (
                "user_accepted",
                "P9_10_1b_closed",
                "full_GRC9V4_conformance",
                "other_six_native_execution",
            )
        )
        or value["new_support"] != []
        or set(value["evidence"]) != {"v1", "v2", "pressure"}
    ):
        raise ValueError("target execution identity/source/scope mismatch")
    historical = next(
        r for r in next(iter(prior.values()))["rows"] if r["family"] == family
    )["enabled_expansion_target"]
    e = value["evidence"]
    if e["v1"]["subject"] != historical or e["v2"]["source_subject"] != historical:
        raise ValueError("target-specific identity replaced by source/family scope")
    for version in ("v1", "v2"):
        v = e[version]
        if (
            v["outcome"] != "successful_target_compatibility"
            or v["surfaces"] != dict.fromkeys(SURFACES, "passed")
            or not all(
                v[k] is True
                for k in (
                    "disabled_replay",
                    "enabled_replay",
                    "full_parent_DAG",
                    "distinct_roles_after_legacy_step",
                )
            )
            or [o["operation"] for o in v["observations"]]
            != ["entry", "step", "reset", "step"]
            or v["enabled_continuation"]["committed"] is not True
        ):
            raise ValueError("target successful execution incomplete")
    if (
        e["v1"]["subject"]["model_identity"] == e["v2"]["subject"]["model_identity"]
        or e["v1"]["subject"]["specialization_id"]
        == e["v2"]["subject"]["specialization_id"]
        or e["v1"]["subject"]["complete_profile_id"]
        != e["v2"]["subject"]["complete_profile_id"]
        or e["pressure"]["outcome"] != "rejection_controls_not_successful_compatibility"
        or len(e["pressure"]["failures"]) != 6
        or not e["pressure"]["complete_publication_rollback"]
    ):
        raise ValueError("target successor or rejection boundary changed")
    return value, ref


def status(root=ROOT):
    rows = [check(root, f) for f in FAMILIES]
    return seal(
        dict(
            schema="p9101b-target-compatibility-status-v1",
            families=list(FAMILIES),
            check_mode="retained_integrity_not_native_rerun",
            tests_run=sum(v["tests_run"] for v, _ in rows),
            user_accepted=False,
            P9_10_1b_closed=False,
            full_GRC9V4_conformance=False,
            compatibility_capability_advertised=False,
            new_support=[],
            G4_accepted=False,
            original_target_surface_cells=16,
            explicit_basin_successor_surface_cells=16,
            other_six_source_cells_executed=0,
            remaining_work=["P9-10.1b acceptance", "P9-10.1c"],
            rows=[
                dict(
                    family=v["family"],
                    versions=[
                        dict(
                            version=k,
                            subject=v["evidence"][k]["subject"],
                            outcome=v["evidence"][k]["outcome"],
                            surfaces=v["evidence"][k]["surfaces"],
                        )
                        for k in ("v1", "v2")
                    ],
                    rejection_controls=6,
                )
                for v, _ in rows
            ],
            records=[r for _, r in rows],
            scope="Exact 17-node targets and explicit basin successors; declared same-graph legacy crossings. No family-wide or all-forty compatibility grant.",
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FAMILIES)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.run and (not args.family or not args.output):
        parser.error(
            "--run requires --family and --output; records are never silently overwritten"
        )
    value = (
        run(ROOT, args.family)
        if args.run
        else check(ROOT, args.family)[0]
        if args.family
        else status(ROOT)
    )
    raw = (json.dumps(value, indent=2) + "\n").encode()
    if args.output:
        path = args.output
        if len(raw) > 1_000_000:
            path = path.with_suffix(path.suffix + ".xz")
            raw = lzma.compress(raw)
        if (
            args.output.exists()
            or args.output.with_suffix(args.output.suffix + ".xz").exists()
        ):
            raise ValueError("evidence output already exists")
        with path.open("xb") as out:
            out.write(raw)
        print(
            json.dumps(
                dict(
                    path=path.as_posix(),
                    bytes=len(raw),
                    record_digest=value["record_digest"],
                )
            )
        )
    else:
        print(raw.decode(), end="")
