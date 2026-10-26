"""Eight larger A_PC event counterparts; unsigned W and two-sided Z transport."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json
import lzma
from unittest.mock import patch
import numpy as np

import p984h_apc_campaign as c
import p984h_cos_covariance as maps
from pygrc.models.grc_9_v4_expansion import apc_profile_template
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry, GRCV4Geometry, OneFormHodge

ROOT,BASE,HERE=c.ROOT,c.BASE,c.HERE
SELF=HERE+'p984h_apc_covariance.py';TEST=HERE+'test_p984h_apc_covariance.py'
INPUTS=BASE+'P9-8.4h-APCCovarianceInputs.json'
KINDS,ROLES=maps.KINDS,c.ROLES
require,seal,digest=c.require,c.seal,c.digest
ATOL=RTOL=2e-13


def path(kind,segment):
    require(kind in KINDS and segment in ('event',*ROLES),'counterpart roster')
    return BASE+f'P9-8.4h-APCCovariance-{kind}-{segment}.json.xz'


def read(kind,segment):return json.loads(lzma.decompress((ROOT/path(kind,segment)).read_bytes()))


@lru_cache(maxsize=1)
def baseline():
    seed,source=c.baseline_source();event=c.read('event')
    require(event==seal(event) and event['outcome']=='completed','baseline event')
    return seed.to_payload(),event['execution']


@contextmanager
def transport():
    with patch.object(maps,'base',return_value=baseline()):yield


def conjugate(matrix,ei,sign):
    return [[matrix[i][j]*sign[k]*sign[l] if matrix[i][j] else 0.
        for l,j in enumerate(ei)] for k,i in enumerate(ei)]


def input_image(original,graph,d,old_event=None,new_event=None):
    ni,ei,sign=maps.mapping(original['reference']['graph'],graph,d,old_event,new_event)
    value=deepcopy(original);ref=value['reference'];ref['graph']=graph
    for owner,key in ((ref,'K4_base'),(value,'H1_form')):owner[key]=conjugate(owner[key],ei,sign)
    weights=ref['reference_hodge']['edge_weights']
    ref['reference_hodge']['edge_weights']={maps.rename(k,d,old_event,new_event):v for k,v in weights.items()}
    port=c.prep.d.GRC9V4PortGraph.from_payload({k:graph[k] for k in ('schema_version','live_node_ids','edges')})
    params=ref['profile']['params_resolved'];identity=ref['profile']['identity_payload'];ident=maps.ordering.b.payload_identity
    params['candidate']['descriptor_backend_id']=c.prep.native.GRC9V4CandidateADifferentialReference(port).identity
    params['geometry']['reference_hodge_digest']=ident('reference_hodge_identity_payload',ref['reference_hodge'])
    params['geometry']['K4_base_digest']=ident('k4_identity_payload',dict(schema_version='grcv4-k4-identity-v1',K4_base=ref['K4_base']))
    identity['params_hash']=ident('resolved_params',params);ref['profile']=maps.ordering.b.resolve_profile(params,identity).to_payload()
    reference=GRCV4ReferenceGeometry.from_payload(ref);before=c.prep.GeometryStageInputs.from_payload(original)
    n=len(ei);roles={}
    for role in ROLES:
        old=original[role];Z=[old['Z_4'][i*n:(i+1)*n] for i in range(n)]
        roles[role]=c.prep.GRCV4AuthoritativeState(tuple(old['C'][i] for i in ni),tuple(old['W_A'][i] for i in ei),
            tuple(x for row in conjugate(Z,ei,sign) for x in row))
    return replace(before,geometry=GRCV4Geometry(reference,OneFormHodge(reference.graph,tuple(map(tuple,value['H1_form'])))),**roles)


@lru_cache(maxsize=8)
def subject(kind):
    require(kind in KINDS,'unknown transform');old,event=baseline()
    with transport():
        d=maps.declaration(kind);inp=input_image(old['inputs'],maps.graph_image(old['inputs']['reference']['graph'],d,source=True),d)
        seed=replace(c.state(old),inputs=inp);request=deepcopy(event['request']);branches=d['chart']['branches'];shares=[0.]*3
        for i,x in enumerate(request['resource_distribution'],1):shares[branches[str(i)]-1]=x
        request.update(operation_id='p984h-apc-covariance-'+kind,source_node_id=maps.rename(request['source_node_id'],d),
            source_state_digest=seed.scientific_digest,source_graph_digest=inp.geometry.reference.graph.graph_digest,
            target_profile_template_id=apc_profile_template(inp.geometry.reference).profile_template_id,
            history_policy=c.prep.apc_history_policy(inp.current,inp.reset),resource_distribution=shares,
            module_chirality=request['module_chirality']*d['chart']['chirality_factor'],growth_phase=branches[str(request['growth_phase'])])
        identity=deepcopy(event['event_identity'])
        for key in identity:
            if key in request and key!='schema_version':identity[key]=request[key]
        for channel in ('candidate','carrier'):
            key=channel+'_history_policy_digest';identity[key]=request['history_policy'][key]
        eid=maps.ordering.b.payload_identity('expansion_event_identity_payload',identity)
        original=event['checkpoint']['state']['inputs']
        graph=maps.graph_image(original['reference']['graph'],d,event['event_id'],eid)
        target=replace(input_image(original,graph,d,event['event_id'],eid),operation_id=request['operation_id'])
    plan=c.prep.plan_for(seed,request)
    require(plan.event_id==eid and plan.event_identity_payload()==identity and plan.target_graph==target.geometry.reference.graph.port_graph,
        'transformed event identity/allocator')
    return seed,request,identity,eid,target


def manifest():
    upstream=c.manifest();require(upstream==json.loads((ROOT/c.INPUTS).read_text()),'baseline manifest drift')
    names=set(upstream['source_bindings'])|{c.INPUTS,SELF,TEST,maps.SELF,maps.ordering.SELF,maps.chart.SELF,maps.chart.b.VECTORS,
        c.path('event'),*(c.path('step',role,1) for role in ROLES)}
    return seal(dict(schema='p984h-apc-covariance-inputs-v1',source_bindings={n:c.prep.sha(n) for n in sorted(names)},
        kinds=list(KINDS),event_cap_seconds=1200,step_cap_seconds=600,max_workers=8,threads_per_worker=1,
        atol=ATOL,rtol=RTOL,native_events=8,target_steps=16,transformed_horizon=1,source_rerun=False,
        backend='flint',numerical_policy='certified_arb_256_weighted_v1',user_accepted=False,aggregate_closed=False))


def compare(actual,expected,label):
    a,b=np.asarray(actual),np.asarray(expected)
    require(a.shape==b.shape and np.isfinite(a).all() and np.isfinite(b).all() and np.allclose(a,b,atol=ATOL,rtol=RTOL),'covariance '+label)
    return float(np.max(abs(a-b))) if a.size else 0.


def indices(kind,original,new,target):
    with transport():
        return maps.mapping(original['reference']['graph'],new.to_payload()['reference']['graph'],maps.declaration(kind),
            baseline()[1]['event_id'] if target else None,subject(kind)[3] if target else None)


def point_pair(old,new,orders):
    ni,ei,sign=orders;left,right=old['actual'],new['actual'];errors={}
    for name in ('current','baseline','flux','flat'):errors[name]=compare(right[name],np.asarray(left[name])[ei]*sign,name)
    for name in ('potential','C'):errors[name]=compare(right[name],np.asarray(left[name])[ni],name)
    for name in ('drive','W_A'):errors[name]=compare(right[name],np.asarray(left[name])[ei],name)
    for name in ('Z','H','source'):errors[name]=compare(c.p.unpack(right[name]),conjugate(c.p.unpack(left[name]),ei,sign),name)
    require(left['certificate']==right['certificate'],'whole-chart certificate covariance')
    return errors


def writer_pair(old,new,orders,kind):
    ni,ei,sign=orders;errors={}
    for key,order,mult in (('C',ni,1),('W_A',ei,1),('J',ei,sign),('drive',ei,1)):
        errors[key]=compare(new[key],np.asarray(old[key])[order]*mult,'writer '+key)
    with transport():branches=maps.declaration(kind)['chart']['branches']
    columns=[next(i-1 for i in (1,2,3) if branches[str(i)]==j) for j in (1,2,3)]
    errors['descriptors']=compare(new['descriptors'],np.asarray(old['descriptors'])[np.ix_(ni,columns)],'writer descriptors')
    return errors


def step_inputs(kind,role):
    event=read(kind,'event');require(event==seal(event) and event['outcome']=='completed','counterpart event')
    target=c.state(event['execution']['checkpoint']['state']).inputs
    return replace(target,current=getattr(target,role),geometry=c.pc.carrier_geometry(target,getattr(target,role)),dt=c.DT),event['record_digest']


def execute(kind,segment,progress):
    if segment=='event':
        seed,request,identity,eid,expected=subject(kind)
        return c.event_capture(seed,request,expected,progress),c.read('event')['record_digest']
    before,predecessor=step_inputs(kind,segment)
    return c.observe(before),predecessor


@c.prep.in_policy
def check(value,kind,segment,m):
    require(value==seal(value) and value['manifest_digest']==m['record_digest'] and value['outcome']=='completed'
        and (value['kind'],value['segment'])==(kind,segment) and value['user_accepted'] is False and value['aggregate_closed'] is False
        and 0<value['seconds']<=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds'],'counterpart identity/scope')
    seed,request,identity,eid,target=subject(kind);e=value['execution'];old=baseline()[1];errors={}
    if segment=='event':
        require(e['request']==request and e['event_identity']==identity and e['event_id']==eid
            and value['predecessor_digest']==c.read('event')['record_digest'],'event lineage')
        require(c.prep.canonical_input_payload(e['checkpoint']['state']['inputs'])==c.prep.canonical_input_payload(target.to_payload())
            and e['native_events']==1 and e['native_steps']==0 and e['rollback_exact'] and e['stale_failure']
            and len(e['admissions'])==2 and len(e['writer_surfaces'])==4,'event target/scope')
        archive=c.GRC9V4APCExpansion(c.prep.plan_for(seed,request),seed.inputs.geometry.reference,seed.inputs.current,seed.inputs.reset).carrier_archive_payload()
        require(e['carrier_archive']==archive and c.contains(e['checkpoint'],archive),'transformed carrier archive')
        for i,before in enumerate((seed.inputs,target)):
            original=baseline()[0]['inputs'] if i==0 else old['checkpoint']['state']['inputs']
            orders=indices(kind,original,before,i==1)
            require(e['admissions'][i]['old_publication_live'],'publication ordering')
            for j,role in enumerate(ROLES):
                c.check_read(e['admissions'][i][role],replace(before,current=getattr(before,role)))
                errors[f'{i}/{role}/point']=point_pair(old['admissions'][i][role],e['admissions'][i][role],orders)
                errors[f'{i}/{role}/writer']=writer_pair(old['writer_surfaces'][2*i+j],e['writer_surfaces'][2*i+j],orders,kind)
    else:
        before,predecessor=step_inputs(kind,segment);require(value['predecessor_digest']==predecessor,'step lineage')
        after=c.check_step(e,before);prior=c.read('step',segment,1)['execution']
        original=c.state(old['checkpoint']['state']).inputs;original=replace(original,current=getattr(original,segment),dt=c.DT)
        orders=indices(kind,original.to_payload(),before,True)
        for name in ('current','reset','final'):errors[name]=point_pair(prior['reads'][name],e['reads'][name],orders)
        errors['C']=compare(after.current.C,np.asarray(prior['next_inputs']['current']['C'])[orders[0]],'written C')
        errors['W_A']=compare(after.current.W_A,np.asarray(prior['next_inputs']['current']['W_A'])[orders[1]],'written W')
        errors['Z']=compare(c.zrows(after.current),conjugate(c.p.unpack(prior['oracle']['Z']),orders[1],orders[2]),'written Z')
        errors['drive']=compare(e['oracle']['drive'],np.asarray(prior['oracle']['drive'])[orders[1]],'unsigned writer drive')
    return errors


def worker(pipe,kind,segment):
    try:
        with c.prep.validation_reuse(),c.prep.exact_backend(c.prep.ExactBackend.FLINT),c.prep.numerical_policy(c.prep.NumericalPolicy.CERTIFIED_ARB_256),c.prep.matrix_operation():
            result=execute(kind,segment,lambda s:pipe.send(('progress',s)))
        pipe.send(('result',result))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


def run_one(kind,segment,m):
    if (ROOT/path(kind,segment)).exists():
        v=read(kind,segment);require(v['covariance_errors']==check(v,kind,segment,m),'retained covariance');return
    cap=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds']
    (execution,predecessor),seconds=c.prep.capped(worker,(kind,segment),cap)
    v=seal(dict(schema='p984h-apc-covariance-segment-v1',manifest_digest=m['record_digest'],kind=kind,segment=segment,
        execution=execution,predecessor_digest=predecessor,seconds=seconds,outcome='completed',user_accepted=False,aggregate_closed=False))
    v['covariance_errors']=check(v,kind,segment,m);v=seal(v)
    require(m==manifest(),'source changed during covariance');c.prep.save(path(kind,segment),v)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run','check'));parser.add_argument('--kind',choices=KINDS)
    args=parser.parse_args();m=manifest()
    if args.action=='prepare':
        with (ROOT/INPUTS).open('x') as stream:json.dump(m,stream,indent=2);stream.write('\n')
    else:
        require(m==json.loads((ROOT/INPUTS).read_text()),'covariance manifest drift')
        for segment in ('event',*ROLES):
            if args.action=='run':run_one(args.kind,segment,m)
            else:
                v=read(args.kind,segment);require(v['covariance_errors']==check(v,args.kind,segment,m),'retained comparison')
