#!/usr/bin/env python3
"""CIP-1 bounded causal witness, exact bounds and pressure; stdout only.

One onset beat, two target beats per role, one beat per one-time control.
Indefinite return/71-proposal obstruction are proofs, not long simulations.
"""
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
INV=Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0,str(ROOT/INV/'research'))
import atc_cip_chain as cip
r,a=cip.r,cip.a
INPUT=ROOT/INV/'evidence/atc-cip/CIP1-Preregistration.json'
INPUT_SHA='c983589eead8283051674bcb63255ee23b573491a23c64bc4290e20b3784cec2'
RECORD=ROOT/INV/'evidence/atc-cip/ATCCIP1Certificate.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def root_evidence(value):
    return dict(selected_joint_root_digest=value['selected_joint_root_digest'],
        role_binding=value['role_binding'],profile_binding=value['profile_binding'],
        certificate_digest=value['certificate_digest'],old_Z_binding=value['old_Z_binding'],
        root_error=value['root_error'],iterations=value['iterations'],
        J=value['read']['current'],H=value['H'],S=value['read']['source'],
        readback=value['read']['readback'],joint_residuals_enclose_zero=True)


def znorm(role): return r.norm_upper(x for row in role.carrier.values for x in row)


def radius(role): return r.norm_upper(c-F(3,2) for c in role.state.C)


def same_matrix(x,y):
    return all(r.same(v,w) for row,other in zip(x,y,strict=True) for v,w in zip(row,other,strict=True))


def reject(name,call):
    try: call()
    except a.AdmissionError as exc: return dict(case=name,reason=str(exc))
    raise AssertionError('unexpected admission: '+name)


