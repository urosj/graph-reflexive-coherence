"""Componentwise infinite-section positivity from the complete inverse chain.

Uniform per-level errors solve a nonnegative 8-variable comparison system.
Exact positive resolvent witness proves its spectral radius is below one.
The terminal unknown section is bounded by rho around I. Outward evaluation
of S(X1,H1) then bounds H0 entrywise, retaining causal smallness of frontier
rows that is lost by a global resource-error subtraction. No native changes.
"""
from flint import arb,arb_mat,ctx,fmpq as Q,fmpq_mat
import p9_arg2b_section as o
p=o.proof
SELF=p.BASE+'verification/p9_arg2b_positive.py'

def bounds(certificate):
 g,_=p.global_bounds();ax,ah,bx,bh=(g[k] for k in ('A_X','A_H','B_X','B_H'))
 d=o.DEPTH;size=2*d;M=fmpq_mat(size,size);rhs=fmpq_mat(size,1)
 # Unknowns x1..x4,h0..h3; x0 is bounded input rounding, h4 by rho.
 for i,row in enumerate(certificate['levels'],1):
  xi=i-1;hi=d+i
  M[xi,xi]=ax
  if i>1:M[xi,xi-1]=1
  else:rhs[xi,0]=Q(certificate['input_coordinate_error'])
  rhs[xi,0]+=Q(row['state_residual'])
  if i<d:M[xi,hi]=ah
  else:rhs[xi,0]+=ah*p.RHO
  parent=d+i-1
  M[parent,xi]=bx/2;rhs[parent,0]=Q(row['geometry_residual'])
  if i<d:M[parent,hi]=bh/2
  else:rhs[parent,0]+=bh*p.RHO
 A=fmpq_mat([[int(i==j) for j in range(size)] for i in range(size)])-M
 witness=A.solve(fmpq_mat([[1] for _ in range(size)]));p.require(all(x>0 for x in witness.entries()),'comparison contraction unproved')
 e=A.solve(rhs);p.require(all(x>=0 for x in e.entries()) and A*e==rhs,'comparison errors invalid')
 return [e[i,0] for i in range(d)],[e[d+i,0] for i in range(d)],witness.entries()

def certify(graph,c,w,work,certificate):
 # Authenticate the complete chain certificate before using any residual.
 xs,hs=o.decode(work);actual=o.certify(graph,c,w,xs,hs,p.graph_certificate(graph))
 p.require(actual==certificate,'componentwise residual source mismatch')
 ex,eh,witness=bounds(certificate);data=o.algebra(graph);mask=data[2];m=len(w)
 with ctx.workprec(o.BITS):
  x=[arb(o.exact(v),ex[0]) for v in xs[1]]
  h=arb_mat([[arb(o.exact(hs[1][i,k]),eh[1]) if mask[i,k] else arb(0) for k in range(m)] for i in range(m)])
  image=o.literal(data,x,h)['image']
  # Intersect two proved enclosures; never recenter without outward endpoints.
  H=[]
  for i in range(m):
   row=[]
   for k in range(m):
    lo=max(o.lower(image[i,k]),o.exact(hs[0][i,k])-eh[0])
    hi=min(o.upper(image[i,k]),o.exact(hs[0][i,k])+eh[0]);p.require(lo<=hi,'inconsistent section enclosures')
    row.append(arb((lo+hi)/2,(hi-lo)/2))
   H.append(row)
  truth=o.literal(data,o.coordinates(c,w),arb_mat(H),retract=False)
  limits=[o.lower(o.ball(v)+truth['increment'][i,0]) for i,v in enumerate(c)]
 return p.seal(dict(policy='joint_inverse_componentwise_image_arb192_v1',
  per_level_state_error=list(map(str,ex)),per_level_geometry_error=list(map(str,eh)),
  comparison_resolvent_witness=list(map(str,witness)),resource_lowers=list(map(str,limits)),
  exact_real_next_resource_lower=str(min(limits)),strictly_positive=min(limits)>0,
  section_certificate_digest=p.digest(certificate),native_reexecution=False))
