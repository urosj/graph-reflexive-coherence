"""Eight bounded A_CI counterparts, with full joint and unsigned-history transport."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json
import lzma
import multiprocessing as mp
import os
import time
from unittest.mock import patch
import numpy as np

import p984h_aci_campaign as c
import p984h_cos_covariance as maps
from pygrc.models.grc_9_v4_expansion import aci_profile_template
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry, GRCV4Geometry, OneFormHodge

ROOT,BASE,HERE=c.ROOT,c.BASE,c.HERE
SELF,TEST=HERE+'p984h_aci_covariance.py',HERE+'test_p984h_aci_covariance.py'
INPUTS=BASE+'P9-8.4h-ACICovarianceInputs.json'
PLAN=BASE+'P9-8.4h-ACICovariancePlan.md'
KINDS,ROLES=maps.KINDS,c.ROLES
require,seal,digest=c.require,c.seal,c.digest
ATOL=RTOL=2e-13


def path(kind,segment):
    require(kind in KINDS and segment in ('event',*ROLES),'counterpart roster')
    return BASE+f'P9-8.4h-ACICovariance-{kind}-{segment}.json.xz'


def read(kind,segment):return json.loads(lzma.decompress((ROOT/path(kind,segment)).read_bytes()))


@lru_cache(maxsize=1)
def baseline():
    seed,source=c.baseline_source(); ev=c.read('event')
    require(ev==seal(ev) and ev['outcome']=='completed','baseline event')
    return seed.to_payload(),ev['execution']


@contextmanager
def transport():
    with patch.object(maps,'base',return_value=baseline()):yield


def input_image(original,g,d,old_event=None,new_event=None):
    ni,ei,sign=maps.mapping(original['reference']['graph'],g,d,old_event,new_event)
    value=deepcopy(original);ref=value['reference'];ref['graph']=g
    for owner,key in ((ref,'K4_base'),(value,'H1_form')):
        old=owner[key];owner[key]=[[old[i][j]*sign[k]*sign[l] if old[i][j] else 0.
            for l,j in enumerate(ei)] for k,i in enumerate(ei)]
    weights=ref['reference_hodge']['edge_weights']
    ref['reference_hodge']['edge_weights']={maps.rename(k,d,old_event,new_event):v for k,v in weights.items()}
    params=ref['profile']['params_resolved'];identity=ref['profile']['identity_payload']
    port=c.p.base.f.prepared.GRC9V4PortGraph.from_payload({k:g[k] for k in ('schema_version','live_node_ids','edges')})
    params['candidate']['descriptor_backend_id']=c.p.native.GRC9V4CandidateADifferentialReference(port).identity
    ident=maps.ordering.b.payload_identity
    params['geometry']['reference_hodge_digest']=ident('reference_hodge_identity_payload',ref['reference_hodge'])
    params['geometry']['K4_base_digest']=ident('k4_identity_payload',dict(schema_version='grcv4-k4-identity-v1',K4_base=ref['K4_base']))
    identity['params_hash']=ident('resolved_params',params)
    ref['profile']=maps.ordering.b.resolve_profile(params,identity).to_payload()
    reference=GRCV4ReferenceGeometry.from_payload(ref)
    before=c.p.GeometryStageInputs.from_payload(original)
    roles={r:c.p.GRCV4AuthoritativeState(tuple(original[r]['C'][i] for i in ni),
        tuple(original[r]['W_A'][i] for i in ei),None) for r in ROLES}
    require(all(original[r]['Z_4'] is None for r in ROLES),'unexpected carrier')
    return replace(before,geometry=GRCV4Geometry(reference,OneFormHodge(reference.graph,tuple(map(tuple,value['H1_form'])))),**roles)


@lru_cache(maxsize=8)
def subject(kind):
    require(kind in KINDS,'unknown transform'); old,ev=baseline()
    with transport():
        d=maps.declaration(kind)
        inp=input_image(old['inputs'],maps.graph_image(old['inputs']['reference']['graph'],d,source=True),d)
        seed=replace(c.state(old),inputs=inp); request=deepcopy(ev['request']); branches=d['chart']['branches']; shares=[0.]*3
        for i,x in enumerate(request['resource_distribution'],1):shares[branches[str(i)]-1]=x
        request.update(operation_id='p984h-aci-covariance-'+kind,source_node_id=maps.rename(request['source_node_id'],d),
            source_state_digest=seed.scientific_digest,source_graph_digest=inp.geometry.reference.graph.graph_digest,
            target_profile_template_id=aci_profile_template(inp.geometry.reference).profile_template_id,
            history_policy=c.p.aos_history_policy(inp.current,inp.reset),resource_distribution=shares,
            module_chirality=request['module_chirality']*d['chart']['chirality_factor'],
            growth_phase=branches[str(request['growth_phase'])])
        identity=deepcopy(ev['event_identity'])
        for key in identity:
            if key in request and key!='schema_version':identity[key]=request[key]
        for channel in ('candidate','carrier'):
            key=channel+'_history_policy_digest';identity[key]=request['history_policy'][key]
        eid=maps.ordering.b.payload_identity('expansion_event_identity_payload',identity)
        old_target=ev['checkpoint']['state']['inputs']
        graph=maps.graph_image(old_target['reference']['graph'],d,ev['event_id'],eid)
        target=replace(input_image(old_target,graph,d,ev['event_id'],eid),operation_id=request['operation_id'])
    plan=c.source.GRC9V4ExpansionPlan(inp.geometry.reference.graph.port_graph,seed.scientific_digest,
        c.source.GRC9V4ExpansionRequestInput.from_payload(request),c.source.GRC9ExpansionPolicy.from_payload(seed.specialization.resolved['expansion']))
    require(plan.event_id==eid and plan.event_identity_payload()==identity and plan.target_graph==target.geometry.reference.graph.port_graph,
        'independent transformed identity/allocator')
    return seed,request,identity,eid,target


def manifest():
    upstream=c.manifest();require(upstream==json.loads((ROOT/c.INPUTS).read_text()),'baseline manifest drift')
    paths=set(upstream['source_bindings'])|{c.INPUTS,SELF,TEST,PLAN,maps.SELF,maps.ordering.SELF,maps.chart.SELF,maps.chart.b.VECTORS,
        c.path('event'),*(c.path('step',r,1) for r in ROLES)}
    return seal(dict(schema='p984h-aci-covariance-inputs-v1',source_bindings={p:c.p.sha(p) for p in sorted(paths)},
        kinds=list(KINDS),event_cap_seconds=1200,step_cap_seconds=600,max_workers=8,threads_per_worker=1,
        atol=ATOL,rtol=RTOL,native_events=8,target_steps=16,source_rerun=False,transformed_horizon=1,
        backend='flint',numerical_policy='certified_arb_256_weighted_v1',
        independent_of_later_baseline_steps=True,baseline_completion_required_for_closeout=True,
        user_accepted=False,aggregate_closed=False))


def compare(actual,expected,label):
    a,b=np.asarray(actual),np.asarray(expected)
    require(a.shape==b.shape and np.isfinite(a).all() and np.isfinite(b).all()
        and np.allclose(a,b,atol=ATOL,rtol=RTOL),'covariance '+label)
    return float(np.max(abs(a-b))) if a.size else 0.


def indices(kind,original,new,target):
    with transport():
        return maps.mapping(original['reference']['graph'],new.to_payload()['reference']['graph'],maps.declaration(kind),
            baseline()[1]['event_id'] if target else None,subject(kind)[3] if target else None)


def root_pair(old,new,orders):
    ni,ei,sign=orders; errors={}
    require(old['joint']['recipe']==new['joint']['recipe'] and old['joint']['domain_id']==new['joint']['domain_id'],'recipe/domain covariance')
    for field in ('current','baseline','flux','flat'):
        errors[field]=compare(new['actual'][field],np.asarray(old['actual'][field])[ei]*sign,field)
    errors['potential']=compare(new['actual']['potential'],np.asarray(old['actual']['potential'])[ni],'node potential')
    errors['drive']=compare(new['actual']['drive'],np.asarray(old['actual']['drive'])[ei],'unsigned drive')
    for field in ('H','source','generated'):
        errors[field]=compare(new['joint'][field],np.asarray(old['joint'][field])[np.ix_(ei,ei)]*np.outer(sign,sign),field)
    return errors


def writer_pair(old,new,orders,kind):
    ni,ei,sign=orders; errors={}
    for key,order,mult in (('C',ni,1),('W_A',ei,1),('J',ei,sign),('drive',ei,1)):
        errors[key]=compare(new[key],np.asarray(old[key])[order]*mult,'writer '+key)
    if 'written_W_A' in old:errors['written_W_A']=compare(new['written_W_A'],np.asarray(old['written_W_A'])[ei],'written W')
    with transport():branches=maps.declaration(kind)['chart']['branches']
    columns=[next(i-1 for i in (1,2,3) if branches[str(i)]==j) for j in (1,2,3)]
    errors['descriptors']=compare(new['descriptors'],np.asarray(old['descriptors'])[np.ix_(ni,columns)],'writer descriptors')
    return errors


def step_inputs(kind,role):
    ev=read(kind,'event');require(ev==seal(ev) and ev['outcome']=='completed','counterpart event')
    target=c.state(ev['execution']['checkpoint']['state']).inputs
    return replace(target,current=getattr(target,role),dt=c.DT),ev['record_digest']


def execute(kind,segment,progress):
    seed,request,identity,eid,expected=subject(kind)
    if segment=='event':
        result=c.event_capture(seed,request,expected,progress); result['event_identity']=identity
        return result,c.read('event')['record_digest']
    before,predecessor=step_inputs(kind,segment)
    return c.observe(before),predecessor


def check(value,kind,segment,m):
    require(value==seal(value) and value['manifest_digest']==m['record_digest'] and value['outcome']=='completed'
        and (value['kind'],value['segment'])==(kind,segment) and value['user_accepted'] is False and value['aggregate_closed'] is False
        and 0<value['seconds']<=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds'],'counterpart identity/scope')
    seed,request,identity,eid,target=subject(kind); e=value['execution']; old=baseline()[1]; errors={}
    if segment=='event':
        require(e['request']==request and e['event_identity']==identity and e['event_id']==eid
            and value['predecessor_digest']==c.read('event')['record_digest'],'counterpart event lineage')
        require(c.p.canonical_input_payload(e['checkpoint']['state']['inputs'])==c.p.canonical_input_payload(target.to_payload())
            and e['native_events']==1 and e['native_steps']==0 and e['rollback_exact'] and e['stale_failure']
            and len(e['admissions'])==2 and len(e['writer_surfaces'])==4,'counterpart target/coverage')
        for i,before in enumerate((seed.inputs,target)):
            original=baseline()[0]['inputs'] if i==0 else old['checkpoint']['state']['inputs']
            orders=indices(kind,original,before,i==1)
            for j,role in enumerate(ROLES):
                actual=replace(before,current=getattr(before,role));r=e['admissions'][i][role]
                require(e['admissions'][i]['old_publication_live'],'publication ordering'); c.check_root(r,actual)
                errors[f'{i}/{role}/root']=root_pair(old['admissions'][i][role],r,orders)
                errors[f'{i}/{role}/writer']=writer_pair(old['writer_surfaces'][2*i+j],e['writer_surfaces'][2*i+j],orders,kind)
    else:
        before,predecessor=step_inputs(kind,segment)
        require(value['predecessor_digest']==predecessor,'counterpart step lineage')
        after=c.check_step(e,before); old_step=c.read('step',segment,1)['execution']
        original=c.state(old['checkpoint']['state']).inputs
        original=replace(original,current=getattr(original,segment),dt=c.DT)
        orders=indices(kind,original.to_payload(),before,True)
        for name in ('current','reset','final'):errors[name]=root_pair(old_step['roots'][name],e['roots'][name],orders)
        errors['writer']=writer_pair(old_step['writer'],e['writer'],orders,kind)
        errors['C']=compare(after.current.C,np.asarray(old_step['next_inputs']['current']['C'])[orders[0]],'poststate C')
        errors['W_A']=compare(after.current.W_A,np.asarray(old_step['next_inputs']['current']['W_A'])[orders[1]],'poststate W')
    return errors


def worker(pipe,kind,segment):
    try:
        with c.exact_backend(c.ExactBackend.FLINT),c.numerical_policy(c.NumericalPolicy.CERTIFIED_ARB_256),c.matrix_operation():
            result=execute(kind,segment,lambda s:pipe.send(('progress',s)))
        pipe.send(('result',result))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


def run_one(kind,segment,m):
    if (ROOT/path(kind,segment)).exists():
        value=read(kind,segment);require(value['covariance_errors']==check(value,kind,segment,m),'retained covariance');return
    cap=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds']
    context=mp.get_context('spawn');receive,send=context.Pipe(False)
    child=context.Process(target=worker,args=(send,kind,segment));start=time.monotonic();child.start();send.close();result=None
    try:
        while time.monotonic()-start<cap:
            if receive.poll(.25):
                try:key,val=receive.recv()
                except EOFError:break
                if key=='error':raise RuntimeError(str(val))
                if key=='result':result=val;break
                print(json.dumps(dict(kind=kind,segment=segment,stage=val,seconds=time.monotonic()-start)),flush=True)
            elif not child.is_alive():break
        child.join(timeout=max(0,min(3,cap-(time.monotonic()-start))));elapsed=time.monotonic()-start
        require(result is not None and child.exitcode==0 and elapsed<=cap,'counterpart incomplete/cap; no retry')
    finally:
        if child.is_alive():child.terminate();child.join(timeout=3)
        if child.is_alive():child.kill();child.join(timeout=3)
        receive.close()
    execution,predecessor=result
    value=seal(dict(schema='p984h-aci-covariance-segment-v1',manifest_digest=m['record_digest'],kind=kind,segment=segment,
        predecessor_digest=predecessor,execution=execution,seconds=elapsed,outcome='completed',user_accepted=False,aggregate_closed=False))
    value['covariance_errors']=check(value,kind,segment,m);value=seal(value)
    require(m==manifest(),'source changed during covariance')
    raw=lzma.compress(json.dumps(value,separators=(',',':'),allow_nan=False).encode()+b'\n')
    require(len(raw)<=2000000,'counterpart compressed budget')
    with (ROOT/path(kind,segment)).open('xb') as stream:stream.write(raw)
    print(json.dumps(dict(kind=kind,segment=segment,outcome='completed',seconds=elapsed,compressed_bytes=len(raw))),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--kind',choices=KINDS);args=parser.parse_args()
    m=manifest()
    if args.action=='prepare':
        with (ROOT/INPUTS).open('x') as stream:json.dump(m,stream,indent=2);stream.write('\n')
    else:
        require(m==json.loads((ROOT/INPUTS).read_text()),'covariance manifest drift')
        require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single-thread policy')
        for segment in ('event',*ROLES):
            if args.action=='run':run_one(args.kind,segment,m)
            else:
                value=read(args.kind,segment);require(value['covariance_errors']==check(value,args.kind,segment,m),'retained comparison')
