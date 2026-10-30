"""Separately declared A_CI_PC allocation/source companion after original exclusion."""
import argparse
import json
import p984g_acipc as g
import p984g_aci_feasibility as leading
import p984g_cci_feasibility as trigger_math
import p984g_apc_feasibility as simplex
import prepare_p983_all_realizations as mechanical
from p9_acipc_compute import worker

import p984d_acipc as storage
from copy import deepcopy

b,q = g.b,g.q
SELF=b.HERE+"p984g_acipc_companion.py"
INPUTS=b.BASE+"P9-8.4g-ACIPCCompanionInputs.json"
RESULTS=b.BASE+"P9-8.4g-ACIPCCompanionResults.json.xz"


def companion(shares,perturb):
    old=storage.read(g.PREPARED)
    shares=list(map(q,shares))
    graph=mechanical.GRC9V4PortGraph.from_envelope(old["source"]["graph"])
    source=old["event_request"]["source_node_id"]
    remote,distance=simplex.compensation_node(old["source"]["graph"],source)
    delta=4*q(old["selected_configuration"]["ordinary_dt"]) if perturb else q(0)
    for authority in old["source"]["roles"].values():
        for node,change in ((source,-delta),(remote,delta)):
            i=graph.live_node_ids.index(node)
            value=q(authority["C"][i])+change
            b.require(value>=0 and q(float(value))==value,"exact source resource shift")
            authority["C"][i]=float(value)
    profile=mechanical.GRCV4Profile.from_canonical_bytes(mechanical.canonical_json_bytes(old["source"]["profile"]))
    spec=mechanical.native.GRC9V4Specialization(mechanical.FrozenJSONMap(old["specialization"]["resolved"]),
        mechanical.FrozenJSONMap(old["specialization"]["identity_payload"]))
    roles={role:mechanical.authority(v,len(graph.edges)) for role,v in old["source"]["roles"].items()}
    with worker():
        state=mechanical.make_state(graph,profile,spec,roles,"A_CI_PC")
        old["source"].update(mechanical.identities(state))
        request=dict(old["event_request"],operation_id="p984g-acipc-companion" if perturb else "p984g-acipc-allocation",
            source_state_digest=state.scientific_digest,resource_distribution=list(map(float,shares)),
            history_policy=mechanical.expansion.apc_history_policy(roles["current"],roles["reset"]))
        plan=mechanical.expansion.GRC9V4ExpansionPlan(graph,state.scientific_digest,
            mechanical.expansion.GRC9V4ExpansionRequestInput.from_payload(request),
            mechanical.expansion.GRC9ExpansionPolicy.from_payload(old["specialization"]["resolved"]["expansion"]))
        profile=mechanical.profile_for(plan.target_graph,"A_CI_PC",old["selected_configuration"])
    matrix=trigger_math.transfer_matrix(graph.live_node_ids,plan.target_graph.live_node_ids,plan.event_id,source,shares)
    target=dict(graph=plan.target_graph.to_envelope(),profile=profile.to_payload(),roles={})
    for role,s in old["source"]["roles"].items():
        c=[sum((x*q(y) for x,y in zip(row,s["C"],strict=True)),q(0)) for row in matrix]
        b.require(all(q(float(x))==x for x in c) and sum(c,q(0))==200,"exact target resource transfer")
        weights=dict(zip((e.edge_id for e in graph.edges),s['W_A'],strict=True))
        target["roles"][role]=dict(C=list(map(float,c)),
            W_A=[weights.get(e.edge_id,plan.policy.bond_seed) for e in plan.target_graph.edges],Z_4=dict(recipe="zero_v1"))
    old.update(target=target,event_request=request,event_id=plan.event_id)
    return b.seal(old),dict(shares=list(map(str,shares)),source_deficit=str(delta),
        compensation_node=remote,compensation_distance=distance,
        carrier_policy="whole_carrier_reset_with_loss_receipt_v1",identity_scope="prebeat_mechanical_declaration")


def manifest():
    original=storage.read(g.PREPARED)
    exclusion=storage.read(b.BASE+"P9-8.4g-ACIPCInvestigation.json")
    b.check_digest(exclusion)
    b.require(any(x["negative_vertices"] for x in exclusion["cases"]),"original exclusion required")
    # The A unit-reference leading operator is L_W squared. It selects
    # allocations only; the composite enabled law receives its own certificate.
    constraints={role:leading.leading_constraints(g.ci_operand(original["target"],role),role) for role in g.ROLES}
    selected=simplex.select(constraints)
    adjusted,identity=companion(selected["shares"],True)
    allocated,allocation=companion(selected["shares"],False)
    return b.seal(dict(schema="p984g-acipc-companion-inputs-v1",family="A_CI_PC",
        original_exclusion_digest=exclusion["record_digest"],constraints=constraints,selection=selected,
        adjusted=adjusted,companion=identity,allocation_only=allocated,allocation=allocation,
        source_bindings=b.bind({SELF,g.SELF,b.BASE+"P9-8.4g-ACIPCInvestigation.json",g.PREPARED,leading.SELF,simplex.SELF,
            b.HERE+"prepare_p983_all_realizations.py",b.HERE+"p9_acipc_compute.py"}),
        changed_tolerances=False,changed_step_size=False,user_accepted=False,aggregate_closed=False))


def calculate(m):
    b.check_digest(m);b.check_bindings(m["source_bindings"])
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(first,[(m['adjusted'],name,role) for name in ('source','target') for role in g.ROLES]))
    b.require(all(not row['negative_vertices'] and not row['unresolved_vertices'] for row in rows),'companion positivity unproved')
    return b.seal(dict(schema='p984g-acipc-companion-results-v1',manifest_digest=m['record_digest'],
        cases=rows,ready_for_native=True,native_steps=0,native_events=0,user_accepted=False,aggregate_closed=False))


def first(job):
    declaration,name,role=job
    with g.ctx.workprec(g.BITS):
        value=g.first_step(declaration[name],role,declaration['selected_configuration']['ordinary_dt'])
    print(name,role,'minimum',float(q(value['minimum_lower'])),flush=True)
    return dict(graph=name,subject_digest=b.digest(declaration[name]),**value)



if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","run","check"))
    args=parser.parse_args()
    if args.action=="prepare":
        m=manifest();storage.save(INPUTS,m)
        print(json.dumps(dict(selection=m["selection"],companion=m["companion"]),indent=2))
    else:
        value=calculate(storage.read(INPUTS))
        if args.action=="run":storage.save(RESULTS,value)
        else:
            retained=storage.read(RESULTS)
            def scientific(v):
                if isinstance(v,dict):return {k:scientific(x) for k,x in v.items() if k not in ("seconds","record_digest")}
                if isinstance(v,list):return list(map(scientific,v))
                return v
            b.require(scientific(value)==scientific(retained),"companion scientific drift")
        print(json.dumps(dict(ready_for_native=value["ready_for_native"],cases=len(value["cases"])),indent=2))
