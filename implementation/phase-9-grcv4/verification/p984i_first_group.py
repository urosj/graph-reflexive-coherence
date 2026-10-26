"""First-group retained coverage reconciliation; no numerical execution or support grant."""
import argparse
import hashlib
import json
import lzma
from pathlib import Path, PurePosixPath
import subprocess

ROOT=Path(__file__).resolve().parents[3]
BASE='implementation/phase-9-grcv4/tranche-8/'
HERE='implementation/phase-9-grcv4/verification/'
SIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/'
REVISION='36c01355'  # accepted first-group merge, not a moving branch
RESULT=BASE+'P9-8.4i-FirstGroup.json'
REVIEW=BASE+'P9-8.4i-FirstGroupReview.md'
AUTHORITY=BASE+'P9-8.4i-FirstGroupAuthority.json'
FAMILIES=('C_OS','C_CI','A_CI','A_PC')
OTHERS=('A_OS','C_PC','C_CI_PC','A_CI_PC','C_RG2b','A_RG2b')
SNAPSHOTS=(SIDE+'tool/phase9-web/tranche8-evidence.js',SIDE+'tool/phase9-web/tranche8-apc-evidence.js')
EVENTS={f:BASE+'P9-8.4h-'+tag+'-event.json.xz' for f,tag in zip(FAMILIES,('COS','CCI','ACI','APC'))}
EVENTS['C_OS']=BASE+'P9-8.4h-COSEventSuccessor.json.xz'


