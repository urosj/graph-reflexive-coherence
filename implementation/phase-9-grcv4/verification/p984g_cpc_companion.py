"""Separately declared C_PC allocation/source companion after original exclusion."""
import argparse
from copy import deepcopy
import json
import p984g_cpc as g
import p984g_cci_feasibility as leading
import p984g_apc_feasibility as simplex
import prepare_p983_all_realizations as mechanical
from p9_cpc_compute import worker

b,q = g.b,g.q
SELF=b.HERE+"p984g_cpc_companion.py"
INPUTS=b.BASE+"P9-8.4g-CPCCompanionInputs.json"
RESULTS=b.BASE+"P9-8.4g-CPCCompanionResults.json"


def companion(shares,perturb):
    old=g.storage.read(g.PREPARED)
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
        state=mechanical.make_state(graph,profile,spec,roles,"C_PC")
        old["source"].update(mechanical.identities(state))
        request=dict(old["event_request"],operation_id="p984g-cpc-companion" if perturb else "p984g-cpc-allocation",
            source_state_digest=state.scientific_digest,resource_distribution=list(map(float,shares)),
            history_policy=mechanical.expansion.cpc_history_policy(roles["current"],roles["reset"]))
        plan=mechanical.expansion.GRC9V4ExpansionPlan(graph,state.scientific_digest,
            mechanical.expansion.GRC9V4ExpansionRequestInput.from_payload(request),
            mechanical.expansion.GRC9ExpansionPolicy.from_payload(old["specialization"]["resolved"]["expansion"]))
        profile=mechanical.profile_for(plan.target_graph,"C_PC",old["selected_configuration"])
    matrix=leading.transfer_matrix(graph.live_node_ids,plan.target_graph.live_node_ids,plan.event_id,source,shares)
    target=dict(graph=plan.target_graph.to_envelope(),profile=profile.to_payload(),roles={})
    for role,s in old["source"]["roles"].items():
        c=[sum((x*q(y) for x,y in zip(row,s["C"],strict=True)),q(0)) for row in matrix]
        b.require(all(q(float(x))==x for x in c) and sum(c,q(0))==200,"exact target resource transfer")
        target["roles"][role]=dict(C=list(map(float,c)),W_A=None,Z_4=dict(recipe="zero_v1"))
    old.update(target=target,event_request=request,event_id=plan.event_id)
    return b.seal(old),dict(shares=list(map(str,shares)),source_deficit=str(delta),
        compensation_node=remote,compensation_distance=distance,
        carrier_policy="whole_carrier_reset_with_loss_receipt_v1",identity_scope="prebeat_mechanical_declaration")


def manifest():
    original=g.storage.read(g.PREPARED)
    exclusion=g.storage.read(g.RESULTS)
    b.check_digest(exclusion)
    b.require(not exclusion["ready_for_native"] and any(x["negative_resources"] for x in exclusion["cases"]),"original exclusion required")
    # The C leading operator is L^2 C at the unit reference; its affine resource
    # constraints are shared algebra, not an inherited CI admission theorem.
    constraints={role:leading.leading_constraints(original["target"],role) for role in g.ROLES}
    selected=simplex.select(constraints)
    adjusted,identity=companion(selected["shares"],True)
    allocated,allocation=companion(selected["shares"],False)
    return b.seal(dict(schema="p984g-cpc-companion-inputs-v1",family="C_PC",
        original_exclusion_digest=exclusion["record_digest"],constraints=constraints,selection=selected,
        adjusted=adjusted,companion=identity,allocation_only=allocated,allocation=allocation,
        source_bindings=b.bind({SELF,g.SELF,g.INPUTS,g.RESULTS,g.PREPARED,leading.SELF,simplex.SELF,
            b.HERE+"prepare_p983_all_realizations.py",b.HERE+"p9_cpc_compute.py"}),
        changed_tolerances=False,changed_step_size=False,user_accepted=False,aggregate_closed=False))


def calculate(m):
    b.check_digest(m);b.check_bindings(m["source_bindings"])
    rows=g.calculate(m["adjusted"])
    diagnostics=[]
    with g.ctx.workprec(g.BITS):
        for role in g.ROLES:
            allocation=g.first_step(m["allocation_only"]["target"],role)
            row=next(r for r in rows if r["graph"]=="source" and r["role"]==role)
            bounds=[g.a(v["lower"]).union(g.a(v["upper"])) for v in row["next_resources"]]
            trigger=leading.trigger_envelope(m["adjusted"],bounds)
            b.require(trigger["saturated"] and trigger["small_gradient"] and trigger["strict_hessian_condition"],"postbeat trigger unproved")
            diagnostics.append(dict(role=role,allocation_only_first_step=allocation,source_postbeat_trigger=trigger))
    b.require(all(r["first_step_nonnegative"] for r in rows),"companion remains inadmissible")
    return b.seal(dict(schema="p984g-cpc-companion-results-v1",manifest_digest=m["record_digest"],
        cases=rows,diagnostics=diagnostics,ready_for_native=True,native_steps=0,native_events=0,
        user_accepted=False,aggregate_closed=False))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","run","check"))
    args=parser.parse_args()
    if args.action=="prepare":
        m=manifest();g.storage.save(INPUTS,m)
        print(json.dumps(dict(selection=m["selection"],companion=m["companion"]),indent=2))
    else:
        value=calculate(g.storage.read(INPUTS))
        if args.action=="run":g.storage.save(RESULTS,value)
        else:b.require(value==g.storage.read(RESULTS),"companion scientific drift")
        print(json.dumps(dict(ready_for_native=value["ready_for_native"],cases=len(value["cases"])),indent=2))
