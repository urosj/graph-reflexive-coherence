"""Finite C_PC source epoch preserving the accepted five-realization evidence.

Only exact named successors are projected to immutable Git bytes. Numerical
producers are never replaced and old executions never certify this successor.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess

REVISION="c9853012"
BASE="implementation/phase-9-grcv4/"
SIDE="implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF=BASE+"verification/p9_cpc_historical.py"
PATH=BASE+"tranche-9/P9-CPC-SourceEpochs.json"
CHANGED={
    *("src/pygrc/models/"+name+".py" for name in ("grc_9_v4_api_lifecycle","grc_9_v4_legacy","grc_9_v4_owner")),
    *("tests/models/test_grc_9_v4_"+name+".py" for name in ("contracts","architecture","crossing","aos_integration")),
    *(BASE+"verification/"+name+".py" for name in ("phase9_specialization_acceptance","phase9_implementation_policy",
        "p994b_runtime_successor","p9_aos_review","p9_aos_acceptance","p9_aos_historical","p9_aos_g2_sources")),
}
CHANGED.update({SIDE+p for p in ("scripts/serve_phase9.py","scripts/run_phase9_notebook.py",
    "src/grcv4_explorer/phase9_verification.py","phase9-web/index.html","notebooks/phase9_verification.ipynb")})
ADDITIONS={"tests/models/test_grc_9_v4_cpc_integration.py",SIDE+"src/grcv4_explorer/cpc.py"}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def seal(value):
    body={k:v for k,v in value.items() if k!="record_digest"}
    return dict(body,record_digest=sha(json.dumps(body,sort_keys=True,separators=(",",":")).encode()))


@lru_cache(maxsize=256)
def original(root,name):
    return subprocess.check_output(["git","show",REVISION+":"+name],cwd=root)


def manifest(root):
    root=Path(root).resolve()
    return seal(dict(schema="p9-cpc-source-epochs-v1",predecessor=REVISION,
        checker_sha256=sha((root/SELF).read_bytes()),
        sources={name:dict(before_sha256=sha(original(root,name)),after_sha256=sha((root/name).read_bytes())) for name in sorted(CHANGED)},
        additions={name:sha((root/name).read_bytes()) for name in sorted(ADDITIONS)},
        old_execution_relabelled=False,user_acceptance_inferred=False))


def epochs(root):
    root=Path(root).resolve()
    value=json.loads((root/PATH).read_bytes())
    if (value!=seal(value) or value["schema"]!="p9-cpc-source-epochs-v1" or value["predecessor"]!=REVISION
        or value["checker_sha256"]!=sha((root/SELF).read_bytes()) or set(value["sources"])!=CHANGED
        or set(value["additions"])!=ADDITIONS or value["old_execution_relabelled"] is not False
        or value["user_acceptance_inferred"] is not False):
        raise ValueError("C_PC source epoch scope drift")
    return value


def previous_sha(root,name,present):
    name=Path(name).as_posix()
    if name not in CHANGED:return None
    root=Path(root).resolve()
    row=epochs(root)["sources"][name]
    if (present!=row["after_sha256"] or sha((root/name).read_bytes())!=present
            or sha(original(root,name))!=row["before_sha256"]):
        raise ValueError("unregistered C_PC source successor: "+name)
    return row["before_sha256"]


def project_sha(root,name,present):
    name=Path(name).as_posix()
    return previous_sha(root,name,present) if name in CHANGED else present


def matches(root,name,expected):
    present=sha((Path(root)/name).read_bytes())
    return present==expected or project_sha(root,name,present)==expected


def project(root,current):
    root=Path(root).resolve()
    result={name:project_sha(root,name,present) for name,present in current.items()}
    for name in ADDITIONS & result.keys():
        expected=epochs(root)["additions"][name]
        if result[name]!=expected or sha((root/name).read_bytes())!=expected:
            raise ValueError("unregistered C_PC roster addition: "+name)
        del result[name]
    return result
