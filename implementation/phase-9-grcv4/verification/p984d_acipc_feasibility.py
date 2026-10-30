"""A_CI_PC deep source/allocation selection aid, followed by full certificates.

The exact frozen-history affine inequalities are a selection aid, not a proof
for the enabled nonlinear law. The separate joint-root preflight and native
campaign must certify every selected input. No ATC rule is inferred here.
"""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product
import math
import numpy as np

import p984b_acipc_runtime as r
import p984c_acipc_runtime as previous
import p984c_cos as construction
import p984d_apc_joint as affine
from p9_acipc_compute import worker

b = r.b
SELF = b.HERE + 'p984d_acipc_feasibility.py'
SOURCE = b.BASE + 'P9-8.4d-ACIPCSourceCompanion.json.xz'


def source():
    old = b.read(r.INPUTS)
    before = b.GeometryStageInputs.from_payload(old['initial_inputs'])
    # Same independent history direction as the accepted A_PC companion.
    before = replace(before, current=replace(before.current,
        W_A=tuple(float(Q(w)+Q(1,32)) for w in before.current.W_A)))
    graph = before.geometry.reference.graph.port_graph.to_payload()
    v = before.current
    out = r.oracle.PaperACIPC(graph).step(v.C, v.W_A, v.Z_4)
    proof = r.oracle.check_step(graph, v.C, v.W_A, v.Z_4, out)
    authority = b.GRCV4AuthoritativeState(tuple(out['C']),tuple(out['W_A']),tuple(out['Z_4']))
    nominal = r.state(old['nominal_source'])
    nominal = replace(nominal,inputs=replace(nominal.inputs,current=authority,reset=before.reset,dt=0))
    m = dict(initial_inputs=before.to_payload(),nominal_source=nominal.to_payload())
    with worker():
        shared, seed = r.run_source(m)
    return b.seal(dict(schema='p984d-acipc-source-companion-v1',
        initial_inputs=before.to_payload(),nominal_source=nominal.to_payload(),
        expected_source=seed.to_payload(),shared=shared, independent_output=out,
        independent_errors={k:str(v) for k,v in proof['errors'].items()},
        history_increment='1/32', history_mean='31/32',
        unchanged=['resources','reset_history','carrier','parameters','timestep','tolerances'],
        source_bindings=b.bind({SELF,r.SELF,b.HERE+'p9_acipc_compute.py'}),
        user_accepted=False,aggregate_closed=False))


def rebind(seed, template, layout):
    case = deepcopy(template)
    request = case['request']
    request.update(source_state_digest=seed.scientific_digest,
        history_policy=r.oracle.history_policy(b.authority_payload(seed.inputs.current),
                                               b.authority_payload(seed.inputs.reset)),
        resource_distribution=layout['shares'])
    for key in case['oracle']['event_identity']:
        if key in request and key != 'schema_version':
            case['oracle']['event_identity'][key] = request[key]
    for channel in ('candidate','carrier'):
        key=channel+'_history_policy_digest'
        case['oracle']['event_identity'][key]=request['history_policy'][key]
    case['oracle'] = construction.target_oracle(seed.to_payload(),case,request,layout)
    return case


def derive(seed, template, layout):
    """Intersect ten exact frozen-W step inequalities, then select dyadic shares.

    Charge is checked on represented products in both roles. No search of
    enabled target outcomes is involved in this declared deterministic choice.
    """
    quarter = dict(layout,shares=[.25,.25,.5])
    case = rebind(seed, template, quarter)
    target = r.independent_target(seed,case)
    graph = case['oracle']['target_graph']; nodes=graph['live_node_ids']
    n=len(nodes); index={node:i for i,node in enumerate(nodes)}
    B=np.zeros((n,len(graph['edges'])),dtype=object)
    for k,edge in enumerate(graph['edges']):
        B[index[edge['tail']['node_id']],k]=Q(-1)
        B[index[edge['head']['node_id']],k]=Q(1)
    constraints=[]; masses=[]
    for role in r.ROLES:
        v=getattr(target.inputs,role)
        W=np.array(list(map(Q,v.W_A)),dtype=object)
        L=B@np.diag(W)@B.T
        M=np.eye(n,dtype=int)+Q(b.DT)*(L@L)
        C=np.array([[Q(c),Q(0),Q(0)] for c in v.C],dtype=object)
        i=seed.inputs.geometry.reference.graph.live_node_ids.index(case['request']['source_node_id'])
        mass=Q(getattr(seed.inputs,role).C[i]);masses.append(mass)
        for k,coeff in enumerate(((0,1,0),(0,0,1),(1,-1,-1)),1):
            C[index[case['oracle']['event_id']+f'/satellite/{k}']]=[mass*x for x in coeff]
        for step in range(1,11):
            C=M@C
            constraints.extend(dict(role=role,step=step,node=node,coefficients=list(map(str,row)))
                for node,row in zip(nodes,C,strict=True))
    polygon=affine.polygon([v['coefficients'] for v in constraints])
    b.require(len(polygon)>=3,'empty frozen-history selection region')
    center=tuple(sum(p[i] for p in polygon)/len(polygon) for i in (0,1))
    for power in range(6,15):
        den=2**power
        options=[sorted({Q(math.floor(x*den),den),Q(math.ceil(x*den),den)}) for x in center]
        valid=[]
        for point in product(*options):
            margin=affine.margin(polygon,point)
            shares=(*point,1-sum(point))
            if margin>0 and all(sum(Q(float(mass*s)) for s in shares)==mass for mass in masses):
                valid.append((margin,point,shares))
        if valid:
            margin,point,shares=sorted(valid,key=lambda x:(-x[0],x[1]))[0]
            return dict(shares=list(map(float,shares)),selection=dict(
                coefficients_digest=b.digest(constraints),polygon=[list(map(str,p)) for p in polygon],
                denominator=den,centroid=list(map(str,center)),margin=str(margin),
                rule='first_dyadic_centroid_neighbors_positive_margin_exact_both_role_charge',
                full_nonlinear_feasibility=False))
    raise ValueError('no charge-exact dyadic candidate in declared search')
