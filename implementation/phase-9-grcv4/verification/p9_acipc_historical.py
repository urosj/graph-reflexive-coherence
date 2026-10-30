"""Finite A_CI+PC source epoch preserving the accepted seven-realization evidence.

Only exact named successors are projected to immutable Git bytes. Numerical
producers are never replaced and old executions never certify this successor.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess

REVISION="b61b60be"
BASE="implementation/phase-9-grcv4/"
SIDE="implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF=BASE+"verification/p9_acipc_historical.py"
PATH=BASE+"tranche-9/P9-ACIPC-SourceEpochs.json"
CHANGED={
    'artifact-storage.json', '.gitignore',
    *("src/pygrc/models/"+name+".py" for name in ("grc_9_v4_api_lifecycle","grc_9_v4_legacy","grc_9_v4_owner")),
    *("tests/models/test_grc_9_v4_"+name+".py" for name in ("contracts","architecture","crossing","owner","aos_integration","cpc_integration","ccipc_integration")),
    *(BASE+"verification/"+name+".py" for name in ("phase9_specialization_acceptance","phase9_implementation_policy",
        "p994b_runtime_successor","p9_ccipc_acceptance","p9_ccipc_historical")),
    *("implementation/Phase-9-GRCV4-"+name+".md" for name in ("Handoff","ImplementationPlan","ImplementationChecklist")),
}
CHANGED.update({SIDE+p for p in ("scripts/serve_phase9.py","scripts/run_phase9_notebook.py",
    "src/grcv4_explorer/phase9_verification.py","phase9-web/index.html","notebooks/phase9_verification.ipynb")})
CHANGED.update({SIDE.removesuffix("tool/")+"GRCV4ExploratorySideToolImplementation"+suffix+".md" for suffix in ("Plan","Checklist")})
ADDITIONS={"tests/models/test_grc_9_v4_acipc_integration.py",SIDE+"src/grcv4_explorer/acipc.py",
           BASE+"verification/test_p9_acipc_history.py"}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def implementation_sha(root,name,present):
    from p9_crg2b_historical import peel_sha
    from p9_acipc_acceptance import previous_sha
    present=peel_sha(root,name,present)
    return previous_sha(root,name,present) or present


def seal(value):
    body={k:v for k,v in value.items() if k!="record_digest"}
    return dict(body,record_digest=sha(json.dumps(body,sort_keys=True,separators=(",",":")).encode()))


@lru_cache(maxsize=256)
def original(root,name):
    return subprocess.check_output(["git","show",REVISION+":"+name],cwd=root)


def manifest(root):
    root=Path(root).resolve()
    return seal(dict(schema="p9-acipc-source-epochs-v1",predecessor=REVISION,
        checker_sha256=sha((root/SELF).read_bytes()),
        sources={name:dict(before_sha256=sha(original(root,name)),after_sha256=sha((root/name).read_bytes())) for name in sorted(CHANGED)},
        additions={name:sha((root/name).read_bytes()) for name in sorted(ADDITIONS)},
        old_execution_relabelled=False,user_acceptance_inferred=False))


def epochs(root):
    root=Path(root).resolve()
    value=json.loads((root/PATH).read_bytes())
    if (value!=seal(value) or value["schema"]!="p9-acipc-source-epochs-v1" or value["predecessor"]!=REVISION
        or value["checker_sha256"]!=implementation_sha(root,SELF,sha((root/SELF).read_bytes())) or set(value["sources"])!=CHANGED
        or set(value["additions"])!=ADDITIONS or value["old_execution_relabelled"] is not False
        or value["user_acceptance_inferred"] is not False):
        raise ValueError("A_CI_PC source epoch scope drift")
    return value


def previous_sha(root,name,present):
    name=Path(name).as_posix()
    if name not in CHANGED:return None
    root=Path(root).resolve()
    present=implementation_sha(root,name,present)
    row=epochs(root)["sources"][name]
    if (present not in (row["before_sha256"],row["after_sha256"]) or implementation_sha(root,name,sha((root/name).read_bytes()))!=row["after_sha256"]
            or sha(original(root,name))!=row["before_sha256"]):
        raise ValueError("unregistered A_CI_PC source successor: "+name)
    return row["before_sha256"]


def project_sha(root,name,present):
    name=Path(name).as_posix()
    return previous_sha(root,name,present) if name in CHANGED else implementation_sha(root,name,present)


def peel_sha(root,name,present):
    """Remove this epoch before an older validator authenticates its subject.

    Older validators may call repeatedly with an already translated hash.
    Always authenticate the live successor, but leave older incoming subjects
    for their owning validator. This function alone does not validate them.
    """
    name=Path(name).as_posix()
    present=implementation_sha(root,name,present)
    if name not in CHANGED:return present
    live=sha((Path(root)/name).read_bytes())
    before=previous_sha(root,name,live)
    row=epochs(root)['sources'][name]
    return before if present==row['after_sha256'] else present


def matches(root,name,expected):
    present=sha((Path(root)/name).read_bytes())
    return present==expected or project_sha(root,name,present)==expected


def project(root,current):
    from p9_crg2b_historical import project as connected_project
    current=connected_project(root,current)
    root=Path(root).resolve()
    result={name:project_sha(root,name,present) for name,present in current.items()}
    for name in ADDITIONS & result.keys():
        expected=epochs(root)["additions"][name]
        if result[name]!=expected or implementation_sha(root,name,sha((root/name).read_bytes()))!=expected:
            raise ValueError("unregistered A_CI_PC roster addition: "+name)
        del result[name]
    return result
