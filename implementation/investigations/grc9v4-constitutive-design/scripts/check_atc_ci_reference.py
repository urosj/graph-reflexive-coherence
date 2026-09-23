#!/usr/bin/env python3
"""CI-3 independent joint-root, lifecycle and finite representation checks.

Research only; prints a source-bound record, writes nothing. No CI/PC/OS
discovery campaign or production registration is performed.
"""
from dataclasses import replace
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
INV=Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0,str(ROOT/INV/'research'))
import atc_ci_reference as t
import atc_ci_oracle as independent
import check_atc_ci_boundaries as boundaries
a,r,p,I,GRID=t.a,t.r,t.p,t.I,t.GRID
require=t.require


def inside(value,enclosure):
    if isinstance(enclosure,I):
        require(enclosure.contains(F(value)), 'independent scalar outside certified enclosure')
        return 1
    if isinstance(enclosure,dict): return sum(inside(value[k],v) for k,v in enclosure.items())
    return sum(inside(x,y) for x,y in zip(value,enclosure,strict=True))


def compare_root(other,root):
    require(root['certificate_digest']==a.digest(a.encode(root['certificate'])), 'root certificate identity')
    require(root['selected_joint_root_digest']==a.digest(a.encode({k:v for k,v in root.items()
            if k!='selected_joint_root_digest'})), 'complete selected joint-root identity')
    return inside(other['H'],root['H'])+inside(other['generated_H'],root['generated_H'])+inside(other['read'],root['read'])


def compare(other,state,details):
    count=inside(other['C'],state.C)+inside(other['W'],state.W)
    count+=compare_root(other['selected'],details['selected'])+compare_root(other['restart'],details['restart'])
    for key in ('writer_descriptor','writer_drive','decay'): count+=inside(other[key],details[key])
    return count


def reject(call,label,exception=a.AdmissionError):
    try: call()
    except exception as exc: return dict(case=label,reason=str(exc))
    raise AssertionError('negative pressure admitted: '+label)


