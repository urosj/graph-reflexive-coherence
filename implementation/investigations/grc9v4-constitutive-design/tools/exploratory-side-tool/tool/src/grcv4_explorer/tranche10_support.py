"""Current bounded support reconciliation; historical P9-9.6 stays accessible."""

from pathlib import Path
import sys

PROJECTION = "d37eeef3f4306e7f8a290bf0e4566e021e2f75e9fb10effba5089cfeb99ca5b6"


def _checker(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import p9101c_acceptance

    return root, p9101c_acceptance


def tranche10_support_status(root):
    root, checker = _checker(root)
    value = checker.status(root)
    if value["record_digest"] != PROJECTION:
        raise ValueError(
            "support reconciliation differs from the pinned review subject"
        )
    return value


def tranche10_support_source(root, name):
    root, checker = _checker(root)
    value = tranche10_support_status(root)
    refs = {r["path"]: r for r in value["source_refs"]}
    for path in (checker.PATH, checker.REVIEW, checker.execution.PATH):
        refs[path] = checker.execution.ref(root, path)
    if name not in refs or Path(name).is_absolute() or ".." in Path(name).parts:
        raise KeyError("source is not indexed by the support reconciliation")
    from p9_aos_historical import read_source
    return read_source(root, refs[name])
