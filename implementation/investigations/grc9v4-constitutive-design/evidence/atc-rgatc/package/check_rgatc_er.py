#!/usr/bin/env python3
"""Execute bounded RGATC-E and R. --check checks identities, not experiments."""
from dataclasses import FrozenInstanceError
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse, hashlib, json, math, sys, time, operator
import rgatc_reference as t
import rgatc_oracle as o
BASE=Path(__file__).resolve().parent; CERT=BASE/'RGATC-ER-Certificate.json'
need=t.need

def inside(e,a):
    if isinstance(a,t.I):need(a.contains(F(e)),'independent value outside enclosure');return 1
    if isinstance(e,dict):return sum(inside(v,a[k]) for k,v in e.items())
    return sum(inside(x,y) for x,y in zip(e,a,strict=True))
def reject(label,fn,classes=(t.AdmissionError,)):
    try:fn()
    except classes as e:return dict(case=label,exception=type(e).__name__,reason=str(e))
    raise AssertionError('negative control accepted: '+label)
def secsum(v):
    s=v['section'] if 'section' in v else v
    return {k:s[k] for k in ('section_digest','H','center','radius','arithmetic_error','inverse_output_residual',
        'input_radius','banach_tail','depth','inverse_shoots','completed_ladder_steps','query_digest','profile_id',
        'proof','all_inverse_ladder_cutoffs_one','previous_geometry_used','CI_root_used','evaluator_policy_id','tolerance','max_shoots')}
def rsum(v):return dict(section=secsum(v),read=v['read'],state_binding=v.get('state_binding'))
def compare_read(e,a):return inside(e['section']['H'],a['section']['H'])+inside(e['read'],a['read'])
def compare_step(e,state,d):
    C,W=state.values()
    n=inside(e['C'],C)+inside(e['W'],W)+inside(e['section']['H'],d['selected']['section']['H'])
    n+=inside(e['selected'],d['selected']['read'])+compare_read(e['restart'],d['restart'])
    return n+sum(inside(e[k],d[k]) for k in ('writer_descriptor','writer_drive','writer_exponent','decay'))
def oracle(graph,C,W,step=False,depth=28):return o.evaluate(t.GRAPHS[graph].payload(),C,W,t.PARAMS,t.DELTA,t.KH,step=step,depth=depth)
def ci_residual(d):
    H=d['selected']['section']['H'];G=d['generated_H']
    rr=tuple(tuple(x-y for x,y in zip(row,other,strict=True)) for row,other in zip(H,G,strict=True))
    need(any(not x.contains(F(0)) for x in t.flat(rr)),'actual same-state CI residual nonzero')
    return rr

