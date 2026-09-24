#!/usr/bin/env python3
"""PC-4 domain/reference/representation pressure; investigation-only stdout.

Uniform rational proof, independent Decimal stages, bounded owner/replay,
four-step publication-rounding comparison per role. No parameter search.
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
import atc_pc_reference as t
a,r,p,I,GRID=t.a,t.r,t.p,t.I,t.GRID
require=t.require

REVIEWED_RECORD_DIGEST='0a1369d4bdfa1edbf44f757c0ef0fcc25b5af5398c14d119075170407975cc91'
REVIEWED_MATH_DIGEST='d78a0c362250b9b371e080105bf18ba26c13724a1aeb0c9fc85aae224b22362f'


def review_metadata(value):
    mathematical={k:value[k] for k in ('contract','profile_digest','evidence')}
    actual=a.digest(mathematical)
    require(actual==REVIEWED_MATH_DIGEST,'PC4 reviewed contract/profile/evidence changed')
    return dict(verdict='PASS_bounded_paired_domain_reference_representation_closure',
        reviewed_record_digest=REVIEWED_RECORD_DIGEST,reviewed_mathematical_payload_digest=actual,
        review_path=(INV/'evidence/atc-ci-pc/PC4-IndependentReview.md').as_posix(),
        independent_reproduction='reported by supplied review; no corrective numerical rerun required',
        reported_extra_pressure=dict(mixed_parameter_corners=18,target_cases=36,source_onset_cases=36,
            source_resolved_k_range=[33597,33623],evidence_kind='reviewer-reported diagnostic; not new local execution or a whole-box formation theorem'),
        whole_box_theorem_scope='uniform obstruction/invariance and transfer-entry/return/asymptotics conditional on an admitted event state with a resolved source-only share; no universal event formation',
        potential_scope='C1 slope-envelope analytic theorem; quadratic-subclass executable reference and oracle',
        source_admission_debt='ATC7-DB-24 remains open',formal_scoped_adjudication_pending=True,
        environment_scope='active coupled-environment carrier transport is a future extension, not a PC4 defect',
        next_work='formal scoped claim/debt adjudication; no PC5 discovery required; parallel CI2/CI3 remain unfinished')


def decimal(value):
    if isinstance(value,D):return value
    value=F(value);return D(value.numerator)/D(value.denominator)


def oracle(graph,C,W,Z,h,profile):
    """Independent edge-local Decimal equations; no reference stage calls."""
    with localcontext() as ctx:
        ctx.prec=110
        n,edges,pos=a.GRAPHS[graph];m=len(edges)
        C,W=tuple(map(decimal,C)),tuple(map(decimal,W))
        Z=tuple(tuple(map(decimal,row)) for row in Z)
        par={k:decimal(v) for k,v in profile.parameters};hh=decimal(h)
        def descriptors(resources):
            values=[]
            for i in range(n):
                numerator,denominator=D(0),D(1)
                for u,v in edges:
                    if i not in (u,v):continue
                    j=v if i==u else u;dx=D(pos[j]-pos[i])
                    numerator+=dx*(resources[j]-resources[i]);denominator+=dx*dx
                values.append(numerator/denominator)
            return tuple(values)
        def conductance(resources,desc,current):
            return tuple((-(par['alpha']*(resources[u]+resources[v])+par['beta']*(desc[u]-desc[v])**2+par['gamma']*j*j)/2).exp()
                         for (u,v),j in zip(edges,current,strict=True))
        def solve(H,b):
            rows=[list(row)+[v] for row,v in zip(H,b,strict=True)]
            for k in range(m):
                pivot=rows[k][k];rows[k]=[x/pivot for x in rows[k]]
                for i in range(k+1,m):
                    factor=rows[i][k];rows[i]=[x-factor*y for x,y in zip(rows[i],rows[k],strict=True)]
            answer=[D(0)]*m
            for k in reversed(range(m)):answer[k]=rows[k][-1]-sum(rows[k][j]*answer[j] for j in range(k+1,m))
            return tuple(answer)
        def read(resources,weights,carrier):
            H=tuple(tuple(D(int(i==j))+par['kh']*z for j,z in enumerate(row)) for i,row in enumerate(carrier))
            differences=tuple(resources[u]-resources[v] for u,v in edges)
            delta=tuple(sum((H[i][j]-int(i==j))*differences[j] for j in range(m)) for i in range(m))
            lap,geometry=[D(0)]*n,[D(0)]*n
            for (u,v),w,d,g in zip(edges,weights,differences,delta,strict=True):
                lap[u]+=w*d;lap[v]-=w*d;geometry[u]+=g;geometry[v]-=g
            potential=tuple(par['a']*c+par['nu']*c*c/2 for c in resources)
            phi=tuple(l-v+par['kah']*g for l,v,g in zip(lap,potential,geometry,strict=True))
            baseline=tuple(-w*(phi[u]-phi[v]) for (u,v),w in zip(edges,weights,strict=True))
            desc=descriptors(resources);drive=conductance(resources,desc,baseline)
            q=tuple((w-g)/(w+g) for w,g in zip(weights,drive,strict=True))
            J=tuple(b/(1-par['chi']*v) for b,v in zip(baseline,q,strict=True))
            readback=tuple(par['chi']*v*j for v,j in zip(q,J,strict=True));flat=solve(H,readback)
            S=tuple(tuple(D(len(set(e)&set(f)))*flat[i]*flat[j]/2 for j,f in enumerate(edges)) for i,e in enumerate(edges))
            return dict(H=H,potential=potential,phi=phi,baseline=baseline,descriptor=desc,
                        drive=drive,current=J,readback=readback,flat=flat,source=S)
        selected=read(C,W,Z);newC=list(C)
        for (u,v),j in zip(edges,selected['current'],strict=True):newC[u]-=hh*j;newC[v]+=hh*j
        desc=descriptors(newC);drive=conductance(newC,desc,selected['current'])
        decay=(-8*hh*D(2).ln()).exp()
        newW=tuple((decay*w.ln()+(1-decay)*g.ln()).exp() for w,g in zip(W,drive,strict=True))
        newZ=tuple(tuple(decay*z+(1-decay)*s for z,s in zip(row,other,strict=True))
                   for row,other in zip(Z,selected['source'],strict=True))
        return dict(C=tuple(newC),W=newW,Z=newZ,selected=selected,writer_descriptor=desc,
                    writer_drive=drive,decay=decay,restart=read(newC,newW,newZ))


def inside(value,enclosure):
    if isinstance(enclosure,I):
        require(enclosure.contains(F(value)),'Decimal cross-check outside outward interval')
        return 1
    if isinstance(enclosure,dict):return sum(inside(value[k],enclosure[k]) for k in enclosure)
    return sum(inside(x,y) for x,y in zip(value,enclosure,strict=True))


def compare(role,details,other):
    count=inside(other['C'],role.state.C)+inside(other['W'],role.state.W)+inside(other['Z'],role.carrier.values)
    count+=inside(other,details)
    return count


def seeds():
    current,reset=r.fixtures()
    roles=(t.Role(current,r.diagonal_z(F(1,16384))),t.Role(reset,r.diagonal_z(F(1,24576))))
    exact=[]
    for x,y,u,v,z in ((F(59,20),F(1,100),F(97,100),F(99,100),F(1,16384)),
                      (F(33,10),-F(3,200),F(49,50),F(97,100),F(1,24576))):
        exact.append(dict(C=((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,),W=(u,u,v,v),
                          Z=tuple(tuple(z if i==j else F(0) for j in range(4)) for i in range(4))))
    return t.Publication(*roles),exact


def oracle_transfer(source,k):
    # Independent canonical 2+2 formula, not the incidence-map implementation.
    with localcontext() as ctx:
        ctx.prec=110
        C,W=tuple(map(decimal,source['C'])),tuple(map(decimal,source['W']))
        Z=tuple(tuple(map(decimal,row)) for row in source['Z'])
        c=Z[0][2];aa,b,d,e=Z[0][0],Z[0][1],Z[2][2],Z[2][3]
        targetZ=((aa,b,D(0),D(0),-c),(b,aa,D(0),D(0),-c),
                 (D(0),D(0),d,e,c),(D(0),D(0),e,d,c),(-c,-c,c,c,D(0)))
        share=D(k)/D(65536)
        return dict(C=C[:4]+(share*C[4],(1-share)*C[4]),W=W+(D(1),),Z=targetZ)


def stage_checks():
    source,exact=seeds();profile=source.profile
    post,details=t.step(source.current,F(1,8),profile)
    other=oracle('paired_source',**exact[0],h=F(1,8),profile=profile)
    comparisons=compare(post,details,other)
    # Existing reviewed point is embedded, not overwritten by generalization.
    old,oldZ,_,restart=r.pc_step(source.current.state,source.current.carrier)
    require(all(r.same(x,y) for x,y in zip(post.state.C,old.C)),'PC3 continuity agrees')
    require(all(x.lo<=y.hi and y.lo<=x.hi for x,y in zip(post.state.W,old.W)),'log-writer encloses PC3 square-root writer')
    chosen=t.select(post,profile)
    with localcontext() as ctx:
        ctx.prec=110
        J=other['restart']['current'];ok=round(D(65536)*(J[0]+J[1])/sum(J))
    require(ok==chosen['k']==33615,'independent poststate PC allocator')
    require(a.encode(details['selected']['current'])!=a.encode(details['restart']['current']),'event read not consumed current')
    rows=[];targets=[]
    for label,role,seed in (('current',post,other),('reset',source.reset,exact[1])):
        target,receipt,rd=t.transfer(role,chosen['k'],profile);odec=oracle_transfer(seed,chosen['k'])
        comparisons+=inside(odec['C'],target.state.C)+inside(odec['W'],target.state.W)+inside(odec['Z'],target.carrier.values)
        targets.append(target)
        for h in (F(3,25),F(1,8)):
            nxt,stage=t.step(target,h,profile)
            od=oracle('paired_target',**odec,h=h,profile=profile)
            n=compare(nxt,stage,od);comparisons+=n
            stale=t.conductance('paired_target',nxt.state.C,stage['selected']['descriptor'],stage['selected']['current'],profile)
            wrong=t.conductance('paired_target',nxt.state.C,stage['writer_descriptor'],stage['restart']['current'],profile)
            def distinct(xs,ys):return any(x.hi<y.lo or y.hi<x.lo for x,y in zip(xs,ys,strict=True))
            require(distinct(stale,stage['writer_drive']),'stale descriptor mutation discriminated')
            require(distinct(wrong,stage['writer_drive']),'poststate writer-current mutation discriminated')
            wrongZ=tuple(tuple(stage['decay']*z+(1-stage['decay'])*s for z,s in zip(row,ss,strict=True))
                         for row,ss in zip(target.carrier.values,stage['restart']['source'],strict=True))
            require(distinct(tuple(v for row in wrongZ for v in row),tuple(v for row in nxt.carrier.values for v in row)),
                    'poststate structural-source substitution discriminated')
            require(stage['decay'].lo>GRID/2 if h==F(3,25) else stage['decay'].contains(F(1,2)),
                    'fixed physical tau, not half decay for every request')
            rows.append(dict(role=label,h=h,scalar_comparisons=n,stage_digest=a.digest(a.encode(stage)),
                             stale_descriptor_rejected=True,poststate_J_writer_rejected=True,new_S_writer_rejected=True))
    # Two declared box corners, not a sampled proof or parameter search.
    C=(F(7,5),)*2+(F(8,5),)*2+(F(3,2),)*2
    W=(F(97,100),)*4+(F(1),)
    Z=tuple(tuple(-r.Z_RADIUS/2 if i==j==4 else F(0) for j in range(5)) for i in range(5))
    corner=t.Role(r.exact_state('paired_target',C,W),r.exact_carrier('paired_target',Z))
    for endpoint,h in ((0,F(3,25)),(1,F(1,8))):
        prof=t.Profile(tuple(sorted((k,v[endpoint]) for k,v in t.PARAMETER_BOX.items())))
        nxt,stage=t.step(corner,h,prof);od=oracle('paired_target',C,W,Z,h,prof)
        n=compare(nxt,stage,od);comparisons+=n
        rows.append(dict(parameter_corner=endpoint,profile=prof.parameters,h=h,scalar_comparisons=n,
                         stage_digest=a.digest(a.encode(stage)),signed_carrier=True))
    return dict(independent_scalar_comparisons=comparisons,source_k=chosen['k'],
        exact_source=exact,checks=rows,PC3_anchor_unchanged=True,oracle='independent 110-digit Decimal edge-local assembly'),source,post,targets


def reject(call,label):
    try:call()
    except a.AdmissionError as exc:return dict(case=label,reason=str(exc))
    raise AssertionError('negative pressure admitted: '+label)


def lifecycle(source,post):
    owner=t.ResearchOwner(source);actions=[]
    for kind,h in (('ordinary',F(1,8)),('split',None),('ordinary',F(3,25)),('reset',None)):
        before=owner.publication
        if kind=='ordinary':owner.ordinary(h)
        elif kind=='split':owner.split();event=owner.publication
        else:owner.reset()
        if kind=='ordinary':require(owner.publication.reset is before.reset,'ordinary step preserves actual reset')
        actions.append(dict(kind=kind,h=str(h) if h is not None else None,before=before.identity,after=owner.publication.identity))
    require(owner.publication.current is event.reset,'reset uses independently transported target C/W/Z')
    sequence=dict(source=source.identity,actions=actions,final=t.snapshot(owner.publication))
    require(t.replay(source,sequence).identity==owner.publication.identity,'full ordinary-event-step-reset replay')
    negatives=[]
    for label,mutate in (
        ('missing_source_lineage',lambda seq:seq.update(source='absent')),
        ('changed_request',lambda seq:seq['actions'][2].update(h='1/8')),
        ('forged_reset_Z',lambda seq:seq['final']['payload']['reset']['Z'][4][4].update(lo='1',hi='1')),
        ('invalid_edge_lineage',lambda seq:seq['final']['payload']['event'][2][0].__setitem__(1,4)),
        ('wrong_profile',lambda seq:seq['final']['payload'].update(profile='other'))):
        altered=json.loads(json.dumps(sequence));mutate(altered)
        altered['final']['digest']=a.digest(altered['final']['payload'])
        negatives.append(reject(lambda:t.replay(source,altered),label))
    event_source=replace(source,current=post)
    bad_reset=t.Role(r.paired_state(F(4),F(0),F(49,50),F(97,100)),source.reset.carrier)
    bad=t.ResearchOwner(replace(event_source,reset=bad_reset));before=bad.publication
    negatives.append(reject(bad.split,'actual_reset_only_transfer_domain_rejection'))
    require(bad.publication is before,'actual failure full-publication rollback')
    detached=t.ResearchOwner(event_source);before=detached.publication;calls=[]
    actual=t.transfer
    def failure(role,k,profile):
        require(detached.publication is before,'premature publication')
        result=actual(role,k,profile);calls.append(role.payload())
        if len(calls)==2:raise a.AdmissionError('injected reset-only target readmission failure')
        return result
    with patch.object(t,'transfer',failure):negatives.append(reject(detached.split,'injected_reset_readmission_after_current_pass'))
    require(len(calls)==2 and detached.publication is before,'reset readmission rollback')
    def late(_):raise a.AdmissionError('injected late publication failure')
    negatives.append(reject(lambda:detached.split(late),'late_event_publication_failure'))
    require(detached.publication is before,'late event rollback')
    stepowner=t.ResearchOwner(event);before=stepowner.publication
    negatives.append(reject(lambda:stepowner.ordinary(F(3,25),late),'late_ordinary_publication_failure'))
    require(stepowner.publication is before,'late ordinary rollback')
    for h in (F(0),F(1,10),F(13,100)):
        negatives.append(reject(lambda h=h:stepowner.ordinary(h),'out_of_domain_request_'+str(h)))
        require(stepowner.publication is before,'request rollback')
    negatives.append(reject(stepowner.split,'descendant_fission_outside_scope'))
    negatives.append(reject(lambda:t.Role(source.current.state.data,source.current.carrier),'raw_state_not_exact_charge_witness'))
    negatives.append(reject(lambda:a.rounded_share(I.bounds(I(F(1,2)-F(1,20000)).lo,I(F(1,2)+F(1,20000)).hi),I(F(1,2))),
                            'unresolved_quantizer'))
    for k in (32766,32767):
        share=F(2*k+1,131072);got,_=a.rounded_share(I(share),I(1-share))
        require(got==round(F(2*k+1,2)),'exact half-tie parity')
    return dict(sequence=sequence,source_publication=source.payload(),event_snapshot=t.snapshot(event),
        independent_role_Z=True,ordinary_onset_then_event=True,full_payload_rollback=True,
        reset_semantics=True,replay=True,negative_pressure=negatives)


def error(exact,represented):
    return max(F(max(abs(x.lo-y.hi),abs(x.hi-y.lo)),GRID) for x,y in zip(exact,represented,strict=True))


def rounded_image(state,Z):
    def vector(xs):return [float(a.bound(x)[0]).hex() for x in xs]
    return dict(C=vector(state.C),W=vector(state.W),Z=[vector(row) for row in Z.values])


def representation(targets,profile):
    cases=[]
    for label,exact in zip(('current','reset'),targets,strict=True):
        state,Z=t.represented(exact);rows=[]
        for h in map(F,t.CONTRACT['finite_schedule']):
            represented_h=F(float(h))
            if represented_h<t.HMIN:represented_h=F(math.nextafter(float(h),math.inf))
            exact,exact_stage=t.step(exact,h,profile)
            state,Z,stage=t.represented_step('paired_target',state,Z,represented_h,profile)
            errors=dict(C=error(exact.state.C,state.C),W=error(exact.state.W,state.W),
                        Z=error(tuple(v for row in exact.carrier.values for v in row),tuple(v for row in Z.values for v in row)))
            require(max(errors.values())<F(t.CONTRACT['finite_error_bound']),'finite represented-error budget')
            charge=sum((a.bound(v)[0] for v in state.C),F(0))-9
            require(r.norm_upper(c-F(3,2) for c in state.C)<F(2,3),'represented target resource ball observed')
            rows.append(dict(h=h,represented_h=represented_h,errors=errors,charge_drift=charge,
                binary64=rounded_image(state,Z),exact_state_digest=a.digest(exact.payload()),
                exact_stage_digest=a.digest(a.encode(exact_stage)),represented_stage_digest=a.digest(a.encode(stage)),
                H_norm_bound=profile.values['kh']*r.norm_upper(v for row in Z.values for v in row)))
        cases.append(dict(role=label,steps=rows,exact_charge_theorem_applied_to_rounded=False))
    return dict(recipe=dict(t.CONTRACT),tau_binary64=a.TAU64,cases=cases,
                intermediate_binary64_rounding=False,infinite_numerical_conformance=False)


def evidence():
    bound=t.domain_bounds()
    stages,source,post,targets=stage_checks()
    return dict(domain_bounds=bound,stages=stages,lifecycle=lifecycle(source,post),
                representation=representation(targets,source.profile),
                environment=dict(active_external_edges='not in selected carrier contract; no active-environment theorem',
                    unaffected_support_control='a disjoint unsplit source component remains governed by its own PC growth cone; fission elsewhere cannot remove its obstruction',
                    argument='block incidence/descriptor/H for block-diagonal carriers leaves that component autonomous',
                    numerical_environment_campaign=False))


def run():
    with patch.object(r,'ci_read',side_effect=AssertionError('CI forbidden in PC4')):
        with patch.object(a,'evaluate',side_effect=AssertionError('OS forbidden in PC4')):
            result=evidence()
    value=a.encode(dict(schema='grcv4_atc_pc4_reference_v1',
        status='PC4_independent_review_PASS_paired_scope_ready_for_adjudication',
        scientific_acceptance=False,graph_admitted=False,native_ATC_executed=False,ATC2_closed=False,
        contract=dict(t.CONTRACT),profile_digest=t.Profile().identity,evidence=result,
        claim_updates=[dict(claim_id='ATC-PC-DOMAIN-04',claim_class='conditional',profile_scope=['A_PC'],
            status='review_PASS_bounded_domain_reference_pending_adjudication',predecessor_handles=['ATC-PC-CHAIN-02','ATC-PC-CARRIER-03'],
            debt_refs=['ATC7-DB-'+n for n in ('02','03','04','06','07','08','10','13','14','15','16','19','21','23','26','28')],
            local_debt_discharge=False,native_authority=False,
            open_debt_refs=['ATC7-DB-24'],
            still_open='DB24/formal scoped source admission; active environment carrier extension; other families; repeated-event/non-Zeno and native implementation')]))
    value['scientific_review']=review_metadata(value)
    paths={Path(__file__).resolve(),ROOT/INV/'decisions/ATCCIPCRealizationNativeProgram.md',
        ROOT/INV/'evidence/atc-ci-pc/ATCPC3CausalChainCertificate.json',
        ROOT/INV/'evidence/atc-ci-pc/PC3-IndependentReview.md',
        ROOT/INV/'evidence/atc-ci-pc/PC4-IndependentReview.md',
        ROOT/INV/'decisions/ATCSectorChannelsAndRequests.md'}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            path=Path(path).resolve()
            if path.is_relative_to(ROOT/INV) and path.suffix=='.py':paths.add(path)
    value['source_bindings']=[dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in sorted(paths)]
    value['record_digest']=a.digest(value)
    return value


if __name__=='__main__':print(json.dumps(run(),indent=2))
