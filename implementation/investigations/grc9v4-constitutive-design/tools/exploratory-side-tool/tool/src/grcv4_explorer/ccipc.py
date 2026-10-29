"""Read-only seventh-realization evidence, separate from accepted predecessors."""
import hashlib
from copy import deepcopy
import importlib
import importlib.util
from pathlib import Path
import sys

BASE="implementation/phase-9-grcv4/tranche-8/"
PLAN=BASE+"P9-CCIPC-Tranches8-9-Plan.md"
REVIEW=BASE+"P9-CCIPC-Tranches8-9-Review.json"
STEPS=("8.4d","8.4e","8.4f","8.4g","8.4h","8.4i","8.5","8.6","tranche8_end",
       "9.1b","9.2","9.3","9.4a","9.4b","9.5","9.6")


def restore_inputs(root):
    spec=importlib.util.spec_from_file_location('ccipc_evidence_storage',root/'scripts/evidence_storage.py')
    storage=importlib.util.module_from_spec(spec);spec.loader.exec_module(storage)
    storage.restore(root,prefix=BASE+'P9-8.4d-CCIPC')


def ccipc_status(repo_root):
    root=Path(repo_root).resolve()
    restore_inputs(root)
    directory=root/"implementation/phase-9-grcv4/verification"
    if str(directory) not in sys.path:sys.path.insert(0,str(directory))
    names={PLAN}
    rows=[dict(checkpoint=k,state="pending",user_accepted=False) for k in STEPS]
    review_digest=None
    if (root/REVIEW).exists():
        review=importlib.import_module("p9_ccipc_review")
        value=review.checked(root)
        rows=value["checkpoints"]
        review_digest=value["record_digest"]
        names|={REVIEW,*(r["path"] for r in value["source_bindings"])}
    else:
        # File presence is only progress, never successful execution credit.
        names|={p.relative_to(root).as_posix() for p in (root/BASE).glob("*CCIPC*") if p.is_file()}
    acceptance=importlib.import_module("p9_ccipc_acceptance")
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
    pending=next((r["checkpoint"] for r in rows if r["state"] not in ("passed_pending_acceptance","bounded_accepted")),None)
    return dict(schema="phase9_ccipc_work_v1",family="C_CI_PC",realization_number=7,
        branch="work/p9-aos-tranches-8-9",scope="P9-8.4d through P9-9.6",
        prerequisites="C_CI_PC G2, P9-8.3 and P9-8.4b/c already accepted",
        checkpoints=rows,user_accepted=bool(accepted),aggregate_closed=False,review_digest=review_digest,
        acceptance_digest=accepted['record_digest'] if accepted else None,
        acceptance=(dict(path=acceptance.PATH,record_digest=accepted['record_digest']) if accepted else None),
        accepted_predecessor_families=["C_OS","C_CI","A_CI","A_PC","A_OS","C_PC"],
        remaining_families=["A_CI_PC","C_RG2b","A_RG2b"],
        optional_completion="unselected",tranche10="deferred",
        check_level="retained_integrity_only_no_numerical_rerun",
        large_cap_seconds=3600,
        next_work=("C_CI_PC bounded Tranches 8–9 accepted; P9-10.2 remains deferred." if accepted else
                   "C_CI_PC: P9-"+pending+"; continue through Tranche 9. P9-10.2 deferred." if pending else
                   "C_CI_PC bounded implementation ready for review; user acceptance pending."),
        source_refs=[dict(path=name,sha256=hashlib.sha256((root/name).read_bytes()).hexdigest()) for name in sorted(names)])


def ccipc_source(repo_root,name):
    root=Path(repo_root).resolve()
    refs={r["path"]:r for r in ccipc_status(root)["source_refs"]}
    if name not in refs:raise KeyError("source is outside the checked C_CI_PC index")
    path=(root/name).resolve()
    if not path.is_relative_to(root):raise KeyError("source escapes repository")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=refs[name]["sha256"]:raise ValueError("C_CI_PC source changed during read")
    return raw,refs[name]
