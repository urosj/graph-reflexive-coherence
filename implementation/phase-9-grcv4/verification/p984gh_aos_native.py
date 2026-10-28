"""FLINT/Arb A_OS large native prerequisites and actual-target continuation.

Every segment is published only after its independent operand checks pass.
The validation memo retains exact schema/payload matches within one worker;
matrix_operation owns bounded exact-content solve reuse. No current is cached.
"""

import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import cProfile
import json
import lzma
import pstats
import time

import p984g_aos as g
from p984h_validation_reuse import validation_reuse, POLICY as VALIDATION_POLICY
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput, aos_history_policy
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_numerics import ExactBackend, NumericalPolicy, exact_backend, numerical_policy, matrix_operation
from pygrc.models.grc_v4_realizations import CandidateAOSPass
from pygrc.models.grc_v4_step import ProvisionalCandidateAOSStep
from pygrc.models.grc_v4_state import FrozenJSONMap

b, q, scalar = g.b, g.q, g.scalar
SELF = b.HERE + "p984gh_aos_native.py"
TEST = b.HERE + "test_p984gh_aos_native.py"
PLAN = b.BASE + "P9-8.4h-AOSPlan.md"
INPUTS = b.BASE + "P9-8.4h-AOSInputs.json"
ROLES = g.ROLES
DT = 2**-12


@contextmanager
def policy():
    with validation_reuse(), exact_backend(ExactBackend.FLINT), numerical_policy(NumericalPolicy.CERTIFIED_ARB_256), matrix_operation():
        yield


def filename(segment, role="current", index=1):
    b.require(segment in ("source", "prepared_target", "event", "step", "final"), "unknown large segment")
    b.require(role in ROLES and 1 <= index <= 10, "unknown role/index")
    suffix = segment if segment == "event" else f"{segment}-{role}" + (f"-{index}" if segment == "step" else "")
    return b.BASE + "P9-8.4h-AOS-" + suffix + ".json.xz"


def read(segment, role="current", index=1):
    return g.storage.read(filename(segment, role, index))


def manifest():
    m = g.storage.read(g.INPUTS)
    result = g.storage.read(g.RESULTS)
    g.check(m, result)
    paths = {x["path"] for x in m["source_bindings"]}
    paths |= {SELF, TEST, PLAN, g.INPUTS, g.RESULTS,
        b.HERE + "p984g_aci_native.py", b.HERE + "p984h_validation_reuse.py"}
    # Bind the numerical implementation actually used; public API registration
    # is a separate Tranche 9 subject and is not a numerical dependency here.
    paths |= {str(p.relative_to(b.ROOT)) for pattern in ("grc_v4*.py", "_grc_v4*.py")
              for p in (b.ROOT / "src/pygrc/models").glob(pattern)}
    paths |= {"src/pygrc/models/" + name for name in
              ("grc_9_v4_lifecycle.py", "grc_9_v4_expansion.py", "grc_9_v4_topology.py")}
    return b.seal(dict(schema="p984h-aos-inputs-v1", source_bindings=b.bind(paths),
        prerequisite_digest=result["record_digest"], exact_backend="flint",
        numerical_policy="certified_arb_256_weighted_v1", validation_memo=VALIDATION_POLICY,
        scope=dict(prepared_source_steps=2, prepared_target_steps=2, events=1,
                   actual_target_steps=20, final_reads=2, current_source_reused=True,
                   larger_covariance_pending=True),
        caps=dict(step=600, event=1200, final=600),
        user_accepted=False, aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m)
    b.check_bindings(m["source_bindings"])
    # Authenticate the exact already-declared prerequisite. Reconstructing the
    # 400-edge mechanical companion on every segment adds no new assurance.
    prior = g.storage.read(g.RESULTS)
    b.check_digest(prior)
    b.require(m["schema"] == "p984h-aos-inputs-v1" and m["prerequisite_digest"] == prior["record_digest"]
              and m["exact_backend"] == "flint" and m["numerical_policy"] == "certified_arb_256_weighted_v1"
              and m["validation_memo"] == VALIDATION_POLICY, "large native declaration drift")


def state(payload):
    spec = payload["specialization"]
    value = native.GRC9V4AOSState(GeometryStageInputs.from_payload(payload["inputs"]),
        native.GRC9V4Specialization(FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])))
    b.require(value.to_payload() == payload, "native state identity drift")
    return value


