"""Explicit connected A_RG2b completion: joint C/scaled-log-W, Arb192.

Four inverse levels, eighteen sweeps, fixed precision and no fallback.
The accepted tree17 implementation remains a separate numerical identity.
"""
from dataclasses import dataclass
from functools import lru_cache
import json,math
import numpy as np
from flint import arb,arb_mat,ctx,fmpq as Q
from . import grc_9_v4_arg2b as tree
from .grc_9_v4_crg2b_connected import graph_algebra,rational_norm,exact,ball,lower,upper,magnitude,matrix,eye,norm
from .grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from .grc_v4_candidate_a import CandidateACurrent
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_state import FrozenJSONMap
from .grc_v4_geometry import GRCV4Geometry,OneFormHodge
from .grc_v4_rg2b import RG2bStageError,_require as require
from .grc_v4_ci import _Interval,_norm
from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_exact import ExactBackend,current_exact_backend

EXTENSION='grc9v4_a_rg2b_connected_signed_argument_completion_v1'
CONTAINMENT='grc9v4_a_rg2b_connected_degree_global_certificate_v1'
APPROXIMATION='grc9v4_a_rg2b_chain4_sweeps18_factored_binary64_arb192_v1'
ERROR_NORM='grc9v4_rg2b_hodge_induced_infinity_v1'
RHO,LIP,DT,SCALE,EPS,KH,CHI,ZETA=Q(1,4096),Q(1,1024),Q(1,4096),Q(512),Q(1,2**24),Q(1,2),Q(1,16),Q(1,2)
DEPTH,SWEEPS,BITS=4,18,192
admit=tree.admit
coordinates=tree.coordinates

@dataclass(frozen=True,slots=True)
class NativeARG2bDomain(tree.NativeARG2bDomain):
 @property
 def identity(self):return EXTENSION
 @classmethod
 def from_identity(cls,value):
  require(type(value) is str and value==EXTENSION,'unknown connected A completion')
  return cls(2.0,1.0,2.25,2.5,3.0,2**-12,2**-10,2**-12)

def global_bounds(bn=Q(9),dn=Q(18),an=Q(9)):
    """Exact derivative bounds in max(C,512 log W) and induced infinity H."""
    require(0<bn<=9 and 0<dn<=18 and 0<an<=9,'nine-port graph norms out of scope')
    span,hinv=Q(6),1/(1-RHO)
    wl,wu=1-1/SCALE,1/(1-1/SCALE)
    j0=wu*dn*(wu+KH*RHO)*span
    j0x=wu*dn*((wu+KH*RHO)*2+(2*wu+KH*RHO)*span/SCALE)
    j0h=wu*KH*dn*span
    row_x=2+2*span/SCALE
    emax,emin=EPS*(10+12*span**2+j0**2)/2,-EPS
    gl,gu=1-emax,1/(1+emin)
    require(gl>Q(1,2) and -emin<1,'read floor/exp bound unresolved')
    qmax=max(abs((wl-gu)/(wl+gu)),abs((wu-gl)/(wu+gl)))
    ex,eh=EPS*(2+24*span*row_x+2*j0*j0x)/2,EPS*j0*j0h
    qx,qh=(1/SCALE+ex)/2,eh/2
    theta=CHI*ZETA*qmax
    require(0<=theta<Q(1,2),'physical inverse unresolved')
    j=j0/(1-theta)
    jx,jh=(j0x+CHI*ZETA*qx*j)/(1-theta),(j0h+CHI*ZETA*qh*j)/(1-theta)
    causal,cx,ch=CHI*qmax*j,CHI*(qx*j+qmax*jx),CHI*(qh*j+qmax*jh)
    mc=DT*bn*j
    post_span=span+2*mc
    post_x,post_h=1+DT*bn*jx,DT*bn*jh
    post_row_x,post_row_h=2*post_x+2*post_span/SCALE,2*post_h
    writer_emax=EPS*(2*(5+mc)+12*post_span**2+j**2)/2
    writer_emin=EPS*(-1-mc)
    require(1-writer_emax>Q(1,2),'writer floor bound unresolved')
    writer_ex=EPS*(2*post_x+24*post_span*post_row_x+2*j*jx)/2
    writer_eh=EPS*(2*post_h+24*post_span*post_row_h+2*j*jh)/2
    ax,ah=max(DT*bn*jx,DT*(1+SCALE*writer_ex)),max(DT*bn*jh,DT*SCALE*writer_eh)
    my=DT*(1+SCALE*max(writer_emax,-writer_emin))
    v,vx,vh=hinv*causal,hinv*cx,hinv*ch+hinv**2*causal
    ms,bx,bh=ZETA*an*v*v,2*ZETA*an*v*vx,2*ZETA*an*v*vh
    ell=ax+ah*LIP
    require(ell<1,'base inverse bound unresolved')
    inv=1/(1-ell);value=KH*ms;image_lip=KH*(bx+bh*LIP)*inv
    q=KH*(bh+(bx+bh*LIP)*inv*ah)
    values=dict(A_X=ax,A_H=ah,M_f=max(mc,my),M_C=mc,M_Y=my,M_S=ms,B_X=bx,B_H=bh,
        J=j,J_X=jx,J_H=jh,current_margin=1-theta,read_exponent_upper=emax,
        writer_exponent_upper=writer_emax,read_drive_upper=gu,weight_lower=wl,weight_upper=wu,
        ell=ell,inverse_lip=inv,value_radius=value,image_lip=image_lip,q_section=q,
        four_level_tail_upper=q**4*value)
    checks=dict(resource_chart_containment=mc<Q(1,4),history_chart_containment=my<Q(1,8),
        section_image=value<RHO,lipschitz_class=image_lip<=LIP,graph_transform=q<1,
        same_four_level_tail_budget=q**4*value<Q(1,2**48))
    return values,checks

