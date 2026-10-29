"""C_CI_PC signed-order and full-chart covariance, both complete carrier histories."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import replace
import json
from unittest.mock import patch

import p984d_ccipc as deep
import p984e_cos as ordering
import p984f_cos as chart
from p9_ccipc_compute import worker
from pygrc.models.grc_9_v4_expansion import ccipc_profile_template, cpc_history_policy

b, r = deep.b, deep.r
SELF = b.HERE + "p984ef_ccipc.py"
POLICY = dict(norm="componentwise_abs_plus_relative", atol=2e-13, rtol=2e-13)
ROLES = r.ROLES


def paths(checkpoint):
    b.require(checkpoint in ("e", "f"), "unknown covariance checkpoint")
    stem = b.BASE + "P9-8.4" + checkpoint + "-CCIPC"
    return stem + "Inputs.json", stem + "Results.json.xz"


def algebra(d):
    return chart if "ports" in d else ordering


def transform(value, d):
    before = b.GeometryStageInputs.from_payload(value)
    p = deepcopy(value)
    original = p["reference"]["graph"]
    if "ports" in d:
        graph = chart.transported_graph(original, d)
        # Retain the source-first representation used by the small fixture.
        graph["live_node_ids"] = ["s", *range(1, 10)]
        rename = lambda x: chart.label(x, d)
    else:
        nodes, edges = ordering.labels(d)
        rename = lambda x: ordering.renamed(x, nodes, edges)
        graph = deepcopy(original)
        graph["live_node_ids"] = [rename(original["live_node_ids"][i]) for i in d["node_order"]]
        graph["edges"] = []
        for i in d["edge_order"]:
            edge = deepcopy(original["edges"][i])
            edge["edge_id"] = rename(edge["edge_id"])
            for end in ("tail", "head"):
                edge[end]["node_id"] = rename(edge[end]["node_id"])
            if d["signs"][i] < 0:
                edge["tail"], edge["head"] = edge["head"], edge["tail"]
            graph["edges"].append(edge)
    ni, ei, signs = algebra(d).mapping(original, graph, d)
    signs = [int(x) for x in signs]
    ref = p["reference"]
    ref["graph"] = graph
    for owner, name in ((ref, "K4_base"), (p, "H1_form")):
        old = owner[name]
        owner[name] = [[old[i][j]*signs[k]*signs[l] if old[i][j] else 0.0
                        for l,j in enumerate(ei)] for k,i in enumerate(ei)]
    for weights in (ref["reference_hodge"]["edge_weights"], ref["profile"]["params_resolved"]["candidate"]["W_C_tr"]):
        items = list(weights.items())
        weights.clear()
        weights.update({rename(k): v for k,v in items})
    ordering.reidentify(ref)
    reference = b.GRCV4ReferenceGeometry.from_payload(ref)
    roles = {role:b.GRCV4AuthoritativeState(tuple(value[role]["C"][i] for i in ni), None,
        tuple(value[role]["Z_4"][i*9+j]*signs[k]*signs[l] if value[role]["Z_4"][i*9+j] else 0.0
              for k,i in enumerate(ei) for l,j in enumerate(ei))) for role in ROLES}
    return replace(before, geometry=b.GRCV4Geometry(reference,
        b.OneFormHodge(reference.graph, tuple(map(tuple,p["H1_form"])))), **roles)


def make_manifest(checkpoint):
    old = deep.read(deep.INPUTS)
    deep.check_manifest(old)
    result = deep.read(deep.RESULTS)
    b.check_digest(result)
    execution = deep.previous.expand(result["execution"])
    b.require(len(execution["cases"]) == 20 and all(x["case_passed"] for x in execution["cases"]), "deep prerequisite incomplete")
    small = deep.read(r.INPUTS)["cases"]
    selections = [(small,52,1,1),(old["cases"],94,-1,3)] if checkpoint == "e" else [
        (small,degree,ch,None if degree == 45 else 1) for degree in (45,52) for ch in (1,-1)]
    cases = [next(c for c in rows if tuple(c["request"][k] for k in
        ("target_effective_degree","module_chirality","growth_phase")) == (degree,ch,phase))
        for rows,degree,ch,phase in selections]
    transforms = (ordering if checkpoint == "e" else chart).declarations()
    return b.seal(dict(schema="p984ef-ccipc-inputs-v1", checkpoint=checkpoint, family="C_CI_PC",
        source_bindings=b.bind(deep.numerical_paths() | {SELF, ordering.SELF, chart.SELF, deep.INPUTS, deep.RESULTS, b.HERE+"p9_ccipc_targets.py"}),
        initial_inputs=old["initial_inputs"], expected_source=old["expected_source"], cases=cases,
        transforms=transforms, comparison=POLICY, steps_per_role=2,
        user_accepted=False, aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m)
    b.check_bindings(m["source_bindings"])
    b.require(m == make_manifest(m["checkpoint"]), "covariance declaration drift")


def expected_case(seed, case, d, checkpoint):
    c = deepcopy(case)
    request = c["request"]
    ref = seed.inputs.geometry.reference
    if "ports" in d:
        shares = [0.0]*3
        for i,share in enumerate(request["resource_distribution"],1):
            shares[d["branches"][str(i)]-1] = share
        request.update(resource_distribution=shares,
            module_chirality=request["module_chirality"]*d["chirality_factor"],
            growth_phase=None if request["growth_phase"] is None else d["branches"][str(request["growth_phase"])])
        node = "s"
    else:
        node = ordering.labels(d)[0]["s"]
    request.update(source_node_id=node, source_state_digest=seed.scientific_digest,
        source_graph_digest=ref.graph.graph_digest, target_profile_template_id=ccipc_profile_template(ref).profile_template_id,
        history_policy=cpc_history_policy(seed.inputs.current, seed.inputs.reset),
        operation_id="p984"+checkpoint+"-ccipc-"+case["fixture_id"]+"-"+d["kind"])
    identity = deepcopy(case["oracle"]["event_identity"])
    for key in identity:
        if key in request and key != "schema_version":
            identity[key] = request[key]
    for channel in ("candidate", "carrier"):
        key = channel+"_history_policy_digest"
        identity[key] = request["history_policy"][key]
    event = "grc-event-sha256:"+b.digest(identity)
    graph = algebra(d).transported_graph(case["oracle"]["target_graph"], d, case["oracle"]["event_id"], event)
    c["oracle"] = dict(event_identity=identity, event_id=event, target_graph=graph)
    return c


from p9_ccipc_targets import target


def checked_event(seed, case, event, numerics=False):
    # Generalize only the independent data constructor. All native producers,
    # certificate checks, charge, archive and receipt consumers remain intact.
    with patch.object(r, "independent_target", target):
        return r.check_event(seed, case, event, numerics=numerics)


def execute(job):
    m,d = job
    with worker():
        before = transform(m["initial_inputs"],d)
        step,value = r.perform_step(before)
        seed = replace(r.state(m["expected_source"]), inputs=replace(step.next_inputs,dt=0))
        source = dict(kind=d["kind"],step=value,state=seed.to_payload())
        rows = []
        for case in m["cases"]:
            c = expected_case(seed,case,d,m["checkpoint"])
            owner = r.native.GRC9V4CCIPCOperation(seed)
            checkpoint = owner.checkpoint()
            stale = dict(c["request"],source_state_digest="grcv4-state-sha256:"+"0"*64)
            rejected = owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(stale))
            b.require(not rejected.committed and owner.checkpoint()==checkpoint,"stale publication rollback")
            owner,outcome,event = r.event_capture(seed,b.GRC9V4ExpansionRequestInput.from_payload(c["request"]))
            b.require(outcome.committed,"covariance event rejected: "+str(outcome.failure))
            actual = checked_event(seed,c,event)
            roles = {}
            for role in ROLES:
                incoming = r.role_input(actual.inputs,role,dt=b.DT)
                steps = []
                for _ in range(2):
                    step,value = r.perform_step(incoming)
                    incoming = step.next_inputs
                    steps.append(value)
                roles[role] = dict(steps=steps,final=r.certified_read(r.CandidateCIRoot(replace(incoming,dt=0))))
            rows.append(dict(layout=case["fixture_id"],kind=d["kind"],case=c,event=event,roles=roles,
                stale_failure=rejected.failure.to_payload(),rollback_exact=True))
    print(m["checkpoint"],d["kind"],"completed",flush=True)
    return source,rows


def pair(a,c,indices):
    ni,ei,signs = indices
    errors = []
    for key in ("J","read_current","baseline","readback","flat","H","source"):
        av = b.np.asarray(a[key])
        expected = av[b.np.ix_(ei,ei)]*b.np.outer(signs,signs) if av.ndim==2 else av[ei]*signs
        errors.append(b.comparison(c[key],expected,POLICY,"C_CI_PC_covariance_"+key)["maximum_error"])
    return max(errors)


def state_pair(a,c,indices):
    ni,ei,signs = indices
    errors = []
    for role in ROLES:
        b.require(a[role]["W_A"] is None and c[role]["W_A"] is None,"invented candidate history")
        errors.append(b.comparison(c[role]["C"],b.np.asarray(a[role]["C"])[ni],POLICY,"resource_covariance")["maximum_error"])
        m = len(ei)
        z = b.np.asarray(a[role]["Z_4"]).reshape(m,m)
        errors.append(b.comparison(b.np.asarray(c[role]["Z_4"]).reshape(m,m),
            z[b.np.ix_(ei,ei)]*b.np.outer(signs,signs),POLICY,"whole_carrier_covariance")["maximum_error"])
    return max(errors)


def check(m, record, numerics=False):
    check_manifest(m)
    b.check_digest(record)
    b.require(record["manifest_digest"]==m["record_digest"] and not record["user_accepted"]
              and not record["aggregate_closed"],"covariance scope drift")
    data = deep.previous.expand(record["execution"])
    sources,rows = data["sources"],data["cases"]
    b.require([x["kind"] for x in sources]==[d["kind"] for d in m["transforms"]],"source roster")
    b.require([(x["kind"],x["layout"]) for x in rows]==[(d["kind"],c["fixture_id"])
        for d in m["transforms"] for c in m["cases"]],"case roster")
    maximum = 0.0
    signed = {}
    def read_check(before,value):
        r.check_read(before,value,numerics=numerics)
        key = b.digest([before.identity,value["record_digest"]])
        if key not in signed:
            cert = value["independent_certificate"]
            b.require(cert["input_identity"]==before.identity and cert["selected_read_digest"]==value["record_digest"]
                and all(0<=r.Q(cert["bounds"][k])<r.LIMITS[k] for k in ("flat_error","readback_error")),"signed operand drift")
            signed[key]=cert
    def step_check(before,value):
        after=r.check_step(before,value,numerics=numerics)
        for operand,read in ((before,value["read"]),(r.role_input(before,"reset"),value["reset_read"]),
                             (replace(after,dt=0),value["restart"])):
            read_check(operand,read)
        return after
    with worker():
        for source,d in zip(sources,m["transforms"],strict=True):
            before=transform(m["initial_inputs"],d)
            after=step_check(before,source["step"])
            seed=replace(r.state(m["expected_source"]),inputs=replace(after,dt=0))
            b.require(seed.to_payload()==source["state"],"source poststate drift")
            ix=algebra(d).mapping(m["initial_inputs"]["reference"]["graph"],before.geometry.reference.graph.to_payload(),d)
            maximum=max(maximum,state_pair(sources[0]["state"]["inputs"],source["state"]["inputs"],ix))
            for key in ("read","reset_read","restart"):
                maximum=max(maximum,pair(sources[0]["step"][key],source["step"][key],ix))
            for case in m["cases"]:
                row=next(x for x in rows if x["kind"]==d["kind"] and x["layout"]==case["fixture_id"])
                base=next(x for x in rows if x["kind"]=="base" and x["layout"]==case["fixture_id"])
                c=expected_case(seed,case,d,m["checkpoint"])
                b.require(row["case"]==c and row["rollback_exact"] and row["stale_failure"],"case/rollback drift")
                actual=checked_event(seed,c,row["event"],numerics)
                bg=base["event"]["actual_target"]["inputs"]["reference"]["graph"]
                tg=actual.inputs.geometry.reference.graph.to_payload()
                ix=algebra(d).mapping(bg,tg,d,base["case"]["oracle"]["event_id"],c["oracle"]["event_id"])
                maximum=max(maximum,state_pair(base["event"]["actual_target"]["inputs"],actual.inputs.to_payload(),ix))
                for parent,reads in zip((seed,actual),row["event"]["admission_reads"],strict=True):
                    read_check(parent.inputs,reads["read"])
                    read_check(r.role_input(parent.inputs,"reset"),reads["reset_read"])
                b.require(set(row["roles"])==set(ROLES),"history roster")
                for role in ROLES:
                    rr,br=row["roles"][role],base["roles"][role]
                    incoming=r.role_input(actual.inputs,role,dt=b.DT)
                    b.require(len(rr["steps"])==2,"continuation horizon")
                    for value,ref in zip(rr["steps"],br["steps"],strict=True):
                        incoming=step_check(incoming,value)
                        maximum=max(maximum,state_pair(ref["poststate"],value["poststate"],ix))
                        for key in ("read","reset_read","restart"):
                            maximum=max(maximum,pair(ref[key],value[key],ix))
                    read_check(replace(incoming,dt=0),rr["final"])
                    maximum=max(maximum,pair(br["final"],rr["final"],ix))
    b.require("signed" not in record or record["signed"]==signed,"signed certificate roster")
    return dict(family="C_CI_PC",checkpoint=m["checkpoint"],events=len(rows),target_steps=4*len(rows),
        final_reads=2*len(rows),source_steps=len(sources),maximum_covariance_error=maximum,
        required_history_cells=2*len(m["cases"])*(len(m["transforms"])-1),signed_reads=len(signed),
        user_accepted=False,aggregate_closed=False),signed


def run(checkpoint, workers=2):
    inputs, results = paths(checkpoint)
    m=deep.read(inputs)
    check_manifest(m)
    journal=b.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated/phase9-verification'/('ccipc-covariance-'+m['record_digest'])
    journal.mkdir(parents=True,exist_ok=True)
    completed={}
    for d in m['transforms']:
        path=journal/(d['kind']+'.json.xz')
        if path.exists():
            value=deep.read(path);b.check_digest(value)
            b.require(value['manifest_digest']==m['record_digest'] and value['kind']==d['kind'],'covariance journal binding')
            completed[d['kind']]=value['output']
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending={pool.submit(execute,(m,d)):d for d in m['transforms'] if d['kind'] not in completed}
        for future in as_completed(pending):
            d=pending[future];output=future.result()
            value=b.seal(dict(manifest_digest=m['record_digest'],kind=d['kind'],output=output))
            deep.save(journal/(d['kind']+'.json.xz'),value)
            completed[d['kind']]=output
    output=[completed[d['kind']] for d in m['transforms']]
    record=b.seal(dict(schema='p984ef-ccipc-results-v1',manifest_digest=m['record_digest'],
        execution=deep.previous.compact(dict(sources=[x[0] for x in output],cases=[r for x in output for r in x[1]])),
        user_accepted=False,aggregate_closed=False))
    status,signed=check(m,record)
    record=b.seal(dict(record,signed=signed))
    deep.save(results,record)
    return status


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint",choices=("e","f"))
    parser.add_argument("action",choices=("prepare","run","check"))
    parser.add_argument("--numerics",action="store_true")
    args=parser.parse_args()
    inputs,results=paths(args.checkpoint)
    if args.action=="prepare":
        deep.save(inputs,make_manifest(args.checkpoint))
    elif args.action=="check":
        print(json.dumps(check(deep.read(inputs),deep.read(results),args.numerics)[0],indent=2))
    else:
        print(json.dumps(run(args.checkpoint),indent=2))
