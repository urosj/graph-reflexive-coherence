"""A_CI exact-real joint-ball and first-step feasibility; no native execution.

Independent fixed-row equations, FLINT rationals and outward Arb bounds.
See P9-8.4g-ACIInvestigation.md for the proof and its numerical ceiling.
"""
import argparse
import hashlib
import json
import math
import numpy as np
from flint import arb, ctx, fmpq
import p984g_cos as shared

ROOT, BASE, HERE = shared.ROOT, shared.BASE, shared.HERE
SELF = HERE + 'p984g_aci_investigation.py'
TEST = HERE + 'test_p984g_aci_investigation.py'
NOTE = BASE + 'P9-8.4g-ACIInvestigation.md'
PREPARED = BASE + 'larger-graph-examples/A_CI.json'
RESULTS = BASE + 'P9-8.4g-ACIInvestigationResults.json'
PREPARED_SHA = 'e2cbc0c686e590db9bf6c3ab761bb96a1aaa996427875a695fe3b08c1ded2109'
BITS = 192
require, read, seal = shared.require, shared.read, shared.seal


def q(x):
    if isinstance(x, fmpq):
        return x
    if isinstance(x, float):
        require(math.isfinite(x), 'nonfinite operand')
        return fmpq(*x.as_integer_ratio())
    return fmpq(x)


def upper(x):
    require(x.is_finite(), 'nonfinite enclosure')
    return x.upper().fmpq()


def lower(x):
    require(x.is_finite(), 'nonfinite enclosure')
    return x.lower().fmpq()


def norm(xs):
    return upper(arb(sum((x*x for x in xs), q(0))).sqrt())


def domain(radius, displacement, contraction, margin, condition, limit):
    require(0 < radius < 1, 'strict SPD ball required')
    require(margin > 0, 'positive physical block required')
    require(0 <= displacement <= radius, 'self-map unproved')
    require(0 <= contraction < 1, 'strict contraction unproved')
    require(1 <= condition <= limit, 'conditioning unproved')


