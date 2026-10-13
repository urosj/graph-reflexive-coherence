"""History-only A_PC companion with source eligibility before target work."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import json

import p984d_apc_companion_runtime as prior

c,r,b=prior.c,prior.r,prior.b
o=r.oracle
SELF=b.HERE+"p984d_apc_history.py"
TEST=b.HERE+"test_p984d_apc_history.py"
PLAN=b.BASE+"P9-8.4d-APCHistoryCompanionPlan.md"
INPUTS=b.BASE+"P9-8.4d-APCHistoryCompanionInputs.json"
RESULTS=b.BASE+"P9-8.4d-APCHistoryCompanionResults.json"
REVIEW=b.BASE+"P9-8.4d-APCHistoryCompanionReview.md"
PRESSURE=b.BASE+"P9-8.4d-APCHistoryCompanionPressure.json"


def initial(offset=Q(0)):
    b.require(offset in (Q(0),-Q(1,256),Q(1,256)),"undeclared history probe")
    before=b.GeometryStageInputs.from_payload(b.read(c.prior.INPUTS)["initial_inputs"])
    current=replace(before.current,W_A=tuple(float(Q(w)+Q(3,64)+offset) for w in before.current.W_A))
    return replace(before,current=current)


def make_manifest():
    old=b.read(c.prior.INPUTS)
    c.prior.check_manifest(old)
    b.require(b.read(c.ACCEPTANCE)==c.acceptance(),"accepted exclusion changed")
    paths={v["path"] for v in old["source_bindings"]}|{
        SELF,TEST,PLAN,c.SELF,prior.SELF,c.prior.INPUTS,c.INPUTS,c.ACCEPTANCE,
        c.RESULTS,prior.INPUTS,prior.RESULTS}
    return b.seal(dict(schema="p984d-apc-history-inputs-v1",family="A_PC",
        source_bindings=b.bind(sorted(paths)),initial_inputs=initial().to_payload(),
        layout_cases=old["cases"],source_current_beats=1,source_reset_beats=0,
        target_beats_per_role=10,pilot=c.PILOT,
        history_increment="3/64",pressure_offsets=["-1/256","1/256"],
        ledger_disposition=b.read(c.INPUTS)["ledger_disposition"],
        authority_trace_reference=dict(path=c.INPUTS,record_digest=b.read(c.INPUTS)["record_digest"]),
        user_accepted=False,aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest);b.check_bindings(manifest["source_bindings"])
    b.require(manifest==make_manifest(),"history companion declaration drift")


def source(before):
    graph=before.geometry.reference.graph.port_graph.to_payload()
    old=before.current
    out=o.PaperAPC(graph).step(old.C,old.W_A,old.Z_4)
    proof=o.check_step(graph,old.C,old.W_A,old.Z_4,out)
    previous=r.state(b.read(c.prior.INPUTS)["expected_source"])
    current=b.GRCV4AuthoritativeState(tuple(out["C"]),tuple(out["W_A"]),tuple(out["Z_4"]))
    after=replace(previous.inputs,current=current,reset=before.reset)
    after=replace(after,geometry=r.geometry(after,current))
    nominal=replace(previous,inputs=after)
    with b.exact_backend(b.ExactBackend.FLINT):
        shared,seed=r.run_source(dict(initial_inputs=before.to_payload(),nominal_source=nominal.to_payload()))
        read=r.certified_read(r.CandidatePCRead(seed.inputs,r.backend(seed.inputs)))
    return seed,shared,dict(nominal_source=nominal.to_payload(),output=out,
        errors={k:str(v) for k,v in proof["errors"].items()}),read


def eligibility(seed,read,certificate=None):
    """Independent interval conditions and fresh native fixed-row detection."""
    certificate=prior.trigger_certificate(seed) if certificate is None else certificate
    spec=seed.specialization.resolved["spark"]
    lo,hi=map(Q,certificate["squared_norm_interval"])
    threshold=Q(spec["gradient_tolerance"])**2
    b.require(certificate["source_state_digest"]==seed.scientific_digest
        and Q(certificate["strict_upper_required"])==threshold and 0<=lo<=hi
        and certificate["gradient_gate_passes"] is (hi<threshold)
        and certificate["gradient_gate_excluded"] is (lo>=threshold)
        and len(certificate["gradient_intervals"])==3
        and all(Q(a)<=Q(z) for a,z in certificate["gradient_intervals"]),"source eligibility certificate drift")
    sign=seed.specialization.identity_payload["hessian_sign"]
    intervals=[[sign*Q(x) for x in pair] for pair in certificate["gradient_intervals"]]
    hessian=[min(min(pair) for pair in intervals),min(max(pair) for pair in intervals)]
    ports=sorted(endpoint.port for edge in seed.inputs.geometry.reference.graph.port_graph.edges
        for endpoint in (edge.tail,edge.head) if endpoint.node_id=="source-s")
    inputs=r.native.GRC9V4PostbeatRows(seed.inputs.geometry.reference.graph.port_graph,
        seed.inputs.geometry.reference.profile,seed.inputs.current,
        tuple(read["J"]),
        seed.inputs.step_index,sign)
    detection=r.native.GRC9V4CandidateDetection(inputs,r.native.GRC9SparkPolicy.from_payload(spec))
    native="source-s" in detection.candidate_node_ids()
    bounded=(ports==list(range(1,10)) and certificate["gradient_gate_passes"]
        and hessian[1]<Q(spec["spark_hessian_tolerance"]))
    b.require(native==bounded,"independent/native source eligibility mismatch")
    return dict(**certificate,occupied_ports=ports,
        signed_hessian_min_interval=list(map(str,hessian)),
        spark_hessian_threshold=str(Q(spec["spark_hessian_tolerance"])),
        independent_eligible=bounded,native_eligible=native,
        fresh_read=read,detector_identity=detection.identity)


def native_manifest(manifest,seed,shared,independent):
    cases=[]
    for old in manifest["layout_cases"]:
        template=deepcopy(old)
        template["request"]["operation_id"]+="-history63"
        case=c.bind_case(seed,template)
        case["changes_from_frozen"]=["preregistered_initial_current_history_and_resulting_source_image"]
        cases.append(case)
    return b.seal(dict(initial_inputs=manifest["initial_inputs"],
        nominal_source=independent["nominal_source"],expected_source=seed.to_payload(),
        shared=shared,cases=cases,user_accepted=False,aggregate_closed=False))


def run_case(job):
    manifest,case=job
    with b.exact_backend(b.ExactBackend.FLINT),prior.previous.data_adapter(manifest):
        row=r.execute_case(r.state(manifest["expected_source"]),case)
    print(case["case_id"],row["outcome"],row["first_failure"],flush=True)
    return row


def run(manifest,workers):
    check_manifest(manifest)
    seed,shared,independent,read=source(b.GeometryStageInputs.from_payload(manifest["initial_inputs"]))
    trigger=eligibility(seed,read)
    print("Fresh source eligibility:",trigger["native_eligible"],flush=True)
    runtime=native_manifest(manifest,seed,shared,independent)
    rows=[]
    if trigger["native_eligible"]:
        pilot=next(v for v in runtime["cases"] if v["case_id"]==c.PILOT)
        rows=[run_case((runtime,pilot))]
        if rows[0]["case_passed"]:
            rest=[v for v in runtime["cases"] if v["case_id"]!=c.PILOT]
            with ProcessPoolExecutor(max_workers=workers) as pool:
                rows+=list(pool.map(run_case,[(runtime,v) for v in rest]))
            by_id={row["case_id"]:row for row in rows}
            rows=[by_id[v["case_id"]] for v in runtime["cases"]]
    execution=b.seal(dict(manifest_digest=runtime["record_digest"],shared=shared,cases=rows,
        native_runtime_executed=True,user_accepted=False,aggregate_closed=False))
    return b.seal(dict(schema="p984d-apc-history-results-v1",manifest_digest=manifest["record_digest"],
        independent_source=independent,source_eligibility=trigger,
        runtime_manifest=runtime,execution=prior.previous.compact(execution),
        user_accepted=False,aggregate_closed=False,uniform_neighborhood_proved=False))


def check(manifest,result,*,numerics=False):
    check_manifest(manifest);b.check_digest(result)
    b.require(result["schema"]=="p984d-apc-history-results-v1"
        and result["manifest_digest"]==manifest["record_digest"]
        and all(result[k] is False for k in ("user_accepted","aggregate_closed","uniform_neighborhood_proved")),
        "history result binding or scope promotion")
    runtime=result["runtime_manifest"];b.check_digest(runtime)
    execution=prior.previous.expand(result["execution"]);b.check_digest(execution)
    shared=execution["shared"];seed=r.state(shared["actual_source"])
    b.require(runtime==native_manifest(manifest,seed,shared,result["independent_source"]),"native source/case binding drift")
    nominal=r.state(result["independent_source"]["nominal_source"])
    independent=result["independent_source"];before=b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    b.require(b.authority_payload(nominal.inputs.current)=={k:independent["output"][k] for k in ("C","W_A","Z_4")}
        and nominal.inputs.reset==before.reset,"independent source authority drift")
    if numerics:
        proof=o.check_step(before.geometry.reference.graph.port_graph.to_payload(),
            before.current.C,before.current.W_A,before.current.Z_4,independent["output"])
        b.require(independent["errors"]=={k:str(v) for k,v in proof["errors"].items()},"independent source certificate drift")
    for key,limit in (("C",o.RESOURCE_ERROR),("W_A",o.HISTORY_ERROR),("Z_4",o.CARRIER_ERROR)):
        b.require(max(abs(Q(x)-Q(y)) for x,y in zip(getattr(seed.inputs.current,key),
            getattr(nominal.inputs.current,key),strict=True))<limit,"independent/native source mismatch")
    trigger=result["source_eligibility"]
    r.check_read(seed.inputs,trigger["fresh_read"],numerics=numerics)
    # Default checking authenticates retained bounds and the cheap native row
    # detector. Independent interval equations are recomputed only explicitly.
    certificate={k:trigger[k] for k in ("source_state_digest","gradient_intervals","squared_norm_interval",
        "strict_upper_required","gradient_gate_passes","gradient_gate_excluded")}
    b.require(trigger==eligibility(seed,trigger["fresh_read"],None if numerics else certificate),"source trigger evidence drift")
    rows=execution["cases"]
    if not trigger["native_eligible"]:
        b.require(rows==[],"event attempted despite held trigger")
    elif len(rows)!=20:
        b.require(len(rows)==1 and rows[0]["case_id"]==c.PILOT and not rows[0]["case_passed"],
            "undeclared incomplete campaign")
    for row in rows:
        case=next(v for v in runtime["cases"] if v["case_id"]==row["case_id"])
        b.require(row["actual_case"]==case,"actual declared history case drift")
        if row["first_failure"] and row["first_failure"]["stage"]=="independent_preflight":
            b.require(not row["event_committed"] and "event" not in row
                and row["continuation"]==[] and row["final_reads"]=={},"preflight failure cannot confer native credit")
    selected=deepcopy(runtime)
    selected["cases"]=[v for v in runtime["cases"] if any(row["case_id"]==v["case_id"] for row in rows)]
    with prior.previous.data_adapter(runtime):
        r.validate(selected,execution,numerics=numerics)
    passed=sum(row["case_passed"] for row in rows)
    return dict(family="A_PC",status="positive_history_companion_pending_acceptance" if passed==20 else "history_companion_held",
        source_steps=1,source_eligible=trigger["native_eligible"],
        cases_required=20,attempted_cases=len(rows),passed_cases=passed,
        native_cases=sum("event" in row for row in rows),committed_events=sum(row["event_committed"] for row in rows),
        target_steps=sum(len(row["continuation"]) for row in rows),final_reads=sum(len(row["final_reads"]) for row in rows),
        accepted_cells=0,passing_pending_cells=2*passed,required_cells=40,
        failures=[dict(case_id=row["case_id"],first_failure=row["first_failure"]) for row in rows if not row["case_passed"]],
        native_trajectories_rerun=False,interval_equations_recomputed=numerics,
        uniform_neighborhood_proved=False,aggregate_closed=False,user_accepted=False)


def diagnose(manifest,result):
    """Locate the failed pilot using unchanged full enabled interval equations.

    No new source choice or native trajectory; stop at the first signed negative
    current-role update. The predeclared neighbors remain gated on pilot success.
    """
    summary=check(manifest,result)
    b.require(summary["source_eligible"] and summary["failures"]==[dict(case_id=c.PILOT,
        first_failure=dict(stage="independent_preflight",role="both",index=0,type="ValueError",
            message="negative next resource",kind="numerical_or_lifecycle_failure"))],"unexpected pilot failure")
    runtime=result["runtime_manifest"]
    seed=r.state(runtime["expected_source"])
    case=next(v for v in runtime["cases"] if v["case_id"]==c.PILOT)
    target=r.independent_target(seed,case)
    graph=case["oracle"]["target_graph"]
    state=target.inputs.current
    cv,w,z=state.C,state.W_A,state.Z_4
    rows=[]
    for index in range(1,11):
        row=dict(index=index,**c.stage(graph,cv,w,z));rows.append(row)
        if row["error"] is not None:break
        cv,w,z=(row["output"][k] for k in ("C","W_A","Z_4"))
    b.require(rows[-1]["error"]=="negative next resource","signed failure not reproduced")
    return b.seal(dict(schema="p984d-apc-history-pressure-v1",manifest_digest=manifest["record_digest"],
        result_digest=result["record_digest"],case_id=c.PILOT,role="current",target=target.to_payload(),
        stages=rows,native_steps=0,native_events=0,neighbor_probes=0,
        neighbor_disposition="not_run_center_failed",reset_continuation_demonstrated=False,
        user_accepted=False,aggregate_closed=False))


def check_pressure(manifest,result,pressure,*,numerics=False):
    b.check_digest(pressure)
    b.require(pressure["schema"]=="p984d-apc-history-pressure-v1"
        and pressure["manifest_digest"]==manifest["record_digest"]
        and pressure["result_digest"]==result["record_digest"] and pressure["case_id"]==c.PILOT
        and pressure["role"]=="current" and pressure["neighbor_disposition"]=="not_run_center_failed"
        and all(pressure[k] is False for k in ("user_accepted","aggregate_closed","reset_continuation_demonstrated"))
        and all(type(pressure[k]) is int and pressure[k]==0 for k in ("native_steps","native_events","neighbor_probes")),
        "diagnostic scope drift")
    runtime=result["runtime_manifest"];seed=r.state(runtime["expected_source"])
    case=next(v for v in runtime["cases"] if v["case_id"]==c.PILOT)
    target=r.independent_target(seed,case)
    b.require(pressure["target"]==target.to_payload(),"diagnostic target drift")
    current=b.authority_payload(target.inputs.current);rows=pressure["stages"]
    b.require(1<=len(rows)<=10,"diagnostic stage count")
    for index,row in enumerate(rows,1):
        b.require(row["index"]==index and row["input"]==current,"diagnostic stage link")
        current={k:row["output"][k] for k in ("C","W_A","Z_4")}
        b.require(row["error"]==("negative next resource" if index==len(rows) else None),"first negative stage drift")
        b.require(len(row["resource_intervals"])==len(current["C"])
            and all(Q(lo)<=Q(hi) for lo,hi in row["resource_intervals"]),"invalid signed resource intervals")
        if index<len(rows):
            b.require(min(map(Q,current["C"]))>=0 and row["errors"] is not None,"preceding stage failed")
    negatives=[dict(node_id=case["oracle"]["target_graph"]["live_node_ids"][i],
        interval=pair,represented_output=rows[-1]["output"]["C"][i])
        for i,pair in enumerate(rows[-1]["resource_intervals"]) if Q(pair[1])<0]
    b.require(negatives and all(v["represented_output"]<0 for v in negatives),"negative sign not established")
    if numerics:b.require(pressure==diagnose(manifest,result),"full enabled diagnostic equations drift")
    worst=min(negatives,key=lambda v:Q(v["interval"][1]))
    upper_with_budget=Q(worst["interval"][1])+o.RESOURCE_ERROR
    b.require(upper_with_budget<0,"existing numerical budget does not establish exclusion")
    return dict(case_id=c.PILOT,role="current",first_negative_step=len(rows),
        negative_nodes=len(negatives),worst=worst,neighbor_probes=0,
        resource_error_budget=str(o.RESOURCE_ERROR),negative_upper_with_budget=str(upper_with_budget),
        native_steps=0,native_events=0,interval_equations_recomputed=numerics,
        claim_scope="pointwise_enabled_equations_at_named_independent_preflight_input_not_general_infeasibility")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare",action="store_true")
    mode.add_argument("--run",action="store_true")
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--pressure",action="store_true")
    mode.add_argument("--check-pressure",action="store_true")
    parser.add_argument("--workers",type=int,default=3)
    parser.add_argument("--recheck-numerics",action="store_true")
    args=parser.parse_args()
    b.require(1<=args.workers<=4 and (not args.recheck_numerics or args.check or args.check_pressure),"invalid options")
    if args.prepare:
        b.write_new(INPUTS,make_manifest());print("History companion preregistered");return
    manifest=b.read(INPUTS)
    if args.run:
        result=run(manifest,args.workers);b.write_new(RESULTS,result)
    else:result=b.read(RESULTS)
    if args.pressure or args.check_pressure:
        check(manifest,result)
        pressure=diagnose(manifest,result) if args.pressure else b.read(PRESSURE)
        if args.pressure:b.write_new(PRESSURE,pressure)
        print(json.dumps(check_pressure(manifest,result,pressure,numerics=args.recheck_numerics),indent=2));return
    print(json.dumps(check(manifest,result,numerics=args.recheck_numerics),indent=2))


if __name__=="__main__":main()
