"""Complete CI+PC event reference lineage and independent pointwise update errors."""
from dataclasses import replace

import p984h_ccipc as n

b,g,q,a,hi=n.b,n.g,n.q,n.a,n.hi
SELF=b.HERE+'p9_ccipc_evidence.py'


def reference_lineage(seed, case, event):
    target=n.r.state(event['actual_target'])
    old,new=seed.inputs.geometry.reference.graph,target.inputs.geometry.reference.graph
    refs=event['checkpoint']['reference_currents']
    b.require(len(refs)==1 and refs[0]['event_id']==case['oracle']['event_id']
              and refs[0]['source_graph_digest']==old.graph_digest
              and refs[0]['target_graph_digest']==new.graph_digest,'composite reference lineage')
    for role,key in (('current','read'),('reset','reset_read')):
        current=event['admission_reads'][0][key]['J']
        lookup=dict(zip(old.live_edge_ids,current,strict=True))
        b.require(refs[0]['roles'][role]==dict(source=current,target=[lookup.get(e,0.0) for e in new.live_edge_ids]),
                  'fresh source-root reference transfer')
        b.require(sum(map(q,getattr(seed.inputs,role).C),q(0))==sum(map(q,getattr(target.inputs,role).C),q(0)),
                  'exact represented event charge')
    return dict(current=True,reset=True,fresh_root_source=True,exact_represented_charge=True)


def step_error_bounds(value):
    """Solve the independent root at the saved input, never a trajectory tube.

The reduced Arb iteration supplies a rigorously bounded tail. This avoids
using the deliberately conservative whole-chart current Lipschitz constant
as the final reported pointwise error. Native production is never called.
"""
    before=b.GeometryStageInputs.from_payload(value['before'])
    after=b.GeometryStageInputs.from_payload(value['after'])
    saved=value['read'];operand=n.subject(before)
    with g.ctx.workprec(g.BITS):
        exact=g.root(operand,'current');bounds=exact['bounds']
        bv,params=g.pc.graph_math.graph_data(operand)
        m=len(saved['J']);dt=q(before.dt)
        error_j=max(hi(abs(a(x)-exact['J'][i])) for i,x in enumerate(saved['J']))
        tail=q(exact['geometry_error'])
        source_lip=2*q(params['candidate']['zeta_C'])*q(bounds['flat_upper'])*q(bounds['flat_lipschitz_upper'])
        error_s=max(hi(abs(a(saved['source'][i][k])-exact['source'][i,k]))
                    for i in range(m) for k in range(m))+source_lip*tail
        error_h=g.frobenius_upper(g.iv.matrix(saved['H'])-exact['H'])+tail
        error_flat=max(hi(abs(a(x)-exact['flat'][i,0])) for i,x in enumerate(saved['flat']))+q(bounds['flat_lipschitz_upper'])*tail
        flux_lip=q(bounds['hodge_upper'])*q(bounds['flat_lipschitz_upper'])+q(bounds['flat_upper'])
        error_read=max(hi(abs(a(x)-exact['readback'][i,0])) for i,x in enumerate(saved['readback']))+flux_lip*tail
        bridge=saved['certificate']['joint_root_error']
        b.require(error_j<=q(bridge['current_error_upper']) and error_h<=q(bridge['geometry_error_upper']),
                  'independent exact root exceeds full-joint residual bridge')
        current=list(map(q,saved['J']));resources=[]
        for i,old in enumerate(before.current.C):
            exact_staged=q(old)-dt*sum((int(x)*y for x,y in zip(bv[i],current,strict=True)),q(0))
            resources.append(abs(q(after.current.C[i])-exact_staged)+dt*sum(abs(int(x)) for x in bv[i])*error_j)
        decay=(-a(before.dt)/a(params['realization']['tau_PC'])).exp();alpha=1-decay
        source=[x for row in saved['source'] for x in row]
        rounding=max(hi(abs(a(out)-(decay*a(old)+alpha*a(src))))
                     for out,old,src in zip(after.current.Z_4,before.current.Z_4,source,strict=True))
        carrier=rounding+hi(abs(alpha))*error_s
        minimum=min(g.lo(a(c)-a(dt)*sum((a(int(w))*j for w,j in zip(row,exact['J'],strict=True)),g.arb(0)))
                    for c,row in zip(before.current.C,bv,strict=True))
    return dict(input_identity=before.identity,read_digest=saved['record_digest'],
        poststate_digest=b.digest(value['after']),root_iterations=exact['iterations'],
        current_error=str(error_j),geometry_error=str(error_h),source_error=str(error_s),
        readback_error=str(error_read),flat_error=str(error_flat),
        resource_error=str(max(resources)),carrier_error=str(carrier),
        exact_one_step_resource_lower=str(minimum),precision_bits=g.BITS,
        uniform_trajectory_enclosure=False)
