"""A_PC larger-event preparation and actual source beat; immutable predecessors."""
import argparse
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache, wraps
import hashlib
import json
import lzma
import multiprocessing as mp
import os
import subprocess
import time
from unittest.mock import patch

import p984g_apc_native as prior
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import apc_history_policy, GRC9V4ExpansionRequestInput, GRC9ExpansionPolicy, GRC9V4ExpansionPlan
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_pc import carrier_geometry
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, FrozenJSONMap
from pygrc.models.grc_v4_numerics import ExactBackend, NumericalPolicy, exact_backend, numerical_policy, matrix_operation
from p984h_aci import canonical_input_payload
from p984h_validation_reuse import validation_reuse, POLICY as VALIDATION_POLICY

ROOT,BASE,HERE=prior.ROOT,prior.BASE,prior.HERE
SELF=HERE+'p984h_apc.py';TEST=HERE+'test_p984h_apc.py'
PLAN=BASE+'P9-8.4h-APCPlan.md';INPUTS=BASE+'P9-8.4h-APCInputs.json'
RESULT=BASE+'P9-8.4h-APC-source.json.xz'
SUMMARY=BASE+'P9-8.4g-APCNativeResults.json'
REVISION='36d6cf0ff3f3d1d173b9cefe8155f9c488cb27e5'
SUMMARY_DIGEST='861800f83204b520e7f3c080fd72ff7060541bb19d7023eb6ed04f8744e6429a'
CAPS=dict(source=600,event=1200,target_step=600,final_read=600)
ROLES=('current','reset');DT=2**-12
p=prior.p;h=prior.h;d=p.feasible.mechanical
require,seal,digest,q=prior.require,prior.seal,prior.digest,prior.q


def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def in_policy(function):
    @wraps(function)
    def call(*args,**kwargs):
        with validation_reuse(),exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
            return function(*args,**kwargs)
    return call


@lru_cache(maxsize=256)
def historical_sha(name):
    return hashlib.sha256(subprocess.check_output(['git','show',REVISION+':'+name],cwd=ROOT)).hexdigest()


def accepted():
    subprocess.check_call(['git','merge-base','--is-ancestor',REVISION,'HEAD'],cwd=ROOT)
    require(sha(SUMMARY)==historical_sha(SUMMARY),'accepted summary bytes')
    v=json.loads((ROOT/SUMMARY).read_text())
    require(v==seal(v) and v['record_digest']==SUMMARY_DIGEST and v['native_prerequisites_complete'],'accepted summary')
    require(sha(h.RESULTS)==historical_sha(h.RESULTS),'accepted independent oracle bytes')
    oracle=h.load();require(oracle==seal(oracle) and oracle['record_digest']==v['hardening_digest'],'accepted independent oracle identity')
    row=next(x for x in v['cases'] if (x['graph'],x['role'])==('source','current'))
    require(sha(row['path'])==row['sha256']==historical_sha(row['path']),'source archive')
    source=json.loads(lzma.decompress((ROOT/row['path']).read_bytes()))
    require(source==seal(source) and source['record_digest']==row['record_digest'] and source['outcome']=='completed','source record')
    for name,expected in source['source_bindings'].items():require(historical_sha(name)==expected,'original source: '+name)
    return source,oracle


@lru_cache(maxsize=1)
@in_policy
def seed():
    _,oracle=accepted();before,backend=prior.inputs_for(oracle['subjects']['source'],'current')
    spec=p.prior.read(p.prior.PREPARED)['specialization']
    return native.GRC9V4APCState(before,native.GRC9V4Specialization(FrozenJSONMap(spec['resolved']),FrozenJSONMap(spec['identity_payload']))),backend


@in_policy
def poststate(initial,result):
    require(result['after_time']==initial.inputs.time+DT and result['after_step_index']==initial.inputs.step_index+1,
        'source chronology/reset')
    z=p.unpack(result['after_Z'])
    authority=GRCV4AuthoritativeState(tuple(result['after_C']),tuple(result['after_W_A']),tuple(x for row in z for x in row))
    after=replace(initial.inputs,current=authority,geometry=carrier_geometry(initial.inputs,authority),
        time=result['after_time'],step_index=result['after_step_index'],dt=0)
    require(after.time==initial.inputs.time+DT and after.step_index==initial.inputs.step_index+1
        and after.reset==initial.inputs.reset,'source chronology/reset')
    return replace(initial,inputs=after)