def executed_chain():
    start,reset=t.seeds();publication=t.Publication(start,reset);c0,w0=start.provenance[1:3]
    post,d=t.ordinary(start);dec=oracle('source',c0,w0,True);count=compare_step(dec,post,d)
    chosen=t.select(post);C,W=post.values();x=C[4]-(C[0]+C[2])/2;y=(C[0]-C[2])/2
    need(c0[4]-(c0[0]+c0[2])/2<3 and x.lo>3*t.GRID,'ordinary inactive-to-active onset')
    need(chosen['k']==32768,'execution confirms T/A implication, not input to selection')
    need(chosen['event_read']['section']['section_digest']==d['restart']['section']['section_digest'],'fresh event section')
    need(chosen['event_read']['section']['section_digest']!=d['selected']['section']['section_digest'],'no consumed section reuse')
    with localcontext() as ctx:
        ctx.prec=110;J=dec['restart']['read']['current'];dk=round(D(65536)*(J[0]+J[1])/sum(J))
    need(dk==chosen['k'],'independent allocation')
    roles={};targets=[];dec_targets=[];secs=[secsum(d['selected']),secsum(d['restart'])];mut=[]
    for name,state,oc,ow in (('current',post,dec['C'],dec['W']),('reset',reset,*reset.provenance[1:3])):
        target,rd=t.transfer(state,chosen['k']);tc,tw=o.transfer(oc,ow,chosen['k'])
        count+=inside(tc,target.values()[0])+inside(tw,target.values()[1])+compare_read(oracle('target',tc,tw),rd)
        targets.append(target);dec_targets.append((tc,tw));live=target;rows=[]
        need(target.values()[1][-1].contains(F(1)),'bridge seed')
        need(all(t.same(a,b) for a,b in zip(state.values()[1],target.values()[1][:4],strict=True)),'exact old-W lineage')
        for beat in range(3):
            old=live;oldC,_=old.values();new,dd=t.ordinary(old)
            od=oracle('target',tc,tw,True);count+=compare_step(od,new,dd);tc,tw=od['C'],od['W']
            prev=t.p.norm2(tuple(c-F(3,2) for c in oldC)).sqrt();nxt=t.p.norm2(tuple(c-F(3,2) for c in new.values()[0])).sqrt()
            ratio=nxt/prev;need(t.upper(ratio)<1-F(3,4)*t.DELTA,'observed target contraction')
            need(all(z.contains(F(0)) for z in t.flat(dd['invariance_residual'])),'RG invariance')
            rows.append(dict(beat=beat+1,after=new.payload(),X=nxt,resource_ratio=ratio,selected=rsum(dd['selected']),restart=rsum(dd['restart']),
                generated_H=dd['generated_H'],invariance_residual=dd['invariance_residual'],same_state_CI_residual=ci_residual(dd),
                history_writes=dd['history_writes'],resource_writes=dd['resource_writes']))
            secs.extend((secsum(dd['selected']),secsum(dd['restart'])))
            if beat==0:
                nc,_=new.values();J=dd['selected']['read']['current']
                _,stale=t.conductance(t.TARGET,nc,dd['selected']['read']['descriptor'],J)
                _,wrong=t.conductance(t.TARGET,nc,dd['writer_descriptor'],dd['restart']['read']['current'])
                different=lambda aa,bb:any(x.hi<y.lo or y.hi<x.lo for x,y in zip(aa,bb,strict=True))
                need(different(stale,dd['writer_exponent']) and different(wrong,dd['writer_exponent']),'writer stage discrimination')
                mut.append(dict(role=name,stale_descriptor_distinct=True,poststate_J_distinct=True))
            live=new
        roles[name]=dict(transferred=target.payload(),initial_target=rsum(rd),beats=rows)
    controls={}
    for name,state in (('no_split',post),('W_reset_only',t.history_reset(post))):
        rows=[]
        for i in range(2):
            cc,_=state.values();pre=cc[4]-(cc[0]+cc[2])/2;nxt,dd=t.ordinary(state)
            cc,_=nxt.values();xx=cc[4]-(cc[0]+cc[2])/2;ratio=xx/pre
            need(t.lower(ratio)>1+t.DELTA/8,'observed source control growth')
            rows.append(dict(beat=i+1,x_before=pre,x_after=xx,ratio=ratio,section=secsum(dd['restart'])));state=nxt
        controls[name]=dict(beats=rows,uniform_obstruction_bound=536870912,horizon_is_theorem_not_executed=True)
    out=dict(source=dict(before=start.payload(),after=post.payload(),x_after=x,y_after=y,k=chosen['k'],raw_index=chosen['raw_index'],
                         selected=rsum(d['selected']),event=rsum(chosen['event_read']),invariance_residual=d['invariance_residual'],same_state_CI_residual=ci_residual(d)),
             roles=roles,controls=controls,independent_scalar_comparisons=count,stage_mutations=mut,
             ordinary_source_onset_beats=1,ordinary_target_beats_per_role=3,ordinary_control_beats_per_case=2,
             section_evaluator='finite graph transform, not whole-ball substitution',native_RG_steps_executed=False)
    return out,publication,post,targets,dec_targets,secs

