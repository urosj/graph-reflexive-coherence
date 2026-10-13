"""Native comparisons for the separately declared A_PC resource companion.

The source runs once. Each independent target preflight precedes its native
event; no changed law, native producer or numerical criterion is supplied.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from fractions import Fraction as Q
import json

import p984d_apc_companion as c

r,b=c.r,c.b
previous=c.prior.previous
SELF=b.HERE+"p984d_apc_companion_runtime.py"
TEST=b.HERE+"test_p984d_apc_companion_runtime.py"
INPUTS=b.BASE+"P9-8.4d-APCSourceCompanionNativeInputs.json"
RESULTS=b.BASE+"P9-8.4d-APCSourceCompanionNativeResults.json"
REVIEW=c.REVIEW


def trigger_certificate(seed):
    """Independent fixed-row source gradient; no native detector used."""
    graph=seed.inputs.geometry.reference.graph.port_graph.to_payload()
    high=r.oracle.IntervalRows(r.oracle.model_for(graph))
    rows=high.rows(r.oracle.vector(seed.inputs.current.C),r.oracle.vector(seed.inputs.current.W_A))
    gradient=rows[graph["live_node_ids"].index("source-s")]
    squared=sum(v*v for v in gradient)
    threshold=Q(seed.specialization.resolved["spark"]["gradient_tolerance"])**2
    return dict(source_state_digest=seed.scientific_digest,
        gradient_intervals=[[str(r.oracle.endpoint(v,s)) for s in (0,1)] for v in gradient],
        squared_norm_interval=[str(r.oracle.endpoint(squared,s)) for s in (0,1)],
        strict_upper_required=str(threshold),
        gradient_gate_passes=r.oracle.endpoint(squared,1)<threshold,
        gradient_gate_excluded=r.oracle.endpoint(squared,0)>=threshold)


def make_manifest():
    declared,pilot=b.read(c.INPUTS),b.read(c.RESULTS)
    c.check(declared,pilot)
    b.require(pilot["status"]=="pilot_positive_pending_remaining_layouts","positive pilot required")
    source_manifest=dict(initial_inputs=declared["initial_inputs"],nominal_source=pilot["nominal_source"])
    with b.exact_backend(b.ExactBackend.FLINT):
        shared,seed=r.run_source(source_manifest)
    cases=[c.bind_case(seed,old) for old in declared["layout_cases"]]
    paths={v["path"] for v in declared["source_bindings"]}|{SELF,TEST,c.INPUTS,c.RESULTS}
    return b.seal(dict(schema="p984d-apc-companion-native-inputs-v1",family="A_PC",
        source_bindings=b.bind(sorted(paths)),initial_inputs=declared["initial_inputs"],
        nominal_source=pilot["nominal_source"],expected_source=seed.to_payload(),
        shared=shared,cases=cases,source_steps=1,
        source_companion_input_digest=declared["record_digest"],
        user_accepted=False,aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    declared,pilot=b.read(c.INPUTS),b.read(c.RESULTS)
    c.check(declared,pilot)
    b.require(manifest["schema"]=="p984d-apc-companion-native-inputs-v1"
        and manifest["initial_inputs"]==declared["initial_inputs"]
        and manifest["nominal_source"]==pilot["nominal_source"]
        and manifest["source_companion_input_digest"]==declared["record_digest"]
        and manifest["source_steps"]==1
        and manifest["user_accepted"] is False and manifest["aggregate_closed"] is False,
        "native companion subject/scope drift")
    paths={v["path"] for v in declared["source_bindings"]}|{SELF,TEST,c.INPUTS,c.RESULTS}
    b.require(manifest["source_bindings"]==b.bind(sorted(paths)),"source roster drift")
    shared=manifest["shared"]
    initial=b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    after=r.check_step(initial,shared["source_step"])
    seed=r.state(shared["actual_source"])
    b.require(seed.inputs==r.replace(after,dt=0)
        and shared["actual_source"]==manifest["expected_source"],"actual source stage drift")
    b.require(manifest["cases"]==[c.bind_case(seed,old) for old in declared["layout_cases"]],
        "actual source event identity/history binding drift")


def run_case(job):
    manifest,case=job
    with b.exact_backend(b.ExactBackend.FLINT),previous.data_adapter(manifest):
        row=r.execute_case(r.state(manifest["expected_source"]),case)
    print(case["case_id"],row["outcome"],row["first_failure"],flush=True)
    return row


def run(manifest,workers):
    check_manifest(manifest)
    pilot=next(case for case in manifest["cases"] if case["case_id"]==c.PILOT)
    first=run_case((manifest,pilot))
    rows=[first]
    if first["case_passed"]:
        remaining=[case for case in manifest["cases"] if case["case_id"]!=c.PILOT]
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows+=list(pool.map(run_case,[(manifest,case) for case in remaining]))
        lookup={row["case_id"]:row for row in rows}
        rows=[lookup[case["case_id"]] for case in manifest["cases"]]
    execution=b.seal(dict(manifest_digest=manifest["record_digest"],shared=manifest["shared"],
        cases=rows,native_runtime_executed=True,user_accepted=False,aggregate_closed=False))
    return b.seal(dict(schema="p984d-apc-companion-native-results-v1",
        manifest_digest=manifest["record_digest"],execution=previous.compact(execution),
        trigger_certificate=trigger_certificate(r.state(manifest["expected_source"])),
        user_accepted=False,aggregate_closed=False))


def check(manifest,record,*,numerics=False):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"]=="p984d-apc-companion-native-results-v1"
        and record["manifest_digest"]==manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False,
        "native companion result promotion")
    execution=previous.expand(record["execution"])
    b.check_digest(execution)
    b.require(execution["shared"]==manifest["shared"],"native source substitution")
    rows=execution["cases"]
    if len(rows)==1 and not rows[0]["case_passed"]:
        b.require(rows[0]["case_id"]==c.PILOT and rows[0]["first_failure"] is not None,
            "incorrect pilot stop")
        row=rows[0]
        event=row["event"]
        b.require(row["event_committed"] is False and row["continuation"]==[]
            and row["final_reads"]=={} and row["first_failure"]["stage"]=="event"
            and event["failure"]["code"]=="invalid_topology_event"
            and event["failure"]["message"]=="source is not a fresh hybrid spark candidate"
            and event["source_checkpoint"]==event["checkpoint"]
            and event["actual_target"]==manifest["expected_source"]
            and event["publication"]==[]
            and len(event["admission_reads"])==1
            and event["detections"][0]["candidate_node_ids"]==[]
            and len(event["receipts"])==1
            and event["receipts"][0]==event["failure"]["failure_receipt"],
            "failed trigger/whole-lifecycle rollback evidence drift")
        # Authenticate the fresh both-role source reads, not a stale candidate list.
        admission=event["admission_reads"][0]
        seed=r.state(manifest["expected_source"])
        b.require(admission["inputs"]==seed.inputs.to_payload()
            and event["detections"][0]["current"]==admission["read"]["J"]
            and event["detections"][0]["published_state"]==seed.scientific_digest,
            "fresh trigger source/current drift")
        r.check_read(seed.inputs,admission["read"],numerics=numerics)
        r.check_read(r.role_input(seed.inputs,"reset"),admission["reset_read"],numerics=numerics)
        cert=record["trigger_certificate"]
        lo,hi=map(Q,cert["squared_norm_interval"])
        b.require(cert["source_state_digest"]==seed.scientific_digest
            and Q(cert["strict_upper_required"])==Q(seed.specialization.resolved["spark"]["gradient_tolerance"])**2
            and lo<=hi and lo>=Q(cert["strict_upper_required"])
            and cert["gradient_gate_passes"] is False and cert["gradient_gate_excluded"] is True,
            "trigger exclusion drift")
        if numerics:b.require(cert==trigger_certificate(seed),"independent gradient bounds drift")
        subset=deepcopy(manifest)
        subset["cases"]=[next(case for case in manifest["cases"] if case["case_id"]==c.PILOT)]
    else:
        subset=manifest
    with previous.data_adapter(manifest):
        checked=r.validate(subset,execution,numerics=numerics)
    return dict(status="positive_native_companion_pending_acceptance" if checked["cases_passed"]==20 else "incomplete_companion",
        cases_required=20,native_cases=sum("event" in row for row in rows),
        native_event_attempts=sum("event" in row for row in rows),
        committed_events=sum(row["event_committed"] for row in rows),
        passed_cases=checked["cases_passed"],successful_history_cells=2*checked["cases_passed"],
        accepted_cells=0,source_steps=1,target_steps=sum(len(row["continuation"]) for row in rows),
        final_reads=sum(len(row["final_reads"]) for row in rows),
        failures=[dict(case_id=row["case_id"],first_failure=row["first_failure"]) for row in rows if not row["case_passed"]],
        trigger_certificate=record["trigger_certificate"],
        native_trajectories_rerun=False,interval_equations_recomputed=numerics,
        uniform_neighborhood_proved=False,accumulated_trajectory_error_bound=False,
        user_accepted=False,aggregate_closed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare",action="store_true")
    mode.add_argument("--run",action="store_true")
    mode.add_argument("--check",action="store_true")
    parser.add_argument("--workers",type=int,default=3)
    parser.add_argument("--recheck-numerics",action="store_true")
    args=parser.parse_args()
    b.require(1<=args.workers<=4 and (not args.recheck_numerics or args.check),"invalid options")
    if args.prepare:
        b.write_new(INPUTS,make_manifest())
        print("One native source beat retained; no events executed")
        return
    manifest=b.read(INPUTS)
    if args.run:
        result=run(manifest,args.workers)
        b.write_new(RESULTS,result)
    else:
        result=b.read(RESULTS)
    print(json.dumps(check(manifest,result,numerics=args.recheck_numerics),indent=2))


if __name__=="__main__":main()
