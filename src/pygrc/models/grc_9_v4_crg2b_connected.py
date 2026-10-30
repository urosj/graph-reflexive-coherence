"""Explicit connected-graph C_RG2b signed completion, separate from tree17.

Graph constants use exact FLINT vertex solves. Binary64 work is certified at
fixed 192-bit Arb precision; there is no retry or fallback. Each physical
read reconstructs its section; cached immutable graph algebra is not history.
See specs/grc-9-v4-connected-rg2b-spec.md.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from functools import lru_cache
import json
import math
from typing import Any
import numpy as np
from flint import arb, arb_mat, ctx, fmpq as Q, fmpq_mat
from .grc_v4_exact import ExactBackend, current_exact_backend
from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_ci import _Interval, _iv, _norm
from .grc_v4_candidate_c import CandidateCCurrent
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_geometry import GRCV4Geometry, OneFormHodge
from .grc_v4_state import FrozenJSONMap
from .grc_v4_rg2b import RG2bStageError, _require as require
from .grc_9_v4_rg2b import NativeCRG2bDomain as _TreeDomain

EXTENSION='grc9v4_c_rg2b_connected_signed_argument_completion_v1'
CONTAINMENT='grc9v4_c_rg2b_connected_resolvent_global_certificate_v1'
APPROXIMATION='grc9v4_c_rg2b_chain6_sweeps18_vertex_binary64_arb192_v1'
ERROR_NORM='grc9v4_rg2b_hodge_induced_infinity_v1'
RHO,LIP,DT=Q(1,4096),Q(1,1024),Q(1,4096)
CHI,ZETA,KM,KH,CUTOFF=Q(16),Q(1,2**37),Q(1,2**24),Q(1,2),Q(1,512)
DEPTH,SWEEPS,BITS=6,18,192

@dataclass(frozen=True,slots=True)
class NativeCRG2bDomain(_TreeDomain):
    @property
    def identity(self):return EXTENSION
    @classmethod
    def from_identity(cls,value):
        require(type(value) is str and value==EXTENSION,'unknown connected signed completion')
        return cls(2.0,1.0,2.25,2.5,3.0,2**-12,2**-10,2**-12)

def rational_eye(n):
    return fmpq_mat([[int(i == j) for j in range(n)] for i in range(n)])

def rational_norm(matrix):
    return max((sum((abs(matrix[i, j]) for j in range(matrix.ncols())), Q(0))
                for i in range(matrix.nrows())), default=Q(0))

def graph_algebra(graph):
    """Independent incidence, port ownership, connectivity and exact diameter."""
    nodes, edges = graph["live_node_ids"], graph["edges"]
    require(len(nodes) >= 2 and len(set(nodes)) == len(nodes), "invalid vertex roster")
    require(len({e['edge_id'] for e in edges}) == len(edges), "duplicate edge identity")
    index = {node: i for i, node in enumerate(nodes)}
    b = [[0] * len(edges) for _ in nodes]
    adjacency = [set() for _ in nodes]
    occupied, pairs = set(), set()
    for k, edge in enumerate(edges):
        ends = []
        for side in ('tail', 'head'):
            end = edge[side]
            node, port = end['node_id'], end['port']
            require(node in index and type(port) is int and 1 <= port <= 9,
                    'invalid nine-port endpoint')
            require((node, port) not in occupied, 'port collision')
            occupied.add((node, port)); ends.append(index[node])
        i, j = ends
        require(i != j and frozenset(ends) not in pairs, 'simple loop-free graph required')
        pairs.add(frozenset(ends))
        b[i][k], b[j][k] = 1, -1
        adjacency[i].add(j); adjacency[j].add(i)
    diameter = 0
    for start in range(len(nodes)):
        distances, queue = {start: 0}, deque([start])
        while queue:
            i = queue.popleft()
            for j in adjacency[i] - distances.keys():
                distances[j] = distances[i] + 1; queue.append(j)
        require(len(distances) == len(nodes), 'connected graph required')
        diameter = max(diameter, max(distances.values()))
    b = fmpq_mat(b)
    absolute = fmpq_mat([[abs(b[i, j]) for j in range(b.ncols())] for i in range(b.nrows())])
    gram, mask = b.transpose() * b, absolute.transpose() * absolute / 2
    return b, gram, mask, diameter

def response_bounds(r0, s0, *, rho=RHO, km=KM):
    """Uniform noncommuting resolvent bound over the ENTIRE H/t chart.

    A0=I+D, R0=A0^-1, E=(tH-I)D R0, A=(I+E)A0.
    R=R0(I+E)^-1. This is a norm proof, not a replacement physical read.
    """
    require(0 <= rho < 1 and 0 <= km < 1 and r0 >= 0 and s0 >= 0,
            'invalid response hypothesis')
    t = 1 / (1 - km)
    perturbation = (t - 1 + t * rho) * s0
    require(perturbation < 1, 'resolvent Neumann bound inconclusive')
    r = r0 / (1 - perturbation)
    complement = s0 + r0 * perturbation / (1 - perturbation)
    return dict(t_upper=t, perturbation=perturbation, response_upper=r,
                complement_upper=complement)

def global_bounds(degree, gram, mask, response, *, rho=RHO, lip=LIP):
    """Literal C equation slopes; no commuting H/D or PSD-only H perturbation."""
    require(0 < rho < 1 and lip >= 0 and min(degree, gram, mask) > 0,
            'invalid section hypothesis')
    t, r, s = (response[k] for k in ('t_upper', 'response_upper', 'complement_upper'))
    tx, hinv = t * KM, 1 / (1 - rho)
    theta = CHI * ZETA * r
    require(theta < 1, 'physical current inverse unproved')
    j0, j0x, j0h = t * gram * (1 + rho) * 6, gram * (1 + rho) * (2*t + 6*tx), t*gram*6
    rx, rh = r*r*tx*(1+rho)*gram, r*r*t*gram
    j = j0 / (1 - theta)
    jx, jh = (j0x + CHI*ZETA*rx*j)/(1-theta), (j0h + CHI*ZETA*rh*j)/(1-theta)
    # RJ0=(R-I)b - Rt(DH-HD)b, ||DH-HD|| <= 2 ||D|| rho.
    causal = CHI * (s + r*t*2*gram*rho) * 6 / (1-theta)
    cx, ch = CHI*(rx*j+r*jx), CHI*(rh*j+r*jh)
    v, vx, vh = hinv*causal, hinv*cx, hinv*ch+hinv*hinv*causal
    ax, ah, mf = DT*degree*jx, DT*degree*jh, DT*degree*j
    ms, bx, bh = ZETA*mask*v*v, 2*ZETA*mask*v*vx, 2*ZETA*mask*v*vh
    ell = ax + ah*lip
    require(ell < 1, 'completed base inverse not contractive')
    inv = 1 / (1-ell)
    image, image_lip = KH*ms, KH*(bx+bh*lip)*inv
    contraction = KH*(bh + (bx+bh*lip)*inv*ah)
    checks = dict(physical_current_inverse=theta < 1,
                  signed_chart_containment=mf < Q(1, 4),
                  section_image=image < rho,
                  lipschitz_class=image_lip <= lip,
                  graph_transform=contraction < 1)
    values = dict(A_X=ax, A_H=ah, M_f=mf, M_S=ms, B_X=bx, B_H=bh,
                  inverse_lipschitz=inv, value_radius=image, image_lipschitz=image_lip,
                  contraction=contraction, current_upper=j, current_inverse_margin=1-theta)
    # Tail alone is not the residual+rounding certificate for a finite native chain.
    values['six_level_tail_upper'] = contraction**6 * image
    return values, checks

def exact(v):
    return Q(*float(v).as_integer_ratio()) if isinstance(v,(float,np.floating)) else Q(v)

def ball(v):return arb(exact(v))

def upper(v):return v.upper().fmpq()

def lower(v):return v.lower().fmpq()

def magnitude(v):return max(abs(lower(v)),abs(upper(v)))

def matrix(v):return arb_mat([[ball(x) for x in row] for row in v])

def eye(n):return arb_mat([[int(i==j) for j in range(n)] for i in range(n)])

def norm(v):return max((sum((magnitude(v[i,j]) for j in range(v.ncols())),Q(0)) for i in range(v.nrows())),default=Q(0))

def proposal(b,mask,query):
    """Fixed 6x18 work; vertex-reduced solve, no implicit precision/fallback."""
    n,m=b.shape;bt=b.T;d=bt@b;ident=np.eye(m);identn=np.eye(n)
    xs=[np.asarray(query,dtype=np.float64).copy() for _ in range(DEPTH+1)]
    hs=[ident.copy() for _ in range(DEPTH+1)]
    def read(x,h):
        c=np.clip(x,-1.,5.)
        t=math.exp(2**-24*math.tanh(math.fsum(c)/n));p=2**-33;s=1-p
        j0=-t*d@(h@(bt@c))
        v=np.linalg.solve(s*identn+t*b@h@bt,b@j0)
        u=(j0-t*h@bt@v)/s
        j=j0+p*u
        flat=np.linalg.solve(h,16*u)
        return -2**-12*(b@j),ident+2**-38*mask*np.outer(flat,flat)
    for _ in range(SWEEPS):
        for i in range(1,DEPTH+1):
            f,_=read(xs[i],hs[i]);xs[i]=xs[i-1]-f
        for i in range(DEPTH,0,-1):
            _,hs[i-1]=read(xs[i],hs[i])
    return xs,hs

def literal(b,mask,values,h):
    """Outward real equations; exact represented operands and signed arguments."""
    n,m=b.nrows(),b.ncols();bt=b.transpose();d=bt*b
    c=arb_mat([[ball(min(Q(5),max(Q(-1),exact(v))))] for v in values])
    t=(ball(KM)*(sum((c[i,0] for i in range(n)),arb(0))/n).tanh()).exp()
    p=ball(CHI*ZETA);s=1-p
    j0=-t*d*h*bt*c
    vertex=(s*eye(n)+t*b*h*bt).solve(b*j0)
    u=(j0-t*h*bt*vertex)/s
    j=j0+p*u
    flat=h.solve(16*u)
    source=arb_mat([[ball(ZETA)*ball(mask[i,k])*flat[i,0]*flat[k,0]
        for k in range(m)] for i in range(m)])
    return -ball(DT)*b*j,eye(m)+source/2,j


@dataclass(frozen=True,slots=True)
class Algebra:
    incidence: Any
    gram: Any
    mask: Any


@lru_cache(maxsize=2)
def _graph_constants(raw):
    """Only exact immutable graph content is cached; no state/section warm start."""
    graph=json.loads(raw)
    b,d,mask,diameter=graph_algebra(graph)
    n,m=b.nrows(),b.ncols()
    gap=(1-RHO)*Q(4,n*diameter)
    require(gap>CUTOFF,'connected completion constant selector gap unproved')
    r0=rational_eye(m)-b.transpose()*(rational_eye(n)+b*b.transpose()).solve(b)
    rb=response_bounds(rational_norm(r0),rational_norm(rational_eye(m)-r0))
    bounds,checks=global_bounds(rational_norm(b),rational_norm(d),rational_norm(mask),rb)
    require(all(checks.values()),'connected completion containment/contraction unproved')
    require(bounds['six_level_tail_upper']<Q(1,2**48),'connected completion finite tail exceeds budget')
    rename={'A_X':'base_X_lipschitz','A_H':'base_h_lipschitz','M_f':'base_displacement_upper',
            'M_S':'source_upper','B_X':'source_X_lipschitz','B_H':'source_h_lipschitz',
            'contraction':'contraction_upper','value_radius':'section_value_radius',
            'image_lipschitz':'image_lipschitz','inverse_lipschitz':'inverse_lipschitz',
            'current_upper':'current_upper'}
    mapped={rename[k]:_Interval(Q(0),v).hi for k,v in bounds.items() if k in rename}
    mapped.update(section_radius=RHO,section_lipschitz=LIP,
                  current_inverse_upper=_Interval(Q(0),1/bounds['current_inverse_margin']).hi)
    matrices=tuple(tuple(tuple(x for x in row) for row in mat.tolist()) for mat in (b,d,mask))
    return Algebra(*matrices),FrozenJSONMap({k:str(v) for k,v in mapped.items()})


def certificate(inputs,backend,domain):
    require(current_exact_backend() is ExactBackend.FLINT,'connected RG2b requires explicit FLINT backend')
    ref=inputs.geometry.reference;p=ref.profile.params_resolved.candidate
    require(backend is None and ref.graph.port_graph is not None and
            ref.profile.identity_payload.profile_family_id=='C_RG2b','connected C_RG2b port owner required')
    require(all(getattr(p,k)==v for k,v in dict(Lambda_C=2**-9,C_ref=1,kappa_M_C=2**-24,
        kappa_Phi_C=1,eta_C=1,tau_C=1,chi_C=16,zeta_C=2**-37).items()) and
        ref.profile.params_resolved.geometry.kappa_H==0.5 and all(v==1 for v in ref.edge_weights.values())
        and all(v==0 for row in ref.K4_base for v in row),'connected completion parameter/reference mismatch')
    require((1+RHO)/(1-RHO)<=exact(ref.profile.params_resolved.solver.conditioning_limit),
            'connected Hodge conditioning unproved')
    algebra,bounds=_graph_constants(canonical_json_bytes(ref.graph.port_graph.to_payload()))
    CandidateCCurrent(inputs)  # Native policy and actual reference read admission remain mandatory.
    return dict(domain=domain,selector_rank=1,graph_data=algebra,bounds=bounds)


def propose(cert,query):
    a=cert.graph_data
    return proposal(np.array(a.incidence,dtype=float),np.array(a.mask,dtype=float),query)


def certify_chain(cert,query,xs,hs):
    a=cert.graph_data;n,m=len(a.incidence),len(a.gram)
    require(len(xs)==DEPTH+1 and len(hs)==DEPTH+1,'wrong connected section depth')
    for arrays,shape in ((xs,(n,)),(hs,(m,m))):
        require(all(isinstance(v,np.ndarray) and v.dtype==np.dtype('float64') and v.shape==shape
                    and np.all(np.isfinite(v)) for v in arrays),'invalid connected section operands')
    require(np.array_equal(xs[0],query) and np.array_equal(hs[-1],np.eye(m)),'section query/terminal changed')
    for h in hs:
        require(np.array_equal(h,h.T),'section symmetry failure')
        require(all(a.mask[i][j] or h[i,j]==0 for i in range(m) for j in range(m)), 'section star support failure')
        require(max(sum((abs(exact(h[i,j])-int(i==j)) for j in range(m)),Q(0)) for i in range(m))<=RHO,
                'section matrix ball failure')
    with _ARB_CONTEXT_LOCK,ctx.workprec(BITS):
        b=matrix(a.incidence);mask=fmpq_mat(a.mask);rx=rh=Q(0)
        for i in range(1,DEPTH+1):
            f,g,_=literal(b,mask,xs[i],matrix(hs[i]))
            require(all(v.is_finite() for v in (*f.entries(),*g.entries())),'nonfinite section enclosure')
            rx=max(rx,max(magnitude(ball(xs[i][k])-ball(xs[i-1][k])+f[k,0]) for k in range(n)))
            rh=max(rh,norm(matrix(hs[i-1])-g))
    bounds={k:Q(v) for k,v in cert.bounds.items()}
    ax,ah,bx,bh=(bounds[k] for k in ('base_X_lipschitz','base_h_lipschitz','source_X_lipschitz','source_h_lipschitz'))
    amp=sum(((1-ax)**(-i) for i in range(1,DEPTH+1)),Q(0));den=1-(bh+bx*amp*ah)/2
    require(den>0,'coupled connected section residual unproved')
    eh=(rh+bx*amp*rx/2)/den;ex=amp*(rx+ah*eh)
    tail=bounds['contraction_upper']**DEPTH*bounds['section_value_radius']
    return eh+tail,dict(state_residual=rx,geometry_residual=rh,state_error=ex,geometry_error=eh,truncation_error=tail)


def section(cert):
    from .grc_v4_rg2b_graph import rounded_upper
    inputs=cert.inputs;params=inputs.geometry.reference.profile.params_resolved.realization
    require(all(abs(exact(v)-2)<=Q(5,2) for v in inputs.current.C),'connected section query outside K')
    evaluations=2*SWEEPS*DEPTH+DEPTH
    require(params.iteration_limit>=evaluations,'connected section evaluation budget exhausted')
    try:
        xs,hs=propose(cert,inputs.current.C)
        error,_=certify_chain(cert,inputs.current.C,xs,hs)
    except (ArithmeticError,ValueError) as exc:
        raise RG2bStageError('connected section proposal/certification failed: '+str(exc)) from exc
    require(error<=exact(params.error_tolerance),'connected section error tolerance unresolved')
    error=rounded_upper(error)
    geometry=GRCV4Geometry(inputs.geometry.reference,OneFormHodge(inputs.geometry.reference.graph,tuple(map(tuple,hs[0].tolist()))))
    return dict(geometry=geometry,enclosure=(str(-error),str(error)),error_upper=str(error),levels=DEPTH,evaluations=evaluations)


def native_bridge(section,point,following,generated):
    a=section.certificate.graph_data
    with _ARB_CONTEXT_LOCK,ctx.workprec(BITS):
        f,g,j=literal(matrix(a.incidence),fmpq_mat(a.mask),section.inputs.current.C,
                      matrix(section.geometry.one_form_hodge.matrix))
        je=_norm(magnitude(ball(v)-j[i,0]) for i,v in enumerate(point.current.values))
        xe=max(magnitude(ball(v)-ball(old)-f[i,0]) for i,(v,old) in
               enumerate(zip(following.current.C,section.inputs.current.C,strict=True)))
        he=norm(matrix(generated.one_form_hodge.matrix)-g)
        current_norm=_norm(magnitude(j[i,0]) for i in range(j.nrows()))
    return je,xe,he,current_norm
