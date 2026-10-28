"""Eight large A_OS counterparts with unsigned history and signed OS reads.

Only mechanical graph/chart transport is shared with the A_CI adapter. Every
native admission, predictor, corrector, writer and independent oracle is A_OS.
"""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json
import lzma
import time
from unittest.mock import patch
import numpy as np

import p984gh_aos_native as n
import p984h_cos_covariance as maps
from p984h_aci_covariance import input_image
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy, GRC9V4ExpansionPlan, GRC9V4ExpansionRequestInput,
    aos_profile_template, aos_history_policy,
)

b=n.b
SELF=b.HERE+'p984h_aos_covariance.py'
TEST=b.HERE+'test_p984h_aos_covariance.py'
INPUTS=b.BASE+'P9-8.4h-AOSCovarianceInputs.json'
KINDS,ROLES=maps.KINDS,n.ROLES
ATOL=RTOL=2e-13


def path(kind,segment):
    b.require(kind in KINDS and segment in ('event',*ROLES),'counterpart roster')
    return b.BASE+f'P9-8.4h-AOSCovariance-{kind}-{segment}.json.xz'


def read(kind,segment):return n.g.storage.read(path(kind,segment))


def plan(seed,request):
    return GRC9V4ExpansionPlan(seed.inputs.geometry.reference.graph.port_graph,seed.scientific_digest,
        GRC9V4ExpansionRequestInput.from_payload(request),
        GRC9ExpansionPolicy.from_payload(seed.specialization.resolved['expansion']))


@lru_cache(maxsize=1)
def baseline():
    seed,_=n.source_state();record=n.read('event');b.check_digest(record)
    return seed.to_payload(),record['execution']


@contextmanager
def transport():
    # A declared data-provider substitution, never a numerical producer mock.
    with patch.object(maps,'base',return_value=baseline()):yield


@lru_cache(maxsize=8)
def subject(kind):
    b.require(kind in KINDS,'unknown transform');old,event=baseline()
    with transport():
        d=maps.declaration(kind)
        inp=input_image(old['inputs'],maps.graph_image(old['inputs']['reference']['graph'],d,source=True),d)
        seed=replace(n.state(old),inputs=inp);request=deepcopy(event['request'])
        branches=d['chart']['branches'];shares=[0.]*3
        for i,x in enumerate(request['resource_distribution'],1):shares[branches[str(i)]-1]=x
        request.update(operation_id='p984h-aos-covariance-'+kind,source_node_id=maps.rename(request['source_node_id'],d),
            source_state_digest=seed.scientific_digest,source_graph_digest=inp.geometry.reference.graph.graph_digest,
            target_profile_template_id=aos_profile_template(inp.geometry.reference).profile_template_id,
            history_policy=aos_history_policy(inp.current,inp.reset),resource_distribution=shares,
            module_chirality=request['module_chirality']*d['chart']['chirality_factor'],
            growth_phase=branches[str(request['growth_phase'])])
        original_plan=plan(n.state(old),event['request']);identity=deepcopy(original_plan.event_identity_payload())
        for key in identity:
            if key in request and key!='schema_version':identity[key]=request[key]
        for channel in ('candidate','carrier'):
            key=channel+'_history_policy_digest';identity[key]=request['history_policy'][key]
        eid=maps.ordering.b.payload_identity('expansion_event_identity_payload',identity)
        original=event['state']['inputs']
        graph=maps.graph_image(original['reference']['graph'],d,event['event_id'],eid)
        target=replace(input_image(original,graph,d,event['event_id'],eid),operation_id=request['operation_id'])
    actual_plan=plan(seed,request)
    b.require(actual_plan.event_id==eid and actual_plan.event_identity_payload()==identity
        and actual_plan.target_graph==target.geometry.reference.graph.port_graph,'transformed identity/allocator')
    return seed,request,identity,eid,target


def manifest():
    upstream=n.g.storage.read(n.INPUTS);n.check_manifest(upstream)
    paths={r['path'] for r in upstream['source_bindings']}
    paths|={SELF,TEST,n.INPUTS,n.filename('event'),maps.SELF,maps.ordering.SELF,maps.chart.SELF,
        b.HERE+'p984h_aci_covariance.py',*(n.filename('step',r,1) for r in ROLES)}
    return b.seal(dict(schema='p984h-aos-covariance-inputs-v1',source_bindings=b.bind(paths),
        kinds=list(KINDS),roles=list(ROLES),atol=ATOL,rtol=RTOL,event_cap=1200,step_cap=600,
        max_workers=4,threads_per_worker=1,native_events=8,target_steps=16,transformed_horizon=1,
        source_rerun=False,backend='flint',numerical_policy='certified_arb_256_weighted_v1',
        user_accepted=False,aggregate_closed=False))


def compare(actual,expected,label):
    a,c=np.asarray(actual),np.asarray(expected)
    b.require(a.shape==c.shape and np.isfinite(a).all() and np.isfinite(c).all()
        and np.allclose(a,c,atol=ATOL,rtol=RTOL),'covariance '+label)
    return float(np.max(abs(a-c))) if a.size else 0.


def indices(kind,original,new):
    with transport():return maps.mapping(original['reference']['graph'],new['reference']['graph'],
        maps.declaration(kind),baseline()[1]['event_id'],subject(kind)[3])


def point_pair(left,right,orders):
    ni,ei,sign=orders;errors={}
    for key in ('current','baseline','flux','flat'):
        errors[key]=compare(right[key],np.asarray(left[key])[ei]*sign,key)
    errors['potential']=compare(right['potential'],np.asarray(left['potential'])[ni],'potential')
    errors['drive']=compare(right['drive'],np.asarray(left['drive'])[ei],'unsigned drive')
    return errors


