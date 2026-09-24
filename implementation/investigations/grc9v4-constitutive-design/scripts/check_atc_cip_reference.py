#!/usr/bin/env python3
"""CIP-2 independent stages, closed boundaries, research lifecycle and finite rounding.

Stdout only. --check validates retained identities without executing the suite.
"""
from dataclasses import replace
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
INV=Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0,str(ROOT/INV/'research'))
import atc_cip_reference as t
import atc_cip_oracle as oracle
from check_atc_ci_reference import inside, reject, error
a,r,p,I,GRID,require=t.a,t.r,t.p,t.I,t.GRID,t.require
RECORD=ROOT/INV/'evidence/atc-cip-successor/ATCCIP2Certificate.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def seeds():
    cfg=json.loads((ROOT/INV/'evidence/atc-cip/CIP1-Preregistration.json').read_text())
    profile=t.Profile(tuple(sorted((k,F(v)) for k,v in cfg['parameters'].items())))
    values=[]
    for name in ('current','reset'):
        v=cfg[name];z=F(v['Z_diagonal'])
        values.append(dict(C=tuple(map(F,v['C'])),W=tuple(map(F,v['W'])),
                           Z=tuple(tuple(z if i==j else F(0) for j in range(4)) for i in range(4))))
    return t.Publication(*(t.exact_role('paired_source',**v) for v in values),profile),values


def root_summary(root):
    return dict(selected_joint_root_digest=root['selected_joint_root_digest'],
        role_binding=root['role_binding'],profile_binding=root['profile_binding'],Z_binding=root['Z_binding'],
        certificate_digest=root['certificate_digest'],root_error=root['root_error'],
        iterations=root['iterations'],J=root['read']['current'],H=root['H'],
        source_digest=a.digest(a.encode(root['read']['source'])))


def compare_root(expected,root):
    require(root['selected_joint_root_digest']==a.digest(a.encode({k:v for k,v in root.items()
            if k!='selected_joint_root_digest'})),'full selected-root digest')
    return inside(expected['H'],root['H'])+inside(expected['generated_H'],root['generated_H'])+inside(expected['read'],root['read'])


def compare(expected,role,details):
    n=inside(expected['C'],role.state.C)+inside(expected['W'],role.state.W)+inside(expected['Z'],role.carrier.values)
    n+=compare_root(expected['selected'],details['selected'])+compare_root(expected['restart'],details['restart'])
    return n+sum(inside(expected[k],details[k]) for k in ('decay','writer_descriptor','writer_drive'))


