"""Bounded D94 allocation feasibility; independent equations, no native events.

Exact affine frozen-W transport is separated from interval-enclosed enabled
feedback, fresh-W and carrier corrections. This is not an ATC allocation law.
"""

from fractions import Fraction as Q
import argparse
import json
import numpy as np

import p984d_apc_runtime as prior

r, b = prior.r, prior.b
o = r.oracle
IV, number, endpoint = o.IV, o.number, o.endpoint
SELF = b.HERE + "p984d_apc_feasibility.py"
TEST = b.HERE + "test_p984d_apc_feasibility.py"
RESULTS = b.BASE + "P9-8.4d-APCAllocationFeasibility.json"
REVIEW = b.BASE + "P9-8.4d-APCAllocationFeasibility.md"


def interval(a, z):
    return IV.mpf([number(a).a, number(z).b])


def affine(coefficients, x, y):
    return IV.matrix([number(row[0])+number(row[1])*x+number(row[2])*y for row in coefficients])


def rational_matrix(values):
    return IV.matrix([[number(x) for x in row] for row in values])


def writer_extension(high,c,w,j,dt):
    """Full writer formula on an enclosure, permitting tiny negative ideal C.

    A represented admitted C can be nonnegative while its exact continuity
    reference is negative by the resource error budget. The reference used
    by the full W-error certificate must not be clipped to the actual state.
    The inactive floor is still certified; no physical input is repaired.
    """
    rows=high.rows(c,w)
    a=IV.exp(-dt)
    result=[]
    for k,edge in enumerate(high.edges):
        u,v=(high.index[edge[end]["node_id"]] for end in ("tail","head"))
        exponent=number(high.params.coefficient)*(c[u]+c[v]
            +sum((x-y)**2 for x,y in zip(rows[u],rows[v]))+j[k]**2)/2
        drive=IV.exp(-exponent)
        b.require(endpoint(drive,0)>Q(1,2),"writer floor unresolved")
        result.append(IV.exp(a*IV.ln(w[k])+(1-a)*IV.ln(drive)))
    return IV.matrix(result)


def context(manifest, case_id="P984D-D94-E-1-P3::A_PC", *, role="current"):
    b.require(role in r.ROLES, "unknown history role")
    case = next(c for c in manifest["cases"] if c["case_id"] == case_id)
    b.require(case["request"]["target_effective_degree"] == 94, "D94 proof only")
    target = r.independent_target(r.state(manifest["expected_source"]), case)
    graph = case["oracle"]["target_graph"]
    state = getattr(target.inputs,role)
    b.require(not any(state.Z_4), "proof requires zero target carrier")
    high = o.IntervalRows(o.model_for(graph))
    B = np.array([[Q(int(high.B[i,j])) for j in range(high.B.cols)] for i in range(high.B.rows)], dtype=object)
    w = np.array(list(map(Q,state.W_A)),dtype=object)
    L = B @ np.diag(w) @ B.T
    initial = np.array([[Q(v),Q(0),Q(0)] for v in state.C],dtype=object)
    source = r.state(manifest["expected_source"])
    mass = Q(getattr(source.inputs,role).C[source.inputs.geometry.reference.graph.live_node_ids.index(case["request"]["source_node_id"])])
    sites = []
    for i, coeff in enumerate(((0,1,0),(0,0,1),(1,-1,-1)),1):
        j = graph["live_node_ids"].index(case["oracle"]["event_id"]+f"/satellite/{i}")
        sites.append(j)
        initial[j] = [mass*c for c in coeff]
    M = np.eye(len(initial),dtype=int).astype(object)+Q(b.DT)*(L@L)
    return dict(case=case,graph=graph,high=high,B=B,w=w,L=L,M=M,
        initial=initial,first=M@initial,second=M@M@initial, sites=sites, mass=mass,role=role)