def prepared(which):
    declaration = g.storage.read(g.INPUTS)["adjusted"]
    subject = declaration[which]
    p = g.mechanical
    graph = p.GRC9V4PortGraph.from_envelope(subject["graph"])
    profile = p.GRCV4Profile.from_canonical_bytes(p.canonical_json_bytes(subject["profile"]))
    spec = declaration["specialization"]
    specialization = native.GRC9V4Specialization(FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"]))
    roles = {role:p.authority(s,len(graph.edges)) for role,s in subject["roles"].items()}
    return p.make_state(graph,profile,specialization,roles,"A_OS")


def subject(before):
    ref = before.geometry.reference
    return dict(graph=ref.graph.port_graph.to_envelope(),profile=ref.profile.to_payload(),
        roles={role:dict(C=list(getattr(before,role).C),W_A=list(getattr(before,role).W_A),Z_4=None) for role in ROLES})


def point(value):
    return {key:list(values) for key,values in dict(potential=value.potential.values,
        baseline=value.baseline.values,drive=value.W_hat_A,current=value.current.values,
        flux=value.read.flux.values,flat=value.read.causal_flat.values).items()}


def compare_point(actual, expected):
    fields=("potential","baseline","drive","current","flux","flat")
    b.require(set(actual)==set(fields) and all(actual[k]==expected[k] for k in fields),
              "native point differs from independent staged equations")


def fixed_read(value, operand, h):
    with scalar.ctx.workprec(scalar.BITS):
        md=scalar.model(operand,"current")
        hm=scalar.matrix(h)
        expected=scalar.represented(md,hm)
        actual=point(value)
        compare_point(actual,expected)
        exact=scalar.analytic(md,hm)
        errors={name:str(max(scalar.hi(abs(scalar.a(x)-truth[i,0])) for i,x in enumerate(actual[name])))
            for name,truth in (("current",exact["J"]),("flat",exact["flat"]))}
        b.require(all(0<=q(x)<q("1/1000000000") for x in errors.values()),"fixed read exact error")
    return dict(actual=actual,staged=expected,errors=errors,operand_digest=b.digest(operand),H_digest=b.digest(h))


def observe_step(before, expected=None):
    operand=subject(before)
    backend=native.GRC9V4CandidateADifferentialReference(before.geometry.reference.graph.port_graph)
    start=time.monotonic()
    step=ProvisionalCandidateAOSStep(before,backend)
    native_seconds=time.monotonic()-start
    expected = g.analyze(operand,"current",before.dt) if expected is None else expected
    compare_point(point(step.os_pass.predictor),expected["predictor"])
    compare_point(point(step.os_pass.corrector),expected["corrector"])
    h=[list(row) for row in step.os_pass.residual.geometry.one_form_hodge.matrix]
    b.require(h==expected["H"] and step.os_pass.residual.admitted,"native OS geometry/split")
    after=step.next_inputs
    b.require(list(after.current.C)==expected["represented_C"] and min(after.current.C)>=0,"native continuity")
    writer=expected["writer"]
    b.require(writer is not None and list(after.current.W_A)==writer["W_A"]
        and list(step.writer.W_drv_A)==writer["drive"]
        and [list(row) for row in step.writer.descriptors]==writer["descriptors"],"OS selected-current history writer")
    b.require(after.reset==before.reset and after.geometry==before.geometry and after.current.Z_4 is None
        and after.step_index==before.step_index+1 and after.time==before.time+before.dt
        and step.resource.continuity_evaluations==1,"native step chronology/authority")
    final_operand=subject(after)
    final=fixed_read(step.final,final_operand,h)
    # Reference Hodge is the declared unit diagonal on this campaign.
    n=len(before.current.W_A)
    reference=[[float(i==j) for j in range(n)] for i in range(n)]
    restart=fixed_read(step.restart,final_operand,reference)
    return dict(before=before.to_payload(),after=after.to_payload(),oracle=expected,
        predictor=point(step.os_pass.predictor),corrector=point(step.os_pass.corrector),
        H=h,final=final,restart=restart,writer=dict(W_A=list(after.current.W_A),
        drive=list(step.writer.W_drv_A),descriptors=[list(row) for row in step.writer.descriptors]),
        charge=step.resource.charge.receipt_values(),continuity_evaluations=1,
        exact_resource_sum_delta=str(sum(map(q,after.current.C),q(0))-sum(map(q,before.current.C),q(0))),
        native_seconds=native_seconds),after


def check_step(value):
    before,after=GeometryStageInputs.from_payload(value["before"]),GeometryStageInputs.from_payload(value["after"])
    expected=value["oracle"]
    b.require(expected["subject_digest"]==b.digest(subject(before)) and expected["role"]=="current"
        and expected["dt"]==before.dt,"step oracle operand")
    compare_point(value["predictor"],expected["predictor"])
    compare_point(value["corrector"],expected["corrector"])
    b.require(value["H"]==expected["H"] and list(after.current.C)==expected["represented_C"]
        and value["writer"]==expected["writer"] and list(after.current.W_A)==expected["writer"]["W_A"],"step consumption")
    c=expected["certificate"]
    b.require(q(c["minimum_resource_lower"])>0 and q(c["split_upper"])<q(before.geometry.reference.profile.params_resolved.realization.tolerance)
        and c["exact_OS_composition"] and not c["uniform_trajectory_enclosure"],"OS bound scope")
    b.require(after.reset==before.reset and after.geometry==before.geometry and after.current.Z_4 is None
        and after.step_index==before.step_index+1 and after.time==before.time+before.dt
        and value["continuity_evaluations"]==1,"step authority/chronology")
    for name in ("final","restart"):
        record=value[name];compare_point(record["actual"],record["staged"])
        b.require(record["operand_digest"]==b.digest(subject(after)) and
            all(0<=q(x)<q("1/1000000000") for x in record["errors"].values()),"final read binding/error")
    return after


def source_state():
    record=read("source")
    b.check_digest(record)
    b.require(record["segment"]=="source" and record["role"]=="current", "wrong source predecessor")
    return state(record["execution"]["state"]),record


def event():
    seed,prior=source_state()
    declaration=g.storage.read(g.INPUTS)["adjusted"]
    req=deepcopy(declaration["event_request"])
    req.update(operation_id="p984h-aos-base",source_state_digest=seed.scientific_digest,
               history_policy=aos_history_policy(seed.inputs.current,seed.inputs.reset))
    owner=native.GRC9V4AOSOperation(seed)
    before=owner.checkpoint()
    stale=dict(req,source_state_digest=declaration["event_request"]["source_state_digest"])
    b.require(stale["source_state_digest"]!=seed.scientific_digest,"source did not evolve")
    rejection=owner.expand(GRC9V4ExpansionRequestInput.from_payload(stale))
    b.require(not rejection.committed and owner.checkpoint()==before,"stale-source rollback")
    result=owner.expand(GRC9V4ExpansionRequestInput.from_payload(req))
    b.require(result.committed,"large A_OS event rejected: "+str(result.failure))
    target=owner.state
    # Independently conserve all resources and retain exact unsigned old-edge W.
    oldgraph=seed.inputs.geometry.reference.graph.port_graph
    newgraph=target.inputs.geometry.reference.graph.port_graph
    identity=json.loads(owner.checkpoint())["reference_currents"][0]["event_id"]
    shares={identity+f"/satellite/{i+1}":q(x) for i,x in enumerate(req["resource_distribution"])}
    for role in ROLES:
        incoming=getattr(seed.inputs,role);actual=getattr(target.inputs,role)
        cs=dict(zip(oldgraph.live_node_ids,incoming.C,strict=True));ws=dict(zip((e.edge_id for e in oldgraph.edges),incoming.W_A,strict=True))
        wanted=[cs[n] if n in cs else float(q(cs[req["source_node_id"]])*shares.get(n,q(0))) for n in newgraph.live_node_ids]
        b.require(list(actual.C)==wanted and list(actual.W_A)==[ws.get(e.edge_id,1.0) for e in newgraph.edges],"actual target independent transfer")
    checkpoint=json.loads(owner.checkpoint())
    b.require(native.GRC9V4AOSOperation.replay(owner.checkpoint()).checkpoint()==owner.checkpoint(),"exact large event replay")
    return dict(request=req,event_id=identity,checkpoint=checkpoint,state=target.to_payload(),
                source_record_digest=prior["record_digest"],stale_failure=rejection.failure.to_payload(),
                stale_rollback_exact=True,exact_replay=True,native_events=1)


def execute(segment,role,index):
    with policy():
        if segment in ("source","prepared_target"):
            initial=prepared("source" if segment=="source" else "target")
            before=replace(initial.inputs,current=getattr(initial.inputs,role),dt=DT)
            value,after=observe_step(before)
            value["state"]=replace(initial,inputs=replace(after,dt=0)).to_payload()
            if segment=="source":
                with scalar.ctx.workprec(scalar.BITS):
                    value["trigger"]=g.f.trigger(g.storage.read(g.INPUTS)["adjusted"],list(map(scalar.a,after.current.C)),list(map(scalar.a,after.current.W_A)))
                b.require(value["trigger"]["small_gradient"] and value["trigger"]["strict_hessian_condition"],"actual source trigger")
            return value
        if segment=="event":return event()
        parent=read("event")
        initial=state(parent["execution"]["state"])
        if segment=="step" and index==1:
            before=replace(initial.inputs,current=getattr(initial.inputs,role),dt=DT)
        else:
            prior=read("step",role,10 if segment=="final" else index-1)
            b.check_digest(prior)
            before=GeometryStageInputs.from_payload(prior["execution"]["after"])
        if segment=="step":
            value,_=observe_step(before)
            value["event_record_digest"]=parent["record_digest"]
            return value
        expected=g.analyze(subject(before),"current",DT)
        passed=CandidateAOSPass(before,native.GRC9V4CandidateADifferentialReference(before.geometry.reference.graph.port_graph))
        compare_point(point(passed.predictor),expected["predictor"])
        compare_point(point(passed.corrector),expected["corrector"])
        return dict(before=before.to_payload(),oracle=expected,predictor=point(passed.predictor),corrector=point(passed.corrector),
                    event_record_digest=parent["record_digest"],read_only=True)


def run(segment,role,index,profile=False):
    m=g.storage.read(INPUTS);check_manifest(m)
    path=filename(segment,role,index)
    b.require(not (b.ROOT/path).exists(),"refuse overwrite")
    cap=m["caps"]["event" if segment=="event" else "final" if segment=="final" else "step"]
    start=time.monotonic();prof=cProfile.Profile() if profile else None
    with b.budget(cap):
        if prof:prof.enable()
        value=execute(segment,role,index)
        if prof:prof.disable()
    if segment in ("source","prepared_target","step"):
        with policy():check_step(value)
    check_manifest(m)
    timings=[]
    if prof:
        stats=pstats.Stats(prof)
        for (filename_,line,name),(cc,nc,tt,ct,_) in sorted(stats.stats.items(),key=lambda x:x[1][3],reverse=True)[:25]:
            filename_=filename_.replace(str(b.ROOT)+"/","")
            timings.append(dict(file=filename_,line=line,function=name,calls=nc,self_seconds=tt,cumulative_seconds=ct))
    record=b.seal(dict(schema="p984h-aos-segment-v1",manifest_digest=m["record_digest"],segment=segment,
        role=role,index=index,execution=value,elapsed_seconds=time.monotonic()-start,profile=timings,
        outcome="completed",user_accepted=False,aggregate_closed=False))
    with (b.ROOT/path).open("xb") as stream:stream.write(lzma.compress(json.dumps(record,separators=(",",":"),allow_nan=False).encode()+b"\n"))
    print(json.dumps(dict(segment=segment,role=role,index=index,outcome="completed",seconds=record["elapsed_seconds"])),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=("prepare","run"))
    p.add_argument("--segment",choices=("source","prepared_target","event","step","final"),default="source")
    p.add_argument("--role",choices=ROLES,default="current")
    p.add_argument("--index",type=int,default=1)
    p.add_argument("--profile",action="store_true")
    args=p.parse_args()
    if args.action=="prepare":b.write_new(INPUTS,manifest())
    else:run(args.segment,args.role,args.index,args.profile)