def stages():
    source,exact=seeds();prof=source.profile
    post,step=t.step(source.current,F(1,8),prof)
    other=oracle.evaluate(a.GRAPHS['paired_source'],**exact[0],parameters=prof.parameters,h=F(1,8))
    count=compare(other,post,step);chosen=t.select(post,prof)
    require(chosen['root']['selected_joint_root_digest']==step['restart']['selected_joint_root_digest'],'fresh whole event root')
    with localcontext() as ctx:
        ctx.prec=110;J=other['restart']['read']['current'];k=round(D(65536)*(J[0]+J[1])/sum(J))
    retained=json.loads((ROOT/INV/'evidence/atc-cip/ATCCIP1Certificate.json').read_text())
    require(k==chosen['k']==retained['evidence']['source']['k'],'independent fresh selector / reviewed result')
    for key,got in (('J',step['restart']['read']['current']),('H',step['restart']['H']),('S',step['restart']['read']['source'])):
        require(a.encode(got)==retained['evidence']['source']['fresh_event'][key],'reviewed scientific root unchanged: '+key)
    # Wrong H with unchanged J must not pass a current-only comparison.
    bad=dict(other['restart']);bad['H']=[list(row) for row in bad['H']];bad['H'][0][0]+=D('1e-8')
    negatives=[reject(lambda:compare_root(bad,step['restart']),'H_only_corruption')]
    rows=[];targets=[];oracle_targets=[]
    for name,role,seed in (('current',post,other),('reset',source.reset,exact[1])):
        target,admitted,_=t.transfer(role,k,prof);dec=oracle.transfer(seed,k)
        targets.append(target);oracle_targets.append(dec)
        count+=inside(dec['C'],target.state.C)+inside(dec['W'],target.state.W)+inside(dec['Z'],target.carrier.values)
        count+=compare_root(oracle.evaluate(a.GRAPHS['paired_target'],**dec,parameters=prof.parameters),admitted)
        for h in (F(3,25),F(1,8)):
            nxt,details=t.step(target,h,prof)
            expected=oracle.evaluate(a.GRAPHS['paired_target'],**dec,parameters=prof.parameters,h=h)
            n=compare(expected,nxt,details);count+=n
            stale=t.ci.conductance('paired_target',nxt.state.C,details['selected']['read']['descriptor'],details['selected']['read']['current'],prof)
            wrong=t.ci.conductance('paired_target',nxt.state.C,details['writer_descriptor'],details['restart']['read']['current'],prof)
            distinct=lambda xs,ys:any(x.hi<y.lo or y.hi<x.lo for x,y in zip(xs,ys,strict=True))
            require(distinct(stale,details['writer_drive']) and distinct(wrong,details['writer_drive']),'descriptor/current staging discrimination')
            wrongZ=tuple(details['decay']*z+(1-details['decay'])*s
                for row,ss in zip(target.carrier.values,details['restart']['read']['source'],strict=True) for z,s in zip(row,ss,strict=True))
            require(distinct(wrongZ,tuple(x for row in nxt.carrier.values for x in row)),'wrong new-source writer discrimination')
            rows.append(dict(role=name,h=h,comparisons=n,selected=root_summary(details['selected']),restart=root_summary(details['restart']),
                             three_stage_mutations_discriminated=True))
    C=(F(7,5),)*2+(F(8,5),)*2+(F(3,2),)*2;W=(F(97,100),)*4+(F(1),)
    Z=tuple(tuple(-t.domains.RZ/2 if i==j==4 else F(0) for j in range(5)) for i in range(5))
    corner=t.exact_role('paired_target',C,W,Z)
    for end,h in ((0,F(3,25)),(1,F(1,8))):
        profile=t.Profile(tuple(sorted((k,v[end]) for k,v in t.domains.PARAMETER_BOX.items())))
        result,details=t.step(corner,h,profile)
        n=compare(oracle.evaluate(a.GRAPHS['paired_target'],C,W,Z,profile.parameters,h),result,details);count+=n
        rows.append(dict(parameter_corner=end,h=h,comparisons=n,profile=profile.parameters,root=root_summary(details['restart'])))
    return dict(independent_scalar_comparisons=count,k=k,reviewed_root_values_unchanged=True,
                negative_pressure=negatives,checks=rows),source,post,targets,oracle_targets


def covariance(target,seed,profile):
    n,edges,pos=a.GRAPHS['paired_target'];m=len(edges)
    vertex=(2,5,0,4,1,3);order=(4,2,0,3,1);signs=(-1,1,-1,1,-1)
    with localcontext() as ctx:
        ctx.prec=110
        C=[None]*n;positions=[None]*n
        for i in range(n):C[vertex[i]]=seed['C'][i];positions[vertex[i]]=pos[i]
        transformed=[]
        for old,sign in zip(order,signs,strict=True):
            u,v=edges[old];u,v=vertex[u],vertex[v];transformed.append((u,v) if sign==1 else (v,u))
        Z=tuple(tuple(signs[i]*signs[j]*seed['Z'][u][v] for j,v in enumerate(order)) for i,u in enumerate(order))
        other=oracle.evaluate((n,tuple(transformed),tuple(positions)),C,tuple(seed['W'][i] for i in order),Z,profile.parameters,F(3,25))
        nxt,details=t.step(target,F(3,25),profile);count=0
        for i in range(n):count+=inside(other['C'][vertex[i]],nxt.state.C[i])
        for i,u in enumerate(order):
            count+=inside(other['W'][i],nxt.state.W[u])
            for j,v in enumerate(order):count+=inside(signs[i]*signs[j]*other['Z'][i][j],nxt.carrier.values[u][v])
        for name in ('selected','restart'):
            for i,u in enumerate(order):
                count+=inside(signs[i]*other[name]['read']['current'][i],details[name]['read']['current'][u])
                for j,v in enumerate(order):
                    for key,ref in (('H',details[name]['H']),('source',details[name]['read']['source'])):
                        got=other[name]['H'] if key=='H' else other[name]['read']['source']
                        count+=inside(signs[i]*signs[j]*got[i][j],ref[u][v])
    return dict(comparisons=count,vertex_relabel=vertex,edge_order=order,signs=signs,
                scope='one full-graph representation of the paired target, not arbitrary graph admission')


