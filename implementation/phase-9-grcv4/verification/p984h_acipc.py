"""Large native A_CI_PC segments with independent saved-operand verification."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import json
import lzma
import tempfile
import time
from unittest.mock import patch

import p984g_acipc_companion as companion
from p9_acipc_targets import target as independent_target
import p984h_apc as process_budget
from p9_acipc_compute import worker as compute_worker
from p9_ccipc_capture import portable
import p984h_acipc_math as math_check
import p984d_acipc as storage
import p984b_acipc_runtime as r
import p9_acipc_compute as compute
check_bindings = r.b.check_bindings
from pygrc.models import grc_v4_linear as linear
from pygrc.models.grc_9_v4_expansion import (
    GRC9V4ExpansionPlan,GRC9ExpansionPolicy,GRC9V4ExpansionRequestInput,apc_history_policy,
)

g=companion.g
b=g.b
q,a,lo,hi=g.q,g.a,g.lo,g.hi
native=r.native
SELF=b.HERE+"p984h_acipc.py"
INPUTS=b.BASE+"P9-8.4h-ACIPCInputs.json"
ROLES=g.ROLES
DT=2**-12
LIMITS = math_check.LIMITS
subject = math_check.subject
capture_read = math_check.capture_read
check_read = math_check.check_read



def filename(segment,role="current",index=1):
    b.require(segment in ("source","prepared_target","event","step","final") and role in ROLES and 1<=index<=10,"segment roster")
    suffix=segment if segment=="event" else segment+"-"+role+("-"+str(index) if segment=="step" else "")
    return b.BASE+"P9-8.4h-ACIPC-"+suffix+".json.xz"


def read(segment,role="current",index=1):
    return storage.read(filename(segment,role,index))


def manifest():
    preflight=storage.read(compute.PREFLIGHT)
    b.check_digest(preflight);b.check_bindings(preflight['source_bindings'])
    b.require(preflight['outcome']=='passed' and preflight['small_root_byte_parity'], 'compute preflight required')
    prior=storage.read(companion.INPUTS)
    result=storage.read(companion.RESULTS)
    b.check_digest(prior);b.check_digest(result);b.check_bindings(prior["source_bindings"])
    b.require(result["manifest_digest"]==prior["record_digest"] and result["ready_for_native"],"large scientific prerequisite")
    paths=storage.numerical_paths() | {SELF,companion.SELF,companion.INPUTS,companion.RESULTS,b.HERE+"p9_acipc_targets.py",
        g.SELF,g.ci.SELF,g.staged.SELF,g.pc.SELF,process_budget.SELF,math_check.SELF,
        b.HERE+'test_p9_acipc_science.py',compute.PREFLIGHT,
        b.HERE+'p9_ccipc_capture.py'}
    paths |= {ref['path'] for ref in prior['source_bindings']}
    return b.seal(dict(schema="p984h-acipc-inputs-v1",family="A_CI_PC",source_bindings=b.bind(paths),
        prerequisite_digest=result["record_digest"],limits=LIMITS,
        caps=dict(step=3600,event=3600,final=3600),
        scope=dict(source_steps=2,prepared_target_steps=2,events=1,target_steps=20,final_reads=2),
        numerical_policy="certified_arb_256",independent_precision_bits=g.BITS,
        user_accepted=False,aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m);check_bindings(m["source_bindings"])
    prior=storage.read(companion.RESULTS);b.check_digest(prior)
    b.require(m["prerequisite_digest"]==prior["record_digest"] and m["limits"]==LIMITS
        and m["caps"]==dict(step=3600,event=3600,final=3600)
        and not m["user_accepted"] and not m["aggregate_closed"],"large declaration drift")


def prepared(which):
    declaration=storage.read(companion.INPUTS)["adjusted"]
    subject=declaration[which]
    p=companion.mechanical
    graph=p.GRC9V4PortGraph.from_envelope(subject["graph"])
    profile=p.GRCV4Profile.from_canonical_bytes(p.canonical_json_bytes(subject["profile"]))
    spec=declaration["specialization"]
    specialization=native.GRC9V4Specialization(b.FrozenJSONMap(spec["resolved"]),b.FrozenJSONMap(spec["identity_payload"]))
    roles={role:p.authority(value,len(graph.edges)) for role,value in subject["roles"].items()}
    return p.make_state(graph,profile,specialization,roles,"A_CI_PC")



@contextmanager
def measure_reuse():
    stats=dict(solve_lookups=0,solve_hits=0,fact_lookups=0,fact_hits=0)
    solve,fact=linear._MatrixFacts.find_solve,linear._MatrixFacts.find
    def find_solve(self,*args,**kwargs):
        value=solve(self,*args,**kwargs)
        stats["solve_lookups"]+=1;stats["solve_hits"]+=int(value is not None)
        return value
    def find_fact(self,*args,**kwargs):
        value=fact(self,*args,**kwargs)
        stats["fact_lookups"]+=1;stats["fact_hits"]+=int(value is not None)
        return value
    with patch.object(linear._MatrixFacts,"find_solve",find_solve),patch.object(linear._MatrixFacts,"find",find_fact):
        yield stats


def retained_read(root):
    # Successful segment records already retain the whole read. Avoid a second
    # private archive per root and cross-worker diagnostic-write contention.
    return capture_read(root)


@contextmanager
def observation():
    with patch.object(r,'certified_read',retained_read),patch.object(r,'check_read',check_read), \
            patch.object(r,'step_errors',step_errors),patch.object(r,'writer_certificate',writer_certificate):
        yield


def writer_certificate(before,value):
    after=b.GeometryStageInputs.from_payload(value['poststate'])
    with g.ctx.workprec(g.BITS):
        md=g.model(subject(before),'current')
        c=list(map(a,after.current.C));w=list(map(a,before.current.W_A));j=list(map(a,value['read']['J']))
        desc=g.staged.feasible.descriptors(subject(before),c,w)
        drive=g.pc.floored_drive(md['p'],md['ends'],c,desc,j)
        error=max(hi(abs(a(x)-y)) for x,y in zip(value['writer_targets'][0]['target'],drive,strict=True))
    return dict(input_identity=before.identity,read_digest=value['read']['record_digest'],poststate_identity=after.identity,
        targets_digest=b.digest(value['writer_targets']),error=str(error))


def step_errors(before,read,after):
    pointwise=math_check.output_certificate(before,read,after)
    return {key+'_error':pointwise['errors'][name] for key,name in
            (('resource','resource'),('history','history'),('carrier','carrier'))}


def observe_step(before):
    start=time.monotonic()
    pointwise=[]
    def observed_errors(incoming,read,after):
        cert=math_check.output_certificate(incoming,read,after)
        pointwise.append(cert)
        return {key+'_error':cert['errors'][key] for key in ('resource','history','carrier')}
    with measure_reuse() as reuse,observation(),patch.object(r,'step_errors',observed_errors):
        step,value=r.perform_step(before)
    b.require(reuse['solve_hits']>0 and reuse['fact_hits']>0,'actual native matrix reuse absent')
    value=portable(dict(value,before=before.to_payload(),after=step.next_inputs.to_payload(),
        native_and_certificate_seconds=time.monotonic()-start,cache_observations=reuse))
    b.require(len(pointwise)==1,'one independent update certificate per executed step')
    value['pointwise_certificate']=pointwise[0]
    check_step(value)
    return value,step.next_inputs


def check_step(value,*,numerics=False):
    before=b.GeometryStageInputs.from_payload(value['before'])
    with observation():after=r.check_step(before,value,numerics=numerics)
    b.require(value['after']==value['poststate']==after.to_payload(),'poststate identity')
    cert=value['pointwise_certificate']
    b.require(cert['before_identity']==before.identity and cert['after_identity']==after.identity
        and cert['read_digest']==value['read']['record_digest'] and cert['pointwise_at_saved_input']
        and not cert['uniform_trajectory_enclosure'] and q(cert['resource_lower'])>=0,'pointwise input/positivity')
    b.require(value['errors']=={key+'_error':cert['errors'][name] for key,name in
        (('resource','resource'),('history','history'),('carrier','carrier'))},'update error consistency')
    if numerics:b.require(cert==math_check.output_certificate(before,value['read'],after),'pointwise equation drift')
    return after


def source_state():
    record=read("source");b.check_digest(record)
    return r.state(record["execution"]["state"]),record


def case_for(seed):
    declaration=storage.read(companion.INPUTS)["adjusted"]
    request=dict(declaration["event_request"],operation_id="p984h-acipc-base",source_state_digest=seed.scientific_digest,
        history_policy=apc_history_policy(seed.inputs.current,seed.inputs.reset))
    plan=GRC9V4ExpansionPlan(seed.inputs.geometry.reference.graph.port_graph,seed.scientific_digest,
        GRC9V4ExpansionRequestInput.from_payload(request),GRC9ExpansionPolicy.from_payload(seed.specialization.resolved["expansion"]))
    graph=deepcopy(declaration["target"]["graph"])
    old=declaration["event_id"]
    rename=lambda x:plan.event_id+x[len(old):] if isinstance(x,str) and x.startswith(old+"/") else x
    graph["live_node_ids"]=[rename(x) for x in graph["live_node_ids"]]
    for edge in graph["edges"]:
        edge["edge_id"]=rename(edge["edge_id"])
        for end in ("tail","head"):edge[end]["node_id"]=rename(edge[end]["node_id"])
    graph={k:graph[k] for k in ("schema_version","live_node_ids","edges")}
    b.require(graph==plan.target_graph.to_payload(),"independently retained larger graph allocation")
    return dict(request=request,oracle=dict(event_id=plan.event_id,event_identity=plan.event_identity_payload(),target_graph=graph))


def check_event(seed,case,value,*,numerics=False):
    with patch.object(r,'independent_target',independent_target),patch.object(r,'check_read',check_read):
        target=r.check_event(seed,case,value,numerics=False)
    # The frozen event consumer checks W-stage identities. Independently check
    # every admitted writer surface on the actual parameterized large subject.
    for index,parent in enumerate((seed,target)):
        for ri,role in enumerate(ROLES):
            surface=value['writer_surfaces'][2*index+ri]
            before=r.role_input(parent.inputs,role)
            with g.ctx.workprec(g.BITS):
                md=g.model(subject(before),'current')
                drive=g.pc.floored_drive(md['p'],md['ends'],list(map(a,md['c'])),
                    [[a(x) for x in row] for row in md['desc']],list(map(a,surface['J'])))
                b.require(max(hi(abs(a(x)-y)) for x,y in zip(surface['target'],drive,strict=True))<q(r.LIMITS['history_error']),
                          'event W admission surface error')
    if numerics:
        for parent,pair in zip((seed,target),value['admission_reads'],strict=True):
            check_read(parent.inputs,pair['read'],numerics=True)
            check_read(r.role_input(parent.inputs,'reset'),pair['reset_read'],numerics=True)
    return target


def event(seed,case):
    owner=native.GRC9V4ACIPCOperation(seed)
    before=owner.checkpoint();pointer=owner._published
    stale=dict(case["request"],source_state_digest="grcv4-state-sha256:"+"0"*64)
    rejection=owner.expand(GRC9V4ExpansionRequestInput.from_payload(stale))
    b.require(not rejection.committed and owner.checkpoint()==before and owner._published is pointer,"stale event rollback")
    # Observe actual native reads; the independent large adapter replaces only
    # the small-fixture observer, never a numerical producer or admission rule.
    with patch.object(r,"certified_read",retained_read):
        owner,outcome,value=r.event_capture(seed,GRC9V4ExpansionRequestInput.from_payload(case["request"]))
    b.require(outcome.committed,"native large A_CI_PC event rejected: "+str(outcome.failure))
    check_event(seed,case,value)
    return dict(case=case,event=value,state=owner.state.to_payload(),checkpoint=value["checkpoint"],
        stale_failure=rejection.failure.to_payload(),rollback_exact=True,native_events=1,native_steps=0)


def execute(segment,role,index):
    if segment in ("source","prepared_target"):
        seed=prepared("source" if segment=="source" else "target")
        before=r.role_input(seed.inputs,role,dt=DT)
        value,after=observe_step(before)
        value["state"]=replace(seed,inputs=replace(after,dt=0)).to_payload()
        if segment=="source":
            with g.ctx.workprec(g.BITS):
                value["trigger"]=companion.leading.trigger(storage.read(companion.INPUTS)["adjusted"],list(map(a,after.current.C)),list(map(a,after.current.W_A)))
            b.require(value["trigger"]["small_gradient"] and value["trigger"]["strict_hessian_condition"],"actual postbeat trigger")
        return value
    if segment=="event":
        seed,prior=source_state()
        return dict(event(seed,case_for(seed)),source_record_digest=prior["record_digest"])
    parent=read("event");b.check_digest(parent)
    if segment=="step" and index==1:
        before=r.role_input(r.state(parent["execution"]["state"]).inputs,role,dt=DT)
        predecessor=parent["record_digest"]
    else:
        prior=read("step",role,10 if segment=="final" else index-1);b.check_digest(prior)
        before=b.GeometryStageInputs.from_payload(prior["execution"]["after"])
        predecessor=prior["record_digest"]
    if segment=="step":value,_=observe_step(before)
    else:
        before=replace(before,dt=0)
        value=dict(before=before.to_payload(),read=retained_read(r.CandidateCIRoot(before,r.backend(before))),read_only=True)
    return dict(value,event_record_digest=parent["record_digest"],predecessor_digest=predecessor)


def child(pipe,segment,role,index):
    try:
        root_times=[]
        original=r.CandidateCIRoot.__post_init__
        def measured(root):
            started=time.monotonic()
            pipe.send(('progress','native joint root started'))
            original(root)
            root_times.append(dict(seconds=time.monotonic()-started,evaluations=root.evaluations))
            pipe.send(('progress','native joint root completed '+str(len(root_times))))
        with compute_worker() as policy,patch.object(r.CandidateCIRoot,'__post_init__',measured):
            pipe.send(("progress",segment+"/"+role+"/"+str(index)+" verified FLINT/Arb/cache policy"))
            value=execute(segment,role,index)
        b.require(policy['serialization_reuse']['hits'] > 0, 'canonical reuse absent')
        pipe.send(("result",portable(dict(execution=value,compute_policy=policy,native_root_timings=root_times))))
    except Exception as exc:
        pipe.send(("error",dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


def run(segment,role,index):
    m=storage.read(INPUTS);check_manifest(m)
    name=filename(segment,role,index)
    b.require(not (b.ROOT/name).exists(),"refuse overwrite")
    cap=m["caps"]["event" if segment=="event" else "final" if segment=="final" else "step"]
    started = time.monotonic()
    try:
        value,seconds=process_budget.capped(child,(segment,role,index),cap)
    except Exception as exc:
        failure=b.seal(dict(schema='p984h-acipc-incomplete-v1',manifest_digest=m['record_digest'],
            segment=segment,role=role,index=index,cap_seconds=cap,elapsed_seconds=time.monotonic()-started,
            error=dict(type=type(exc).__name__,message=str(exc)),outcome='incomplete',campaign_credit=False))
        storage.save(name.replace('.json.xz','-incomplete-'+str(time.time_ns())+'.json.xz'),failure)
        raise
    check_manifest(m)
    record=b.seal(dict(schema="p984h-acipc-segment-v1",manifest_digest=m["record_digest"],segment=segment,
        role=role,index=index,**value,elapsed_seconds=seconds,outcome="completed",user_accepted=False,aggregate_closed=False))
    storage.save(name,record)
    print(json.dumps(dict(segment=segment,role=role,index=index,seconds=seconds,
        cache=value["execution"].get("cache_observations"))),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","run"))
    parser.add_argument("--segment",choices=("source","prepared_target","event","step","final"),default="source")
    parser.add_argument("--role",choices=ROLES,default="current")
    parser.add_argument("--index",type=int,default=1)
    args=parser.parse_args()
    if args.action=="prepare":storage.save(INPUTS,manifest())
    else:run(args.segment,args.role,args.index)
