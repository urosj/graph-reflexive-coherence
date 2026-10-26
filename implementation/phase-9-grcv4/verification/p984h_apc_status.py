"""Pinned A_PC larger-event observations; read-only, without numerical reruns."""
import hashlib
import json
import lzma
from fractions import Fraction
import p984h_apc_campaign as c
import p984h_apc_covariance as cov

SELF=c.HERE+'p984h_apc_status.py'
REVIEW=c.BASE+'P9-8.4h-APCReview.md'


def view(sources,pins):
    for name in pins:sources.raw(name)
    def record(name):
        raw=sources.raw(name)
        value=json.loads(lzma.decompress(raw) if name.endswith('.xz') else raw)
        c.require(value==c.seal(value),'A_PC retained seal')
        return value
    def manifest(name):
        m=record(name)
        for path,h in m['source_bindings'].items():
            c.require(hashlib.sha256(sources.current_bytes(path)).hexdigest()==h,'A_PC execution source drift: '+path)
        return m
    def segment(name,m,predecessor,cap):
        v=record(name)
        c.require(v['manifest_digest']==m['record_digest'] and v['predecessor_digest']==predecessor
            and v['outcome']=='completed' and 0<v['seconds']<=cap
            and not v['user_accepted'] and not v['aggregate_closed'],'A_PC linkage/scope')
        return v
    sm=manifest(c.prep.INPUTS);src=record(c.prep.RESULT);se=src['execution']
    c.require(src['manifest_digest']==sm['record_digest'] and src['outcome']=='completed'
        and 0<src['seconds']<=sm['caps']['source'] and not src['user_accepted'] and not src['aggregate_closed']
        and (se['native_steps'],se['native_reads'],se['native_events'])==(1,3,0)
        and se['trigger']['small_gradient'] and Fraction(se['trigger']['minimum_signed_hessian_upper'])<0,'A_PC source scope')
    m=manifest(c.INPUTS);ev=segment(c.path('event'),m,src['record_digest'],m['caps']['event']);e=ev['execution']
    c.require((ev['segment'],ev['role'],ev['step'])==('event','current',1)
        and e['native_events']==1 and e['native_steps']==0 and len(e['admissions'])==2 and len(e['writer_surfaces'])==4
        and e['request']==se['request'] and e['rollback_exact'] and c.contains(e['checkpoint'],e['carrier_archive']),
        'A_PC event and carrier archive')
    roles={}
    for role in c.ROLES:
        predecessor=ev['record_digest'];steps=[];final=0;gap=False;refs=[]
        for k in range(1,12):
            which='final' if k==11 else 'step';step=min(k,10);name=c.path(which,role,step)
            if name not in pins:gap=True;continue
            c.require(not gap,'A_PC baseline chain gap')
            r=segment(name,m,predecessor,m['caps']['final_read' if k==11 else 'target_step']);x=r['execution']
            c.require((r['segment'],r['role'],r['step'])==(which,role,step) and x['native_events']==0,'A_PC baseline identity')
            predecessor=r['record_digest'];refs.append(sources.ref(name))
            if k==11:
                c.require(x['final_reads']==1 and x['native_steps']==0,'A_PC final credit');final=1
            else:
                lower=min(Fraction(b['lower']) for b in x['oracle']['resource_bounds'])
                c.require(x['native_steps']==1 and lower>0 and x['reset_unchanged'] and x['detached_continuation'],'A_PC continuation credit')
                effect=x['carrier_separation']
                c.require((effect is not None)==(k in (1,10)),'A_PC declared effect pressure')
                if effect:c.require(Fraction(effect['margin'])>0 and effect['changed_current_coordinates']>0,'A_PC resolved carrier')
                steps.append(dict(step=k,seconds=r['seconds'],minimum_resource=min(x['next_inputs']['current']['C']),
                    minimum_W_A=min(x['next_inputs']['current']['W_A']),exact_PC_lower_approx=float(lower),
                    represented_charge=x['charge'],exact_resource_sum_delta=x['exact_resource_sum_delta'],
                    carrier_separation=effect))
        roles[role]=dict(native_steps=len(steps),final_reads=final,steps=steps,results=refs)
    continuation=dict(roles=roles,target_steps=sum(r['native_steps'] for r in roles.values()),final_reads=sum(r['final_reads'] for r in roles.values()),
        baseline_complete=all(r['native_steps']==10 and r['final_reads']==1 for r in roles.values()),
        local_PC_resource_enclosures=True,uniform_trajectory_enclosure=False,inputs=sources.ref(c.INPUTS),plan=sources.ref(c.prep.PLAN),review=sources.ref(REVIEW))
    covariance=None
    if cov.INPUTS in pins:
        cm=manifest(cov.INPUTS);cases=[];events=steps=0
        def maximum(v):return max(map(maximum,v.values()),default=0.) if isinstance(v,dict) else float(v)
        for kind in cov.KINDS:
            segments=[];event_digest=None
            for which in ('event',*c.ROLES):
                name=cov.path(kind,which)
                if name not in pins:continue
                r=segment(name,cm,ev['record_digest'] if which=='event' else event_digest,
                    cm['event_cap_seconds' if which=='event' else 'step_cap_seconds']);x=r['execution']
                c.require((r['kind'],r['segment'])==(kind,which),'A_PC covariance identity')
                if which=='event':
                    c.require(x['native_events']==1 and x['native_steps']==0 and c.contains(x['checkpoint'],x['carrier_archive']),'A_PC covariance event')
                    event_digest=r['record_digest'];events+=1
                else:
                    c.require(event_digest is not None and x['native_events']==0 and x['native_steps']==1
                        and min(Fraction(b['lower']) for b in x['oracle']['resource_bounds'])>0,'A_PC covariance history');steps+=1
                segments.append(dict(segment=which,seconds=r['seconds'],maximum_covariance_error=maximum(r['covariance_errors']),result=sources.ref(name)))
            cases.append(dict(kind=kind,complete=[x['segment'] for x in segments]==['event',*c.ROLES],segments=segments))
        covariance=dict(cases=cases,native_events=events,target_steps=steps,covariance_complete=all(x['complete'] for x in cases),
            transformed_horizon=1,source_prefix_rerun=False,full_PC_points=True,unsigned_candidate_history=True,
            signed_carrier_transport=True,user_accepted=False,aggregate_closed=False,inputs=sources.ref(cov.INPUTS),plan=sources.ref(c.prep.PLAN),review=sources.ref(REVIEW))
    complete=bool(continuation['baseline_complete'] and covariance and covariance['covariance_complete'])
    closeout_name=c.BASE+'P9-8.4h-APCCloseout.json';closeout=None
    if closeout_name in pins:
        reviewed=record(closeout_name)
        c.require(complete and reviewed['bounded_coverage_complete']
            and (reviewed['native_source_steps'],reviewed['native_events'],reviewed['target_steps'],reviewed['final_reads'])==(1,9,36,2)
            and len(reviewed['event_checkpoints'])==9 and not reviewed['user_accepted'] and not reviewed['aggregate_closed'],'A_PC closeout scope')
        for path,h in {**reviewed['record_bindings'],**reviewed['checker_bindings']}.items():
            c.require(hashlib.sha256(sources.current_bytes(path)).hexdigest()==h,'A_PC closeout binding drift')
        closeout=sources.ref(closeout_name)
    return dict(family='A_PC',checkpoint='8.4h',status='baseline_and_covariance_complete_pending_acceptance' if complete else 'native_event_complete_continuation_pending',
        native_steps=1,native_events=1,target_steps=continuation['target_steps'],final_reads=continuation['final_reads'],
        total_native_events=1+(covariance['native_events'] if covariance else 0),total_target_steps=continuation['target_steps']+(covariance['target_steps'] if covariance else 0),
        continuation=continuation,covariance=covariance,source_full_point_parity=True,fresh_trigger=dict(eligible=True,**se['trigger']),
        full_PC_points=True,unsigned_candidate_history=True,signed_carrier_transport=True,explicit_carrier_loss_and_zero_target=True,
        native_numerics_rerun=False,user_accepted=False,aggregate_closed=False,uniform_trajectory_enclosure=False,
        original_execution_flags_unchanged=True,retained_checkpoint_review=closeout,
        segments=[dict(segment='source',seconds=src['seconds'],result=sources.ref(c.prep.RESULT)),dict(segment='event',seconds=ev['seconds'],result=sources.ref(c.path('event')))],
        inputs=sources.ref(c.INPUTS),plan=sources.ref(c.prep.PLAN),review=sources.ref(REVIEW))