def lifecycle(source,post):
    owner=t.ResearchOwner(source);actions=[]
    for kind,h in (('ordinary',F(1,8)),('split',None),('ordinary',F(3,25)),('reset',None)):
        before=owner.publication
        if kind=='ordinary':owner.ordinary(h);require(owner.publication.reset is before.reset,'ordinary preserves reset')
        elif kind=='split':owner.split();event=owner.publication
        else:owner.reset()
        actions.append(dict(kind=kind,h=str(h) if h is not None else None,before=before.identity,after=owner.publication.identity))
    require(owner.publication.current is event.reset,'reset restores actual target C/W/Z')
    sequence=dict(source=source.identity,actions=actions,final=t.snapshot(owner.publication))
    require(t.replay(source,sequence).identity==owner.publication.identity,'deterministic full-state replay')
    mutations=(('missing_lineage',lambda v:v.update(source='absent')),
        ('changed_request',lambda v:v['actions'][2].update(h='1/8')),
        ('wrong_profile',lambda v:v['final']['payload'].update(profile='other')),
        ('forged_reset_Z',lambda v:v['final']['payload']['reset']['carrier']['values'][4][4].update(lo='1',hi='1')),
        ('wrong_W_lineage',lambda v:v['final']['payload']['event'][1][0].__setitem__(1,4)),
        ('current_only_root_digest',lambda v:v['final']['payload']['event'].__setitem__(4,'current-only')),
        ('wrong_carrier_policy',lambda v:v['final']['payload']['event'].__setitem__(3,'projection')))
    negatives=[]
    for label,mutate in mutations:
        value=json.loads(json.dumps(sequence));mutate(value);value['final']['digest']=a.digest(value['final']['payload'])
        negatives.append(reject(lambda:t.replay(source,value),label))
    good=t.ResearchOwner(replace(source,current=post));before=good.publication
    def late(_):raise RuntimeError('injected late failure')
    negatives.append(reject(lambda:good.split(late),'late_event_failure',RuntimeError))
    require(good.publication is before,'late event full-publication rollback')
    actual=t.transfer;seen=[]
    def fail_reset(*args):
        require(good.publication is before,'both roles admitted before publication')
        value=actual(*args);seen.append(value)
        if len(seen)==2:raise a.AdmissionError('reset root failure')
        return value
    with patch.object(t,'transfer',side_effect=fail_reset):negatives.append(reject(good.split,'reset_target_root_failure'))
    require(len(seen)==2 and good.publication is before,'reset failure rollback')
    badreset=t.Role(t.predicates.paired_state(F(4),F(0),F(49,50),F(97,100)),source.reset.carrier)
    bad=t.ResearchOwner(replace(before,reset=badreset));captured=bad.publication
    negatives.append(reject(bad.split,'actual_reset_only_domain_failure'))
    require(bad.publication is captured,'actual domain rejection preserves publication')
    stepowner=t.ResearchOwner(source);before=stepowner.publication;actual_root=t.root;calls=[]
    def fail_restart(*args):
        calls.append(None);value=actual_root(*args)
        if len(calls)==3:raise a.AdmissionError('final restart failure')
        return value
    with patch.object(t,'root',side_effect=fail_restart):
        negatives.append(reject(lambda:stepowner.ordinary(F(1,8)),'ordinary_restart_failure'))
    require(len(calls)==3 and stepowner.publication is before,'ordinary scientific rollback')
    negatives.append(reject(lambda:stepowner.ordinary(F(1,8),late),'late_ordinary_failure',RuntimeError))
    require(stepowner.publication is before,'late ordinary rollback')
    for h in (F(0),F(1,10),F(13,100)):
        negatives.append(reject(lambda h=h:stepowner.ordinary(h),'invalid_request_'+str(h)))
        require(stepowner.publication is before,'invalid request rollback')
    negatives.append(reject(owner.split,'descendant_event_not_in_domain'))
    # Raw numerical output and serialized receipts cannot mint exact successors.
    for label,value in (('raw_output_not_request',post.state.data),('receipt_not_authority',source.payload())):
        with patch.object(t,'root',side_effect=AssertionError('forgery reached a root')):
            negatives.append(reject(lambda:t.step(source.current,value,source.profile),label))
    negatives.append(reject(lambda:t.Carrier('paired_source',source.current.carrier.values,t.domains.RZ**2,'forged'),
                            'caller_minted_carrier'))
    return dict(sequence=sequence,event_snapshot=t.snapshot(event),negatives=negatives,
                replay=True,complete_rollback=True,scope='research owner, not native ATC runtime')


