"""P9-9.5 execution or retained-integrity checking; checking never runs the model."""

import argparse
import hashlib
import json
import lzma
import math
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/tranche-9/"
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")
CLASSES = dict(
    zip(FAMILIES, ("COSConflict", "CCIConflict", "ACIConflict", "APCConflict"))
)
NAMES = (
    "test_public_step_and_run_preserve_entire_publication",
    "test_rejected_operation_is_absent_from_replay_and_reset",
    "test_strict_native_trigger_boundaries_not_saturation_alone",
)
AUTHORITY = BASE + "P9-9.5-Authority.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ),
    )


def filename(family):
    if family not in FAMILIES:
        raise ValueError("unselected conflict family")
    return BASE + "P9-9.5-" + family + ".json"


def predecessor(root):
    from p994b_acceptance import decision, PATH

    v = decision(root)
    return dict(
        path=PATH,
        sha256=sha((root / PATH).read_bytes()),
        record_digest=v["record_digest"],
    )


def run(root, family):
    sys.path[:0] = [str(root), str(root / "src")]
    import test_p995_public_conflict as tests

    tests.EVIDENCE.clear()
    sources = list((root / "src").rglob("*.py"))
    sources += list((root / "src/pygrc/models/grc_v4_assets").glob("*.json"))
    sources += list((root / "tests/models").glob("test_grc*.py"))
    sources += [Path(__file__).resolve(), Path(tests.__file__).resolve()]
    authority = json.loads((root / AUTHORITY).read_bytes())
    inputs = [
        root / name
        for name in (
            BASE + f"P9-9.1b-{family}.json",
            AUTHORITY,
            authority["rows"][0]["source_ref"]["path"],
            "specs/grc-9-v4-spec.md",
            "specs/grc-common-interface-v4-ext.md",
        )
    ]

    def refs(paths):
        return [
            dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
            for p in sorted(set(paths))
        ]

    prior = predecessor(root)
    before = refs(sources + inputs)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        getattr(tests, CLASSES[family])
    )
    roster = [t.id() for t in suite]
    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError("public conflict suite failed")
    if refs(sources + inputs) != before:
        raise ValueError("execution input changed during run")
    imported = {
        Path(m.__file__).resolve()
        for m in list(sys.modules.values())
        if getattr(m, "__file__", None)
    }
    return seal(
        dict(
            schema="p995-public-conflict-execution-v1",
            family=family,
            outcome="passed",
            tests=roster,
            tests_run=result.testsRun,
            failures=0,
            errors=0,
            skips=0,
            predecessor=prior,
            elapsed_seconds=time.monotonic() - start,
            source_refs=refs(
                [p for p in sources if p in imported or p.suffix == ".json"]
            ),
            input_refs=refs(inputs),
            execution=dict(
                python=sys.version.split()[0],
                exact_backend="flint",
                numerical_policy="legacy_exact_v1",
                workers_per_record=1,
            ),
            evidence=tests.EVIDENCE,
            public_api=True,
            user_accepted=False,
            full_GRC9V4_conformance=False,
            aggregate_closed=False,
            scope="four_family_public_disabled_saturated_conflict",
        )
    )


def read(root, family):
    p = root / filename(family)
    q = p.with_suffix(".json.xz")
    if p.exists() and q.exists():
        raise ValueError("ambiguous evidence storage")
    return json.loads(p.read_bytes() if p.exists() else lzma.decompress(q.read_bytes()))


