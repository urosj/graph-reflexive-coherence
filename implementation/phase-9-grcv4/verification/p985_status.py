"""Read-only 8.5 family projection; acceptance is separate from execution flags."""
import json
from contextlib import contextmanager
from pathlib import Path
import subprocess
import os
import sys
from unittest.mock import patch
import p985_cos as cos
import p985_batch as batch

ACCEPTANCE=cos.BASE+'P9-8.5-COSAcceptance.json'
ACCEPTANCE_DIGEST='2bc1972e6cf6560a9fc4f4edc6aeca787c4222c655c2c6d4f1304964bc220701'
GROUP_ACCEPTANCE=cos.BASE+'P9-8.5-FirstGroupAcceptance.json'
GROUP_DIGEST='64f102670b4a46d0310ac2d2b2f6eca819dafb24203019408fe4e3d2ce42045c'
COS_REVISION='5b8a432e'
LIFECYCLE='src/pygrc/models/grc_v4_lifecycle.py'
EXECUTION_POLICY=cos.HERE+'phase9_implementation_policy.py'
POLICY_SNAPSHOT=cos.BASE+'P9-8.5-ExecutionMaintenancePolicy.py.txt'
POLICY_DIGEST='c7ebd6223b1c62ac2222f31b1e62c232346a7bb5e21d958a9ad76912472297f4'


def successor_sources(root, manifest):
    """Authenticate only exact named refactor epochs; never bless other drift."""
    from p994b_runtime_successor import SOURCES, historical_source
    result = {}
    for name, row in SOURCES.items():
        expected = manifest['source_bindings'].get(name)
        if expected is not None and cos.sha((root/name).read_bytes()) != expected:
            cos.require(historical_source(root,name,expected)==expected,
                        'unrecognized execution source successor: '+name)
            result[root/name] = subprocess.check_output(
                ['git','show',row['predecessors'][expected]+':'+name],cwd=root)
    return result


def historical_refs(value):
    from p994b_runtime_successor import SOURCES
    for ref in value['source_refs']:
        row = SOURCES.get(ref['path'])
        if row and ref['sha256'] in row['predecessors']:
            ref.update(revision=row['predecessors'][ref['sha256']],basis='historical_git')
    value['current_code_conformance_inferred'] = False
    return value


@contextmanager
def cos_execution_epoch(root):
    """Metadata-only adapter for the accepted pre-integration execution source.

    Authenticate the exact original Git blob against its recorded hash. No
    numerical function is executed or replaced, and no current-code claim follows.
    All other bindings still use their actual current bytes and fail on drift.
    """
    root=Path(root);m=json.loads((root/cos.INPUTS).read_text())
    raw=subprocess.check_output(['git','show',COS_REVISION+':'+LIFECYCLE],cwd=root)
    cos.require(cos.sha(raw)==m['source_bindings'][LIFECYCLE],'original C_OS execution source unavailable')
    sources=successor_sources(root,m)
    sources[root/LIFECYCLE]=raw
    original=Path.read_bytes
    def read(path):return sources[path] if path in sources else original(path)
    with patch.object(Path,'read_bytes',read):yield


@contextmanager
def batch_execution_epoch(root, family):
    """Original imported maintenance metadata, not replacement numerical code."""
    root=Path(root)
    manifest=json.loads((root/batch.path(family,'inputs')).read_text())
    sources=successor_sources(root,manifest)
    if EXECUTION_POLICY in manifest['source_bindings']:
        raw=(root/POLICY_SNAPSHOT).read_bytes()
        cos.require(cos.sha(raw)==POLICY_DIGEST==manifest['source_bindings'][EXECUTION_POLICY],
                    'original execution maintenance source unavailable')
        sources[root/EXECUTION_POLICY]=raw
    original=Path.read_bytes
    def read(path):return sources[path] if path in sources else original(path)
    with patch.object(Path,'read_bytes',read):yield


def checked_batch(root,family):
    # Direct use is for a single verification worker; API calls isolate it below.
    with batch_execution_epoch(root,family):return batch.check(family,root)