def proposal(data,query):
    b,d,mask,rows,ends=data
    b,d,mask=[np.asarray(a.tolist(),dtype=float) for a in (b,d,mask)]
    n,m=b.shape;ident=np.eye(m)
    xs=[np.asarray(query,dtype=np.float64).copy() for _ in range(DEPTH+1)]
    hs=[ident.copy() for _ in range(DEPTH+1)]
    def literal(x,h):
        c,y=np.clip(x[:n],-1.,5.),np.clip(x[n:],-1.,1.)
        w=np.array([math.exp(float(v)/512) for v in y])
        def exponent(cc,j):
            r=[[sum(w[k]*(cc[v]-cc[u]) for k,v in row)/sum(w[k] for k,_ in row) if row else 0.
                for row in node] for u,node in enumerate(rows)]
            return np.array([(cc[u]+cc[v]+sum((a-z)**2 for a,z in zip(r[u],r[v]))+j[k]**2)/2**25
                for k,(u,v) in enumerate(ends)])
        z=b.T@c;j0=-w*(d@(w*z+.5*((h-ident)@z)))
        g=np.array([math.exp(-float(e)) for e in exponent(c,j0)])
        q=(w-g)/(w+g);j=j0/(1-q/32)
        flat=np.linalg.solve(h,q*j/16)
        dc=-2**-12*(b@j)
        # Direct log-drive E avoids an unnecessary exp/log cancellation.
        dy=(-math.expm1(-2**-12))*(-512*exponent(c+dc,j)-y)
        return np.concatenate((dc,dy)),ident+.25*mask*np.outer(flat,flat)
    for _ in range(SWEEPS):
        for i in range(1,DEPTH+1):
            f,_=literal(xs[i],hs[i]);xs[i]=xs[i-1]-f
        for i in range(DEPTH,0,-1):_,hs[i-1]=literal(xs[i],hs[i])
    return xs,hs

def clip(v,lo,hi):
    if not isinstance(v,arb):return ball(min(Q(hi),max(Q(lo),exact(v))))
    a,b=max(Q(lo),min(Q(hi),lower(v))),max(Q(lo),min(Q(hi),upper(v)))
    return arb((a+b)/2,(b-a)/2)

def square(v):
    # Arb's general power path can return NaN for a nonexact ball containing
    # zero. Multiplication is a valid outward enclosure on that whole ball.
    return v*v

