"""Eight larger C_PC counterparts, with signed complete carrier transport."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json
import time
from unittest.mock import patch
import numpy as np
import p984h_cpc as n
import p984h_cos_covariance as maps
import p9_cpc_large_runner as optimized
import p9_cpc_covariance_compute as compute
from p9_cpc_covariance_compute import wire_reuse
from pygrc.models.grc_9_v4_expansion import cpc_profile_template
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry,GRCV4Geometry,OneFormHodge

b=n.b
SELF=b.HERE+'p984h_cpc_covariance.py'
INPUTS=b.BASE+'P9-8.4h-CPCCovarianceInputs.json'
KINDS,ROLES=maps.KINDS,n.ROLES

def path(kind,segment):
    b.require(kind in KINDS and segment in ('event',*ROLES),'counterpart roster')
    return b.BASE+f'P9-8.4h-CPCCovariance-{kind}-{segment}.json.xz'

def read(kind,segment):return n.g.storage.read(path(kind,segment))

@lru_cache(maxsize=1)
def baseline_source():
    # Immutable, source-bound data construction; no native read or admission.
    return n.source_state()[0]

@lru_cache(maxsize=1)
def baseline():
    event=n.read('event');b.check_digest(event)
    return baseline_source().to_payload(),event['execution']

@contextmanager
def transport():
    with patch.object(maps,'base',return_value=baseline()):yield

def conjugate(matrix,ei,sign):
    return [[matrix[i][j]*sign[k]*sign[l] if matrix[i][j] else 0.
        for l,j in enumerate(ei)] for k,i in enumerate(ei)]


def input_image(original,graph,d,old_event=None,new_event=None,*,before=None):
    ni,ei,sign=maps.mapping(original['reference']['graph'],graph,d,old_event,new_event)
    value=deepcopy(original);ref=value['reference'];ref['graph']=graph
    for owner,key in ((ref,'K4_base'),(value,'H1_form')):owner[key]=conjugate(owner[key],ei,sign)
    weights=ref['reference_hodge']['edge_weights']
    ref['reference_hodge']['edge_weights']={maps.rename(k,d,old_event,new_event):v for k,v in weights.items()}
    params=ref['profile']['params_resolved'];identity=ref['profile']['identity_payload'];ident=maps.ordering.b.payload_identity
    weights=params['candidate']['W_C_tr']
    params['candidate']['W_C_tr']={maps.rename(k,d,old_event,new_event):v for k,v in weights.items()}
    params['candidate']['W_C_tr_content_digest']=ident('wctr_identity_payload',dict(schema_version='grcv4-wctr-identity-v1',W_C_tr=params['candidate']['W_C_tr']))
    params['geometry']['reference_hodge_digest']=ident('reference_hodge_identity_payload',ref['reference_hodge'])
    params['geometry']['K4_base_digest']=ident('k4_identity_payload',dict(schema_version='grcv4-k4-identity-v1',K4_base=ref['K4_base']))
    identity['params_hash']=ident('resolved_params',params);ref['profile']=maps.ordering.b.resolve_profile(params,identity).to_payload()
    reference=GRCV4ReferenceGeometry.from_payload(ref)
    size=len(ei);roles={}
    for role in ROLES:
        old=original[role];Z=[old['Z_4'][i*size:(i+1)*size] for i in range(size)]
        roles[role]=b.GRCV4AuthoritativeState(tuple(old['C'][i] for i in ni),None,
            tuple(x for row in conjugate(Z,ei,sign) for x in row))
    geometry=GRCV4Geometry(reference,OneFormHodge(reference.graph,tuple(map(tuple,value['H1_form']))))
    if before is not None:return replace(before,geometry=geometry,**roles)
    # The baseline is an authenticated retained event. Construct the transformed
    # subject directly, instead of rebuilding its discarded original geometry.
    # Typed constructors still validate the new reference, Hodge and full state;
    # actual native admission and independent target comparison run afterwards.
    b.require(original['context']==reference.context.to_payload() and original['trial_current'] is None,
        'transformed context/trial scope')
    fields={key:original[key] for key in ('operation_id','Q_target','receipt_ids','step_index',
        'time','dt','stage','evaluation_index')}
    return b.GeometryStageInputs(geometry=geometry,context=reference.context,**roles,**fields,trial_current=None)


@lru_cache(maxsize=8)
def subject(kind):
    old,event=baseline()
    with transport():
        d=maps.declaration(kind)
        original=baseline_source()
        incoming=input_image(old['inputs'],maps.graph_image(old['inputs']['reference']['graph'],d,source=True),d,before=original.inputs)
        seed=replace(original,inputs=incoming)
        case=deepcopy(event['case']);request=case['request'];branches=d['chart']['branches'];shares=[0.]*3
        for i,x in enumerate(request['resource_distribution'],1):shares[branches[str(i)]-1]=x
        request.update(operation_id='p984h-cpc-covariance-'+kind,source_node_id=maps.rename(request['source_node_id'],d),
            source_state_digest=seed.scientific_digest,source_graph_digest=incoming.geometry.reference.graph.graph_digest,
            target_profile_template_id=cpc_profile_template(incoming.geometry.reference).profile_template_id,
            history_policy=n.cpc_history_policy(incoming.current,incoming.reset),resource_distribution=shares,
            module_chirality=request['module_chirality']*d['chart']['chirality_factor'],growth_phase=branches[str(request['growth_phase'])])
        identity=case['oracle']['event_identity']
        for key in identity:
            if key in request and key!='schema_version':identity[key]=request[key]
        for channel in ('candidate','carrier'):
            key=channel+'_history_policy_digest';identity[key]=request['history_policy'][key]
        eid=b.payload_identity('expansion_event_identity_payload',identity)
        original=event['state']['inputs'];old_event=event['case']['oracle']['event_id']
        graph=maps.graph_image(original['reference']['graph'],d,old_event,eid)
        target=replace(input_image(original,graph,d,old_event,eid),operation_id=request['operation_id'])
        case['oracle']=dict(event_identity=identity,event_id=eid,target_graph=graph)
    plan=n.GRC9V4ExpansionPlan(incoming.geometry.reference.graph.port_graph,seed.scientific_digest,
        n.GRC9V4ExpansionRequestInput.from_payload(request),n.GRC9ExpansionPolicy.from_payload(seed.specialization.resolved['expansion']))
    b.require(plan.event_id==eid and plan.target_graph==target.geometry.reference.graph.port_graph,'independent transformed allocator')
    return seed,case,target


def manifest():
    upstream=n.g.storage.read(n.INPUTS);n.check_manifest(upstream)
    paths={x['path'] for x in upstream['source_bindings']}|{SELF,n.INPUTS,maps.SELF,maps.ordering.SELF,maps.chart.SELF,
        n.filename('event'),*(n.filename('step',r,1) for r in ROLES)}
    paths|={ref['path'] for ref in compute.bindings()}
    return b.seal(dict(schema='p984h-cpc-covariance-inputs-v1',source_bindings=b.bind(paths),kinds=list(KINDS),
        event_cap_seconds=1800,step_cap_seconds=1800,preparation_cap_seconds=600,
        preparation='immutable_transport_before_native_event_worker',threads_per_worker=1,atol=2e-13,rtol=2e-13,
        serialization_capacity=compute.LIMITS,
        native_events=8,target_steps=16,source_rerun=False,transformed_horizon=1,user_accepted=False,aggregate_closed=False))


def indices(kind,old,new,target=True):
    with transport():
        return maps.mapping(old['reference']['graph'],new['reference']['graph'],maps.declaration(kind),
            baseline()[1]['case']['oracle']['event_id'] if target else None,
            subject(kind)[1]['oracle']['event_id'] if target else None)


def compare(actual,expected,label):
    return b.comparison(actual,expected,dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13),label)['maximum_error']


def point_pair(old,new,orders):
    _,ei,sign=orders
    errors={name:compare(new[name],np.asarray(old[name])[ei]*sign,name)
            for name in ('current','read_current','baseline','readback','flat')}
    errors.update({name:compare(new[name],conjugate(old[name],ei,sign),name) for name in ('H','source')})
    return errors


def check(value,kind,segment,m):
    b.check_digest(value);b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(value['manifest_digest']==m['record_digest'] and (value['kind'],value['segment'])==(kind,segment)
        and value['outcome']=='completed' and not value['user_accepted'] and not value['aggregate_closed']
        and value['serialization_reuse']['hits']>0 and value['serialization_reuse']['retained_bytes']==0
        and value['serialization_reuse']['max_entries']==m['serialization_capacity']['MAX_ENTRIES']
        and value['serialization_reuse']['total_byte_budget']==m['serialization_capacity']['TOTAL_BYTES']
        and 0<=value['preparation_seconds']<=m['preparation_cap_seconds']
        and 0<value['seconds']<=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds'],'counterpart scope')
    seed,case,target=subject(kind);e=value['execution'];old=baseline()[1];errors={}
    if segment=='event':
        b.require(e['case']==case and e['state']['inputs']==target.to_payload() and e['rollback_exact'] and e['stale_failure']
            and value['predecessor_digest']==n.read('event')['record_digest'],'event lineage/transport')
        n.check_event(seed,case,e['event'])
        for i,incoming in enumerate((seed.inputs,target)):
            original=baseline()[0]['inputs'] if i==0 else old['state']['inputs']
            orders=indices(kind,original,incoming.to_payload(),i==1)
            for key in ('read','reset_read'):
                errors[str(i)+'/'+key]=point_pair(old['event']['admission_reads'][i][key],e['event']['admission_reads'][i][key],orders)
    else:
        event=read(kind,'event');b.check_digest(event)
        before=n.r.role_input(n.r.state(event['execution']['state']).inputs,segment,dt=n.DT)
        b.require(e['before']==before.to_payload() and value['predecessor_digest']==event['record_digest'],'counterpart incoming state')
        n.check_step(e)
        prior=n.read('step',segment,1)['execution'];orders=indices(kind,prior['before'],e['before'])
        for name in ('read','reset_read','restart'):errors[name]=point_pair(prior[name],e[name],orders)
        ni,ei,sign=orders;size=len(ei)
        for role in ROLES:
            errors[role+'/C']=compare(e['after'][role]['C'],np.asarray(prior['after'][role]['C'])[ni],'written resources')
            oldz=np.asarray(prior['after'][role]['Z_4']).reshape(size,size)
            errors[role+'/Z']=compare(np.asarray(e['after'][role]['Z_4']).reshape(size,size),oldz[np.ix_(ei,ei)]*np.outer(sign,sign),'written whole carrier')
            b.require(e['after'][role]['W_A'] is None,'invented candidate history')
    return errors


def child(pipe,kind,segment,prepared=None):
    try:
        with wire_reuse() as stats,n.compute_worker():
            pipe.send(('progress',kind+'/'+segment+' verified FLINT/Arb/cache policy'))
            if segment=='event':
                seed_payload,case,predecessor=prepared
                execution=n.event(n.r.state(seed_payload),case)
            else:
                event=read(kind,'event');b.check_digest(event)
                before=n.r.role_input(n.r.state(event['execution']['state']).inputs,segment,dt=n.DT)
                execution,_=n.observe_step(before);predecessor=event['record_digest']
        pipe.send(('result',(execution,predecessor,stats)))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


def run(kind):
    m=n.g.storage.read(INPUTS);b.check_digest(m);b.check_bindings(m['source_bindings'])
    start=time.monotonic()
    with b.budget(m['preparation_cap_seconds']),wire_reuse(),n.compute_worker():
        seed,case,_=subject(kind)
        prepared=(seed.to_payload(),case,n.read('event')['record_digest'])
    preparation_seconds=time.monotonic()-start
    print(json.dumps(dict(kind=kind,preparation_seconds=preparation_seconds,native_execution_started=False)),flush=True)
    for segment in ('event',*ROLES):
        if (b.ROOT/path(kind,segment)).exists():
            with n.compute_worker():
                value=read(kind,segment);b.require(value['covariance_errors']==check(value,kind,segment,m),'saved counterpart drift')
            continue
        cap=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds']
        (execution,predecessor,stats),seconds=n.process_budget.capped(child,(kind,segment,prepared if segment=='event' else None),cap)
        value=b.seal(dict(schema='p984h-cpc-covariance-segment-v1',manifest_digest=m['record_digest'],kind=kind,segment=segment,
            execution=execution,predecessor_digest=predecessor,serialization_reuse=stats,preparation_seconds=preparation_seconds,
            seconds=seconds,outcome='completed',user_accepted=False,aggregate_closed=False))
        with n.compute_worker():errors=check(value,kind,segment,m)
        value=b.seal(dict(value,covariance_errors=errors));b.check_bindings(m['source_bindings'])
        n.g.storage.save(path(kind,segment),value)
        print(json.dumps(dict(kind=kind,segment=segment,seconds=seconds)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run'))
    parser.add_argument('--kind',choices=KINDS);args=parser.parse_args()
    with wire_reuse(),n.compute_worker():
        if args.action=='prepare':n.g.storage.save(INPUTS,manifest())
        else:run(args.kind)

