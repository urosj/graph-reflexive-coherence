"""Independent C_PC whole-chart bounds and vertex-reduced Arb equations.

No native current, selector, carrier certificate or step is used here. The
constant sector follows from connectedness and a strict whole-ball gap. A
Woodbury reduction solves on vertices; flat requires one Hodge RHS solve.
"""
import argparse
from copy import deepcopy
import json
from flint import arb, ctx, fmpq
import p984d_cpc as storage
import p984g_cos as graph_math
import p984g_cos_bounds as iv

b = storage.b
q,a,lo,hi = iv.q,iv.a,iv.lo,iv.hi
SELF = b.HERE+"p984g_cpc.py"
PREPARED = b.BASE+"larger-graph-examples/C_PC.json"
INPUTS = b.BASE+"P9-8.4g-CPCInputs.json"
RESULTS = b.BASE+"P9-8.4g-CPCResults.json"
BITS = 192
ROLES = ("current","reset")
DT = 2**-12


def chart(subject):
    bv,params = graph_math.graph_data(subject)
    p,pc,g = (params[k] for k in ("candidate","realization","geometry"))
    b.require(subject["profile"]["identity_payload"]["profile_family_id"]=="C_PC", "C_PC only")
    b.require(pc["schema_version"]=="grcv4-pc-params-v1"
        and pc["writer_id"]=="zero_order_hold_exponential_v1"
        and pc["carrier_norm_id"]=="symmetric_star_frobenius_v1", "PC law drift")
    prefix="pc_compact_base_chart_v1:"
    name=pc["source_envelope_id"]
    b.require(name.startswith(prefix),"compact chart required")
    values=[float.fromhex(x) for x in name[len(prefix):].split(":")]
    b.require(len(values)==3 and name==prefix+":".join(x.hex() for x in values),"canonical chart")
    M,wl,wu=map(q,values)
    R,tau=q(pc["radius"]),q(pc["tau_PC"])
    b.require(M>0 and wl==wu==1 and R>0 and tau>0,"chart bounds")
    b.require(p["transport_id"]=="C-HM-STIFFNESS-BASELINE-v1"
        and p["potential_evaluator_id"]=="quadratic_site_potential_zero_derivative_v1"
        and p["C_ref"]>0 and p["tau_C"]>=0
        and g["star_cover_id"]=="vertex_star_exact_overlap_v1"
        and g["overlap_normalization_id"]=="edge_multiplicity_inverse_sqrt_v1"
        and g["candidate_adapter_id"]=="candidate_c_exact_star_adapter_v1", "Candidate C hypothesis")
    return bv,params,M,R,tau


def whole_chart(subject):
    bv,params,M,R,tau=chart(subject)
    p= params["candidate"]
    n,m=bv.shape
    radius=abs(q(params["geometry"]["kappa_H"]))*R
    lower,upper=1-radius,1+radius
    gap=lower/q(n*(n-1))-q(p["Lambda_C"])
    beta=q(p["zeta_C"])*q(p["chi_C"])
    limit=q(params["solver"]["conditioning_limit"])
    b.require(lower>0 and gap>0 and q(p["Lambda_C"])>0 and 0<=beta<1,"whole-ball gap/feedback")
    degree=max(sum(abs(int(x)) for x in row) for row in bv)
    dnorm=q(2*degree)
    with ctx.workprec(BITS):
        t=hi(a(abs(q(p["kappa_M_C"]))).exp())
        similarity=hi(a(upper/lower).sqrt())
        baseline=abs(q(p["eta_C"])*q(p["kappa_Phi_C"]))*t*dnorm*hi(a(dnorm).sqrt())*M*upper
        J=similarity*baseline/(1-beta)
        F=abs(q(p["chi_C"]))*J/lower
        source=abs(q(p["zeta_C"]))*F*F
    b.require(beta*similarity<1,"physical inverse margin")
    condition=(1+beta*similarity)/(1-beta*similarity)
    b.require(source<=R and condition<=limit and upper/lower<=limit,"whole-chart carrier invariance/conditioning")
    return {k:str(v) for k,v in dict(resource_norm_upper=M,carrier_radius=R,tau=tau,
        geometry_radius=radius,hodge_lower=lower,hodge_upper=upper,selector_gap_lower=gap,
        retained_scalar_upper=t,current_upper=J,flat_upper=F,source_upper=source,
        source_slack=R-source,current_condition_upper=condition).items()}


def carrier(subject,role,m):
    value=subject["roles"][role]["Z_4"]
    if isinstance(value,list):
        b.require(len(value)==m*m,"whole carrier dimensions")
        return [[q(x) for x in value[i*m:(i+1)*m]] for i in range(m)]
    if value==dict(recipe="zero_v1"):
        return [[q(0)]*m for _ in range(m)]
    b.require(set(value)=={"recipe","scale"} and value["recipe"]=="alternating_diagonal_v1","carrier recipe")
    return [[q(value["scale"])*(-1)**i if i==j else q(0) for j in range(m)] for i in range(m)]