def enclose(ctx, bounds=(Q(0),Q(1),Q(0),Q(1)), *, represented=False):
    """Exact-real two-step extension, conditioned on first resource admission.

    The returned corrections enclose full PC equations on the rectangle's
    intersection with the closed simplex. Clipping only uses necessary domain
    conditions, never removes an admitted trajectory.
    """
    x0,x1,y0,y1 = bounds
    b.require(type(represented) is bool, "represented mode must be boolean")
    b.require(high_parameters(ctx), "frozen equation coefficients changed")
    b.require(0 <= x0 <= x1 <= 1 and 0 <= y0 <= y1 <= 1 and x0+y0<=1,"invalid simplex box")
    x,y = interval(x0,x1),interval(y0,y1)
    high=ctx["high"];B=high.B;dt=number(Q(b.DT))
    b.require(0 < ctx["mass"] < 4, "transfer rounding bound requires mass below four")
    e0=IV.matrix([interval(-Q(1,2**48),Q(1,2**48)) if represented and i in ctx["sites"] else number(0)
        for i in range(len(ctx["initial"]))])
    resource_error=interval(-r.LIMITS["resource_error"],r.LIMITS["resource_error"]) if represented else number(0)
    c=affine(ctx["initial"],x,y)+e0
    for i in range(len(c)):
        c[i]=interval(max(Q(0),endpoint(c[i],0)),endpoint(c[i],1))
    w=IV.matrix([number(v) for v in ctx["w"]])
    baseline_coeff=-np.diag(ctx["w"])@ctx["B"].T@ctx["L"]@ctx["initial"]
    K=-np.diag(ctx["w"])@ctx["B"].T@ctx["L"]
    j0=affine(baseline_coeff,x,y)+rational_matrix(K)*e0
    drive=high.conductance(c,w,j0)
    q=IV.matrix([(v-g)/(v+g) for v,g in zip(w,drive)])
    feedback=IV.matrix([j*qv/32/(1-qv/32) for j,qv in zip(j0,q)])
    j=j0+feedback
    e1=rational_matrix(ctx["M"])*e0-dt*B*feedback
    ideal_c1=affine(ctx["first"],x,y)+e1
    e1=IV.matrix([v+resource_error for v in e1])
    c1=affine(ctx["first"],x,y)+e1
    if any(endpoint(v,1)<0 for v in c1):
        return dict(first_error=e1,second_error=None)
    # Necessary condition for a first-step-admitted member of this box.
    for i in range(len(c1)):
        c1[i]=interval(max(Q(0),endpoint(c1[i],0)),endpoint(c1[i],1))
    if represented:
        ideal_c1=IV.matrix([interval(max(-r.LIMITS["resource_error"],endpoint(v,0)),endpoint(v,1)) for v in ideal_c1])
        w1=writer_extension(high,ideal_c1,w,j,dt)
    else:
        w1=high.write(c1,w,j)
    if represented:
        radius=interval(-r.LIMITS["history_error"],r.LIMITS["history_error"])
        w1=IV.matrix([v+radius for v in w1])
    dw=w1-w
    decay=IV.exp(-dt)
    flat=IV.matrix([qv*jv/16 for qv,jv in zip(q,j)])
    z1=IV.matrix([[(1-decay)*number(high.mask[i,k])*flat[i]*flat[k]/2
        for k in range(len(w))] for i in range(len(w))])
    if represented:
        radius=interval(-r.LIMITS["carrier_error"],r.LIMITS["carrier_error"])
        z1=IV.matrix([[z1[i,k]+radius for k in range(len(w))] for i in range(len(w))])
    dh=number(Q(o.KAPPA_H))*z1
    # Exact decomposition of the full fresh-W/generated-geometry baseline.
    dc=B.T*c1
    base_delta=-IV.diag(list(dw))*rational_matrix(ctx["B"].T@ctx["L"])*c1 \
        -IV.diag(list(w1))*B.T*(B*IV.diag(list(dw))*dc+B*dh*dc/2)
    j1base=affine(baseline_coeff+Q(b.DT)*(-np.diag(ctx["w"])@ctx["B"].T@ctx["L"]@ctx["L"]@ctx["L"]@ctx["initial"]),x,y) \
        -rational_matrix(np.diag(ctx["w"])@ctx["B"].T@ctx["L"])*e1+base_delta
    g1=high.conductance(c1,w1,j1base)
    q1=IV.matrix([(v-g)/(v+g) for v,g in zip(w1,g1)])
    f1=IV.matrix([jv*qv/32/(1-qv/32) for jv,qv in zip(j1base,q1)])
    e2=rational_matrix(ctx["M"])*e1-dt*B*(base_delta+f1)
    e2=IV.matrix([v+resource_error for v in e2])
    return dict(first_error=e1,second_error=e2)