def seeds():
    exact=[]
    for x,y,u,v in ((F(59,20),F(1,100),F(97,100),F(99,100)),
                      (F(33,10),-F(3,200),F(49,50),F(97,100))):
        exact.append(dict(C=((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,),W=(u,u,v,v)))
    return t.Publication(*(t.exact_state('paired_source',**value) for value in exact)),exact


def root_summary(root,full=False):
    value=dict(selected_joint_root_digest=root['selected_joint_root_digest'],
        certificate_digest=root['certificate_digest'],profile_binding=root['profile_binding'],
        state_binding=root['state_binding'],graph=root['graph'],
        domain_witness_binding=root['domain_witness_binding'],
        H_digest=a.digest(a.encode(root['H'])),current_digest=a.digest(a.encode(root['read']['current'])),
        root_error=root['root_error'],residual_at_center=root['residual_at_center'],iterations=root['iterations'],
        joint_current_residual_upper=r.norm_upper(root['joint_current_residual']),
        joint_geometry_residual_upper=r.norm_upper(x for row in root['joint_geometry_residual'] for x in row))
    if full:value.update(H=root['H'],current=root['read']['current'])
    return value


def stage_checks():
    source,exact=seeds();profile=source.profile
    post,details=t.step(source.current,F(1,8),profile)
    other=independent.evaluate(a.GRAPHS['paired_source'],**exact[0],parameters=profile.parameters,h=F(1,8))
    comparisons=compare(other,post,details)
    chosen=t.select(post,profile)
    require(a.encode(chosen['root'])==a.encode(details['restart']),
            'fresh event operand equals complete restart root, including interval values')
    with localcontext() as ctx:
        ctx.prec=110
        J=other['restart']['read']['current'];k=round(D(65536)*(J[0]+J[1])/sum(J))
    require(chosen['k']==k==33616, 'independent CI-native allocator and unchanged CI1 anchor')
    old=json.loads((ROOT/INV/'evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json').read_text())['CI_1']
    require(int(old['choice']['k'])==k,'retained reviewed CI1 prescription')
    for values,retained in ((post.C,old['postbeat']['C']),(post.W,old['postbeat']['W']),
                           (chosen['root']['read']['current'],old['poststate_root']['current'])):
        require(all(x.lo<=int(y['hi']) and int(y['lo'])<=x.hi for x,y in zip(values,retained,strict=True)),
                'reviewed CI1 anchor enclosures agree')
    require(a.encode(details['selected']['H'])!=a.encode(details['restart']['H']), 'poststate geometry is fresh')
    require(a.encode(details['selected']['read']['current'])!=a.encode(details['restart']['read']['current']),
            'poststate current is not consumed current')
    # Keep J identical but corrupt only H: the full-root comparison must fail.
    altered=dict(other['restart']);H=[list(row) for row in altered['H']]
    with localcontext() as ctx:
        ctx.prec=110;H[0][0]+=D('1e-8')
    altered['H']=H
    root_mutation=reject(lambda:compare_root(altered,details['restart']),'H_only_mutation_with_unchanged_J')
    rows=[];targets=[];oracle_targets=[]
    for label,state,seed in (('current',post,other),('reset',source.reset,exact[1])):
        target,admitted=t.transfer(state,k,profile);dec=independent.transfer(seed,k)
        targets.append(target);oracle_targets.append(dec)
        comparisons+=inside(dec['C'],target.C)+inside(dec['W'],target.W)
        comparisons+=compare_root(independent.evaluate(a.GRAPHS['paired_target'],**dec,parameters=profile.parameters),admitted)
        for h in (t.domains.HMIN,t.domains.HMAX):
            nxt,stage=t.step(target,h,profile)
            oracle=independent.evaluate(a.GRAPHS['paired_target'],**dec,parameters=profile.parameters,h=h)
            n=compare(oracle,nxt,stage);comparisons+=n
            stale=t.conductance('paired_target',nxt.C,stage['selected']['read']['descriptor'],stage['selected']['read']['current'],profile)
            wrong=t.conductance('paired_target',nxt.C,stage['writer_descriptor'],stage['restart']['read']['current'],profile)
            distinct=lambda xs,ys:any(x.hi<y.lo or y.hi<x.lo for x,y in zip(xs,ys,strict=True))
            require(distinct(stale,stage['writer_drive']), 'stale descriptor mutation separated')
            require(distinct(wrong,stage['writer_drive']), 'poststate-current writer mutation separated')
            radius=r.norm_upper(c-F(3,2) for c in nxt.C)
            require(radius<F(2,3), 'both-role target entry')
            require(stage['decay'].lo>GRID/2 if h==t.domains.HMIN else stage['decay'].contains(F(1,2)),
                    'physical tau fixed while request varies')
            rows.append(dict(role=label,h=h,scalar_comparisons=n,first_step_radius=radius,
                selected=root_summary(stage['selected']),restart=root_summary(stage['restart']),
                stale_descriptor_rejected=True,poststate_J_writer_rejected=True))
    C=(F(7,5),)*2+(F(8,5),)*2+(F(3,2),)*2;W=(F(97,100),)*4+(F(1),)
    corner=t.exact_state('paired_target',C,W)
    for endpoint,h in ((0,t.domains.HMIN),(1,t.domains.HMAX)):
        prof=t.Profile(tuple(sorted((k,v[endpoint]) for k,v in t.domains.PARAMETER_BOX.items())))
        nxt,stage=t.step(corner,h,prof)
        n=compare(independent.evaluate(a.GRAPHS['paired_target'],C,W,prof.parameters,h),nxt,stage);comparisons+=n
        rows.append(dict(parameter_corner=endpoint,h=h,profile=prof.parameters,scalar_comparisons=n,
            selected=root_summary(stage['selected']),restart=root_summary(stage['restart'])))
    return dict(independent_scalar_comparisons=comparisons,source_k=k,
        source_selected=root_summary(details['selected']),source_event=root_summary(details['restart'],full=True),
        complete_restart_equals_fresh_root=True,reviewed_CI1_anchor_preserved=True,
        H_only_mutation=root_mutation,checks=rows,
        oracle='independent 110-digit Decimal edge-local equations with nonidentity initial geometry'),source,post,targets,oracle_targets


def covariance(target,oracle_target,profile):
    graph=a.GRAPHS['paired_target'];n,edges,pos=graph;m=len(edges)
    vertex=(2,5,0,4,1,3);order=(4,2,0,3,1);signs=(-1,1,-1,1,-1)
    newC=[None]*n;newpos=[None]*n
    for i in range(n):newC[vertex[i]]=oracle_target['C'][i];newpos[vertex[i]]=pos[i]
    newedges=[]
    for old,sign in zip(order,signs,strict=True):
        u,v=edges[old];u,v=vertex[u],vertex[v]
        newedges.append((u,v) if sign==1 else (v,u))
    got=independent.evaluate((n,tuple(newedges),tuple(newpos)),newC,
        tuple(oracle_target['W'][i] for i in order),profile.parameters)
    ref=t.root(target,profile);checks=0
    with localcontext() as ctx:
        ctx.prec=110
        for i,old in enumerate(order):
            checks+=inside(signs[i]*got['read']['current'][i],ref['read']['current'][old])
            for j,other in enumerate(order):
                checks+=inside(signs[i]*signs[j]*got['H'][i][j],ref['H'][old][other])
    return dict(vertex_relabel=vertex,edge_reorder=order,orientation_signs=signs,
        joint_J_H_comparisons=checks,oracle_residual=str(got['residual']),
        scope='one full-graph representation pressure; not arbitrary-template admission')


def lifecycle(source,post):
    owner=t.ResearchOwner(source);actions=[]
    for kind,h in (('ordinary',F(1,8)),('split',None),('ordinary',F(3,25)),('reset',None)):
        before=owner.publication
        if kind=='ordinary':owner.ordinary(h)
        elif kind=='split':event_roots=owner.split();event=owner.publication
        else:owner.reset()
        if kind=='ordinary':require(owner.publication.reset is before.reset,'ordinary preserves actual reset')
        actions.append(dict(kind=kind,h=str(h) if h is not None else None,before=before.identity,after=owner.publication.identity))
    require(owner.publication.current is event.reset,'reset restores independently transported target W/C')
    sequence=dict(source=source.identity,actions=actions,final=t.snapshot(owner.publication))
    require(t.replay(source,sequence).identity==owner.publication.identity,'physical sequence replay')
    negatives=[]
    for label,mutate in (
        ('missing_source_lineage',lambda v:v.update(source='absent')),
        ('changed_request',lambda v:v['actions'][2].update(h='1/8')),
        ('wrong_profile',lambda v:v['final']['payload'].update(profile='other')),
        ('forged_reset_W',lambda v:v['final']['payload']['reset']['numerical']['W'][0].update(lo='1',hi='1')),
        ('invalid_W_lineage',lambda v:v['final']['payload']['event'][1][0].__setitem__(1,4)),
        ('forged_joint_root_identity',lambda v:v['final']['payload']['event'].__setitem__(4,'current-only'))):
        changed=json.loads(json.dumps(sequence));mutate(changed)
        changed['final']['digest']=a.digest(changed['final']['payload'])
        negatives.append(reject(lambda:t.replay(source,changed),label))
    event_source=replace(source,current=post)
    bad=t.ResearchOwner(replace(event_source,reset=t.paired_state(F(4),F(0),F(49,50),F(97,100))))
    before=bad.publication
    negatives.append(reject(bad.split,'actual_reset_only_transfer_domain_rejection'))
    require(bad.publication is before and before.current is post,'failed event preserves committed postbeat')
    good=t.ResearchOwner(event_source);before=good.publication;actual=t.transfer;calls=[]
    def reset_failure(state,k,profile):
        require(good.publication is before,'no publication before both roles admit')
        result=actual(state,k,profile);calls.append(result)
        if len(calls)==2:raise a.AdmissionError('injected reset target root rejection')
        return result
    with patch.object(t,'transfer',reset_failure):
        negatives.append(reject(good.split,'reset_root_failure_after_current_root_pass'))
    require(len(calls)==2 and good.publication is before,'both-role root rollback')
    def late(_):raise RuntimeError('unexpected late publication error')
    negatives.append(reject(lambda:good.split(late),'unexpected_late_event_error',RuntimeError))
    require(good.publication is before,'unexpected event error preserves full publication')
    stepowner=t.ResearchOwner(source);before=stepowner.publication;actual_root=t.root;seen=[]
    def restart_failure(state,profile):
        seen.append(state)
        result=actual_root(state,profile)
        if len(seen)==3:raise a.AdmissionError('injected final joint-root rejection')
        return result
    with patch.object(t,'root',restart_failure):
        negatives.append(reject(lambda:stepowner.ordinary(F(1,8)),'ordinary_final_root_failure'))
    require(len(seen)==3 and stepowner.publication is before,'ordinary final-root atomicity')
    negatives.append(reject(lambda:stepowner.ordinary(F(1,8),late),'unexpected_late_ordinary_error',RuntimeError))
    require(stepowner.publication is before,'unexpected ordinary error preserves full publication')
    for h in (F(0),F(1,10),F(13,100)):
        negatives.append(reject(lambda h=h:stepowner.ordinary(h),'request_outside_domain_'+str(h)))
        require(stepowner.publication is before,'invalid request rollback')
    negatives.append(reject(owner.split,'descendant_event_outside_scope'))
    negatives.append(reject(lambda:t.root(source.current.data,source.profile),'raw_state_not_exact_charge_witness'))
    negatives.append(reject(lambda:t.raw_root('paired_source',source.current.data,source.profile),'raw_source_root_without_witness'))
    negatives.append(reject(lambda:t.step(source.current,F(1,8),t.Profile(tuple(sorted({**a.PARAMS,'kh':F(2)}.items())))),
                            'profile_outside_proved_box'))
    selected=t.root(source.current,source.profile)
    negatives.append(reject(lambda:t.advance_raw('paired_source',source.reset.data,F(1,8),selected,source.profile,domain_witness=source.reset),
                            'stale_root_wrong_state'))
    alt=t.Profile(tuple(sorted({**a.PARAMS,'kh':F(1)}.items())))
    negatives.append(reject(lambda:t.advance_raw('paired_source',source.current.data,F(1,8),selected,alt,domain_witness=source.current),
                            'stale_root_wrong_profile'))
    negatives.append(reject(lambda:a.rounded_share(I.bounds(I(F(1,2)-F(1,20000)).lo,I(F(1,2)+F(1,20000)).hi),I(F(1,2))),
                            'unresolved_share'))
    for k in (32766,32767):
        share=F(2*k+1,131072);got,_=a.rounded_share(I(share),I(1-share))
        require(got==round(F(2*k+1,2)),'exact half-tie parity')
    return dict(sequence=sequence,event_snapshot=t.snapshot(event),source_publication=source.payload(),
        current_target_root=root_summary(event_roots['current_root'],full=True),reset_target_root=root_summary(event_roots['reset_root'],full=True),
        both_role_roots=True,zero_time_event=True,complete_rollback=True,replay=True,
        negative_pressure=negatives)


def error(xs,ys):
    return max(F(max(abs(x.lo-y.hi),abs(x.hi-y.lo)),GRID) for x,y in zip(xs,ys,strict=True))


def representation(targets,profile):
    cases=[]
    for label,exact in zip(('current','reset'),targets,strict=True):
        rounded=exact.data.represented();rows=[]
        for h in map(F,t.CONTRACT['finite_schedule']):
            represented_h=F(float(h))
            if represented_h<t.domains.HMIN: represented_h=F(math.nextafter(float(h),math.inf))
            exact,exact_stage=t.step(exact,h,profile)
            rounded,rounded_stage=t.represented_step(rounded,represented_h,profile)
            er,rr=exact_stage['restart'],rounded_stage['restart']
            errors=dict(C=error(exact.C,rounded.C),W=error(exact.W,rounded.W),
                J=error(er['read']['current'],rr['read']['current']),
                H=error(tuple(v for row in er['H'] for v in row),tuple(v for row in rr['H'] for v in row)))
            require(max(errors.values())<F(t.CONTRACT['finite_error_bound']), 'finite C/W/J/H error budget')
            require(r.norm_upper(c-F(3,2) for c in rounded.C)<F(2,3),'represented return ball observed')
            rows.append(dict(h=h,represented_h=represented_h,errors=errors,
                charge_drift=sum((a.bound(v)[0] for v in rounded.C),F(0))-9,
                binary64={k:[float(a.bound(v)[0]).hex() for v in getattr(rounded,k)] for k in ('C','W')},
                exact_root=root_summary(er),represented_root=root_summary(rr)))
        cases.append(dict(role=label,steps=rows,exact_charge_theorem_applied_to_rounded=False))
    return dict(recipe=dict(t.CONTRACT),tau_binary64=a.TAU64,cases=cases,
        intermediate_binary64_rounding=False,geometry_is_reconstructed_not_stored=True,
        infinite_numerical_conformance=False)


def run():
    # Any accidental reuse of a realization-specific predecessor fails loudly.
    with patch.object(r,'ci_read',side_effect=AssertionError('old point CI solver forbidden in new reference')), \
         patch.object(r,'pc_read',side_effect=AssertionError('PC read forbidden in CI')), \
         patch.object(a,'evaluate',side_effect=AssertionError('OS pass forbidden in CI')):
        stage,source,post,targets,oracle_targets=stage_checks()
        evidence=dict(stages=stage,covariance=covariance(targets[0],oracle_targets[0],source.profile),
            lifecycle=lifecycle(source,post),representation=representation(targets,source.profile),
            boundary_admission=boundaries.run())
    value=a.encode(dict(schema='grcv4_atc_ci3_reference_v1',
        status='reviewed_core_and_boundary_pass_provenance_fix_validated_ready_for_scoped_adjudication',
        scientific_acceptance=False,graph_admitted=False,native_ATC_executed=False,ATC2_closed=False,
        review_disposition=dict(CI2='PASS; scientifically closed',CI3_core='PASS',
            CI3_original_domain_admission='PASS; independently reviewed after correction',
            CI3_derived_witness_provenance='review HOLD addressed by executing-only certified_step and forgery controls',
            correction='sealed successor execution, predicate compatibility and explicit funding; checked by boundary_admission',
            independent_postcorrection_review=False),
        contract=dict(t.CONTRACT),profile_digest=t.Profile().identity,evidence=evidence,
        claim_updates=[dict(claim_id='ATC-CI-REFERENCE-03',claim_class='conditional',profile_scope=['A_CI'],
            predecessor_handles=['ATC-CI-DOMAIN-02','ATC-CI-CHAIN-01','ATC-CI-STEP-01'],
            debt_refs=['ATC7-DB-'+n for n in ('03','05','10','13','14','15','16','21','23','26','28')],
            local_debt_discharge=False,native_authority=False,
            still_open='independent review and DB24/source admission; exact production conservation policy, native integration, wider environment/formation and aggregate ATC2')]))
    paths={Path(__file__).resolve(),ROOT/INV/'decisions/ATCCIDomainsAndReference.md',
        ROOT/INV/'evidence/atc-ci-successor/ATCCI2DomainCertificate.json',
        ROOT/INV/'evidence/atc-ci-successor/CI2CI3-IndependentReview.md',
        ROOT/INV/'evidence/atc-ci-successor/CI3-DerivedWitness-IndependentReview.md',
        ROOT/INV/'evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json'}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/INV) and path.suffix=='.py':paths.add(path)
    value['source_bindings']=[dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                              for path in sorted(paths)]
    value['record_digest']=a.digest(value)
    return value


if __name__=='__main__': print(json.dumps(run(),indent=2))
