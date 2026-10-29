"""Current fifth-realization work, separate from accepted four-family evidence."""

import hashlib
import importlib
import importlib.util
from pathlib import Path
import sys
from copy import deepcopy

BASE = "implementation/phase-9-grcv4/tranche-8/"
PLAN = BASE + "P9-AOS-Tranches8-9-Plan.md"
STEPS = ("8.4d", "8.4e", "8.4f", "8.4g", "8.4h", "8.4i", "8.5", "8.6",
         "tranche8_end", "9.1b", "9.2", "9.3", "9.4a", "9.4b", "9.5", "9.6")


def restore_inputs(root):
    """Authenticate and restore the one expanded A_OS input on fresh checkouts."""
    spec = importlib.util.spec_from_file_location(
        "aos_evidence_storage", root / "scripts/evidence_storage.py")
    storage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(storage)
    storage.restore(root, prefix=BASE + "P9-8.4d-AOSOracleInputs.json")


def aos_status(repo_root):
    root = Path(repo_root).resolve()
    restore_inputs(root)
    path = root / "implementation/phase-9-grcv4/verification"
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    review = importlib.import_module("p9_aos_review")
    names = {PLAN}
    rows = [dict(checkpoint=k, state="pending", user_accepted=False) for k in STEPS]
    review_digest = None
    if (root / review.PATH).is_file():
        value = review.checked(root)
        rows = value["checkpoints"]
        review_digest = value["record_digest"]
        names |= {review.PATH, *(r["path"] for r in value["source_bindings"])}
    else:
        # An in-progress record is not a completed bounded review. The complete
        # consumer runs when the review is built; this view never starts solvers.
        names |= {p for p in review.required_paths() if (root / p).is_file()}
    acceptance=importlib.import_module("p9_aos_acceptance")
    accepted=acceptance.decision(root)
    if accepted:
        rows=deepcopy(rows)
        for row in rows:
            row.update(state="bounded_accepted",user_accepted=True)
            if row['checkpoint']=='9.3':
                row['execution']['execution_counts']=row['execution']['counts']
                row['execution']['counts']=accepted['compatibility_counts']
        names|={acceptance.PATH,acceptance.EPOCHS,acceptance.SELF,acceptance.TEST,
                *(r['path'] for r in accepted['validation'])}
    pending = next((r["checkpoint"] for r in rows if r["state"] not in ("passed_pending_acceptance","bounded_accepted")), None)
    return dict(schema="phase9_aos_work_v1", family="A_OS", realization_number=5,
        branch="work/p9-aos-tranches-8-9", scope="P9-8.4d through P9-9.6",
        prerequisites="A_OS P9-8.4b/c already accepted; historical evidence unchanged",
        checkpoints=rows, user_accepted=bool(accepted), aggregate_closed=False,
        acceptance_digest=accepted['record_digest'] if accepted else None,
        acceptance=(dict(path=acceptance.PATH,record_digest=accepted['record_digest']) if accepted else None),
        first_group_families=["C_OS", "C_CI", "A_CI", "A_PC"],
        remaining_families=["C_PC", "C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"],
        optional_completion="unselected", tranche10="deferred",
        check_level="retained_integrity_only_no_numerical_rerun", review_digest=review_digest,
        next_work=("A_OS bounded Tranches 8–9 accepted; P9-10.2 remains deferred." if accepted else
                   "A_OS: P9-" + pending + "; continue the fifth realization through Tranche 9. P9-10.2 deferred."
                   if pending else "A_OS bounded implementation ready for review; user acceptance pending."),
        source_refs=[dict(path=name, sha256=hashlib.sha256((root / name).read_bytes()).hexdigest())
                     for name in sorted(names)])


def aos_source(repo_root, name):
    root = Path(repo_root).resolve()
    refs = {r["path"]: r for r in aos_status(root)["source_refs"]}
    if name not in refs:
        raise KeyError("source is outside the checked A_OS index")
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise KeyError("source escapes repository")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != refs[name]["sha256"]:
        raise ValueError("A_OS source changed during read")
    return raw, refs[name]