def accepted_group(root,value):
    record=json.loads((root/GROUP_ACCEPTANCE).read_text())
    cos.require(record==cos.seal(record) and record['record_digest']==GROUP_DIGEST
        and set(record['families'])=={'C_OS','C_CI','A_CI','A_PC'}
        and record['user_accepted'] and record['first_group_closed']
        and not record['aggregate_closed'], 'unbound first-group acceptance')
    row=record['families'][value['family']]
    cos.require(row['manifest_digest']==value['manifest_digest']
        and row['execution_digests']=={k:v['record_digest'] for k,v in value['executions'].items()},
        'first-group acceptance differs from execution')
    value.update(status='accepted',user_accepted=True,first_group_closed=True,first_group_acceptance=record)
    if value['family']!='C_OS':value['acceptance']=record
    value['source_refs'].append(dict(path=GROUP_ACCEPTANCE,sha256=cos.sha((root/GROUP_ACCEPTANCE).read_bytes()),revision=None))
    return value


def _view(root,family):
    root=Path(root)
    cos.require(family in ('C_OS',*batch.FAMILIES),'8.5 requires an executed first-group family')
    if family=='C_OS':
        with cos_execution_epoch(root):
            frozen=json.loads((root/cos.INPUTS).read_text())
            current=cos.manifest()
            # Only the recorded execution population belongs to this epoch.
            # New unrelated implementation files are not historical inputs.
            current['source_bindings']={n:current['source_bindings'][n] for n in frozen['source_bindings']}
            cos.require(frozen==cos.seal(current),
                '8.5 execution manifest differs from its frozen source roster')
            value=cos.status(root)
        for ref in value['source_refs']:
            if ref['path']==LIFECYCLE:ref.update(revision=COS_REVISION,basis='historical_git')
        value['execution_source_epoch']=COS_REVISION
        value['current_code_conformance_inferred']=False
        acceptance=json.loads((root/ACCEPTANCE).read_text())
        cos.require(acceptance==cos.seal(acceptance) and acceptance['record_digest']==ACCEPTANCE_DIGEST
            and acceptance['family']==family and acceptance['user_accepted']
            and acceptance['manifest_digest']==value['manifest_digest']
            and acceptance['execution_digests']=={k:v['record_digest'] for k,v in value['executions'].items()},
            'unbound C_OS acceptance')
        value.update(status='accepted',user_accepted=True,acceptance=acceptance)
        value['source_refs'].append(dict(path=ACCEPTANCE,sha256=cos.sha((root/ACCEPTANCE).read_bytes()),revision=None))
        return accepted_group(root,historical_refs(value))
    manifest,records=checked_batch(root,family)
    paths=set(manifest['source_bindings'])|{batch.path(family,k) for k in ('inputs','small','large','review')}
    metadata_snapshot=EXECUTION_POLICY in manifest['source_bindings']
    if metadata_snapshot:
        paths.remove(EXECUTION_POLICY);paths.add(POLICY_SNAPSHOT)
    with batch_execution_epoch(root,family):
        source_refs=[dict(path=p,sha256=cos.sha(cos.safe(root,p).read_bytes()),revision=None) for p in sorted(paths)]
    value=dict(schema='phase9_tranche8_lifecycle_v1',checkpoint='8.5',family=family,
        status='verified_pending_acceptance',user_accepted=False,acceptance=None,aggregate_closed=False,
        public_specialization_facade=False,native_trajectories_rerun=False,retained_integrity_only=True,
        manifest_digest=manifest['record_digest'],executions=records,
        execution_metadata_sources=({EXECUTION_POLICY:POLICY_SNAPSHOT} if metadata_snapshot else {}),
        source_refs=source_refs)
    return accepted_group(root,historical_refs(value))


def view(root,family):
    # Each metadata adapter is isolated from concurrent HTTP/API requests.
    cos.require(family in ('C_OS',*batch.FAMILIES),'8.5 requires an executed first-group family')
    root=Path(root).resolve();env=dict(os.environ)
    env['PYTHONPATH']=os.pathsep.join(str(root/p) for p in ('src','.','tests',cos.HERE))
    raw=subprocess.check_output([sys.executable,str(root/cos.HERE/'p985_status.py'),'worker',family],
        cwd=root,env=env,timeout=60)
    return json.loads(raw)


if __name__=='__main__':
    cos.require(len(sys.argv)==3 and sys.argv[1]=='worker','private retained-status worker only')
    print(json.dumps(_view(cos.ROOT,sys.argv[2])))
