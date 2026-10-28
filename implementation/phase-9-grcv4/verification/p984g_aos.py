"""Large A_OS staged and exact two-pass equations, never a CI-root certificate."""

import argparse
from copy import deepcopy
import json
import lzma

import p984d_aos_oracle as storage
import p984g_aci_staged as scalar
import p984g_apc_feasibility as selection
import prepare_p983_all_realizations as mechanical

b = storage.b
f = scalar.feasible
q, a, lo, hi = scalar.q, scalar.a, scalar.lo, scalar.hi
SELF = b.HERE + "p984g_aos.py"
TEST = b.HERE + "test_p984g_aos.py"
PLAN = b.BASE + "P9-8.4g-AOSPlan.md"
PREPARED = b.BASE + "larger-graph-examples/A_OS.json"
INPUTS = b.BASE + "P9-8.4g-AOSInputs.json"
RESULTS = b.BASE + "P9-8.4g-AOSResults.json.xz"
ROLES = ("current", "reset")


def companion(shares, *, perturb):
    shares = tuple(map(q, shares))
    original = storage.read(PREPARED)
    graph = mechanical.GRC9V4PortGraph.from_envelope(original["source"]["graph"])
    source_node = original["event_request"]["source_node_id"]
    remote, distance = selection.compensation_node(original["source"]["graph"], source_node)
    delta = 4 * q(original["selected_configuration"]["ordinary_dt"]) if perturb else q(0)
    for state in original["source"]["roles"].values():
        for node, change in ((source_node, -delta), (remote, delta)):
            i = graph.live_node_ids.index(node)
            value = q(state["C"][i]) + change
            b.require(value >= 0 and q(float(value)) == value, "exact nonnegative source shift")
            state["C"][i] = float(value)
    profile = mechanical.GRCV4Profile.from_canonical_bytes(mechanical.canonical_json_bytes(original["source"]["profile"]))
    spec = mechanical.native.GRC9V4Specialization(mechanical.FrozenJSONMap(original["specialization"]["resolved"]),
                                                mechanical.FrozenJSONMap(original["specialization"]["identity_payload"]))
    states = {role:mechanical.authority(s, len(graph.edges)) for role, s in original["source"]["roles"].items()}
    with mechanical.exact_backend(mechanical.ExactBackend.FLINT):
        state = mechanical.make_state(graph, profile, spec, states, "A_OS")
        original["source"].update(mechanical.identities(state))
        request = deepcopy(original["event_request"])
        request.update(operation_id="p984g-aos-companion" if perturb else "p984g-aos-allocation",
            source_state_digest=state.scientific_digest, resource_distribution=list(map(float, shares)),
            history_policy=mechanical.expansion.aos_history_policy(states["current"], states["reset"]))
        plan = mechanical.expansion.GRC9V4ExpansionPlan(graph, state.scientific_digest,
            mechanical.expansion.GRC9V4ExpansionRequestInput.from_payload(request),
            mechanical.expansion.GRC9ExpansionPolicy.from_payload(original["specialization"]["resolved"]["expansion"]))
        target = dict(graph=plan.target_graph.to_envelope(),
            profile=mechanical.profile_for(plan.target_graph, "A_OS", original["selected_configuration"]).to_payload(), roles={})
    share_map = {plan.event_id + f"/satellite/{i+1}":q(x) for i,x in enumerate(shares)}
    for role, source in original["source"]["roles"].items():
        cs = dict(zip(graph.live_node_ids, map(q, source["C"]), strict=True))
        ws = dict(zip((e.edge_id for e in graph.edges), source["W_A"], strict=True))
        values = [cs[n] if n in cs else share_map.get(n,q(0))*cs[source_node] for n in plan.target_graph.live_node_ids]
        b.require(sum(values,q(0)) == sum(cs.values(),q(0)) and all(q(float(x)) == x for x in values), "exact target transfer")
        target["roles"][role] = dict(C=list(map(float,values)), W_A=[ws.get(e.edge_id,1.0) for e in plan.target_graph.edges], Z_4=None)
    original.update(target=target, event_request=request, event_id=plan.event_id)
    return b.seal(original), dict(shares=list(map(str, map(q, shares))), source_deficit=str(delta),
                         compensation_node=remote, compensation_distance=distance,
                         history_policy_unchanged=True, identity_scope="prebeat_mechanical_declaration")