def check(root, family):
    root = Path(root).resolve()
    v = read(root, family)
    if (
        v != seal(v)
        or v["schema"] != "p995-public-conflict-execution-v1"
        or v["family"] != family
        or v["outcome"] != "passed"
        or v["tests_run"] != 3
        or v["tests"]
        != ["test_p995_public_conflict." + CLASSES[family] + "." + n for n in NAMES]
        or any(
            v[k]
            for k in (
                "errors",
                "failures",
                "skips",
                "user_accepted",
                "aggregate_closed",
                "full_GRC9V4_conformance",
            )
        )
        or v["public_api"] is not True
        or v["predecessor"] != predecessor(root)
        or v["scope"] != "four_family_public_disabled_saturated_conflict"
        or v["execution"]["exact_backend"] != "flint"
        or v["execution"]["numerical_policy"] != "legacy_exact_v1"
    ):
        raise ValueError("invalid bounded public conflict evidence")
    e = v["evidence"]
    if set(e) != {"rejection", "replay_reset", "boundaries"}:
        raise ValueError("incomplete conflict evidence")
    r, replay = e["rejection"], e["replay_reset"]
    c, f = r["candidate"], r["failure"]
    if (
        r["occupied_ports"] != list(range(1, 10))
        or r["legacy_conflict_endpoint"] != ["s_2", 5]
        or c["active_degree"] != 9
        or c["eps_gradient"] != 0.05
        or c["eps_spark"] != 0.05
        or not 0 < c["gradient_norm"] < c["eps_gradient"]
        or not 0 < c["min_signed_hessian"] < c["eps_spark"]
        or any(
            c[k] is not True
            for k in (
                "saturation_gate",
                "basin_interior_gate",
                "signed_hessian_degeneracy_gate",
            )
        )
        or f["code"] != "legacy_expansion_target_undefined"
        or f["stage"] != "target_readmission"
        or f["prestate_digest"] != f["poststate_digest"]
        or f["pre_lifecycle_digest"] != f["post_lifecycle_digest"]
        or r["before_snapshot_sha256"] != r["after_snapshot_sha256"]
        or r["before_snapshot_sha256"] != replay["checkpoint_sha256"]
        or r["current_state_digest"] == r["reset_state_digest"]
        or r["successful_receipts"] <= 0
        or r["journal_actions"] != 1
        or r["rejected_public_calls"] != 3
        or any(
            r[k] is not True
            for k in (
                "whole_publication_preserved",
                "successful_history_unchanged",
                "no_v4_substitution",
                "fresh_native_candidate_observed",
            )
        )
        or replay["rejected_actions_in_journal"] != 0
        or any(
            replay[k] is not True
            for k in (
                "duplicate_exact",
                "save_load_exact",
                "deterministic_rejection",
                "reset_native_parity",
                "reset_next_step_native_parity",
                "original_unchanged",
            )
        )
    ):
        raise ValueError("missing conflict/rollback/replay discrimination")
    rows = e["boundaries"]
    expected = [
        (p, d, label)
        for p, d in (
            ("eps_gradient", "gradient_norm"),
            ("eps_spark", "min_signed_hessian"),
        )
        for label in ("below", "equal", "above")
    ]
    if len(rows) != len(expected):
        raise ValueError("incomplete native trigger boundary controls")
    for row, (parameter, diagnostic, position) in zip(rows, expected):
        value = c[diagnostic]
        threshold = (
            value
            if position == "equal"
            else math.nextafter(value, math.inf if position == "above" else -math.inf)
        )
        if row != dict(
            parameter=parameter,
            diagnostic=diagnostic,
            value=value,
            position=position,
            threshold=threshold,
            candidate_count=int(position == "above"),
            outcome="rejected_undefined"
            if position == "above"
            else "native_step_equal",
        ):
            raise ValueError("native strict-boundary evidence mismatch")
    refs = v["source_refs"] + v["input_refs"]
    if len({r["path"] for r in refs}) != len(refs):
        raise ValueError("duplicate source binding")
    required = {
        "src/pygrc/models/grc_9_v4.py",
        "src/pygrc/models/grc_9_v4_crossing.py",
        "src/pygrc/models/grc_9_v4_legacy.py",
        "src/pygrc/models/grc_9_v3.py",
        "src/pygrc/models/grc_9_v3_sparks.py",
        AUTHORITY,
        "implementation/phase-9-grcv4/verification/test_p995_public_conflict.py",
        "implementation/phase-9-grcv4/verification/p995_public_conflict.py",
    }
    if not required <= {r["path"] for r in refs}:
        raise ValueError("missing critical source binding")
    for ref in refs:
        from p994b_runtime_successor import historical_source

        p = (root / ref["path"]).resolve()
        if (
            Path(ref["path"]).is_absolute()
            or not p.is_relative_to(root)
            or (
                sha(p.read_bytes()) != ref["sha256"]
                and historical_source(root, ref["path"], ref["sha256"]) != ref["sha256"]
            )
        ):
            raise ValueError("public conflict input drift: " + ref["path"])
    return v


def status(root):
    root = Path(root).resolve()
    records = [check(root, f) for f in FAMILIES]
    paths = [filename(f) for f in FAMILIES] + [AUTHORITY, BASE + "P9-9.5-Review.md"]
    refs = []
    for name in paths:
        p = root / name
        if not p.exists():
            p = p.with_suffix(".json.xz")
        refs.append(
            dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
        )
    return dict(
        schema="p995-public-conflict-status-v1",
        iteration="P9-9.5",
        families=list(FAMILIES),
        state="executed_pending_acceptance",
        user_accepted=False,
        public_api=True,
        aggregate_closed=False,
        full_GRC9V4_conformance=False,
        check_level="retained_integrity_only_no_native_rerun",
        records=[
            dict(
                family=v["family"],
                tests=v["tests_run"],
                outcome=v["outcome"],
                record_digest=v["record_digest"],
                elapsed_seconds=v["elapsed_seconds"],
                failure_code=v["evidence"]["rejection"]["failure"]["code"],
                rollback=True,
                boundary_controls=len(v["evidence"]["boundaries"]),
            )
            for v in records
        ],
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
            raise FileExistsError(
                "retained execution already exists; check it or run the tests directly"
            )
        v = run(ROOT, args.family)
        raw = (json.dumps(v, indent=2) + "\n").encode()
        if len(raw) > 1_000_000:
            p, raw = p.with_suffix(".json.xz"), lzma.compress(raw)
        with p.open("xb") as stream:
            stream.write(raw)
    else:
        v = check(ROOT, args.family)
    print(
        json.dumps(
            dict(
                family=args.family,
                outcome=v["outcome"],
                record_digest=v["record_digest"],
                mode="native_execution" if args.run else "retained_integrity_only",
            )
        )
    )


if __name__ == "__main__":
    main()