def covariance(target,decimals):
    g=t.TARGET;vp=(2,5,0,4,1,3);order=(4,2,0,3,1);signs=(-1,1,-1,1,-1)
    oldC,oldW=target.values();C=[None]*6;pos=[None]*6
    for i in range(6):C[vp[i]]=oldC[i];pos[vp[i]]=g.positions[i]
    edges=[]
    for idx,sign in zip(order,signs,strict=True):
        a,b=g.edges[idx];a,b=vp[a],vp[b];edges.append((a,b) if sign>0 else (b,a))
    gp=t.Graph('target_relabelled',6,tuple(edges),tuple(pos));W=tuple(oldW[u] for u in order)
    sec=t.section(gp,tuple(C),W);C1,W1,rd=t.raw_step(gp,tuple(C),W,sec['H'],physical=True)
    sec1=t.section(gp,C1,W1);rr=t.fixed_read(gp,C1,W1,sec1['H']);can,cd=t.ordinary(target);canC,canW=can.values();count=0
    with localcontext() as ctx:
        ctx.prec=110;dc,dw=decimals;dcnew=[None]*6
        for i in range(6):dcnew[vp[i]]=dc[i]
        od=o.evaluate(gp.payload(),tuple(dcnew),tuple(dw[u] for u in order),t.PARAMS,t.DELTA,t.KH,step=True)
        count+=inside(od['section']['H'],sec['H'])+inside(od['selected'],rd['selected'])+inside(od['C'],C1)+inside(od['W'],W1)
        count+=inside(od['restart']['section']['H'],sec1['H'])+inside(od['restart']['read'],rr)
        for i in range(6):count+=inside(od['C'][vp[i]],canC[i])
        for i,u in enumerate(order):count+=inside(od['W'][i],canW[u])
        for orr,crr,oh,ch in ((od['selected'],cd['selected']['read'],od['section']['H'],cd['selected']['section']['H']),
                (od['restart']['read'],cd['restart']['read'],od['restart']['section']['H'],cd['restart']['section']['H'])):
            for i,u in enumerate(order):
                count+=inside(signs[i]*orr['current'][i],crr['current'][u])
                for j,v in enumerate(order):
                    count+=inside(signs[i]*signs[j]*oh[i][j],ch[u][v]);count+=inside(signs[i]*signs[j]*orr['source'][i][j],crr['source'][u][v])
    return dict(comparisons=count,vertex_permutation=vp,edge_order=order,edge_signs=signs,transformed_section=secsum(sec),transformed_restart=secsum(sec1),
                scope='one complete target coordinate transform; analytic equivariance from T/A')