def require(ok,message):
    if not ok:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def seal(value):
    value=dict(value);value.pop('record_digest',None)
    value['record_digest']=sha(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    return value


def safe(root,name):
    p=PurePosixPath(name)
    require(type(name) is str and str(p)==name and not p.is_absolute() and '..' not in p.parts and '\\' not in name,'unsafe evidence path')
    path=Path(root)/name
    require(path.resolve()==path.absolute() and not path.is_symlink(),'unsafe evidence symlink')
    return path


def git_bytes(root,name,revision=REVISION):
    safe(root,name)
    return subprocess.check_output(['git','show',revision+':'+name],cwd=root,stderr=subprocess.PIPE)


def refs(value):
    if isinstance(value,dict):
        if {'path','sha256'}<=value.keys():yield value
        else:
            for item in value.values():yield from refs(item)
    elif isinstance(value,list):
        for item in value:yield from refs(item)


def reference(root,name):
    return dict(path=name,sha256=sha(safe(root,name).read_bytes()),revision=None)


def authenticate(root,ref):
    """Portable original bytes, including files stored only as lossless XZ."""
    path=safe(root,ref['path'])
    if ref.get('revision') and ref.get('basis')=='historical_git':
        raw=git_bytes(root,ref['path'],ref['revision'])
    elif path.exists():raw=path.read_bytes()
    else:
        from scripts.evidence_storage import entries,packed_bytes,unpack
        row=next((r for r in entries(Path(root)) if r['path']==ref['path']),None)
        require(row is not None and row['sha256']==ref['sha256'],'missing retained evidence: '+ref['path'])
        raw=unpack(packed_bytes(Path(root),row),row)
    require(sha(raw)==ref['sha256'],'retained source drift: '+ref['path'])
    return raw


def unique_refs(values):
    result={}
    for r in refs(values):
        item={k:r[k] for k in ('path','sha256','revision','basis') if k in r}
        key=(r['path'],r.get('revision'))
        require(key not in result or result[key]['sha256']==r['sha256'],'conflicting source identity')
        result[key]=item
    return sorted(result.values(),key=lambda r:(r['path'],r.get('revision') or ''))


def one(rows,family):
    found=[r for r in rows if r['family']==family]
    require(len(found)==1,'missing/duplicate family '+family)
    return found[0]


def project(index,apc):
    c=index['coverage'];result=[]
    for f in FAMILIES:
        rows={'b':one(c['families'],f)}
        for letter,key in (('c','boundary_contract'),('d','deep_expansion'),('e','ordering_covariance'),('f','chart_covariance')):
            rows[letter]=one(c[key]['family_results'],f)
        for letter,count in zip('bcdef',(32,64,40,20,24)):
            require(rows[letter]['required_cells']==rows[letter]['accepted_cells']==count,'unclosed '+f+' '+letter)
        h=apc['runtime'] if f=='A_PC' else one(c['larger_runtime'],f)
        require(h['user_accepted'] and not h['aggregate_closed'] and h['continuation']['baseline_complete']
            and h['covariance']['covariance_complete'],'unaccepted/incomplete larger family')
        events=h['native_events'] if f=='C_OS' else h['total_native_events']
        steps=h['continuation']['target_steps']+h['covariance']['target_steps']
        require((events,steps,h['continuation']['final_reads'])==(9,36,2),'larger coverage drift')
        g=(one(c['larger_prerequisites']['family_results'],f) if f=='C_OS'
            else one(c['larger_prerequisites']['investigations'],f))
        b_runs=[r for r in c['runs'] if r['family']==f]
        result.append(dict(family=f,accepted_history_cells={k:r['accepted_cells'] for k,r in rows.items()},
            frozen_b_cell_ids=rows['b']['accepted_cell_ids'],
            larger=dict(source_steps=2 if f=='C_OS' else 1,events=events,target_steps=steps,final_reads=2,
                baseline_horizon_per_role=10,mapped_horizon_per_role=1,mapped_events=8),
            evidence_refs=unique_refs([rows,b_runs,g,h]),larger_acceptance=h['acceptance'],
            positive_event=EVENTS[f],checkpoint_pointer='/execution/checkpoint',
            prerequisite_scope='accepted named companions; original exclusions retained',
            accepted_by_user=True))
    return result


def build(root=ROOT):
    root=Path(root).resolve();snap=[];inputs=[]
    for name in SNAPSHOTS:
        raw=git_bytes(root,name)
        snap.append(json.loads(raw.decode().split(' = ',1)[1].rstrip(';\n')))
        inputs.append(dict(path=name,sha256=sha(raw),revision=REVISION,basis='historical_git'))
    rows=project(*snap)
    coverage=json.loads(git_bytes(root,BASE+'P9-8.4a-Coverage.json'))
    inputs.append(reference(root,BASE+'P9-8.4a-Coverage.json'))
    inputs.extend(reference(root,p) for p in (AUTHORITY,REVIEW,HERE+'p984i_first_group.py',HERE+'test_p984i_first_group.py',
        HERE+'verify_p972a_proposal.py',HERE+'test_p972a_proposal.py','specs/README.md','specs/grc-9-v4-spec.md','specs/grc-v4-spec.md',
        'specs/grc-common-interface-v4-ext.md','specs/grc-v4-numerical-policy.md',
        'implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md'))
    for row in rows:
        raw=safe(root,row['positive_event']).read_bytes();event=json.loads(lzma.decompress(raw));e=event['execution'];cp=e['checkpoint']
        require(event['outcome']=='completed' and e['rollback_exact'] and len(cp['receipts'])==4,'event witness incomplete')
        row['event_id']=e['event_id'];row['event_record_digest']=event['record_digest']
        row['source_state_digest']=cp['initial']['scientific_digest'];row['target_state_digest']=cp['state']['scientific_digest']
        row['target_reset_digest']=cp['state']['reset_digest'];row['event_checkpoint_lifecycle_digest']=cp['lifecycle_digest']
        row['witness_ref']=reference(root,row['positive_event'])
    authority=json.loads(safe(root,AUTHORITY).read_bytes())
    require(len(authority['traces'])==6 and all(t['rows'] and t['trace_digest'] for t in authority['traces']),'missing authority traces')
    # The typed trace retains design-level runtime-pending dispositions verbatim.
    inputs.extend(reference(root,p) for p in sorted({r['source_ref']['path'] for t in authority['traces'] for r in t['rows']}))
    sources=unique_refs([inputs,rows])
    for ref in sources:authenticate(root,ref)
    return seal(dict(schema='p984i-first-group-handoff-v1',checkpoint='P9-8.4i[first-group]',
        accepted_execution_revision=REVISION,status='first_group_8_4_accepted',families=rows,
        first_group_h_accepted=True,first_group_i_accepted=True,first_group_8_4_closed=True,
        accepted_on='2026-10-26',all_ten_8_4_closed=False,
        remaining_families=list(OTHERS),counts=dict(families=4,source_steps=5,events=36,target_steps=144,final_reads=8),
        atomic_failure_vectors=coverage['atomic_handoff'],
        authority_traces=[dict(query=t['query'],trace_digest=t['trace_digest']) for t in authority['traces']],
        next=dict(P9_8_5='scoped first-group lifecycle/rollback/replay campaign; not yet executed',
            P9_8_6='first-group conformance decision after 8.5; no arbitrary-graph numerical claim'),
        configuration_discovery_changed=False,public_support_changed=False,new_G2_G3_support=False,
        numerical_trajectories_rerun=False,current_runtime_conformance_inferred=False,
        source_refs=sources))


def check(root=ROOT):
    actual=json.loads(safe(root,RESULT).read_bytes());expected=build(root)
    require(actual==expected,'handoff coverage/identity/scope drift')
    return actual


def status(root=ROOT):
    value=check(root)
    return dict(schema='phase9_tranche8_first_group_handoff_v1',family='first_group',checkpoint='8.4i',
        handoff=value,source_refs=unique_refs([value['source_refs'],reference(root,RESULT),reference(root,REVIEW)]),
        other_families_checked=False,native_trajectories_rerun=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('record','check','status'));a=p.parse_args()
    if a.action=='record':
        value=build()
        with (ROOT/RESULT).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    else:value=status() if a.action=='status' else check()
    print(json.dumps(value if a.action=='status' else {k:value[k] for k in ('checkpoint','status','counts','all_ten_8_4_closed')}))
