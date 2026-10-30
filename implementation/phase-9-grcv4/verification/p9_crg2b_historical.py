"""Finite connected-completion successor; accepted executions stay unchanged."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess

BASE='dbc013fb'
PREFIX='implementation/phase-9-grcv4/'
SIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/'
SELF=PREFIX+'verification/p9_crg2b_historical.py'
PATH=PREFIX+'tranche-8/P9-CRG2b-SourceEpochs.json'
CHANGED={
    'artifact-storage.json','.gitignore',
    'scripts/evidence_storage.py','docs/reference/EvidenceStorage.md',
    *('src/pygrc/models/'+name+'.py' for name in
      ('grc_v4_rg2b','grc_9_v4_api_lifecycle','grc_9_v4_owner','grc_9_v4_legacy')),
    *('tests/models/test_grc_9_v4_'+name+'_integration.py' for name in ('aos','cpc','ccipc','acipc')),
    *(PREFIX+'verification/'+name+'.py' for name in
      ('p9_acipc_acceptance','p9_acipc_historical','phase9_implementation_policy','phase9_specialization_acceptance')),
    *('implementation/Phase-9-GRCV4-'+name+'.md' for name in
      ('ImplementationPlan','ImplementationChecklist','Handoff')),
    *(SIDE+'GRCV4ExploratorySideToolImplementation'+name+'.md' for name in ('Plan','Checklist')),
    *(SIDE+'tool/'+name for name in ('scripts/serve_phase9.py','scripts/run_phase9_notebook.py',
       'src/grcv4_explorer/phase9_verification.py','phase9-web/index.html','notebooks/phase9_verification.ipynb')),
}

ADDITIONS={'src/pygrc/models/grc_9_v4_crg2b_connected.py',
           'scripts/evidence_dedup.py','tests/test_evidence_dedup.py',
           'tests/models/test_grc_9_v4_crg2b_integration.py',
           SIDE+'tool/src/grcv4_explorer/crg2b.py'}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def seal(value):
    body={k:v for k,v in value.items() if k!='record_digest'}
    return dict(body,record_digest=sha(json.dumps(body,sort_keys=True,separators=(',',':')).encode()))


@lru_cache(maxsize=64)
def original(root,name):return subprocess.check_output(['git','show',BASE+':'+name],cwd=root)


def manifest(root):
    root=Path(root).resolve()
    return seal(dict(schema='p9-crg2b-connected-epochs-v1',predecessor=BASE,
        checker_sha256=sha((root/SELF).read_bytes()),
        sources={name:dict(before_sha256=sha(original(root,name)),after_sha256=sha((root/name).read_bytes())) for name in sorted(CHANGED)},
        additions={name:sha((root/name).read_bytes()) for name in sorted(ADDITIONS)},
        native_sources_changed=True,accepted_evidence_rewritten=False,user_acceptance_inferred=False))


def epochs(root):
    from p9_arg2b_historical import peel_sha
    root=Path(root).resolve();value=json.loads((root/PATH).read_bytes())
    if value!=seal(value) or value['schema']!='p9-crg2b-connected-epochs-v1' or value['predecessor']!=BASE \
        or set(value['sources'])!=CHANGED or value['checker_sha256']!=peel_sha(root,SELF,sha((root/SELF).read_bytes())) \
        or value['native_sources_changed'] is not True or set(value['additions'])!=ADDITIONS \
        or any(value[k] is not False for k in ('accepted_evidence_rewritten','user_acceptance_inferred')):
        raise ValueError('C_RG2b research source epoch drift')
    return value


def peel_sha(root,name,present):
    from p9_arg2b_historical import peel_sha as successor_sha
    present=successor_sha(root,name,present)
    name=Path(name).as_posix()
    if name not in CHANGED:return present
    root=Path(root).resolve();row=epochs(root)['sources'][name]
    if successor_sha(root,name,sha((root/name).read_bytes()))!=row['after_sha256'] or sha(original(root,name))!=row['before_sha256']:
        raise ValueError('unregistered C_RG2b research successor: '+name)
    return row['before_sha256'] if present==row['after_sha256'] else present


def project(root,current):
    from p9_arg2b_historical import project as successor_project
    from p9_arg2b_historical import peel_sha as successor_sha
    current=successor_project(root,current)
    root=Path(root).resolve();value=epochs(root)
    result={name:peel_sha(root,name,present) for name,present in current.items()}
    for name in ADDITIONS & result.keys():
        expected=value['additions'][name]
        if result[name]!=expected or successor_sha(root,name,sha((root/name).read_bytes()))!=expected:
            raise ValueError('unregistered connected C_RG2b addition: '+name)
        del result[name]
    return result
