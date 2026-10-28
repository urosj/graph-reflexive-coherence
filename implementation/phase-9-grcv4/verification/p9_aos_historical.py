"""Exact pre-A_OS Tranche 10 source epoch, without replacing numerical code."""
import hashlib
import json
from pathlib import Path
import subprocess

REVISION='02528b5d'
BASE='implementation/phase-9-grcv4/'
SELF=BASE+'verification/p9_aos_historical.py'
PATH=BASE+'tranche-9/P9-AOS-SourceEpochs.json'
ADDITIONS={'tests/models/test_grc_9_v4_aos_integration.py'}
CHANGED={
    *('src/pygrc/models/'+n+'.py' for n in ('grc_9_v4_api_lifecycle','grc_9_v4_legacy','grc_9_v4_owner')),
    *('tests/models/test_grc_9_v4_'+n+'.py' for n in ('contracts','architecture')),
    *(BASE+'verification/'+n+'.py' for n in ('phase9_specialization_acceptance','p994b_runtime_successor',
        'p9101a_native','p9101a_basin_pressure','p9101b_target_compatibility',
        'p9101c_target_basin','p9101c_support_reconciliation')),
}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def seal(value):
    body={k:v for k,v in value.items() if k!='record_digest'}
    return dict(body,record_digest=sha(json.dumps(body,sort_keys=True,separators=(',',':')).encode()))


def original(root,name):
    return subprocess.check_output(['git','show',REVISION+':'+name],cwd=root)


def manifest(root):
    root=Path(root).resolve()
    return seal(dict(schema='p9-aos-source-epochs-v1',predecessor=REVISION,
        checker_sha256=sha((root/SELF).read_bytes()),new_paths=sorted(ADDITIONS),
        sources={name:dict(current_sha256=sha((root/name).read_bytes()),
            predecessor_sha256=sha(original(root,name))) for name in sorted(CHANGED)},
        old_execution_relabelled=False,user_acceptance_inferred=False))


def epoch(root):
    root=Path(root).resolve();value=json.loads((root/PATH).read_bytes())
    if (value!=seal(value) or value['schema']!='p9-aos-source-epochs-v1'
        or value['predecessor']!=REVISION or set(value['sources'])!=CHANGED
        or value['new_paths']!=sorted(ADDITIONS) or value['checker_sha256']!=sha((root/SELF).read_bytes())
        or value['old_execution_relabelled'] is not False or value['user_acceptance_inferred'] is not False):
        raise ValueError('A_OS source epoch scope drift')
    return value


def original_checked(root,name,current_sha,epochs):
    row=epochs['sources'].get(name)
    if row is None or row['current_sha256']!=current_sha:
        raise ValueError('unregistered historical source successor: '+name)
    raw=original(root,name)
    if sha(raw)!=row['predecessor_sha256']:
        raise ValueError('historical Git source drift: '+name)
    return raw


def references_match(root,expected,current):
    """Authenticate the original roster; exclude only the named new test."""
    root=Path(root).resolve();epochs=epoch(root)
    old={r['path']:r for r in expected};new={r['path']:r for r in current}
    if len(old)!=len(expected) or len(new)!=len(current) or not set(old)<=set(new) or set(new)-set(old)-ADDITIONS:
        return False
    for name,row in old.items():
        if row==new[name]:continue
        raw=original_checked(root,name,new[name]['sha256'],epochs)
        if row!=dict(path=name,sha256=sha(raw)):return False
    return True


def reference(root,name):
    root=Path(root).resolve();current=sha((root/name).read_bytes())
    if name in CHANGED:current=sha(original_checked(root,name,current,epoch(root)))
    return dict(path=name,sha256=current)


def read_source(root,ref):
    root=Path(root).resolve();name=ref['path'];path=Path(name)
    if path.is_absolute() or '..' in path.parts:raise KeyError('nonportable source')
    raw=(root/path).read_bytes()
    if sha(raw)!=ref['sha256']:
        raw=original_checked(root,name,sha(raw),epoch(root))
        if sha(raw)!=ref['sha256']:raise ValueError('source does not match historical reference')
        ref=dict(ref,revision=REVISION,basis='historical_git')
    return raw,ref


if __name__=='__main__':
    root=Path(__file__).resolve().parents[3]
    target=root/PATH
    with target.open('x') as stream:json.dump(manifest(root),stream,indent=2);stream.write('\n')