def boundary_checks(profile):
    R=t.domains.RZ;tiny=F(1,2**300);rows=[];negatives=[]
    source=t.predicates.paired_state(F(29,10),F(0),F(24,25),F(99,100))
    target=t.predicates.exact_state('paired_target',(F(7,5),)*2+(F(8,5),)*2+(F(3,2),)*2,(F(24,25),)*5)
    for state in (source,target):
        m=len(state.W)
        for sign in (-1,1):
            # Four equal diagonal entries have Frobenius norm exactly R.
            Z=tuple(tuple(sign*R/2 if i==j and i<4 else F(0) for j in range(m)) for i in range(m))
            carrier=t.exact_carrier(state.graph,Z);role=t.Role(state,carrier)
            require(carrier.norm_squared_upper==R**2 and r.norm_upper(x for row in carrier.values for x in row)>R,
                    'boundary actually straddles outward-grid norm; exact predicate must decide')
            selected=t.root(role,profile);following,details=t.step(role,F(3,25),profile)
            require(following.carrier.norm_squared_upper<=R**2,'executing convex invariant')
            if state.graph=='paired_source':
                event_source=t.Role(t.predicates.paired_state(F(3),F(0),F(24,25),F(99,100)),carrier)
                transferred,_,_=t.transfer(event_source,32768,profile)
                require(transferred.carrier.norm_squared_upper==R**2,'lossless endpoint transfer')
            for direction in (-1,1):
                changed=tuple(tuple(x*(1+direction*tiny) for x in row) for row in Z)
                if direction<0:t.root(t.Role(state,t.exact_carrier(state.graph,changed)),profile)
                else:negatives.append(reject(lambda:t.exact_carrier(state.graph,changed),'RZ_outside_subgrid_'+state.graph+str(sign)))
            rows.append(dict(graph=state.graph,sign=sign,root=root_summary(selected),
                             after_bound=following.carrier.norm_squared_upper,exact_radius=True))
    # Exact shape/support/decoration are checked before intervals can hide them.
    Z=[[F(0)]*5 for _ in range(5)];Z[0][2]=Z[2][0]=tiny
    negatives.append(reject(lambda:t.exact_carrier('paired_target',tuple(map(tuple,Z))),'nonstar_subgrid'))
    Z=[[F(0)]*4 for _ in range(4)];Z[0][0]=tiny
    negatives.append(reject(lambda:t.exact_carrier('paired_source',tuple(map(tuple,Z))),'broken_decoration_subgrid'))
    for label,st in (('x_below',t.predicates.paired_state(F(29,10)-tiny,F(0),F(99,100),F(1))),
                    ('W_below',t.predicates.paired_state(F(3),F(0),F(24,25)-tiny,F(99,100)))):
        negatives.append(reject(lambda:t.Role(st,t.exact_carrier('paired_source',tuple((F(0),)*4 for _ in range(4)))),label))
    # Actual binary64 points straddling R, no epsilon-expanded admission.
    data=a.State(target.C,(I(F(97,100)),)*5).represented();value=float(R)
    low=math.nextafter(value,-math.inf);high=math.nextafter(value,math.inf)
    require(F(low)<R<F(high),'represented bracketing')
    def matrix(x):return tuple(tuple(I(F(x)) if i==j==4 else I(0) for j in range(5)) for i in range(5))
    t.represented_root(data,matrix(low),profile)
    negatives.append(reject(lambda:t.represented_root(data,matrix(high),profile),'represented_outside_RZ'))
    drift=list(data.C);drift[0]=drift[1]=data.C[0]+F(1,2**48);drift=a.State(tuple(drift),data.W)
    rd=t.represented_root(drift,matrix(low),profile)
    require(rd['role_binding'] is None and sum(F(x.lo,GRID) for x in drift.C)!=9,'no charge-nine authority for represented root')
    negatives.append(reject(lambda:t.root(drift,profile),'represented_state_not_exact_role'))
    invalid=[list(row) for row in matrix(low)];invalid[0][0]=I.bounds(-1,1)
    negatives.append(reject(lambda:t.represented_root(data,tuple(map(tuple,invalid)),profile),'overlapping_nonpoint_Z'))
    return dict(exact_boundary_cases=rows,negative_pressure=negatives,subgrid_offset=tiny,
                represented_inside=F(low),represented_outside=F(high),no_epsilon=True,
                represented_nonzero_charge_drift_not_promoted=True)