def literal(data,values,h,*,retract=True):
    """Independent outward edge equations and complete fresh-resource writer."""
    b,d,mask,rows,ends=data;n,m=b.nrows(),b.ncols()
    bi,di=matrix(b.tolist()),matrix(d.tolist());ident=eye(m)
    c=[clip(v,-1,5) if retract else (v if isinstance(v,arb) else ball(v)) for v in values[:n]]
    y=[clip(v,-1,1) if retract else (v if isinstance(v,arb) else ball(v)) for v in values[n:]]
    w=[(v/512).exp() for v in y]
    def exponent(cc,j):
        rr=[[sum((w[k]*(cc[v]-cc[u]) for k,v in row),arb(0))/sum((w[k] for k,_ in row),arb(0)) if row else arb(0)
             for row in node] for u,node in enumerate(rows)]
        return [(cc[u]+cc[v]+sum((square(a-z) for a,z in zip(rr[u],rr[v])),arb(0))+square(j[k]))/2**25
                for k,(u,v) in enumerate(ends)]
    z=bi.transpose()*arb_mat([[v] for v in c]);correction=(h-ident)*z
    j0=bi.transpose()*(bi*arb_mat([[w[k]*z[k,0]+correction[k,0]/2] for k in range(m)]))
    j0=[-w[k]*j0[k,0] for k in range(m)]
    g=[(-e).exp() for e in exponent(c,j0)];q=[(ww-gg)/(ww+gg) for ww,gg in zip(w,g)]
    j=[v/(1-z/32) for v,z in zip(j0,q)];flux=[z*v/16 for z,v in zip(q,j)]
    flat=h.solve(arb_mat([[v] for v in flux]))
    source=arb_mat([[ball(mask[i,k])*flat[i,0]*flat[k,0]/2 for k in range(m)] for i in range(m)])
    dc=-ball(DT)*bi*arb_mat([[v] for v in j])
    ew=exponent([v+dc[i,0] for i,v in enumerate(c)],j)
    dy=[(1-(-ball(DT)).exp())*(-512*e-v) for e,v in zip(ew,y)]
    require(all(v.is_finite() for v in (*dc.entries(),*dy,*source.entries())),'nonfinite literal bounds')
    return dict(increment=arb_mat([[v] for v in (*dc.entries(),*dy)]),image=ident+source/2,
                J=arb_mat([[v] for v in j]),baseline=arb_mat([[v] for v in j0]),
                readback=arb_mat([[v] for v in flux]),flat=flat,source=source,
                writer_target=[(-e).exp() for e in ew])

