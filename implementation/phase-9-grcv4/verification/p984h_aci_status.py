"""Pinned A_CI .h observations for selected CLI/API/notebook/browser views.

No native producer, reconstruction, interval solve, or full campaign checker is
called here. Exact execution identities and bounded credit remain distinct from
acceptance, which this view does not grant.
"""
from fractions import Fraction
import hashlib
import json
import lzma
import p984h_aci_campaign as c
import p984h_aci_covariance as cov

SELF=c.HERE+'p984h_aci_status.py'
TEST=c.HERE+'test_p984h_aci_surfaces.py'
REVIEW=c.BASE+'P9-8.4h-ACIReview.md'


def view(sources,pins):
    require=c.require
    for name in pins:sources.raw(name)
    def record(name):
        raw=sources.raw(name)
        value=json.loads(lzma.decompress(raw) if name.endswith('.xz') else raw)
        require(value==c.seal(value),'A_CI retained seal')
        return value
    def manifest(name):
        m=record(name)
        for path,h in m['source_bindings'].items():
            require(hashlib.sha256(sources.current_bytes(path)).hexdigest()==h,'A_CI execution source drift: '+path)
        return m
    source_m=manifest(c.source.INPUTS); src=record(c.source.RESULT)
    require(src['manifest_digest']==source_m['record_digest'] and src['outcome']=='completed'
        and 0<src['seconds']<=source_m['cap_seconds'] and not src['user_accepted'] and not src['aggregate_closed'],'A_CI source scope')
    se=src['execution'];tr=se['result']['poststep_trigger']
    require((se['native_steps'],se['native_events'],se['native_roots'])==(1,0,3)
        and tr['saturated'] and tr['small_gradient'] and tr['strict_hessian_condition'],'A_CI source credit')
    m=manifest(c.INPUTS); ev=record(c.path('event'));e=ev['execution']
    charge_manifest_name=c.BASE+'P9-8.4h-ACIChargeInputs.json'
    charge_manifest=manifest(charge_manifest_name) if charge_manifest_name in pins else None
    if charge_manifest:
        require(charge_manifest['original_manifest_digest']==m['record_digest']
            and charge_manifest['caps']==m['caps'] and charge_manifest['allowed_role']=='current'
            and charge_manifest['allowed_steps']==[8,9,10] and charge_manifest['allowed_final_step']==10
            and not charge_manifest['tolerance_changed'] and not charge_manifest['production_changed'],
            'A_CI charge checker successor scope')
    reset_charge_name=c.BASE+'P9-8.4h-ACIResetChargeInputs.json'
    reset_charge=manifest(reset_charge_name) if reset_charge_name in pins else None
    if reset_charge:
        require(charge_manifest and reset_charge['prior_charge_correction_digest']==charge_manifest['record_digest']
            and reset_charge['original_manifest_digest']==m['record_digest'] and reset_charge['caps']==m['caps']
            and reset_charge['allowed_role']=='reset' and reset_charge['allowed_steps']==[10]
            and reset_charge['allowed_final_step']==10 and not reset_charge['tolerance_changed']
            and not reset_charge['production_changed'],'A_CI reset charge correction scope')
    require(ev['manifest_digest']==m['record_digest'] and ev['predecessor_digest']==src['record_digest']
        and ev['segment']=='event' and ev['outcome']=='completed' and 0<ev['seconds']<=m['caps']['event']
        and e['native_events']==1 and e['native_steps']==0 and len(e['admissions'])==2 and len(e['writer_surfaces'])==4
        and e['request']==se['request'] and e['rollback_exact'] and not ev['user_accepted'] and not ev['aggregate_closed'],'A_CI event credit')
    roles={}
    for role in c.ROLES:
        predecessor=ev['record_digest'];steps=[];final=0;gap=False;refs=[]
        for k in range(1,12):
            segment='final' if k==11 else 'step';step=min(k,10);name=c.path(segment,role,step)
            if name not in pins:gap=True;continue
            require(not gap,'A_CI baseline chain gap')
            r=record(name);x=r['execution']
            successor=bool(charge_manifest and role=='current' and step>=8)
            expected_manifest=charge_manifest if successor else m
            if reset_charge and role=='reset' and step==10:expected_manifest=reset_charge
            require(r['manifest_digest']==expected_manifest['record_digest'] and r['predecessor_digest']==predecessor
                and (r['segment'],r['role'],r['step'])==(segment,role,step) and r['outcome']=='completed'
                and 0<r['seconds']<=m['caps']['final_root' if k==11 else 'target_step']
                and not r['user_accepted'] and not r['aggregate_closed'] and x['native_events']==0,'A_CI baseline linkage/scope')
            predecessor=r['record_digest']
            refs.append(sources.ref(name))
            if k==11:
                require(x['final_roots']==1 and x['native_steps']==0,'A_CI final credit');final=1
            else:
                require(x['native_steps']==1 and Fraction(x['minimum_exact_root_resource_lower'])>0
                    and x['reset_unchanged'] and x['detached_continuation'],'A_CI continuation credit')
                steps.append(dict(step=k,seconds=r['seconds'],minimum_resource=min(x['next_inputs']['current']['C']),
                    minimum_W_A=min(x['next_inputs']['current']['W_A']),
                    exact_root_lower_approx=float(Fraction(x['minimum_exact_root_resource_lower'])),
                    represented_charge=x['charge'],
                    exact_resource_sum_delta=x['exact_resource_sum_delta']))
        roles[role]=dict(native_steps=len(steps),final_reads=final,steps=steps,results=refs)
    continuation=dict(roles=roles,target_steps=sum(r['native_steps'] for r in roles.values()),
        final_reads=sum(r['final_reads'] for r in roles.values()),
        baseline_complete=all(r['native_steps']==10 and r['final_reads']==1 for r in roles.values()),
        local_joint_root_resource_enclosures=True,uniform_trajectory_enclosure=False,
        inputs=sources.ref(c.INPUTS),plan=sources.ref(c.PLAN),review=sources.ref(REVIEW))
    covariance=None
    if cov.INPUTS in pins:
        cm=manifest(cov.INPUTS);cases=[];events=steps=0
        def maximum(v):return max(map(maximum,v.values()),default=0.) if isinstance(v,dict) else float(v)
        for kind in cov.KINDS:
            segments=[];event_digest=None
            for segment in ('event',*c.ROLES):
                name=cov.path(kind,segment)
                if name not in pins:continue
                r=record(name);x=r['execution']
                require(r['manifest_digest']==cm['record_digest'] and (r['kind'],r['segment'])==(kind,segment)
                    and r['outcome']=='completed' and 0<r['seconds']<=cm['event_cap_seconds' if segment=='event' else 'step_cap_seconds']
                    and not r['user_accepted'] and not r['aggregate_closed'],'A_CI covariance scope')
                if segment=='event':
                    require(r['predecessor_digest']==ev['record_digest'] and x['native_events']==1 and x['native_steps']==0,'A_CI covariance event')
                    event_digest=r['record_digest'];events+=1
                else:
                    require(event_digest is not None and r['predecessor_digest']==event_digest and x['native_events']==0
                        and x['native_steps']==1 and Fraction(x['minimum_exact_root_resource_lower'])>0,'A_CI covariance history')
                    steps+=1
                segments.append(dict(segment=segment,seconds=r['seconds'],maximum_covariance_error=maximum(r['covariance_errors']),result=sources.ref(name)))
            cases.append(dict(kind=kind,complete=[x['segment'] for x in segments]==['event',*c.ROLES],segments=segments))
        covariance=dict(cases=cases,native_events=events,target_steps=steps,covariance_complete=all(x['complete'] for x in cases),
            transformed_horizon=1,source_prefix_rerun=False,full_joint_roots=True,unsigned_candidate_history=True,
            user_accepted=False,aggregate_closed=False,
            inputs=sources.ref(cov.INPUTS),plan=sources.ref(c.PLAN),review=sources.ref(REVIEW))
    complete=continuation['baseline_complete'] and covariance and covariance['covariance_complete']
    closeout_name=c.BASE+'P9-8.4h-ACICloseout.json'
    closeout=None
    if closeout_name in pins:
        reviewed=record(closeout_name)
        require(complete and reviewed['bounded_coverage_complete']
            and (reviewed['native_source_steps'],reviewed['native_events'],reviewed['target_steps'],reviewed['final_roots'])==(1,9,36,2)
            and len(reviewed['event_checkpoints'])==9 and not reviewed['user_accepted'] and not reviewed['aggregate_closed'],
            'A_CI retained closeout scope')
        for path,h in {**reviewed['record_bindings'],**reviewed['checker_bindings']}.items():
            require(hashlib.sha256(sources.current_bytes(path)).hexdigest()==h,'A_CI closeout binding drift')
        closeout=sources.ref(closeout_name)
    return dict(family='A_CI',checkpoint='8.4h',
        status='baseline_and_covariance_complete_pending_acceptance' if complete else 'native_event_complete_continuation_pending',
        native_steps=1,native_events=1,target_steps=continuation['target_steps'],final_reads=continuation['final_reads'],
        total_native_events=1+(covariance['native_events'] if covariance else 0),
        total_target_steps=continuation['target_steps']+(covariance['target_steps'] if covariance else 0),
        continuation=continuation,covariance=covariance,source_full_joint_parity=True,
        fresh_trigger=dict(eligible=True,**tr),native_numerics_rerun=False,covariance_executed=bool(covariance),
        unsigned_candidate_history=True,full_joint_roots=True,user_accepted=False,aggregate_closed=False,
        uniform_trajectory_enclosure=False,original_execution_flags_unchanged=True,
        retained_checkpoint_review=closeout,
        charge_checker_successor=sources.ref(charge_manifest_name) if charge_manifest else None,
        reset_charge_checker_successor=sources.ref(reset_charge_name) if reset_charge else None,
        segments=[dict(segment='source',seconds=src['seconds'],result=sources.ref(c.source.RESULT)),
                  dict(segment='event',seconds=ev['seconds'],result=sources.ref(c.path('event')))],
        inputs=sources.ref(c.INPUTS),plan=sources.ref(c.PLAN),review=sources.ref(REVIEW))
