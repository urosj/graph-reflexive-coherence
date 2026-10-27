"""Read-only first-group Tranche 9 execution evidence; no authority promotion."""

import hashlib
import importlib
from pathlib import Path
import sys


def _checker(root):
    path = Path(root) / "implementation/phase-9-grcv4/verification"
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    return importlib.import_module("p991b_lifecycle")


def tranche9_status(repo_root):
    root = Path(repo_root).resolve()
    checker = _checker(root)
    records = [checker.check(root, family) for family in checker.FAMILIES]
    from p991b_acceptance import decision

    accepted = decision(root)
    names = [checker.filename(f) for f in checker.FAMILIES]
    names += [
        checker.BASE + n
        for n in (
            "P9-9.1b-Review.md",
            "P9-9.1b-Authority.json",
            "P9-9.1b-Acceptance.json",
        )
    ]
    refs = []
    for name in names:
        path = root / name
        if not path.is_file() and name.endswith(".json"):
            path = path.with_suffix(".json.xz")
        refs.append(
            dict(
                path=path.relative_to(root).as_posix(),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )
    return dict(
        schema="phase9_tranche9_first_group_v1",
        iteration="P9-9.1b",
        state="bounded_accepted",
        families=list(checker.FAMILIES),
        check_level="retained_integrity_only_no_numerical_rerun",
        user_accepted=accepted["user_accepted"],
        aggregate_closed=False,
        full_GRC9V4_conformance=False,
        optional_completion="unselected",
        disabled_compatibility="pending_16_selected_cells",
        next_work="P9-9.2: execute sixteen selected compatibility cells; retain the full P9-9.3 matrix.",
        records=[
            dict(
                family=v["family"],
                tests=v["tests_run"],
                outcome=v["outcome"],
                elapsed_seconds=v["elapsed_seconds"],
                record_digest=v["record_digest"],
                successful_groups=v["evidence"]["successful_groups"],
                exact_replay=v["evidence"]["exact_replay"],
            )
            for v in records
        ],
        source_refs=refs,
    )


def tranche9_source(repo_root, path):
    root = Path(repo_root).resolve()
    view = tranche9_status(root)
    refs = {r["path"]: r for r in view["source_refs"]}
    if path not in refs:
        raise KeyError("unindexed Tranche 9 source")
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != refs[path]["sha256"]:
        raise ValueError("source changed during read")
    return raw, refs[path]


def tranche9_compatibility_status(repo_root):
    root = Path(repo_root).resolve()
    _checker(root)  # Install the repository-owned verification import path.
    return importlib.import_module("p993_acceptance").status(root)


def tranche9_compatibility_source(repo_root, path):
    root = Path(repo_root).resolve()
    refs = {r["path"]: r for r in tranche9_compatibility_status(root)["source_refs"]}
    if path not in refs:
        raise KeyError("unindexed compatibility source")
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != refs[path]["sha256"]:
        raise ValueError("source changed during read")
    return raw, refs[path]


def tranche9_crossing_status(repo_root):
    root = Path(repo_root).resolve()
    _checker(root)
    return importlib.import_module("p994a_acceptance").status(root)


def tranche9_crossing_source(repo_root, path):
    root = Path(repo_root).resolve()
    refs = {r["path"]: r for r in tranche9_crossing_status(root)["source_refs"]}
    if path not in refs:
        raise KeyError("unindexed crossing source")
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != refs[path]["sha256"]:
        raise ValueError("source changed during read")
    return raw, refs[path]