def high_parameters(ctx):
    params=ctx["high"].params
    return (params.coefficient == Q(1,2**24) and params.chi_a == Q(1,16)
        and params.zeta_a == Q(1,2) and b.DT == 2**-12 and o.KAPPA_H == 2**-14)


def clip(poly,a,c):
    result=[]
    for left,right in zip(poly,poly[1:]+poly[:1]):
        fl=sum(v*x for v,x in zip(a,left))+c
        fr=sum(v*x for v,x in zip(a,right))+c
        if fl>=0:result.append(left)
        if (fl<0)!=(fr<0):
            result.append(tuple(x+(y-x)*fl/(fl-fr) for x,y in zip(left,right)))
    return result


def inspect_box(ctx,bounds=(Q(0),Q(1),Q(0),Q(1)), *, represented=False):
    result=enclose(ctx,bounds,represented=represented)
    x0,x1,y0,y1=bounds
    poly=clip([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],(-1,-1),Q(1))
    constraints=[]
    for i,(row,err) in enumerate(zip(ctx["first"],result["first_error"])):
        constraints.append(dict(stage=1,node=ctx["graph"]["live_node_ids"][i],
            affine=list(map(str,row)),correction=[str(endpoint(err,s)) for s in (0,1)]))
        poly=clip(poly,row[1:],row[0]+endpoint(err,1))
        if not poly:return dict(excluded=True,stage=1,vertices=0,constraints=constraints)
    if result["second_error"] is None:
        raise ValueError("inconsistent first-step exclusion")
    first_poly=list(poly)
    for i,(row,err) in enumerate(zip(ctx["second"],result["second_error"])):
        upper=endpoint(err,1)
        margin=max(row[0]+row[1]*x+row[2]*y+upper for x,y in poly)
        constraints.append(dict(stage=2,node=ctx["graph"]["live_node_ids"][i],
            affine=list(map(str,row)),correction=[str(endpoint(err,s)) for s in (0,1)]))
        poly=clip(poly,row[1:],row[0]+endpoint(err,1))
        if not poly:return dict(excluded=True,stage=2,vertices=0,constraints=constraints,
            first_step_polygon=[[str(x),str(y)] for x,y in first_poly],
            terminal_resource_upper=str(margin), terminal_node=ctx["graph"]["live_node_ids"][i])
    return dict(excluded=False,stage=None,vertices=len(poly),polygon=poly)


def domain():
    return dict(shares="entire_closed_simplex3",source="frozen_actual_A_PC_source",
        role="current_suffices_to_exclude_both_role_admission",max_updates=2,
        initial_resource_rounding_allowance=str(Q(1,2**48)),
        represented_step_budgets={k:str(r.LIMITS[k]) for k in ("resource_error","history_error","carrier_error")},
        represented_claim="conditional_on_existing_full_formula_error_budgets_not_native_execution")


def source_paths(manifest):
    return {v["path"] for v in manifest["source_bindings"]}|{SELF,TEST,prior.INPUTS,prior.RESULTS,prior.PRESSURE}


def build():
    manifest=b.read(prior.INPUTS)
    prior.check_manifest(manifest)
    cases=[]
    for case in manifest["cases"]:
        if case["request"]["target_effective_degree"] != 94:
            continue
        ctx=context(manifest,case["case_id"])
        cases.append(dict(case_id=case["case_id"], role="current",
            graph_digest=b.digest(ctx["graph"]),
            exact=inspect_box(ctx), represented=inspect_box(ctx,represented=True)))
    return b.seal(dict(schema="p984d-apc-allocation-feasibility-v1",
        manifest_digest=manifest["record_digest"],source_bindings=b.bind(sorted(source_paths(manifest))),
        domain=domain(),
        cases=cases,native_steps=0,topology_events=0,runtime_cells_closed=0,
        all_sources_infeasible=False,all_depths_infeasible=False,user_accepted=False,aggregate_closed=False))