def request(post):
    value=deepcopy(p.prior.read(p.prior.PREPARED)['event_request'])
    value.update(operation_id='p984h-apc-base',source_state_digest=post.scientific_digest,
        resource_distribution=[.25,.375,.375],history_policy=apc_history_policy(post.inputs.current,post.inputs.reset))
    return value


def plan_for(post,req):
    return GRC9V4ExpansionPlan(post.inputs.geometry.reference.graph.port_graph,post.scientific_digest,
        GRC9V4ExpansionRequestInput.from_payload(req),GRC9ExpansionPolicy.from_payload(post.specialization.resolved['expansion']))


@lru_cache(maxsize=1)
@in_policy
def _preflight():
    old,oracle=accepted();initial,_=seed();post=poststate(initial,old['result']);req=request(post)
    for before in (initial.inputs,post.inputs):
        restored=GeometryStageInputs.from_payload(json.loads(json.dumps(before.to_payload())))
        require(canonical_input_payload(restored.to_payload())==canonical_input_payload(before.to_payload()),'full C/W/Z roundtrip')
    require(post.inputs.current!=post.inputs.reset and post.inputs.reset==initial.inputs.reset,'distinct reset')
    require(req['history_policy']!=apc_history_policy(initial.inputs.current,initial.inputs.reset),'fresh W/Z content binding')
    plan=plan_for(post,req)
    return dict(historical_source_digest=old['record_digest'],historical_oracle_digest=oracle['record_digest'],
        source_state_digest=post.scientific_digest,request_digest=digest(req),event_id=plan.event_id,
        source_nodes=len(plan.source_graph.live_node_ids),source_edges=len(plan.source_graph.edges),
        target_nodes=len(plan.target_graph.live_node_ids),target_edges=len(plan.target_graph.edges),
        full_C_W_Z_roundtrip=True,distinct_reset=True,fresh_history_binding=True,
        scope='historical_operand_rehearsal_not_current_execution_or_event_admission')


def preflight():
    # One immutable-operand rehearsal per process; manifest() still rehashes
    # every live input before and after execution. No numerical solve is cached.
    return deepcopy(_preflight())


def manifest():
    old,_=accepted();paths=set(old['source_bindings'])|{SELF,TEST,PLAN,SUMMARY,h.RESULTS,
        HERE+'p984h_aci.py',HERE+'p984g_apc_native_targets.py',HERE+'p984h_validation_reuse.py',HERE+'test_p984h_validation_reuse.py'}
    paths.update(str(x.relative_to(ROOT)) for x in (ROOT/'src/pygrc/models').glob('*grc*v4*.py'))
    return seal(dict(schema='p984h-apc-inputs-v1',family='A_PC',source_bindings={n:sha(n) for n in sorted(paths)},
        historical_revision=REVISION,changed_since_prerequisite=sorted(n for n,v in old['source_bindings'].items() if sha(n)!=v),
        caps=CAPS,exact_backend='flint',numerical_policy='certified_arb_256_weighted_v1',validation_memo=VALIDATION_POLICY,
        planned=dict(source_steps=1,events=9,target_steps=36,final_reads=2),compressed_budget_bytes=25000000,
        preflight=preflight(),user_accepted=False,aggregate_closed=False))


def execute_source(progress):
    old,oracle=accepted()
    # Only the historical oracle's source authentication is adapted. Current
    # native PC reads, writers, admission and all result comparisons execute.
    with patch.object(h,'check_retained',return_value=oracle):result=prior.execute('source','current',progress)
    require(result==old['result'],'whole source parity differs from accepted prerequisite')
    initial,_=seed();post=poststate(initial,result);req=request(post);plan=plan_for(post,req)
    declaration=deepcopy(p.prior.read(p.prior.PREPARED));declaration['source']=oracle['subjects']['source']
    with p.ctx.workprec(p.BITS):trigger=p.prior.scalar.trigger(declaration,list(map(p.a,result['after_C'])),list(map(p.a,result['after_W_A'])))
    require(trigger['small_gradient'] and q(trigger['minimum_signed_hessian_upper'])<0,'postbeat trigger prerequisites')
    return dict(result=result,state=post.to_payload(),request=req,event_identity=plan.event_identity_payload(),
        event_id=plan.event_id,trigger=trigger,historical_source_digest=old['record_digest'],
        native_steps=1,native_reads=3,native_events=0)