def representation(targets,profile):
    rows=[]
    for name,exact in zip(('current','reset'),targets,strict=True):
        data=exact.state.data.represented();Z=tuple(tuple(a.project(x) for x in row) for row in exact.carrier.values)
        beats=[]
        for request in t.CONTRACT['finite_schedule']:
            h=F(request);rh=F(float(h))
            if rh<t.domains.ci.HMIN:rh=F(math.nextafter(float(h),math.inf))
            exact,details=t.step(exact,h,profile)
            data,Z,rounded=t.represented_step(data,Z,rh,profile)
            er,rr=details['restart'],rounded['restart']
            flatten=lambda matrix:tuple(x for row in matrix for x in row)
            errors=dict(C=error(exact.state.C,data.C),W=error(exact.state.W,data.W),
                Z=error(flatten(exact.carrier.values),flatten(Z)),
                J=error(er['read']['current'],rr['read']['current']),H=error(flatten(er['H']),flatten(rr['H'])))
            require(max(errors.values())<F(t.CONTRACT['finite_error_bound']),'finite C/W/Z/J/H error bound')
            require(rr['role_binding'] is None,'rounded diagnostics never have exact proof witness')
            beats.append(dict(h=h,represented_h=rh,errors=errors,charge_drift=sum(F(x.lo,GRID) for x in data.C)-9,
                binary64=dict(C=[float(F(x.lo,GRID)).hex() for x in data.C],W=[float(F(x.lo,GRID)).hex() for x in data.W],
                              Z=[[float(F(x.lo,GRID)).hex() for x in row] for row in Z]),
                exact_root_digest=er['selected_joint_root_digest'],represented_root_digest=rr['selected_joint_root_digest']))
        rows.append(dict(role=name,steps=beats))
    return dict(cases=rows,tau_binary64=a.TAU64,intermediate_binary64_rounding=False,
                exact_charge_theorem_applied_to_rounded=False,infinite_numerical_conformance=False)


def run():
    stages_result,source,post,targets,dec=stages()
    evidence=dict(stages=stages_result,covariance=covariance(targets[0],dec[0],source.profile),
        lifecycle=lifecycle(source,post),boundaries=boundary_checks(source.profile),
        representation=representation(targets,source.profile),domains=t.bounds())
    paths={Path(__file__).resolve(),ROOT/INV/'decisions/ATCCIP2Reference.md',
           ROOT/INV/'evidence/atc-cip/ATCCIP0Certificate.json',ROOT/INV/'evidence/atc-cip/ATCCIP1Certificate.json',
           ROOT/INV/'evidence/atc-cip/CIP1-Preregistration.json'}
    paths.update((ROOT/INV/'evidence/atc-cip-successor').glob('*Review*.md'))
    paths.add(ROOT/INV/'evidence/atc-cip-successor/CIP01-ReviewDisposition.json')
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/INV) and path.suffix=='.py':paths.add(path)
    record=a.encode(dict(schema='grcv4_atc_cip2_v1',status='prepared_pending_independent_review',
        scientific_acceptance=False,graph_admitted=False,native_ATC_executed=False,ATC2_closed=False,
        contract=t.CONTRACT,evidence=evidence,
        claim_updates=[dict(claim_id='ATC-CIP-REFERENCE-02',claim_class='proposed_conditional',profile_scope=['A_CI_PC'],
            predecessor_handles=['ATC-CIP-ROOT-00','ATC-CIP-CHAIN-01'],
            debt_refs=['ATC7-DB-'+x for x in ('03','04','05','10','13','14','15','16','21','23','24','26','28')],
            local_debt_discharge=False,native_authority=False)],
        source_bindings=[dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)) for path in sorted(paths)]))
    record['record_digest']=a.digest(record)
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        value=json.loads(RECORD.read_text())
        require(value['record_digest']==a.digest({k:v for k,v in value.items() if k!='record_digest'}),'record identity')
        for row in value['source_bindings']:require(sha(ROOT/row['path'])==row['sha256'],'source drift: '+row['path'])
        print(json.dumps(dict(status='passed',scope='retained identities only',record_digest=value['record_digest'])))
    else:print(json.dumps(run(),indent=2))