def operands(subject, role):
    graph = subject['graph']
    nodes, edges = graph['live_node_ids'], graph['edges']
    require(len(nodes) > 1 and len(nodes) == len(set(nodes)), 'vertex identities')
    require(edges and len({e['edge_id'] for e in edges}) == len(edges), 'edge identities')
    index = {n:i for i,n in enumerate(nodes)}
    occupied, pairs, ends = set(), set(), []
    b = np.zeros((len(nodes), len(edges)), dtype=np.int64)
    rows = [[[] for _ in range(3)] for _ in nodes]
    state = subject['roles'][role]
    c, w = [q(x) for x in state['C']], [q(x) for x in state['W_A']]
    require(len(c)==len(nodes) and len(w)==len(edges), 'coordinate coverage')
    require(all(x>=0 for x in c) and all(x>0 for x in w), 'resource/history domain')
    require(state['Z_4'] is None, 'nonpersistent CI required')
    for k,e in enumerate(edges):
        u,v = (index[e[end]['node_id']] for end in ('tail','head'))
        require(u!=v and frozenset((u,v)) not in pairs, 'simple loop-free graph required')
        pairs.add(frozenset((u,v))); ends.append((u,v))
        b[u,k],b[v,k] = 1,-1
        for end,i,j in (('tail',u,v),('head',v,u)):
            port = e[end]['port']
            require(type(port) is int and 1<=port<=9 and (i,port) not in occupied, 'port occupancy')
            occupied.add((i,port)); rows[i][(port-1)//3].append((k,j))
    descriptors = [[sum((w[k]*(c[j]-c[i]) for k,j in cell),q(0))/sum((w[k] for k,j in cell),q(0))
                    if cell else q(0) for cell in row] for i,row in enumerate(rows)]
    return b,ends,c,w,descriptors


def certificate(subject, role, dt):
    require(subject['profile']['identity_payload']['profile_family_id']=='A_CI', 'A_CI only')
    params = subject['profile']['params_resolved']
    p, real, geo = params['candidate'], params['realization'], params['geometry']
    require(real['schema_version']=='grcv4-ci-params-v1', 'non-composite CI required')
    require(p['site_potential_id']=='quadratic_site_potential_zero_derivative_v1'
            and p['conductance_evaluator_id']=='curvature_disabled_G_W_v1', 'constitutive recipe')
    require(geo['star_cover_id']=='vertex_star_exact_overlap_v1'
            and geo['overlap_normalization_id']=='edge_multiplicity_inverse_sqrt_v1'
            and geo['candidate_adapter_id']=='candidate_a_exact_star_adapter_v1', 'geometry recipe')
    require(real['contraction_domain_id'].startswith('ci_reference_frobenius_ball_v1:'), 'Frobenius domain')
    r = q(float.fromhex(real['contraction_domain_id'].split(':',1)[1]))
    limit = q(params['solver']['conditioning_limit'])
    domain(r,0,0,1,1,limit)
    require((1+r)/(1-r)<=limit, 'Hodge conditioning')
    dt = q(dt); require(dt>0, 'positive dt')
    pnum = {k:q(p[k]) for k in ('eta','kappa_c','kappa_Ah','alpha','beta','gamma','W_floor','chi_A','zeta_A')}
    require(pnum['W_floor']>0, 'positive conductance floor')
    b,ends,c,w,desc = operands(subject,role)
    gram = b.T @ b
    dc = [c[u]-c[v] for u,v in ends]
    j0 = [-pnum['eta']*w[i]*pnum['kappa_c']*sum((q(int(x))*wj*d for x,wj,d in zip(row,w,dc)),q(0)) for i,row in enumerate(gram)]
    dnorm = norm(dc)
    lips = [abs(pnum['eta']*wi*pnum['kappa_Ah'])*norm([q(int(x)) for x in row])*dnorm for wi,row in zip(w,gram)]
    jbounds,qlips,qs,jref,flats,drives = [],[],[],[],[],[]
    beta = pnum['zeta_A']*pnum['chi_A']
    blocks = []
    for i,(u,v) in enumerate(ends):
        a,z = j0[i]-lips[i]*r,j0[i]+lips[i]*r
        square_lo = q(0) if a<=0<=z else min(a*a,z*z)
        square_hi = max(a*a,z*z)
        constant = -(pnum['alpha']*(c[u]+c[v])+pnum['beta']*sum(((x-y)**2 for x,y in zip(desc[u],desc[v])),q(0)))/2
        exps = [constant-pnum['gamma']*s/2 for s in (square_lo,square_hi)]
        glo,ghi = lower(arb(min(exps)).exp()),upper(arb(max(exps)).exp())
        require(glo>pnum['W_floor'], 'inactive floor chart not proved')
        qlo,qhi = (w[i]-ghi)/(w[i]+ghi),(w[i]-glo)/(w[i]+glo)
        blocks.extend((1-beta*qlo,1-beta*qhi))
        qs.extend((abs(qlo),abs(qhi)))
        bound = max(abs(a),abs(z)); jbounds.append(bound)
        qlips.append(abs(pnum['gamma'])*bound*lips[i]/2)
        gref = arb(constant-pnum['gamma']*j0[i]**2/2).exp()
        contrast = (arb(w[i])-gref)/(arb(w[i])+gref)
        j = arb(j0[i])/(1-arb(beta)*contrast)
        jref.append(j); flats.append(arb(pnum['chi_A'])*contrast*j); drives.append(glo)
    margin,high = min(blocks),max(blocks)
    require(margin>0, 'physical block margin')
    jmax,lj0 = norm(jbounds),norm(lips)
    qm,lq = max(qs),max(qlips)
    jmax,lj = jmax/margin, lj0/margin+ jmax*abs(beta)*lq/margin**2
    chi = abs(pnum['chi_A'])
    flat = chi*qm*jmax/(1-r)
    lf = chi*(qm*jmax/(1-r)**2+(lq*jmax+qm*lj)/(1-r))
    gain = abs(q(geo['kappa_H'])*pnum['zeta_A'])
    displacement, contraction = gain*flat**2, 2*gain*flat*lf
    domain(r,displacement,contraction,margin,high/margin,limit)
    # ||K o ff^T||_F <= ||f||_2^2, no 400-RHS inverse needed at H_ref=I.
    residual = gain*upper(sum((x*x for x in flats),arb(0)))
    distance = min(displacement,residual/(1-contraction))
    jerror = lj*distance
    resources, negative, unresolved = [],[],[]
    for i,row in enumerate(b):
        center = arb(c[i])-arb(dt)*sum((int(x)*j for x,j in zip(row,jref)),arb(0))
        error = dt*norm([q(int(x)) for x in row])*jerror
        lo,hi = lower(center)-error,upper(center)+error
        resources.append((lo,hi))
        if hi<0: negative.append(dict(vertex=subject['graph']['live_node_ids'][i],lower=str(lo),upper=str(hi)))
        elif lo<0: unresolved.append(subject['graph']['live_node_ids'][i])
    bounds = dict(radius=r, hodge_lower=1-r, conductance_lower=min(drives),
        current_margin_lower=margin,physical_condition_upper=high/margin,
        current_upper=jmax,current_lipschitz_upper=lj,flat_upper=flat,flat_lipschitz_upper=lf,
        displacement_upper=displacement,contraction_upper=contraction,
        reference_joint_residual_upper=residual,root_geometry_distance_upper=distance,
        root_current_distance_upper=jerror,first_step_resource_lower=min(x[0] for x in resources),
        first_step_resource_minimum_upper=min(x[1] for x in resources))
    return dict(vertices=len(c),edges=len(w),exact_real_unique_joint_root=True,
        bounds={k:str(v) for k,v in bounds.items()},certified_negative_vertices=negative,
        unresolved_resource_vertices=unresolved,
        exact_real_first_step_resources_nonnegative=not negative and not unresolved,
        native_stopping_or_positivity_claim=False)


def calculate():
    require(hashlib.sha256((ROOT/PREPARED).read_bytes()).hexdigest()==PREPARED_SHA, 'frozen A_CI declaration changed')
    declaration = read(PREPARED)
    require(declaration['reference_recipe']==dict(unit_vertex_measures=True,unit_edge_weights=True,
        K4_base='exact zero m by m in each graph edge order',
        context=dict(contract_id='constant_zero_context_v1',values={})), 'unit zero-base reference required')
    with ctx.workprec(BITS):
        cases = [dict(graph=g,role=r,**certificate(declaration[g],r,declaration['selected_configuration']['ordinary_dt'])) for g,r in shared.CASES]
    paths = [SELF,TEST,NOTE,PREPARED,shared.SELF,'specs/grc-v4-spec.md','specs/grc-9-v4-spec.md']
    return seal(dict(schema='p984g-aci-investigation-v1',family='A_CI',cases=cases,
        source_bindings={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        scalar_backend='FLINT rational + Arb outward bounds',precision_bits=BITS,
        scope='exact_real_joint_ball_and_first_resource_step_not_staged_or_native',
        native_roots=0,native_steps=0,native_events=0,user_accepted=False,ready_for_8_4h=False,
        authority=dict(contract_id='D10.2-EC-PARENT-REAL-CI',
            trace_digest='78573a598dca697e4d67e819b510ad29ac08631c40419b0fefb7282789ba99b6',
            support_disposition='indeterminate_requires_review',
            interpretation='provenance only; local root evidence is not global stability or new accepted authority'),
        aggregate_closed=False,open_obligations=['lawful source/allocation feasibility if excluded',
            'fixed-row staged whole joint-root oracle and mechanism/error separation',
            'review oracle before native roots; final-C/history readmission and trigger',
            '8.4h actual event, both-role transfer and continued evolution']))


def check(value=None):
    value = read(RESULTS) if value is None else value
    require(value==calculate(), 'A_CI investigation/source/scope drift')
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('run','check'))
    args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no evidence overwrite')
        raw=json.dumps(calculate(),indent=2)+'\n'
        require(len(raw.encode())<=1000000,'compress evidence above 1 MB')
        (ROOT/RESULTS).write_text(raw)
    else: check()


if __name__=='__main__': main()