def worker(pipe):
    try:
        with validation_reuse(),exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
            result=execute_source(lambda s:pipe.send(('progress',s)))
        pipe.send(('result',result))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


def capped(target,args,cap):
    require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single-thread policy')
    context=mp.get_context('spawn');receive,send=context.Pipe(False)
    child=context.Process(target=target,args=(send,*args));start=time.monotonic();child.start();send.close();result=None
    try:
        while time.monotonic()-start<cap:
            if receive.poll(.25):
                try:kind,value=receive.recv()
                except EOFError:break
                if kind=='progress':print(json.dumps(dict(stage=value,seconds=time.monotonic()-start)),flush=True)
                elif kind=='error':raise RuntimeError(str(value))
                elif kind=='result':result=value;break
            elif not child.is_alive():break
        child.join(timeout=max(0,min(3,cap-(time.monotonic()-start))));seconds=time.monotonic()-start
        require(result is not None and child.exitcode==0 and seconds<=cap,'incomplete/capped execution; no fallback')
    finally:
        if child.is_alive():child.terminate();child.join(timeout=3)
        if child.is_alive():child.kill();child.join(timeout=3)
        receive.close()
    return result,seconds


def save(name,value):
    raw=lzma.compress(json.dumps(value,separators=(',',':'),allow_nan=False).encode()+b'\n')
    used=sum(x.stat().st_size for x in (ROOT/BASE).glob('P9-8.4h-APC*.json.xz'))
    require(len(raw)<2000000 and used+len(raw)<=25000000,'compressed evidence budget')
    with (ROOT/name).open('xb') as stream:stream.write(raw)
    print(json.dumps(dict(path=name,seconds=value.get('seconds'),compressed_bytes=len(raw))),flush=True)


def check_source(value=None):
    m=manifest();require(m==json.loads((ROOT/INPUTS).read_text()),'source manifest drift')
    value=json.loads(lzma.decompress((ROOT/RESULT).read_bytes())) if value is None else value
    require(value==seal(value) and value['manifest_digest']==m['record_digest'] and value['outcome']=='completed'
        and 0<value['seconds']<=CAPS['source'] and value['user_accepted'] is False and value['aggregate_closed'] is False,'source identity/scope')
    e=value['execution'];old,oracle=accepted();require(e['result']==old['result'] and e['historical_source_digest']==old['record_digest'],'source full parity')
    initial,_=seed();post=poststate(initial,e['result']);req=request(post);plan=plan_for(post,req)
    require(e['state']==post.to_payload() and e['request']==req and e['event_identity']==plan.event_identity_payload()
        and e['event_id']==plan.event_id and (e['native_steps'],e['native_reads'],e['native_events'])==(1,3,0),'source operands/credit')
    require(e['trigger']['small_gradient'] and q(e['trigger']['minimum_signed_hessian_upper'])<0,'trigger declaration')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run','check'));args=parser.parse_args()
    if args.action=='prepare':
        with (ROOT/INPUTS).open('x') as stream:json.dump(manifest(),stream,indent=2);stream.write('\n')
    elif args.action=='run':
        require(not (ROOT/RESULT).exists(),'no overwrite');m=manifest();require(m==json.loads((ROOT/INPUTS).read_text()),'manifest drift')
        result,seconds=capped(worker,(),CAPS['source']);require(m==manifest(),'sources changed during execution')
        v=seal(dict(schema='p984h-apc-source-v1',manifest_digest=m['record_digest'],execution=result,seconds=seconds,
            outcome='completed',user_accepted=False,aggregate_closed=False));check_source(v);save(RESULT,v)
    else:check_source();print('source retained check passes; no native rerun')
