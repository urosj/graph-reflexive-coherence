"""Native basin evidence, separate from immutable scientific authority traces."""

from pathlib import Path
import sys

PROJECTION = "b805bcc2cc8d62a9321a0ef5e45f4e807bba1b63cbfbfd314443ff67990a6d13"


def _checker(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import p9101a_acceptance

    return root, p9101a_acceptance


def basin_native_status(root):
    root, checker = _checker(root)
    value = checker.status(root)
    if value["record_digest"] != PROJECTION:
        raise ValueError("native basin evidence differs from the pinned review subject")
    return value


def basin_native_source(root, name):
    root, checker = _checker(root)
    view = basin_native_status(root)
    refs = {r["path"]: r for r in (*view["records"], *view["source_refs"])}
    for group in checker.execution.predecessor.CLASSES:
        refs.update(
            (r["path"], r)
            for r in checker.execution.predecessor.check(root, group)["source_refs"]
        )
    for group in checker.execution.GROUPS:
        refs.update(
            (r["path"], r)
            for r in checker.execution.check(root, group)[0]["source_refs"]
        )
    if name not in refs or Path(name).is_absolute() or ".." in Path(name).parts:
        raise KeyError("source is not part of the native basin evidence")
    from p9_aos_historical import read_source
    return read_source(root, refs[name])
