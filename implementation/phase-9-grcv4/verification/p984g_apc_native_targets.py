"""Normalize expected numeric representation; repeat only affected targets."""
import argparse
import hashlib
import json
import lzma
from unittest.mock import patch
import p984g_apc_native as base

ROOT,BASE,HERE=base.ROOT,base.BASE,base.HERE
SELF=HERE+'p984g_apc_native_targets.py';TEST=HERE+'test_p984g_apc_native_targets.py'
PLAN=BASE+'P9-8.4g-APCNativeTargetPlan.md';NOTE=base.NOTE;RESULTS=base.RESULTS
DIRECTORY=BASE+'P9-8.4g-APCNativeTargets/'
CASES,seal,require=base.CASES,base.seal,base.require
_BINDINGS=base.bindings;_PATH=base.case_path;_POINT=base.compare_point;_ASSESS=base.assess


def bindings():
    v=_BINDINGS()
    for name in (SELF,TEST,PLAN):v[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    return v


def case_path(graph,role):
    require((graph,role) in CASES,'case roster')
    return DIRECTORY+graph+'-'+role+'.json.xz' if graph=='target' else _PATH(graph,role)


def compare_point(actual,expected,c,w,z,subject):
    # Native and independent point identities use binary64 C/W. This does not
    # alter values: require exact representability before normalizing JSON types.
    require(all(base.q(x)==base.q(float(x)) for x in c+w),'inexact expected normalization')
    return _POINT(actual,expected,list(map(float,c)),list(map(float,w)),z,subject)


def worker(pipe,graph,role):
    with patch.object(base,'compare_point',compare_point):base.worker(pipe,graph,role)


def run(graph,role):
    require(graph=='target','source successes must not be rerun')
    with patch.object(base,'bindings',bindings),patch.object(base,'case_path',case_path),patch.object(base,'worker',worker):base.run(graph,role)


def assess(v,oracle):
    if v['graph']=='source':return _ASSESS(v,oracle)
    with patch.object(base,'bindings',bindings),patch.object(base,'compare_point',compare_point):return _ASSESS(v,oracle)


def summary():
    oracle=base.h.check_retained();cases=[];history=[]
    for graph,role in CASES:
        name=case_path(graph,role);raw=(ROOT/name).read_bytes();v=json.loads(lzma.decompress(raw))
        require((v['graph'],v['role'])==(graph,role),'case path')
        cases.append(dict(graph=graph,role=role,**assess(v,oracle),path=name,sha256=hashlib.sha256(raw).hexdigest(),record_digest=v['record_digest'],seconds=v['seconds']))
        if graph=='target':
            oldname=_PATH(graph,role);oldraw=(ROOT/oldname).read_bytes();old=json.loads(lzma.decompress(oldraw))
            row=_ASSESS(old,oracle);require(row['outcome']=='incomplete','historical target disposition')
            history.append(dict(graph=graph,role=role,**row,path=oldname,sha256=hashlib.sha256(oldraw).hexdigest(),record_digest=old['record_digest']))
    return seal(dict(schema='p984g-apc-native-summary-v1',family='A_PC',cases=cases,historical_target_attempts=history,source_bindings=bindings(),
        hardening_digest=oracle['record_digest'],native_steps=sum(c['native_steps'] for c in cases),native_reads=sum(c['native_reads'] for c in cases),
        native_prerequisites_complete=all(c['outcome']=='completed' for c in cases),scope='prepared_role_steps_not_postbeat_event_or_uniform_domain',
        native_events=0,committed_steps=0,user_accepted=False,ready_for_8_4h=False,retained_check_only=True,native_trajectories_rerun=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('run','summarize','check'))
    parser.add_argument('--graph',choices=('target',));parser.add_argument('--role',choices=('current','reset'));args=parser.parse_args()
    if args.mode=='run':run(args.graph,args.role)
    else:
        v=summary()
        if args.mode=='summarize':
            require(not (ROOT/RESULTS).exists(),'no overwrite');(ROOT/RESULTS).write_text(json.dumps(v,indent=2)+'\n')
        else:require(v==json.loads((ROOT/RESULTS).read_text()),'summary drift')
        print(json.dumps({k:v[k] for k in ('native_steps','native_reads','native_prerequisites_complete')}))