def boundaries():
    comparisons=0
    with localcontext() as ctx:
        ctx.prec=110
        for x in (F(-1024),F(-2),F(-1,8),F(0),F(1,8),F(1),F(2)):comparisons+=inside(o.dec(x).exp(),t.expi(t.I(x)))
        for x in (F(1,2),F(3,4),F(1),F(5,4),F(3,2)):comparisons+=inside(o.dec(x).ln(),t.logi(t.I(x)))
        need(float(1/(8*D(2).ln())).hex()==t.TAU64,'tau hex')
    s,r=t.seeds();C,W=s.values();neg=[];pos=[]
    for label,state in (('source_W_floor',t.source_state(F(3),F(0),t.M,F(99,100))),
        ('source_x_root_boundary',t.source_state(F(29,10),F(0),F(99,100),F(1))),
        ('target_W_floor',t.exact_state('target',(F(7,5),)*2+(F(8,5),)*2+(F(3,2),)*2,(t.M,)*5))):
        rd=t.read(state);nxt,_=t.ordinary(state);pos.append(dict(case=label,section=secsum(rd),successor=nxt.identity))
    tiny=F(1,2**300)
    neg.append(reject('exact_W_below_subgrid',lambda:t.source_state(F(3),F(0),t.M-tiny,F(99,100))))
    neg.append(reject('source_x_below_subgrid',lambda:t.source_state(F(29,10)-tiny,F(0),F(99,100),F(1))))
    bad=list(s.provenance[1]);bad[0]+=tiny;bad[1]-=tiny
    neg.append(reject('exact_pairing_broken_subgrid',lambda:t.exact_state('source',tuple(bad),s.provenance[2])))
    bad=list(s.provenance[1]);bad[4]+=tiny
    neg.append(reject('exact_charge_forgery_subgrid',lambda:t.exact_state('source',tuple(bad),s.provenance[2])))
    neg.append(reject('insufficient_graph_transform_depth',lambda:t.section(t.SOURCE,C,W,depth=12)))
    neg.append(reject('exhausted_inverse_work',lambda:t.section(t.SOURCE,C,W,max_shoots=1)))
    neg.append(reject('unresolved_wide_query',lambda:t.section(t.SOURCE,tuple(c+t.span(-F(1,1000),F(1,1000)) for c in C),W)))
    for d in (F(0),F(1,8),t.DELTA/2,-t.DELTA):neg.append(reject('wrong_frozen_duration_'+str(d),lambda d=d:t.ordinary(s,d)))
    with patch.object(t,'raw_step',side_effect=AssertionError('exterior raw logarithm')):outside=t.section(t.SOURCE,(t.I(-3),)*5,(t.I(0),)*4)
    need(all(c==int(i==j) for i,row in enumerate(outside['center']) for j,c in enumerate(row)),'exterior identity')
    auxC=(F(21,2),)*4+(F(-3,2),);auxW=(F(29,20),)*4
    aux=t.section(t.SOURCE,tuple(map(t.I,auxC)),tuple(map(t.I,auxW)));od=oracle('source',auxC,auxW)
    comparisons+=inside(od['section']['H'],aux['H'])
    ar=t.fixed_read(t.SOURCE,tuple(map(t.I,auxC)),tuple(map(t.I,auxW)),aux['H']);comparisons+=inside(od['read'],ar)
    need(any(g.lo==t.GRID//2 for g in ar['drive']),'auxiliary floor active')
    eps=F(1,2**40);edge=t.exact_state('source',(eps,)*4+(9-4*eps,),(F(99,100),)*4)
    neg.append(reject('negative_physical_proposal_not_auxiliary_continuation',lambda:t.ordinary(edge)))
    deep=t.section(t.SOURCE,C,W,depth=28,tolerance=F(1,10**40));std=t.section(t.SOURCE,C,W)
    need(all(a.lo<=b.hi and b.lo<=a.hi for a,b in zip(t.flat(deep['H']),t.flat(std['H']),strict=True)),'depth refinement agreement')
    neg.append(reject('raw_output_not_request',lambda:t.ordinary(s,dict(C=C,W=W))))
    neg.append(reject('caller_minted_State',lambda:t.State('source',C,W,None,('forged',))))
    neg.append(reject('no_geometry_transport_argument',lambda:t.transfer(r,32768,H=std['H']),(TypeError,)))
    neg.append(reject('immutable_interval_payload',lambda:setattr(s.C[0],'lo',-1),(FrozenInstanceError,)))
    neg.append(reject('frozen_parameter_mapping',lambda:operator.setitem(t.PARAMS,'chi',F(1)),(TypeError,)))
    neg.append(reject('frozen_profile_mapping',lambda:operator.setitem(t.PROFILE,'delta',F(1,8)),(TypeError,)))
    expected=oracle('source',*s.provenance[1:3]);actual=t.read(s)
    expected['section']['H']=[list(row) for row in expected['section']['H']]
    expected['section']['H'][0][0]+=D('1e-20')
    neg.append(reject('H_only_corruption_with_unchanged_J',lambda:compare_read(expected,actual)))
    return dict(arithmetic_and_auxiliary_oracle_comparisons=comparisons,positive_boundaries=pos,negatives=neg,
        outside_completion=secsum(outside),active_floor_auxiliary=secsum(aux),deep_section=secsum(deep),standard_section=secsum(std),
        subgrid_offset=tiny,auxiliary_negative_C_is_not_physical=True,
        numerical_section_domain='certified finite-work subset; not complete executable coverage of every theoretical point')

def lifecycle(source):
    owner=t.Owner(source);actions=[];event=None
    for kind in ('ordinary','split','ordinary','reset'):
        before=owner.publication
        if kind=='ordinary':owner.ordinary();need(owner.publication.reset is before.reset,'ordinary reset independence')
        elif kind=='split':owner.split();event=owner.publication;need(owner.publication.clock==before.clock,'zero-time event')
        else:owner.reset();need(owner.publication.current is event.reset,'reset target role')
        actions.append(dict(kind=kind,delta=str(t.DELTA) if kind=='ordinary' else None,before=before.identity,after=owner.publication.identity))
    record=dict(source=source.identity,actions=actions,final=t.snapshot(owner.publication))
    need(t.replay(source,record).identity==owner.publication.identity,'physics replay')
    mutations=(('missing_lineage',lambda x:x.update(source='missing')),('changed_duration',lambda x:x['actions'][0].update(delta='1/8')),
      ('forged_profile',lambda x:x['final']['payload'].update(profile_id='different')),
      ('forged_reset_W',lambda x:x['final']['payload']['reset']['W'][0].update(lo='0',hi='0')),
      ('wrong_edge_lineage',lambda x:x['final']['payload']['event'][1][0].__setitem__(1,3)),
      ('forged_section_digest',lambda x:x['final']['payload']['event'].__setitem__(4,'current-only')),
      ('nonzero_event_duration',lambda x:x['actions'][1].update(delta=str(t.DELTA))))
    neg=[]
    for label,change in mutations:
        val=json.loads(json.dumps(t.enc(record)));change(val);val['final']['digest']=t.digest(val['final']['payload'])
        neg.append(reject(label,lambda val=val:t.replay(source,val)))
    go=t.Owner(source);go.ordinary();before=go.publication
    def late(_):raise RuntimeError('injected late failure')
    neg.append(reject('late_event_exception',lambda:go.split(late),(RuntimeError,)));need(go.publication is before,'late event rollback')
    actual=t.transfer;calls=[]
    def fail_reset(*args):
        need(go.publication is before,'no early current-only publication');out=actual(*args);calls.append(out)
        if len(calls)==2:raise t.AdmissionError('injected reset readmission failure')
        return out
    with patch.object(t,'transfer',side_effect=fail_reset):neg.append(reject('second_role_readmission_failure',go.split))
    need(len(calls)==2 and go.publication is before,'both-role atomicity')
    oo=t.Owner(source);before=oo.publication;actual_read=t.read;calls=[]
    def fail_final(*args):
        calls.append(None);out=actual_read(*args)
        if len(calls)==3:raise t.AdmissionError('injected final section failure')
        return out
    with patch.object(t,'read',side_effect=fail_final):neg.append(reject('ordinary_final_readmission_failure',oo.ordinary))
    need(len(calls)==3 and oo.publication is before,'ordinary rollback')
    neg.append(reject('late_ordinary_exception',lambda:oo.ordinary(after=late),(RuntimeError,)));need(oo.publication is before,'late ordinary rollback')
    neg.append(reject('prebeat_event_forbidden',oo.split));neg.append(reject('descendant_event_forbidden',owner.split))
    aa=t.Owner(source);neg.append(reject('automatic_event_failure',lambda:t.autonomous_beat(aa,after_event=late),(RuntimeError,)))
    need(aa.publication is not source and aa.publication.last=='ordinary' and aa.publication.clock==t.DELTA,'event failure retains completed ordinary')
    inactive=t.source_state(F(59,20),F(1,100),F(97,100),F(99,100));no=t.Owner(t.Publication(inactive,source.reset));rn=t.autonomous_beat(no)
    need(rn['event_status']=='outside_sufficient_event_domain' and no.publication.last=='ordinary','no-event ordinary')
    yes=t.Owner(source);ra=t.autonomous_beat(yes);need(ra['event_status']=='committed_fission' and yes.publication.clock==t.DELTA,'autonomous zero-time split')
    return dict(sequence=record,replay=True,event_snapshot=t.snapshot(event),negatives=neg,automatic_onset_k=ra['event']['choice']['k'],
        automatic_event_clock=yes.publication.clock,failed_event_keeps_ordinary=True,no_event_status=rn['event_status'],
        no_H_or_Z_in_authoritative_state=True,native_owner=False)

def representation(targets):
    rows=[];neg=[]
    for name,start in zip(('current','reset'),targets,strict=True):
        cc,ww=start.values();C,W=tuple(t.project(x) for x in cc),tuple(t.project(x) for x in ww);exact=start;beats=[]
        for n in range(4):
            exact,ed=t.ordinary(exact);C,W,rd=t.represented_step(C,W);ec,ew=exact.values();er,rr=ed['restart'],rd['restart']
            errors=dict(C=max(t.absup(x-y) for x,y in zip(ec,C,strict=True)),W=max(t.absup(x-y) for x,y in zip(ew,W,strict=True)))
            for key,a,b in (('H',t.flat(er['section']['H']),t.flat(rr['section']['H'])),('J',er['read']['current'],rr['read']['current'])):
                errors[key]=max(t.absup(x-y) for x,y in zip(a,b,strict=True))
            need(max(errors.values())<F(1,10**10),'represented finite error budget')
            need(rr['state_binding'] is None and not rr['exact_charge_authority'],'no represented exact-Q9 authority')
            beats.append(dict(beat=n+1,delta=t.DELTA,errors=errors,charge_drift=sum(C)-9,
                binary64=dict(C=[float(x).hex() for x in C],W=[float(x).hex() for x in W]),exact_section_digest=er['section']['section_digest'],
                represented_section=secsum(rr),writer_tau_binary64=t.TAU64,section_tau='exact frozen 1/(8 log 2)',
                local_exact_map_error=rd['local_exact_map_error'],invariance_defect_bound=rd['invariance_defect_bound'],
                invariance_center_gap=rd['invariance_center_gap']))
        rows.append(dict(role=name,beats=beats))
    C,W=tuple(t.project(x) for x in targets[0].values()[0]),tuple(t.project(x) for x in targets[0].values()[1])
    low,high=F(math.nextafter(float(t.M),-math.inf)),F(math.nextafter(float(t.M),math.inf));need(low<t.M<high,'W bracket')
    t.represented_read(C,(high,)*5);neg.append(reject('represented_W_below_floor',lambda:t.represented_read(C,(low,)*5)))
    bad=list(C);bad[0]+=F(1,2**48);neg.append(reject('represented_unequal_pairs',lambda:t.represented_read(tuple(bad),W)))
    neg.append(reject('represented_boxes_not_points',lambda:t.represented_read(targets[0].values()[0],W)))
    altered=list(C);altered[0]+=F(1,2**48);altered[1]+=F(1,2**48);rd=t.represented_read(tuple(altered),W)
    need(sum(altered)!=9 and rd['state_binding'] is None,'non-Q9 diagnostic not promoted')
    return dict(roles=rows,negatives=neg,budget=F(1,10**10),steps_per_role=4,intermediate_all_binary64=False,rounded_tau=t.TAU64,
        section_profile_unchanged=True,exact_charge_claim=False,arbitrary_numerical_horizon_claim=False,
        admission_may_fail_at_rounding_boundary=True,represented_floor_inside=high,represented_floor_outside=low)

def run():
    start=time.time();print('frozen T/A regeneration',file=sys.stderr,flush=True)
    original=json.loads((BASE/'predecessor/RGATC-TA-Certificate.json').read_text());need(t.ta.run()==original,'unchanged T/A regeneration')
    print('E section execution and independent oracle',file=sys.stderr,flush=True);E,source,post,targets,decs,secs=executed_chain()
    for oldkey,newkey in (('post_x','x_after'),('post_y','y_after'),('raw_dyadic_index','raw_index')):
        old=original['anchor'][oldkey];new=E['source'][newkey]
        need(F(old['lo'])<=t.lower(new)<=t.upper(new)<=F(old['hi']),'execution refines T/A envelope '+oldkey)
    E['TA_envelope_refinement']=True
    print('R coordinate covariance',file=sys.stderr,flush=True);cov=covariance(targets[0],decs[0])
    print('R elementary functions, boundaries, completion',file=sys.stderr,flush=True);bnd=boundaries()
    print('R lifecycle, replay, failure pressure',file=sys.stderr,flush=True);life=lifecycle(source)
    print('R finite represented publication',file=sys.stderr,flush=True);rep=representation(targets)
    paths=[BASE/'rgatc_reference.py',BASE/'rgatc_oracle.py',BASE/'check_rgatc_er.py']+sorted((BASE/'predecessor').rglob('*.py'))
    paths += [BASE/'predecessor/RGATC-TA-Certificate.json',BASE/'predecessor/RGATC-T.md',BASE/'predecessor/RGATC-A.md']
    record=t.enc(dict(schema='rgatc_er_execution_v1',status='executed_and_internally_pressured_pending_independent_review',
      independent_acceptance=False,native_profile_admission=False,aggregate_ATC2_closed=False,predecessor_record_digest=original['record_digest'],
      profile=t.PROFILE,profile_id=t.PROFILE_ID,evaluator_contract=t.EVALUATOR,E=E,R=dict(covariance=cov,boundaries=bnd,lifecycle=life,representation=rep),
      proof_constants=dict(section_ball=t.R,graph_transform_contraction=t.Q,section_Lipschitz=t.L,depth=t.DEPTH,maximum_inverse_shoots=t.MAX_SHOOTS,
        max_completed_maps_per_query=t.DEPTH*t.MAX_SHOOTS,max_E_section_error=max(s['radius'] for s in secs),max_E_inverse_shoots=max(s['inverse_shoots'] for s in secs)),
      scope=dict(frozen_completion_only=True,fixed_delta_only=True,paired_graphs_only=True,source_obstruction_not_executed_to_theorem_horizon=True,
        executable_section_not_global_native_support=True,exact_real_theorem_depends_on_TA=True,all_tests_internal=True),
      source_bindings=[dict(path=str(p.relative_to(BASE)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(paths))]))
    record['record_digest']=t.digest(record)
    print('complete: %.2f seconds, %d section queries'%(time.time()-start,t.SECTION_QUERIES),file=sys.stderr,flush=True)
    return record

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');ap.add_argument('--write',action='store_true');ap.add_argument('--compare',action='store_true');args=ap.parse_args()
    if args.check:
        v=json.loads(CERT.read_text());need(v['record_digest']==t.digest({k:x for k,x in v.items() if k!='record_digest'}),'record digest')
        for b in v['source_bindings']:need(hashlib.sha256((BASE/b['path']).read_bytes()).hexdigest()==b['sha256'],'source drift '+b['path'])
        print(json.dumps(dict(status='identity_checks_pass',scientific_rerun=False,record_digest=v['record_digest']),indent=2))
    else:
        v=run()
        if args.compare:need(v==json.loads(CERT.read_text()),'regenerated evidence exactly equals retained')
        if args.write:CERT.write_text(json.dumps(v,indent=2)+'\n')
        print(json.dumps(v if not(args.write or args.compare) else dict(status='internal_suite_pass',record_digest=v['record_digest'],retained_equal=args.compare),indent=2))
