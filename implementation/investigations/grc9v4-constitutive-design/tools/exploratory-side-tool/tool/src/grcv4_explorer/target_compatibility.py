"""Exact expanded-target evidence; support reconciliation belongs to P9-10.1c."""

from pathlib import Path
import sys

PROJECTION = "05ceba81064f1e4bb336a2b89dc2fbd7d8a4f1516baf30f3a6082b459422f2aa"


def _checker(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import p9101b_target_compatibility

    return root, p9101b_target_compatibility


def target_compatibility_status(root):
    root, checker = _checker(root)
    import p9101b_acceptance

    value = p9101b_acceptance.status(root)
    if value["record_digest"] != PROJECTION:
        raise ValueError("expanded-target evidence differs from the pinned subject")
    return value


def target_compatibility_source(root, name):
    root, checker = _checker(root)
    view = target_compatibility_status(root)
    refs = {
        r["path"]: r
        for r in (*view["records"], *view["source_refs"], *checker.load(root, "C_OS")[0]["source_refs"])
    }
    if name not in refs or Path(name).is_absolute() or ".." in Path(name).parts:
        raise KeyError("source is not indexed by expanded-target evidence")
    from p9_aos_historical import read_source
    return read_source(root, refs[name])