def step_pair(kind,role,value):
    old=n.read('step',role,1)['execution'];orders=indices(kind,old['before'],value['before'])
    ni,ei,sign=orders;errors={}
    for key in ('predictor','corrector'):errors[key]=point_pair(old[key],value[key],orders)
    for key in ('final','restart'):errors[key]=point_pair(old[key]['actual'],value[key]['actual'],orders)
    errors['H']=compare(value['H'],np.asarray(old['H'])[np.ix_(ei,ei)]*np.outer(sign,sign),'signed H')
    for r in ROLES:
        for key,order in (('C',ni),('W_A',ei)):
            errors[r+'/'+key]=compare(value['after'][r][key],np.asarray(old['after'][r][key])[order],r+'/'+key)
        b.require(value['after'][r]['Z_4'] is None,'A_OS carrier introduced')
    errors['writer_drive']=compare(value['writer']['drive'],np.asarray(old['writer']['drive'])[ei],'unsigned writer')
    with transport():branches=maps.declaration(kind)['chart']['branches']
    columns=[next(i-1 for i in (1,2,3) if branches[str(i)]==j) for j in (1,2,3)]
    errors['descriptors']=compare(value['writer']['descriptors'],np.asarray(old['writer']['descriptors'])[np.ix_(ni,columns)],'descriptor columns')
    return errors


def execute(kind,segment):
    seed,request,identity,eid,target=subject(kind)
    if segment=='event':
        owner=n.native.GRC9V4AOSOperation(seed);before=owner.checkpoint()
        stale=dict(request,source_state_digest=n.g.storage.read(n.g.INPUTS)['adjusted']['event_request']['source_state_digest'])
        b.require(stale['source_state_digest']!=seed.scientific_digest,'stale declaration aliases source')
        rejected=owner.expand(GRC9V4ExpansionRequestInput.from_payload(stale))
        b.require(not rejected.committed and owner.checkpoint()==before,'stale counterpart rollback')
        result=owner.expand(GRC9V4ExpansionRequestInput.from_payload(request))
        b.require(result.committed,'counterpart event rejected: '+str(result.failure))
        b.require(owner.state.inputs==target,'independent whole target transport')
        b.require(n.native.GRC9V4AOSOperation.replay(owner.checkpoint()).checkpoint()==owner.checkpoint(),'counterpart replay')
        return dict(request=request,event_identity=identity,event_id=eid,state=owner.state.to_payload(),
            checkpoint=json.loads(owner.checkpoint()),stale_failure=rejected.failure.to_payload(),
            rollback_exact=True,exact_replay=True,native_events=1),n.read('event')['record_digest']
    record=read(kind,'event');b.check_digest(record)
    initial=n.state(record['execution']['state']).inputs
    value,_=n.observe_step(replace(initial,current=getattr(initial,segment),dt=n.DT))
    return value,record['record_digest']


def check(value,kind,segment,m):
    b.check_digest(value)
    b.require(value['schema']=='p984h-aos-covariance-segment-v1' and value['manifest_digest']==m['record_digest']
        and (value['kind'],value['segment'])==(kind,segment) and value['outcome']=='completed'
        and value['user_accepted'] is False and value['aggregate_closed'] is False
        and 0<value['seconds']<=m['event_cap' if segment=='event' else 'step_cap'],'counterpart scope')
    seed,request,identity,eid,target=subject(kind);e=value['execution']
    if segment=='event':
        b.require(e['request']==request and e['event_identity']==identity and e['event_id']==eid
            and e['state']['inputs']==target.to_payload() and e['checkpoint']['state']==e['state']
            and e['rollback_exact'] and e['exact_replay'] and e['stale_failure'] and e['native_events']==1
            and value['predecessor_digest']==n.read('event')['record_digest'],'counterpart event lineage/transport')
        return {}
    event=read(kind,'event');b.check_digest(event)
    initial=n.state(event['execution']['state']).inputs
    wanted=replace(initial,current=getattr(initial,segment),dt=n.DT)
    b.require(e['before']==wanted.to_payload() and value['predecessor_digest']==event['record_digest'],'counterpart step input')
    n.check_step(e)
    return step_pair(kind,segment,e)


def run(kind):
    m=n.g.storage.read(INPUTS);b.check_digest(m);b.check_bindings(m['source_bindings'])
    for segment in ('event',*ROLES):
        with n.policy():
            if (b.ROOT/path(kind,segment)).exists():
                v=read(kind,segment);b.require(v['covariance_errors']==check(v,kind,segment,m),'saved covariance');continue
            start=time.monotonic()
            with b.budget(m['event_cap' if segment=='event' else 'step_cap']):execution,prior=execute(kind,segment)
            v=b.seal(dict(schema='p984h-aos-covariance-segment-v1',manifest_digest=m['record_digest'],kind=kind,
                segment=segment,execution=execution,predecessor_digest=prior,seconds=time.monotonic()-start,
                outcome='completed',user_accepted=False,aggregate_closed=False))
            v['covariance_errors']=check(v,kind,segment,m);v=b.seal(v)
        b.check_bindings(m['source_bindings'])
        with (b.ROOT/path(kind,segment)).open('xb') as stream:
            stream.write(lzma.compress(json.dumps(v,separators=(',',':'),allow_nan=False).encode()+b'\n'))
        print(json.dumps(dict(kind=kind,segment=segment,seconds=v['seconds'],outcome='completed')),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','run'))
    p.add_argument('--kind',choices=KINDS);args=p.parse_args()
    if args.action=='prepare':b.write_new(INPUTS,manifest())
    else:run(args.kind)