def check_certificate(ctx,certificate):
    """Exact rational replay of necessary halfplanes, separate from interval math."""
    b.require(certificate["excluded"] is True and certificate["stage"] == 2
        and certificate["vertices"] == 0,"incomplete allocation exclusion")
    poly=[(Q(0),Q(0)),(Q(1),Q(0)),(Q(0),Q(1))]
    rows=certificate["constraints"]
    terminal=ctx["graph"]["live_node_ids"].index(certificate["terminal_node"])
    wanted=[(1,i) for i in range(len(ctx["initial"]))]+[(2,i) for i in range(terminal+1)]
    b.require(len(rows)==len(wanted),"constraint roster drift")
    for row,(stage,i) in zip(rows,wanted,strict=True):
        expected=ctx["first" if stage==1 else "second"][i]
        b.require(row["stage"]==stage and row["node"]==ctx["graph"]["live_node_ids"][i]
            and row["affine"]==list(map(str,expected)),"affine transport/row drift")
        lo,hi=map(Q,row["correction"])
        b.require(lo<=hi,"invalid correction enclosure")
        maximum=max(expected[0]+expected[1]*x+expected[2]*y+hi for x,y in poly)
        poly=clip(poly,expected[1:],expected[0]+hi)
        if stage==1 and i==len(ctx["initial"])-1:
            b.require([[str(x),str(y)] for x,y in poly]==certificate["first_step_polygon"],"first-step polygon drift")
        if not poly:
            b.require(stage==2 and i==terminal
                and row["node"]==certificate["terminal_node"]
                and maximum==Q(certificate["terminal_resource_upper"])<0,
                "unresolved terminal contradiction")
    b.require(not poly,"nonempty admitted polygon")


def check(record,*,numerics=False):
    b.check_digest(record)
    b.check_bindings(record["source_bindings"])
    manifest=b.read(prior.INPUTS)
    prior.check_manifest(manifest)
    b.require(record["domain"]==domain() and record["source_bindings"]==b.bind(sorted(source_paths(manifest))),
        "domain/budget/source roster drift")
    b.require(record["schema"]=="p984d-apc-allocation-feasibility-v1"
        and record["manifest_digest"]==manifest["record_digest"]
        and all(record[k] is False for k in ("all_sources_infeasible","all_depths_infeasible","user_accepted","aggregate_closed"))
        and all(type(record[k]) is int and record[k]==0 for k in ("native_steps","topology_events","runtime_cells_closed")),
        "feasibility scope drift")
    expected=[c["case_id"] for c in manifest["cases"] if c["request"]["target_effective_degree"]==94]
    b.require([c["case_id"] for c in record["cases"]]==expected,"D94 population drift")
    for row in record["cases"]:
        ctx=context(manifest,row["case_id"])
        b.require(row["role"]=="current" and row["graph_digest"]==b.digest(ctx["graph"]),"history/graph binding drift")
        for mode in ("exact","represented"):
            check_certificate(ctx,row[mode])
            if numerics:
                b.require(row[mode]==inspect_box(ctx,represented=mode=="represented"),"enabled enclosure drift")
    return dict(status="frozen_source_allocation_excluded",D94_cases=6,
        simplex_coverage="entire_closed_simplex3",max_updates=2,native_steps=0,runtime_cells_closed=0,
        interval_equations_recomputed=numerics,
        least_negative_resource_upper=float(max(Q(c["represented"]["terminal_resource_upper"]) for c in record["cases"])))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run",action="store_true")
    mode.add_argument("--check",action="store_true")
    parser.add_argument("--recheck-numerics",action="store_true")
    args=parser.parse_args()
    b.require(not args.recheck_numerics or args.check,"recheck requires check")
    if args.run:
        result=build()
        summary=check(result)
        b.write_new(RESULTS,result)
    else:
        summary=check(b.read(RESULTS),numerics=args.recheck_numerics)
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