def run():
    r.require(sha(INPUT)==INPUT_SHA,'fixed preregistration changed')
    cfg=json.loads(INPUT.read_text())
    profile=cip.Profile(tuple(sorted((k,F(v)) for k,v in cfg['parameters'].items())))
    def initial(name):
        v=cfg[name]
        return cip.exact_role(tuple(map(F,v['C'])),tuple(map(F,v['W'])),F(v['Z_diagonal']))
    before,reset=initial('current'),initial('reset');h=F(cfg['onset_request'])
    theorem=cip.bounds()
    r.require(before.state.predicates.x[1]<3,'prebeat guard inactive')
    captured=(before.identity,reset.identity)
    reset_read=cip.root(reset,profile)
    after,details=cip.step(before,h,profile)
    chosen,targets=cip.event(after,reset,profile)
    r.require(chosen['selected']['selected_joint_root_digest']==details['restart']['selected_joint_root_digest'],
              'event reconstructs full fresh committed joint root')
    r.require(a.encode(details['selected']['read']['current'])!=a.encode(chosen['selected']['read']['current']),
              'consumed current cannot substitute for fresh event root')
    r.require(after.state.predicates.x[0]>=3 and captured==(before.identity,reset.identity),
              'positive ordinary onset; independent reset unchanged')
    captured_live=after.identity
    r.require(r.p.norm2(chosen['selected']['read']['readback']).lo>0,
              'fresh combined witness has genuinely nonzero Read-Back')
    roles={}
    for name,source in (('current',after),('reset',reset)):
        item=targets[name];target=item['role'];share=F(chosen['k'],65536)
        r.require(all(r.same(x,y) for x,y in zip(target.state.W[:4],source.state.W,strict=True))
                  and target.state.W[4].lo==target.state.W[4].hi==r.GRID,'W lineage and bridge-only seed')
        r.require(r.same(target.state.C[4],share*source.state.C[4]) and
                  r.same(target.state.C[5],(1-share)*source.state.C[4]),'same current-selected share for actual role')
        r.require(znorm(target)==znorm(source),'lossless role-specific carrier norm')
        minor=target.carrier.values[0][0]*target.carrier.values[4][4]-target.carrier.values[0][4].square()
        if name=='current':r.require(minor.hi<0,'non-PSD carrier actually admitted by coupled root')
        beats=[];role=target
        for number,request in enumerate(cfg['target_requests_each_role'],1):
            previous=role;role,beat=cip.step(previous,F(request),profile)
            held=tuple(tuple(beat['decay']*z+(1-beat['decay'])*s for z,s in zip(row,other,strict=True))
                       for row,other in zip(previous.carrier.values,beat['selected']['read']['source'],strict=True))
            r.require(same_matrix(role.carrier.values,cip.decorated_tensor(held)),'one old-Z / held-selected-source write')
            r.require(beat['selected']['old_Z_binding']==a.digest(a.encode(previous.carrier.values)) and
                      beat['restart']['old_Z_binding']==a.digest(a.encode(role.carrier.values)),'old/new root carriers')
            r.require(not same_matrix(role.carrier.values,previous.carrier.values) and
                      any(not r.same(x,y) for x,y in zip(role.state.W,previous.state.W,strict=True)),'both histories evolve')
            r.require(radius(role)<F(2,3),'actual target remains in return domain')
            if number==1:r.require(radius(role)<theorem['target_first_X_upper'],'observed entry')
            else:
                old_lower=F(r.p.norm2(tuple(c-F(3,2) for c in previous.state.C)).sqrt().lo,r.GRID)
                r.require(radius(role)<theorem['target_return_factor']*old_lower,'independently bounded norm contraction')
            r.require(role.carrier.values[4][4].lo>0,'ordinary target leaves five-dimensional event image')
            beats.append(dict(beat=number,h=request,role=role.payload(),X_upper=radius(role),Z_norm_upper=znorm(role),
                selected=root_evidence(beat['selected']),restart=root_evidence(beat['restart']),
                decay=beat['decay'],same_source_write_checked=True,outside_event_image=True))
        roles[name]=dict(source=source.payload(),event_target=target.payload(),receipt=item['receipt'],
            admitted_root=root_evidence(item['read']),signed_minor=minor,beats=beats)
    controls={}
    for label,w,z in (('no_split',False,False),('W_reset_only',True,False),
                      ('Z_reset_only',False,True),('both_reset',True,True)):
        control=cip.control(after,reset_W=w,reset_Z=z)
        following,beat=cip.step(control,h,profile)
        r.require(following.state.predicates.x[0]>=theorem['source_multiplier']*control.state.predicates.x[1],
                  'observed source growth agrees with obstruction')
        if z:r.require(r.p.norm2(tuple(x for row in following.carrier.values for x in row)).lo>0,
                       'one-time Z reset resumes genuinely nonzero carrier writing')
        controls[label]=dict(before=control.payload(),after_one_beat=following.payload(),
            selected=root_evidence(beat['selected']),restart=root_evidence(beat['restart']),
            x_before=control.state.predicates.x,x_after=following.state.predicates.x,
            Z_after_norm=znorm(following),writer_remains_active=True,
            obstruction_within=71,obstruction_is_uniform_proof_not_executed_71_steps=True)
    rejected=[reject('prebeat_guard',lambda:cip.select(before,profile)),
        reject('alternate_carrier_policy',lambda:cip.event(after,reset,profile,policy_id='projection')),
        reject('PC_admitted_CIP_excluded_carrier',lambda:cip.Role(before.state,r.diagonal_z(F(1,8192)))),
        reject('standalone_CI_gain',lambda:cip.Profile(tuple(sorted({**profile.values,'kh':F(3,4)}.items())))),
        reject('reset_outside_transfer_domain',lambda:cip.event(after,
            cip.Role(cip.predicates.paired_state(F(4),F(0),F(49,50),F(97,100)),reset.carrier),profile))]
    original_root=cip.root
    def failure_at(n):
        calls=[]
        def injected(*args):
            calls.append(None)
            if len(calls)==n:raise a.AdmissionError('injected final combined readmission')
            return original_root(*args)
        return injected
    with patch.object(cip,'root',side_effect=failure_at(2)):
        rejected.append(reject('ordinary_restart_rejection',lambda:cip.step(after,h,profile)))
    with patch.object(cip,'root',side_effect=failure_at(5)):
        rejected.append(reject('reset_target_root_rejection',lambda:cip.event(after,reset,profile)))
    r.require(rejected[2]['reason']=='narrower CIP carrier ball','carrier rejection belongs to CIP, not old PC boundary')
    r.require(captured==(before.identity,reset.identity) and captured_live==after.identity,
              'all captured roles preserved; no partial result publication')
    evidence=dict(preregistration=cfg,profile_identity=profile.identity,bounds=theorem,
        source=dict(before=before.payload(),reset=reset.payload(),postbeat=after.payload(),
            consumed=root_evidence(details['selected']),fresh_event=root_evidence(chosen['selected']),
            reset_root=root_evidence(reset_read),k=chosen['k'],share=chosen['share'],
            positive_onset=True,reset_does_not_select=True),roles=roles,controls=controls,rejected=rejected,
        execution_scope='1 source onset; 2 target beats per role; 1 further beat per one-time control; bounded failure pressure',
        event_duration=0,extra_event_writers=0,native_ATC_executed=False)
    paths={Path(__file__).resolve(),INPUT,ROOT/INV/'decisions/ATCCIP1CausalChain.md',
           ROOT/INV/'evidence/atc-cip/ATCCIP0Certificate.json'}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/INV) and path.suffix=='.py':paths.add(path)
    value=a.encode(dict(schema='grcv4_atc_cip1_v1',status='prepared_pending_independent_review',
        scientific_acceptance=False,graph_admitted=False,ATC2_closed=False,CIP2_completed=False,
        evidence=evidence,claim_updates=[dict(claim_id='ATC-CIP-CHAIN-01',claim_class='proposed_conditional',
            profile_scope=['A_CI_PC'],predecessor_handles=['ATC-CIP-ROOT-00','ATC-CI-DOMAIN-02','ATC-PC-CARRIER-03'],
            debt_refs=['ATC7-DB-'+n for n in ('02','03','04','06','07','08','13','14','15','16','19','26')],
            local_debt_discharge=False,native_authority=False,
            still_open='CIP2 independent reference/lifecycle/representation; review/adjudication; wider/aggregate ATC2')],
        source_bindings=[dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)) for path in sorted(paths)]))
    value['record_digest']=a.digest(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.check:
        value=json.loads(RECORD.read_text())
        r.require(value['record_digest']==a.digest({k:v for k,v in value.items() if k!='record_digest'}),'record identity')
        for row in value['source_bindings']:
            r.require(sha(ROOT/row['path'])==row['sha256'],'source drift: '+row['path'])
        print(json.dumps(dict(status='passed',scope='retained identities only',record_digest=value['record_digest'])))
    else:
        print(json.dumps(run(),indent=2))