def make_manifest():
    original = storage.read(PREPARED)
    constraints = {role:f.leading_constraints(original["target"], role) for role in ROLES}
    selected = selection.select(constraints)
    allocated, allocation = companion(selected["shares"], perturb=False)
    adjusted, identity = companion(selected["shares"], perturb=True)
    paths = [SELF, TEST, PLAN, PREPARED, scalar.SELF, f.SELF, f.prior.SELF,
             selection.SELF, b.HERE + "prepare_p983_all_realizations.py"]
    return b.seal(dict(schema="p984g-aos-inputs-v1", family="A_OS", source_bindings=b.bind(paths),
        leading_constraints=constraints, selection=selected, allocation=allocation, companion=identity,
        original=original, allocation_only=allocated, adjusted=adjusted,
        precision_bits=scalar.BITS, policy="fixed_192_bit_Arb_no_retry",
        numerical_scope="pointwise_exact_two_pass_OS_at_saved_entries_not_CI_or_uniform_trajectory",
        user_accepted=False, aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m)
    b.check_bindings(m["source_bindings"])
    b.require(m == make_manifest(), "large A_OS declaration drift")


def analyze(subject, role, dt):
    """Independent exact-real OS composition alongside explicit binary64 staging."""
    b.require(subject["profile"]["identity_payload"]["profile_family_id"] == "A_OS", "A_OS only")
    with scalar.ctx.workprec(scalar.BITS):
        md = scalar.model(subject, role)
        ident = scalar.eye(len(md["w"]))
        predictor = scalar.represented(md, ident)
        h = scalar.image(md, predictor["flat"], staged=True)
        corrector = scalar.represented(md, h)
        regenerated = scalar.image(md, corrector["flat"], staged=True)
        exact_predictor = scalar.analytic(md, ident)
        exact_h = scalar.image(md, exact_predictor["flat"], staged=False)
        exact_corrector = scalar.analytic(md, exact_h)
        exact_regenerated = exact_corrector["generated"]
        split = scalar.norm(exact_h-exact_regenerated)
        geometry = scalar.norm(exact_h-ident)
        b.require(split < q(subject["profile"]["params_resolved"]["realization"]["tolerance"])
                  and geometry < q("1/2"), "OS geometry/split domain")
        margin = min(lo(x) for x in exact_corrector["block"])
        b.require(margin > q("1/2"), "OS regularity")
        rate = md["b"]*exact_corrector["J"]
        after = [a(x)-a(dt)*rate[i,0] for i,x in enumerate(md["c"])]
        error = max(hi(abs(a(x)-exact_corrector["J"][i,0])) for i,x in enumerate(corrector["current"]))
        represented_c = [float(c)-float(dt)*sum(float(x)*j for x,j in zip(row,corrector["current"],strict=True))
                         for c,row in zip(md["c"],md["bv"],strict=True)]
        writer = None
        if min(represented_c) >= 0:
            # Same fixed scalar writer equations, with the OS-selected J.
            from p984g_aci_native import writer_oracle
            writer = writer_oracle(subject,role,represented_c,corrector["current"],float(dt))
        return dict(subject_digest=b.digest(subject), role=role, dt=float(dt),
            predictor=predictor, corrector=corrector,
            H=[[scalar.unique(h[i,j]) for j in range(h.ncols())] for i in range(h.nrows())],
            regenerated_digest=b.digest([[scalar.unique(regenerated[i,j]) for j in range(h.ncols())] for i in range(h.nrows())]),
            certificate=dict(split_upper=str(split),geometry_upper=str(geometry),regularity_lower=str(margin),
                current_error_upper=str(error),resource_bounds=f.pack(after),
                minimum_resource_lower=str(min(lo(x) for x in after)), minimum_resource_upper=str(min(hi(x) for x in after)),
                exact_OS_composition=True,uniform_trajectory_enclosure=False),
            represented_C=represented_c,writer=writer)


def run(m):
    check_manifest(m)
    b.require(not (b.ROOT / RESULTS).exists(), "refuse overwrite")
    rows=[]
    for variant in ("original", "allocation_only", "adjusted"):
        declaration=m[variant]
        for graph in ("source", "target"):
            for role in ROLES:
                value=analyze(declaration[graph],role,declaration["selected_configuration"]["ordinary_dt"])
                if graph == "source":
                    b.require(value["writer"] is not None,"source writer prerequisite")
                    with scalar.ctx.workprec(scalar.BITS):
                        value["represented_trigger"]=f.trigger(declaration,list(map(a,value["represented_C"])),list(map(a,value["writer"]["W_A"])))
                rows.append(dict(variant=variant,graph=graph,role=role,result=value))
                print(variant,graph,role,value["certificate"]["minimum_resource_lower"],flush=True)
    record=b.seal(dict(schema="p984g-aos-results-v1",manifest_digest=m["record_digest"],cases=rows,
        native_steps=0,native_events=0,native_runtime_executed=False,
        ready_for_8_4h=False,user_accepted=False,aggregate_closed=False))
    status=check(m,record)
    with (b.ROOT/RESULTS).open("xb") as stream:
        stream.write(lzma.compress(json.dumps(record,separators=(",",":"),allow_nan=False).encode()+b"\n"))
    return status


def check(m,r):
    check_manifest(m);b.check_digest(r)
    b.require(r["schema"]=="p984g-aos-results-v1" and r["manifest_digest"]==m["record_digest"],"large oracle identity")
    b.require([ (x["variant"],x["graph"],x["role"]) for x in r["cases"] ] ==
        [(v,g,role) for v in ("original","allocation_only","adjusted") for g in ("source","target") for role in ROLES],"large oracle roster")
    for row in r["cases"]:
        v=row["result"];c=v["certificate"];s=m[row["variant"]][row["graph"]]
        b.require(v["subject_digest"]==b.digest(s) and v["role"]==row["role"] and v["dt"]==m[row["variant"]]["selected_configuration"]["ordinary_dt"],"large oracle operand")
        b.require(c["exact_OS_composition"] and not c["uniform_trajectory_enclosure"]
            and 0<=q(c["split_upper"])<q(s["profile"]["params_resolved"]["realization"]["tolerance"])
            and 0<=q(c["geometry_upper"])<q("1/2") and q(c["regularity_lower"])>q("1/2")
            and 0<=q(c["current_error_upper"])<q("1/1000000000"),"large oracle domain/error")
        b.require(len(c["resource_bounds"])==len(s["roles"][row["role"]]["C"])
            and all(q(x["lower"])<=q(x["upper"]) for x in c["resource_bounds"]),"resource enclosure shape")
        if row["variant"]=="adjusted":
            b.require(q(c["minimum_resource_lower"])>0 and v["writer"] is not None,"companion continuation excluded")
            if row["graph"]=="source":
                b.require(v["represented_trigger"]["small_gradient"] and v["represented_trigger"]["strict_hessian_condition"],"companion source trigger")
    original=next(x["result"] for x in r["cases"] if (x["variant"],x["graph"],x["role"])==("original","target","reset"))
    b.require(q(original["certificate"]["minimum_resource_upper"])<0,"original reset exclusion lost")
    b.require(r["native_steps"]==r["native_events"]==0 and all(r[k] is False for k in
        ("native_runtime_executed","ready_for_8_4h","user_accepted","aggregate_closed")),"oracle promoted")
    return dict(family="A_OS",status="oracle_passed_native_prerequisite_pending",original_reset_excluded=True,
                companion=m["companion"],native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","run","check"))
    args=parser.parse_args()
    if args.action=="prepare":b.write_new(INPUTS,make_manifest())
    elif args.action=="run":print(json.dumps(run(storage.read(INPUTS)),indent=2))
    else:print(json.dumps(check(storage.read(INPUTS),storage.read(RESULTS)),indent=2))
