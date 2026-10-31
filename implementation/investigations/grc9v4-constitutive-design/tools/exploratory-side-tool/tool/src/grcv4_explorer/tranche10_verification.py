"""P9-10.2 saved-evidence checks; never execute native trajectories on access."""

from pathlib import Path
import sys


def _checker(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import p9102_verification
    return root, p9102_verification


def tranche10_verification_status(root):
    root, checker = _checker(root)
    from p9102_acceptance import status
    return status(root)


def tranche10_verification_source(root, name):
    root, checker = _checker(root)
    value = tranche10_verification_status(root)
    refs = {r["path"]: r for r in value["source_refs"]}
    for row in value["families_checked"]:
        for ref in (row["execution_ref"], row["exact_target_ref"],
                    row["inherited_replay_modes"]["source_ref"]):
            refs[ref["path"]] = ref
    refs[value["predecessor"]["path"]] = value["predecessor"]
    refs[checker.PATH] = checker.reference(root, checker.PATH)
    if name not in refs or Path(name).is_absolute() or ".." in Path(name).parts:
        raise KeyError("source is not indexed by P9-10.2")
    from p910_basin_source_epoch import read_source
    return read_source(root, refs[name])