@lru_cache(maxsize=2)
def _graph_constants(raw):
 graph=json.loads(raw);b,d,mask,_=graph_algebra(graph)
 require(rational_norm(b)<=9 and rational_norm(d)<=18 and rational_norm(mask)<=9,'connected A graph norms fail')
 nodes=graph['live_node_ids'];index={v:i for i,v in enumerate(nodes)}
 rows=[[[] for _ in range(3)] for _ in nodes];ends=[]
 for k,e in enumerate(graph['edges']):
  u,v=index[e['tail']['node_id']],index[e['head']['node_id']];ends.append((u,v))
  rows[u][(e['tail']['port']-1)//3].append((k,v));rows[v][(e['head']['port']-1)//3].append((k,u))
 bounds,checks=global_bounds();require(all(checks.values()),'connected A completion/tail unproved')
 rename={'A_X':'base_X_lipschitz','A_H':'base_h_lipschitz','M_f':'base_displacement_upper',
  'M_C':'resource_displacement_upper','M_Y':'scaled_log_displacement_upper','M_S':'source_upper',
  'B_X':'source_X_lipschitz','B_H':'source_h_lipschitz','J':'current_upper','q_section':'contraction_upper',
  'inverse_lip':'inverse_lipschitz','value_radius':'section_value_radius','image_lip':'image_lipschitz'}
 mapped={rename[k]:v for k,v in bounds.items() if k in rename}
 mapped.update(section_radius=RHO,section_lipschitz=LIP,current_inverse_upper=1/bounds['current_margin'])
 matrices=[tuple(tuple(v for v in row) for row in a.tolist()) for a in (b,d,mask)]
 data=tree.Algebra(*matrices,tuple(tuple(tuple(row) for row in n) for n in rows),tuple(ends))
 return data,FrozenJSONMap({k:str(v) for k,v in mapped.items()})


def certificate(inputs,backend,domain):
 require(current_exact_backend() is ExactBackend.FLINT,'connected A requires explicit FLINT backend')
 ref=inputs.geometry.reference;p=ref.profile.params_resolved.candidate
 require(type(backend) is GRC9V4CandidateADifferentialReference and ref.graph.port_graph is not None
   and ref.profile.identity_payload.profile_family_id=='A_RG2b','connected A fixed-port owner required')
 expected=dict(eta=1,kappa_c=1,W_floor=.5,alpha=2**-24,beta=2**-24,gamma=2**-24,kappa_Ah=.5,chi_A=1/16,zeta_A=.5,tau_A=1)
 require(all(getattr(p,k)==v for k,v in expected.items()) and ref.profile.params_resolved.geometry.kappa_H==.5
  and all(v==1 for v in ref.edge_weights.values()) and all(v==0 for row in ref.K4_base for v in row),'connected A parameter/reference mismatch')
 require((1+RHO)/(1-RHO)<=exact(ref.profile.params_resolved.solver.conditioning_limit),'A Hodge conditioning unproved')
 data,bounds=_graph_constants(canonical_json_bytes(ref.graph.port_graph.to_payload()))
 CandidateACurrent(inputs,backend)
 return dict(domain=domain,selector_rank=0,graph_data=data,bounds=bounds)


def data_for(cert):
 a=cert.graph_data
 from flint import fmpq_mat
 return fmpq_mat(a.incidence),fmpq_mat(a.gram),fmpq_mat(a.mask),a.rows,a.ends


def propose(cert,query):return proposal(data_for(cert),query)


def certify_chain(cert,query,x,h,exact_query):
 a=cert.graph_data;n,m=len(a.incidence),len(a.gram)
 require(len(x)==DEPTH+1 and len(h)==DEPTH+1,'wrong connected A depth')
 for values,shape in ((x,(n+m,)),(h,(m,m))):
  require(all(isinstance(v,np.ndarray) and v.dtype==np.dtype('float64') and v.shape==shape
   and np.all(np.isfinite(v)) for v in values),'invalid connected A chain operands')
 require(np.array_equal(x[0],query) and np.array_equal(h[-1],np.eye(m)),'A query/terminal changed')
 for hi in h:
  require(np.array_equal(hi,hi.T) and all(a.mask[i][k] or hi[i,k]==0 for i in range(m) for k in range(m)), 'A section symmetry/support')
  require(max(sum((abs(exact(hi[i,k])-int(i==k)) for k in range(m)),Q(0)) for i in range(m))<=RHO,'A section matrix ball')
 with _ARB_CONTEXT_LOCK,ctx.workprec(BITS):
  data=data_for(cert);rx=rh=Q(0)
  for i in range(1,DEPTH+1):
   v=literal(data,x[i],matrix(h[i]));f,g=v['increment'],v['image']
   rx=max(rx,max(magnitude(ball(x[i][k])-ball(x[i-1][k])+f[k,0]) for k in range(n+m)))
   rh=max(rh,norm(matrix(h[i-1])-g))
  input_error=LIP*max((_Interval(exact(float(v)),exact(float(v)))-z).magnitude for v,z in zip(x[0],exact_query,strict=True))
 bounds={k:Q(v) for k,v in cert.bounds.items()}
 ax,ah,bx,bh=(bounds[k] for k in ('base_X_lipschitz','base_h_lipschitz','source_X_lipschitz','source_h_lipschitz'))
 amp=sum(((1-ax)**(-i) for i in range(1,DEPTH+1)),Q(0));den=1-(bh+bx*amp*ah)/2
 require(den>0,'A coupled residual bound unproved')
 eh=(rh+bx*amp*rx/2)/den;ex=amp*(rx+ah*eh)
 tail=bounds['contraction_upper']**DEPTH*bounds['section_value_radius']
 return eh+tail+input_error,dict(input_error=input_error,state_residual=rx,geometry_residual=rh,state_error=ex,geometry_error=eh,truncation_error=tail)


def section(cert):
 from .grc_v4_rg2b_graph import rounded_upper
 inputs=cert.inputs;p=inputs.geometry.reference.profile.params_resolved.realization
 actual=admit(inputs.current,ordinary=False)
 query=tuple(inputs.current.C)+tuple(512*math.log(w) for w in inputs.current.W_A)
 evaluations=2*SWEEPS*DEPTH+DEPTH
 require(p.iteration_limit>=evaluations,'connected A evaluation budget exhausted')
 try:
  x,h=propose(cert,query);error,_=certify_chain(cert,query,x,h,actual)
 except (ArithmeticError,ValueError) as exc:raise RG2bStageError('connected A section failed: '+str(exc)) from exc
 require(error<=exact(p.error_tolerance),'connected A section error tolerance unresolved')
 error=rounded_upper(error)
 geometry=GRCV4Geometry(inputs.geometry.reference,OneFormHodge(inputs.geometry.reference.graph,tuple(map(tuple,h[0].tolist()))))
 return dict(geometry=geometry,enclosure=(str(-error),str(error)),error_upper=str(error),levels=DEPTH,evaluations=evaluations)


def native_bridge(section,point,following,generated):
 before=section.inputs.current;after=following.current
 with _ARB_CONTEXT_LOCK,ctx.workprec(BITS):
  x=[ball(v) for v in before.C]+[512*ball(v).log() for v in before.W_A]
  y=[ball(v) for v in after.C]+[512*ball(v).log() for v in after.W_A]
  v=literal(data_for(section.certificate),x,matrix(section.geometry.one_form_hodge.matrix))
  je=_norm(magnitude(ball(z)-v['J'][i,0]) for i,z in enumerate(point.current.values))
  xe=max(magnitude(z-old-v['increment'][i,0]) for i,(z,old) in enumerate(zip(y,x,strict=True)))
  he=norm(matrix(generated.one_form_hodge.matrix)-v['image'])
  jn=_norm(magnitude(z) for z in v['J'].entries())
 return je,xe,he,jn
