"""Large native C_CI_PC segments with independent saved-operand verification."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import json
import lzma
import tempfile
import time
from unittest.mock import patch

import p984g_ccipc_companion as companion
from p9_ccipc_targets import target as independent_target
import p984h_apc as process_budget
from p9_ccipc_compute import worker as compute_worker
from p9_ccipc_capture import portable
import p984h_ccipc_math as math_check
import p984d_ccipc as storage
import p984b_ccipc_runtime as r
import p9_ccipc_compute as compute
check_bindings = r.b.check_bindings
from pygrc.models import grc_v4_linear as linear
from pygrc.models.grc_9_v4_expansion import (
    GRC9V4ExpansionPlan,GRC9ExpansionPolicy,GRC9V4ExpansionRequestInput,cpc_history_policy,
)

g=companion.g
b=g.b
q,a,lo,hi=g.q,g.a,g.lo,g.hi
native=r.native
SELF=b.HERE+"p984h_ccipc.py"
INPUTS=b.BASE+"P9-8.4h-CCIPCInputs.json"
ROLES=g.ROLES
DT=g.pc.DT
LIMITS = math_check.LIMITS
subject = math_check.subject
capture_read = math_check.capture_read
check_read = math_check.check_read



def filename(segment,role="current",index=1):
    b.require(segment in ("source","prepared_target","event","step","final") and role in ROLES and 1<=index<=10,"segment roster")
    suffix=segment if segment=="event" else segment+"-"+role+("-"+str(index) if segment=="step" else "")
    return b.BASE+"P9-8.4h-CCIPC-"+suffix+".json.xz"


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
    paths=storage.numerical_paths() | {SELF,companion.SELF,companion.INPUTS,companion.RESULTS,b.HERE+"p9_ccipc_targets.py",
        g.SELF,g.pc.graph_math.SELF,g.iv.SELF,process_budget.SELF,math_check.SELF,
        math_check.staged.SELF,b.HERE+'test_p984h_ccipc_math.py',b.HERE+'test_p984h_ccipc.py',compute.PREFLIGHT,
        b.HERE+'p9_ccipc_capture.py'}
    paths |= {ref['path'] for ref in prior['source_bindings']}
    return b.seal(dict(schema="p984h-ccipc-inputs-v1",family="C_CI_PC",source_bindings=b.bind(paths),
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
    return p.make_state(graph,profile,specialization,roles,"C_CI_PC")



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
    raw=portable(r.capture_root(root))
    private=b.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated/phase9-verification/ccipc-large-raw'
    private.mkdir(parents=True,exist_ok=True)
    name=private/(raw['record_digest']+'.json.xz')
    if not name.exists():
        storage.save(name,b.seal(dict(inputs=root.inputs.to_payload(),read=raw,
            verifier_sha=b.sha((b.ROOT/SELF).read_bytes()),campaign_credit=False)))
    raw['certificate']=math_check.certificate(root.inputs,raw)
    check_read(root.inputs,raw)
    return raw


def observe_step(before):
    calls=[]
    scalar=r.pc.scalar_zoh
    def observed(z,source,dt,tau):
        calls.append(dict(Z=list(z),source=list(source),dt=dt,tau=tau))
        return scalar(z,source,dt,tau)
    start=time.monotonic()
    with measure_reuse() as reuse,patch.object(r.pc,"scalar_zoh",observed):
        step=r.ProvisionalCandidateCIStep(before)
    native_seconds=time.monotonic()-start
    b.require(reuse["solve_hits"]>0 and reuse["fact_hits"]>0,"actual C_CI_PC native cache reuse absent")
    after=step.next_inputs
    reads={name:retained_read(value) for name,value in (("read",step.root),("reset_read",step.reset_root),("restart",step.restart))}
    value=dict(before=before.to_payload(),after=after.to_payload(),**reads,
        selection_current=list(step.resource.selection.current.values),carrier_writes=step.carrier_writes,
        carrier_calls=calls,writer=None if step.writer is None else "unexpected_candidate_writer",
        continuity_evaluations=step.resource.continuity_evaluations,
        charge=step.resource.charge.receipt_values(),native_seconds=native_seconds,cache_observations=reuse)
    check_step(value)
    return value,after


def check_step(value,*,numerics=False):
    before=b.GeometryStageInputs.from_payload(value["before"])
    after=b.GeometryStageInputs.from_payload(value["after"])
    for operand,name in ((before,"read"),(r.role_input(before,"reset"),"reset_read"),(replace(after,dt=0),"restart")):
        check_read(operand,value[name],numerics=numerics)
    current=value["read"]["J"]
    source=[x for row in value["read"]["source"] for x in row]
    tau=before.geometry.reference.profile.params_resolved.realization.tau_PC
    b.require(value["selection_current"]==current and value["carrier_writes"]==value["continuity_evaluations"]==1
        and value["writer"] is None and value["carrier_calls"]==[dict(Z=list(before.current.Z_4),source=source,dt=before.dt,tau=tau)],"one held-source write/continuity")
    authority=b.GRCV4AuthoritativeState(r.represented_continuity(before,current),None,
        r.held_write(before.current.Z_4,source,before.dt,tau))
    expected=replace(before,current=authority,geometry=r.geometry(before,authority),
        step_index=before.step_index+1,time=float(r.Q(before.time)+r.Q(before.dt)))
    b.require(after==expected and min(after.current.C)>=0,"independent continuity/ZOH/reset/clock")
    reuse=value["cache_observations"]
    b.require(reuse["solve_lookups"]>=reuse["solve_hits"]>0 and reuse["fact_lookups"]>=reuse["fact_hits"]>0,"native reuse evidence")
    charge=value["charge"]
    policy=before.geometry.reference.profile.params_resolved.charge
    b.require(charge["target_charge"]==before.Q_target
        and abs(q(charge["admitted_charge"])-q(before.Q_target))<=q(policy.absolute_tolerance)
        and q(charge["residual"])==q(float(q(charge["admitted_charge"])-q(before.Q_target))),"native charge receipt")
    return after


def source_state():
    record=read("source");b.check_digest(record)
    return r.state(record["execution"]["state"]),record


def case_for(seed):
    declaration=storage.read(companion.INPUTS)["adjusted"]
    request=dict(declaration["event_request"],operation_id="p984h-ccipc-base",source_state_digest=seed.scientific_digest,
        history_policy=cpc_history_policy(seed.inputs.current,seed.inputs.reset))
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
    expected=independent_target(dict(expected_source=seed.to_payload()),case)
    target=replace(seed,inputs=expected)
    b.require(value["actual_target"]==target.to_payload() and len(value["admission_reads"])==2,"actual target/complete admission")
    for parent,admission in zip((seed,target),value["admission_reads"],strict=True):
        b.require(admission["inputs"]==parent.inputs.to_payload() and admission["published_state"]==seed.scientific_digest,"admission/publication chronology")
        check_read(parent.inputs,admission["read"],numerics=numerics)
        check_read(r.role_input(parent.inputs,"reset"),admission["reset_read"],numerics=numerics)
    detection=value["detections"]
    b.require(len(detection)==1 and detection[0]["current"]==value["admission_reads"][0]["read"]["J"]
        and case["request"]["source_node_id"] in detection[0]["candidate_node_ids"]
        and detection[0]["published_state"]==seed.scientific_digest,"fresh trigger identity")
    b.require(value["publication"]==[dict(admission_pairs=2,published_state=seed.scientific_digest)],"early publication")
    cp=value["checkpoint"];receipts=value["receipts"]
    b.require(cp["initial"]==seed.to_payload() and cp["state"]==target.to_payload()
        and cp["requests"]==[case["request"]] and cp["receipts"]==receipts and len(receipts)==4,"event checkpoint")
    _,checked=native.make_commit_receipts([v["identity_payload"] for v in receipts],
        operation_id=case["request"]["operation_id"],source_state_digest=seed.scientific_digest,
        target_state_digest=target.scientific_digest,target_step_index=target.inputs.step_index,target_time=target.inputs.time)
    b.require([x.to_payload() for x in checked]==receipts and cp["lifecycle_digest"]==target.lifecycle_digest(checked),"receipt chain")
    content=dict(schema_version="grcv4-history-content-identity-v1",subject="carrier",content=list(seed.inputs.current.Z_4+seed.inputs.reset.Z_4))
    archive=cp["carrier_archives"]
    b.require(len(archive)==1 and archive[0]["history_content"]==content
        and archive[0]["source_edge_ids"]==list(seed.inputs.geometry.reference.graph.live_edge_ids)
        and archive[0]["source_state_digest"]==seed.scientific_digest
        and archive[0]["source_graph_digest"]==seed.inputs.geometry.reference.graph.graph_digest
        and archive[0]["history_digest"]==b.payload_identity("history_content_identity_payload",content),"whole role-pair carrier archive")
    target_content=dict(content,content=list(target.inputs.current.Z_4+target.inputs.reset.Z_4))
    history=dict(schema_version="grcv4-history-bundle-receipt-v1",candidate=dict(subject="candidate",disposition="rederived",source_history_digest=None,
        target_history_digest=None,information_loss="none"),carrier=dict(subject="carrier",disposition="whole_carrier_reset",
        source_history_digest=archive[0]["history_digest"],target_history_digest=b.payload_identity("history_content_identity_payload",target_content),
        information_loss="carrier_history_loss"))
    b.require(receipts[0]["identity_payload"]["event_id"]==case["oracle"]["event_id"]
        and receipts[0]["identity_payload"]["history"]==history
        and all(x["identity_payload"]["core"]["information_losses"]==["carrier_history_loss"] for x in receipts)
        and value["failure"] is None and value["replay_identical"],"whole-reset receipt/replay")
    for role in ROLES:
        charge=sum(map(q,getattr(target.inputs,role).C),q(0))
        b.require(abs(charge-q(target.inputs.Q_target))<=q(target.inputs.geometry.reference.profile.params_resolved.charge.absolute_tolerance),"event charge")
    return target


def event(seed,case):
    owner=native.GRC9V4CCIPCOperation(seed)
    before=owner.checkpoint();pointer=owner._published
    stale=dict(case["request"],source_state_digest="grcv4-state-sha256:"+"0"*64)
    rejection=owner.expand(GRC9V4ExpansionRequestInput.from_payload(stale))
    b.require(not rejection.committed and owner.checkpoint()==before and owner._published is pointer,"stale event rollback")
    # Observe actual native reads; the independent large adapter replaces only
    # the small-fixture observer, never a numerical producer or admission rule.
    with patch.object(r,"certified_read",retained_read):
        owner,outcome,value=r.event_capture(seed,GRC9V4ExpansionRequestInput.from_payload(case["request"]))
    b.require(outcome.committed,"native large C_CI_PC event rejected: "+str(outcome.failure))
    try:
        check_event(seed,case,value)
    except Exception as exc:
        # Preserve completed native event/replay observations for diagnosing a
        # consumer failure. This private capture grants no passing evidence.
        capture=b.seal(dict(schema="p984h-ccipc-unchecked-native-capture-v1",source=seed.to_payload(),
            case=case,event=value,consumer_error=str(exc),source_code=(b.ROOT/SELF).read_text(),
            source_sha256=b.sha((b.ROOT/SELF).read_bytes()),native_credit=False))
        raw=lzma.compress(json.dumps(portable(capture),separators=(",",":"),allow_nan=False).encode())
        with tempfile.NamedTemporaryFile(prefix="ccipc-native-event-",suffix=".json.xz",dir="/tmp",delete=False) as stream:
            stream.write(raw)
            print(json.dumps(dict(unchecked_native_capture=stream.name)),flush=True)
        raise
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
                value["trigger"]=companion.leading.trigger_envelope(storage.read(companion.INPUTS)["adjusted"],list(map(a,after.current.C)))
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
        value=dict(before=before.to_payload(),read=retained_read(r.CandidateCIRoot(before)),read_only=True)
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
        failure=b.seal(dict(schema='p984h-ccipc-incomplete-v1',manifest_digest=m['record_digest'],
            segment=segment,role=role,index=index,cap_seconds=cap,elapsed_seconds=time.monotonic()-started,
            error=dict(type=type(exc).__name__,message=str(exc)),outcome='incomplete',campaign_credit=False))
        storage.save(name.replace('.json.xz','-incomplete-'+str(time.time_ns())+'.json.xz'),failure)
        raise
    check_manifest(m)
    record=b.seal(dict(schema="p984h-ccipc-segment-v1",manifest_digest=m["record_digest"],segment=segment,
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