def point(subject,role,*,zero_carrier=False,zero_feedback=False):
    bv,params,M,R,_=chart(subject)
    p=params["candidate"]
    n,m=bv.shape
    cs=list(map(q,subject["roles"][role]["C"]))
    z=carrier(subject,role,m)
    b.require(subject["roles"][role]["W_A"] is None and len(cs)==n and min(cs)>=0
        and sum((x*x for x in cs),q(0))<=M*M
        and sum((x*x for row in z for x in row),q(0))<=R*R
        and all(z[i][j]==z[j][i] for i in range(m) for j in range(i)),"actual PC chart membership")
    if zero_carrier:z=[[q(0)]*m for _ in range(m)]
    h=iv.eye(m)+a(params["geometry"]["kappa_H"])*iv.matrix(z)
    bm=iv.matrix(bv)
    c=iv.matrix([[x] for x in cs])
    mean=sum(cs,q(0))/n
    t=(a(p["kappa_M_C"])*(a(mean)/a(p["C_ref"])).tanh()).exp()
    cp=dict(p,zeta_C=0) if zero_feedback else p
    J,flux,flat,domain=iv.real_read(bm,c,h,cp,t)
    baseline=-a(p["eta_C"])*a(p["kappa_Phi_C"])*bm.transpose()*bm*(t*h)*bm.transpose()*c
    return dict(bv=bv,b=bm,c=cs,z=z,H=h,J=J,readback=flux,flat=flat,baseline=baseline,
                params=params,domain=domain)


def encode(values):
    return [dict(lower=str(lo(x)),upper=str(hi(x))) for x in values]


def first_step(subject,role,dt=DT):
    bounds=whole_chart(subject)
    with ctx.workprec(BITS):
        md=point(subject,role)
        rate=md["b"]*md["J"]
        after=[a(x)-a(dt)*rate[i,0] for i,x in enumerate(md["c"])]
        negative=[dict(vertex=subject["graph"]["live_node_ids"][i],lower=str(lo(x)),upper=str(hi(x)))
                  for i,x in enumerate(after) if hi(x)<0]
        unresolved=[subject["graph"]["live_node_ids"][i] for i,x in enumerate(after) if lo(x)<0<=hi(x)]
        controls={}
        for name,kwargs in (("old_carrier",dict(zero_carrier=True)),("readback_feedback",dict(zero_feedback=True))):
            alternate=point(subject,role,**kwargs)
            effects=[abs(md["J"][i,0]-alternate["J"][i,0]) for i in range(md["J"].nrows())]
            controls[name]=dict(max_lower=str(max(lo(x) for x in effects)),max_upper=str(max(hi(x) for x in effects)))
        fields={k:encode([md[k][i,0] for i in range(md[k].nrows())]) for k in ("J","readback","flat","baseline")}
    return dict(subject_digest=b.digest(subject),role=role,dt=dt,whole_chart=bounds,
        fields=fields,next_resources=encode(after),negative_resources=negative,unresolved_resources=unresolved,
        controls=controls,first_step_nonnegative=not negative and not unresolved,
        scope="pointwise_exact_PC_equations_not_staged_native_or_uniform_trajectory")


def calculate(declaration):
    return [dict(graph=graph,**first_step(declaration[graph],role))
            for graph in ("source","target") for role in ROLES]


def make_manifest():
    original=storage.read(PREPARED)
    return b.seal(dict(schema="p984g-cpc-inputs-v1",family="C_PC",original=original,
        source_bindings=b.bind({SELF,PREPARED,graph_math.SELF,iv.SELF}),precision_bits=BITS,
        policy="FLINT_rational_Arb_192_vertex_reduction",user_accepted=False,aggregate_closed=False))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","run","check"))
    args=parser.parse_args()
    if args.action=="prepare":storage.save(INPUTS,make_manifest())
    else:
        m=storage.read(INPUTS)
        b.check_digest(m);b.check_bindings(m["source_bindings"])
        rows=calculate(m["original"])
        result=b.seal(dict(schema="p984g-cpc-results-v1",manifest_digest=m["record_digest"],cases=rows,
            ready_for_native=all(r["first_step_nonnegative"] for r in rows),native_steps=0,native_events=0,
            user_accepted=False,aggregate_closed=False))
        if args.action=="run":storage.save(RESULTS,result)
        else:b.require(result==storage.read(RESULTS),"independent preflight drift")
        print(json.dumps([{k:r[k] for k in ("graph","role","first_step_nonnegative","negative_resources","unresolved_resources","controls")} for r in rows],indent=2))
