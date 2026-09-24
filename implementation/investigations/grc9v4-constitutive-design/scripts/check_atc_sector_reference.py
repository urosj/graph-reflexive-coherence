#!/usr/bin/env python3
"""Bounded G7-R conformance; prints evidence, never writes or imports src."""
from dataclasses import replace
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
import atc_sector_reference as r

p,I,GRID=r.p,r.I,r.GRID
require=r.require


def seed(C,W):
    C,W=tuple(map(F,C)),tuple(map(F,W))
    return r.State(tuple(map(I,C)),tuple(map(I,W)),(C,W))


def fixtures():
    def paired(x,y,u,v):
        return seed(((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,), (u,u,v,v))
    def embedded(ru,rv,z,u,v,w):
        return seed((ru,ru,rv,rv,F(41,5)-2*(ru+rv+z),z,z),(u,u,v,v,w,w))
    return {
        'paired':r.Publication('paired_source',
            paired(F(13,4),F(1,100),F(97,100),F(99,100)),
            paired(F(33,10),-F(3,200),F(49,50),F(97,100))),
        'embedded':r.Publication('embedded_source',
            embedded(F(20001,20000),F(19999,20000),F(40001,40000),F(99,100),F(19999,20000),F(39999,40000)),
            embedded(F(24999,25000),F(100007,100000),F(99993,100000),F(19801,20000),F(99991,100000),F(99997,100000)))
    }


def dec(q):
    q=F(q);return D(q.numerator)/D(q.denominator)


def oracle(graph,C,W,h):
    """Independent Decimal edge-local assembly; no interval/reduced-stage calls.

    A cross-check, not the certification engine. Its arithmetic is explicitly
    distinct from the outward rational proof, and gets tested for enclosure.
    """
    with localcontext() as ctx:
        ctx.prec=110
        n,edges,pos=r.mathref.GRAPHS[graph];C=tuple(map(dec,C));W=tuple(map(dec,W))
        a={k:dec(v) for k,v in r.PARAMS.items()};hh=dec(h);m=len(edges)
        def descriptors(C):
            out=[]
            for i in range(n):
                num,den=D(0),D(1)
                for u,v in edges:
                    if i not in (u,v):continue
                    j=v if i==u else u;dx=D(pos[j]-pos[i])
                    num+=dx*(C[j]-C[i]);den+=dx*dx
                out.append(num/den)
            return tuple(out)
        def solve(H,b):
            rows=[list(row)+[v] for row,v in zip(H,b,strict=True)]
            for k in range(m):
                pivot=rows[k][k];rows[k]=[x/pivot for x in rows[k]]
                for i in range(k+1,m):
                    f=rows[i][k];rows[i]=[x-f*y for x,y in zip(rows[i],rows[k],strict=True)]
            answer=[D(0)]*m
            for k in reversed(range(m)):answer[k]=rows[k][-1]-sum(rows[k][j]*answer[j] for j in range(k+1,m))
            return tuple(answer)
        def drive(C,desc,b):
            return tuple((-(a['alpha']*(C[u]+C[v])+a['beta']*(desc[u]-desc[v])**2+a['gamma']*j*j)/2).exp()
                         for (u,v),j in zip(edges,b,strict=True))
        def stage(H):
            lap=[D(0)]*n;geom=[D(0)]*n
            d=tuple(C[u]-C[v] for u,v in edges)
            correction=tuple(sum((H[i][j]-int(i==j))*d[j] for j in range(m)) for i in range(m))
            for (u,v),w,x,g in zip(edges,W,d,correction,strict=True):
                lap[u]+=w*x;lap[v]-=w*x;geom[u]+=g;geom[v]-=g
            potential=tuple(a['a']*c+a['nu']*c*c/2 for c in C)
            phi=tuple(x-z+a['kah']*g for x,z,g in zip(lap,potential,geom,strict=True))
            bare=tuple(-w*(phi[u]-phi[v]) for (u,v),w in zip(edges,W,strict=True))
            desc=descriptors(C);hat=drive(C,desc,bare)
            q=tuple((w-t)/(w+t) for w,t in zip(W,hat,strict=True))
            J=tuple(b/(1-a['chi']*v) for b,v in zip(bare,q,strict=True))
            f=solve(H,tuple(a['chi']*v*j for v,j in zip(q,J,strict=True)))
            return dict(potential=potential,phi=phi,baseline=bare,descriptor=desc,drive=hat,current=J,flat=f)
        H0=tuple(tuple(D(int(i==j)) for j in range(m)) for i in range(m))
        ref=stage(H0)
        H=tuple(tuple(D(int(i==j))+a['kh']*D(len(set(e)&set(f)))*ref['flat'][i]*ref['flat'][j]/2
                      for j,f in enumerate(edges)) for i,e in enumerate(edges))
        fresh=stage(H);Cn=list(C)
        for (u,v),j in zip(edges,fresh['current'],strict=True):Cn[u]-=hh*j;Cn[v]+=hh*j
        Dn=descriptors(Cn);drv=drive(Cn,Dn,fresh['current'])
        rho=(-8*hh*D(2).ln()).exp()
        Wn=tuple((rho*w.ln()+(1-rho)*t.ln()).exp() for w,t in zip(W,drv,strict=True))
        return dict(C=tuple(Cn),W=Wn,reference=ref,fresh=fresh,writer_descriptor=Dn,writer_drive=drv,rho=rho,generated_H=H)


def inside(actual,interval):
    if isinstance(interval,I):
        require(interval.contains(F(actual)),'independent oracle outside exact enclosure')
        return 1
    return sum(inside(x,y) for x,y in zip(actual,interval,strict=True))


def point_checks(sources):
    rows=[]
    for name,source in sources.items():
        selected=r.prescribe(source.graph,source.current)
        graph,target=r.transfer(source.graph,source.current,selected['k'])
        for g,state in ((source.graph,source.current),(graph,target)):
            # Exact rational preimages of transported target C/W are known
            # independently from the chosen dyadic share and source preimage.
            C,W=source.current.source_exact
            if g==graph:
                share=F(selected['k'],65536);C=C[:4]+(share*C[4],(1-share)*C[4])+C[5:];W=W[:4]+(F(1),)+W[4:]
            for h in (F(1,8),F(3,25)):
                out,full=r.evaluate(g,state,h);other=oracle(g,C,W,h)
                count=inside(other['C'],out.C)+inside(other['W'],out.W)
                for stage in ('reference','fresh'):
                    for key in other[stage]:count+=inside(other[stage][key],full[stage][key])
                for key in ('writer_descriptor','writer_drive','rho','generated_H'):count+=inside(other[key],full[key])
                stale=r.conductance(g,out.C,full['reference']['descriptor'],full['fresh']['current'])
                wrong_current=r.conductance(g,out.C,full['writer_descriptor'],full['reference']['current'])
                def separated(v,w):return any(a.hi<b.lo or b.hi<a.lo for a,b in zip(v,w,strict=True))
                require(separated(stale,full['writer_drive']),'stale descriptor mutation not discriminated')
                require(separated(wrong_current,full['writer_drive']),'reference/fresh writer mutation not discriminated')
                rows.append(dict(graph=g,h=str(h),independent_scalar_comparisons=count,
                    old_descriptor_mutation_rejected=True,reference_writer_current_mutation_rejected=True,
                    stage_digest=r.digest(r.encode(full))))
    return rows


def source_controls(sources):
    rows=[]
    for name,source in sources.items():
        for reset_history in (False,True):
            state=source.current
            if reset_history:state=replace(state,W=(I(1),)*len(state.W),source_exact=None)
            owner=r.ResearchOwner(replace(source,current=state));attempts=[]
            for k in range(1,68):
                before=owner.publication
                h=F(1,8) if k%2 else F(3,25)
                try:
                    owner.step(h)
                except r.AdmissionError as exc:
                    require(str(exc)=='resource rejection before writer','source control failed for wrong reason: '+str(exc))
                    require(owner.publication is before,'ordinary resource-failure rollback')
                    attempts.append(dict(attempt=k,h=str(h),status='resource_rejection',writer_executed=False))
                    break
                attempts.append(dict(attempt=k,h=str(h),status='admitted',
                    minimum_C=r.encode(p.minimum(owner.publication.current.C)),state_digest=owner.publication.identity))
            else:raise AssertionError('source control did not reject by G6 horizon')
            rows.append(dict(graph=name,control='history_reset_only' if reset_history else 'no_split',
                             attempts=attempts,whole_publication_rollback=True,no_event_fallback=True))
    return rows


def must_reject(action,reason):
    try:action()
    except r.AdmissionError as exc:
        return dict(case=reason,rejection=str(exc))
    raise AssertionError('did not reject '+reason)


def lifecycle_checks(sources):
    rows=[];targets={}
    for name,source in sources.items():
        owner=r.ResearchOwner(source);old=owner.publication
        selected=owner.split(F(1,8));target=owner.publication;targets[name]=target
        # A represented source read is only a finite comparison. In particular
        # rounded embedded resources need not retain exact charge 41/5, so it
        # is NOT passed off as an admitted exact-domain source publication.
        represented_read=r.read(source.graph,source.current.represented(),r.identity(len(source.current.W)))
        jk,_=r.rounded_share(sum(represented_read['current'][:2],I(0)),sum(represented_read['current'][2:4],I(0)))
        require(jk==selected['k'],'represented source chooses same certified dyadic bin')
        require(old.current.payload()!=old.reset.payload(),'independent actual roles')
        require(target.reset.payload()!=target.current.payload(),'transport did not flatten roles')
        require(target.parent==source.identity,'parent linkage')
        old_endpoint=source.current.C[0].lo
        try:source.current.C[0].lo=0
        except AttributeError:pass
        else:raise AssertionError('retained interval was mutable')
        require(source.current.C[0].lo==old_endpoint,'retained scientific state unchanged')
        expected=tuple((i,i if i<4 else i+1) for i in range(len(source.current.W)))
        require(target.event[1]==expected,'old edge lineage including environment')
        for a,b in expected:
            require(r.encode(target.current.W[b])==r.encode(source.current.W[a]) and
                    r.encode(target.reset.W[b])==r.encode(source.reset.W[a]),'both-role old history transport')
        require(target.current.W[4].contains(1) and target.reset.W[4].contains(1),'bridge-only seed')
        snap=r.snapshot(target)
        require(r.replay_event(source,snap).identity==target.identity,'event replay')
        actions=[dict(kind='split',h='1/8',before=source.identity,after=target.identity)]
        owner.step(F(3,25));require(owner.publication.reset.payload()==target.reset.payload(),'ordinary step reset persistence')
        after_step=owner.publication.identity
        actions.append(dict(kind='step',h='3/25',before=target.identity,after=after_step))
        owner.reset();require(owner.publication.current.payload()==target.reset.payload(),'reset after event and step')
        actions.append(dict(kind='reset',h=None,before=after_step,after=owner.publication.identity))
        sequence=dict(source=source.identity,actions=actions,final=r.snapshot(owner.publication))
        require(r.replay_sequence(source,sequence).identity==owner.publication.identity,'whole sequence replay')
        controls=[]
        altered=r.snapshot(target);altered['payload']['parent']='absent';altered['digest']=r.digest(altered['payload'])
        controls.append(must_reject(lambda:r.replay_event(source,altered),'missing lineage, recomputed digest'))
        changed=r.snapshot(target);changed['payload']['event'][1][0][1]=4;changed['digest']=r.digest(changed['payload'])
        controls.append(must_reject(lambda:r.replay_event(source,changed),'invalid lineage map, recomputed digest'))
        changed=r.snapshot(target);changed['payload']['profile']='other';changed['digest']=r.digest(changed['payload'])
        controls.append(must_reject(lambda:r.replay_event(source,changed),'wrong profile, recomputed digest'))
        changed=r.snapshot(target);changed['payload']['reset']['W'][0]=r.encode(I(1));changed['digest']=r.digest(changed['payload'])
        controls.append(must_reject(lambda:r.replay_event(source,changed),'forged reset history, recomputed digest'))
        changed_sequence=json.loads(json.dumps(sequence));changed_sequence['actions'][1]['h']='1/8'
        controls.append(must_reject(lambda:r.replay_sequence(source,changed_sequence),'changed request in replay'))
        # Reset-only domain failure, with valid current held fixed.
        badC=list(source.reset.source_exact[0]);badC[0],badC[1]=F(2),F(2)
        badC[4]=(F(9) if name=='paired' else F(41,5))-sum(badC[:4])-sum(badC[5:])
        bad=replace(source,reset=seed(badC,source.reset.source_exact[1]))
        badowner=r.ResearchOwner(bad);before=badowner.publication
        controls.append(must_reject(lambda:badowner.split(F(1,8)),'reset-only transfer-domain failure'))
        require(badowner.publication is before,'reset failure whole-publication rollback')
        detached=r.ResearchOwner(source);before=detached.publication;calls=[]
        real_admit=r.target_admit
        def reject_reset(graph,state,h):
            calls.append(state.payload())
            require(detached.publication is before,'publication changed before both-role admission')
            if len(calls)==2:raise r.AdmissionError('injected reset-only readmission failure')
            return real_admit(graph,state,h)
        with patch.object(r,'target_admit',reject_reset):
            controls.append(must_reject(lambda:detached.split(F(1,8)), 'injected reset-only target readmission; current passed'))
        require(len(calls)==2 and detached.publication is before,'both-role readmission rollback')
        late=r.ResearchOwner(source);before=late.publication
        def injected(_):raise r.AdmissionError('injected late publication failure')
        controls.append(must_reject(lambda:late.split(F(1,8),injected),'late failure'))
        require(late.publication is before,'late failure whole-publication rollback')
        for h in (F(0),F(1,10),F(13,100)):
            controls.append(must_reject(lambda h=h:late.step(h),'out-of-domain request '+str(h)))
            require(late.publication is before,'request failure rollback')
        # A truly unresolved quantization interval, plus exact half-bin parity.
        controls.append(must_reject(lambda:r.rounded_share(I.bounds(I(F(1,2)-F(1,20000)).lo,I(F(1,2)+F(1,20000)).hi),I(F(1,2))), 'uncertain dyadic selection'))
        for k in (32766,32767):
            x=F(2*k+1,131072);got,_=r.rounded_share(I(x),I(1-x))
            require(got==round(F(2*k+1,2)),'round-even exact tie')
        rows.append(dict(graph=name,selected_k=selected['k'],source=source.payload(),event_snapshot=snap,
            represented_source_bin_agrees=True,represented_source_domain_admission_claimed=False,
            exact_roles_independent=True,old_history_lineage=expected,bridge_seed_only=True,sequence=sequence,
            replay_matches=True,reset_after_event_and_step=True,negative_controls=controls,
            whole_publication_rollback=True,retained_endpoint_mutation_rejected=True))
    return rows,targets


def difference(a,b):
    return max(max(abs(x.lo-y.hi),abs(x.hi-y.lo)) for x,y in zip(a,b,strict=True))/F(GRID)


def image(state):
    def vector(values):return [float(r.bound(r.project(v))[0]).hex() for v in values]
    return dict(C_binary64=vector(state.C),W_binary64=vector(state.W),
                enclosure_digest=r.digest(state.payload()))


def continuation_checks(targets):
    result=[];schedule=(F(1,8),F(3,25),F(31,250),F(121,1000))*4
    for name,pub in targets.items():
        for role in ('current','reset'):
            exact=getattr(pub,role);represented=exact.represented();rows=[]
            charge=F(9) if name=='paired' else F(41,5)
            for index,h in enumerate(schedule,1):
                exact,detail=r.evaluate(pub.graph,exact,h)
                # h is also represented; use its exact binary64 value, and
                # never silently put binary64 0.12 below the admitted range.
                h64=F(float(h))
                if h64<F(3,25):h64=F(float.fromhex('0x1.eb851eb851eb9p-4'))
                before=represented
                represented,rounded_detail=r.evaluate(pub.graph,before,h64,represented_tau=True)
                represented=represented.represented()
                ec=difference(exact.C,represented.C);ew=difference(exact.W,represented.W)
                # Predeclared finite comparison thresholds, not new gates.
                require(max(ec,ew)<F(1,10**10),'finite represented error envelope')
                c=charge/len(exact.C);R=F(2,3) if name=='paired' else F(1,4)
                require(p.norm2(tuple(x-c for x in exact.C)).hi<GRID*R*R,'exact return entry/continuation')
                require(p.norm2(tuple(x-c for x in represented.C)).hi<GRID*R*R,'represented finite return check')
                qsum=sum(represented.C,I(0));charge_error=max(abs(qsum.lo-GRID*charge),abs(qsum.hi-GRID*charge))/GRID
                rows.append(dict(step=index,h_exact=str(h),h_binary64=float(h64).hex(),
                    C_error_upper=str(ec),W_error_upper=str(ew),represented_charge_error=str(charge_error),
                    exact_state=image(exact),represented_state=image(represented),
                    residual_squared_upper=r.encode(detail['residual_squared']),
                    exact_stage_digest=r.digest(r.encode(detail)),represented_stage_digest=r.digest(r.encode(rounded_detail))))
            result.append(dict(graph=name,role=role,steps=rows,
                max_C_error_upper=max((x['C_error_upper'] for x in rows),key=F),
                max_W_error_upper=max((x['W_error_upper'] for x in rows),key=F),
                max_charge_error=max((x['represented_charge_error'] for x in rows),key=F),
                infinite_binary64_conformance_claimed=False))
    return result


def evidence():
    sources=fixtures();points=point_checks(sources)
    lifecycle,targets=lifecycle_checks(sources)
    return dict(profile=r.profile_payload(),profile_identity=r.PROFILE_ID,
                point_checks=points,source_controls=source_controls(sources),
                lifecycle=lifecycle,continuation=continuation_checks(targets))


def main():
    base=p.ROOT/p.INV;refs=base/'evidence/autonomous-topology-change'
    accepted=json.loads((refs/'ATCSectorChannelsAdjudication.json').read_text())
    body=dict(accepted);prior=body.pop('record_digest')
    require(r.digest(body)==prior and accepted['G5_accepted'] and accepted['G6_accepted'],'G5-G6 accepted prerequisite')
    for b in accepted['source_bindings']:
        require(hashlib.sha256((p.ROOT/b['path']).read_bytes()).hexdigest()==b['sha256'],'accepted binding '+b['path'])
    record=dict(schema='grcv4_atc_g7_reference_conformance_v1',status='bounded_G7_R_results_pending_review',
        scientific_acceptance=False,G7_native_closed=False,native_ATC_executed=False,
        src_modified=False,ATC2_closed=False,predecessor_adjudication=prior,evidence=evidence(),source_bindings=[])
    for path in (Path(__file__).resolve(),base/'research/atc_sector_reference.py',
                 base/'scripts/certify_atc_sector_channels.py',base/'scripts/certify_atc_sector_state_domain.py',
                 base/'scripts/certify_atc_sector_readback_box.py',base/'scripts/certify_atc_sector_readback_point.py',
                 refs/'ATCSectorChannelsAdjudication.json',base/'decisions/ATCSectorReferenceConformance.md'):
        record['source_bindings'].append(dict(path=str(path.relative_to(p.ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    record['record_digest']=r.digest(record)
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
