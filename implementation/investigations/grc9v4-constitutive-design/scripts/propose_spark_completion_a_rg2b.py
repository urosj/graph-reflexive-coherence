"""Optional floating proposals; only the declared prefix endpoint is used.

SciPy proposes a stationary center and a full C/scaled-log-W curve. Exact
rational coefficients, interval jets, the complete section and all physical
membership checks are certified separately using FLINT/Arb. This script
never supplies proof or scientific authority.
"""
import argparse,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.optimize import root
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--inputs',required=True);p.add_argument('--output',required=True)
p.add_argument('--entry',type=int,default=300);p.add_argument('--duration',type=int,default=16)
p.add_argument('--degree',type=int,default=40);p.add_argument('--source-proposal',action='store_true')
args=p.parse_args();v=json.loads(Path(args.inputs).read_text())
class Model:
 def __init__(self,g,dt):
  self.g=g; self.nodes=g['live_node_ids'];self.edges=g['edges'];self.n=len(self.nodes);self.m=len(self.edges);self.dt=dt
  self.pairs=[(self.nodes.index(e['tail']['node_id']),self.nodes.index(e['head']['node_id'])) for e in self.edges]
  self.b=np.array([[(i==a)-(i==b) for a,b in self.pairs] for i in range(self.n)],float)
  self.terms=[[[] for _ in range(3)] for _ in self.nodes]
  for k,e in enumerate(self.edges):
   for a,b in [('tail','head'),('head','tail')]:self.terms[self.nodes.index(e[a]['node_id'])][(e[a]['port']-1)//3].append((k,self.nodes.index(e[b]['node_id'])))
 def exponent(self,c,w,j):
  rows=np.array([[sum(w[k]*(c[z]-c[i]) for k,z in row)/sum(w[k] for k,z in row) if row else 0 for row in t] for i,t in enumerate(self.terms)])
  return np.array([-(c[i]+c[z]+np.sum((rows[i]-rows[z])**2)+j[k]**2)/65536 for k,(i,z) in enumerate(self.pairs)])
 def step(self,c,l):
  w=np.exp(l);phi=self.b@(w*(self.b.T@c))/64-((c-2)**3-(c-2));j0=-w*(self.b.T@phi)/1024
  g=np.exp(self.exponent(c,w,j0));q=(w-g)/(w+g);j=j0/(1-q/4)
  ca=c-self.dt*(self.b@j);lp=np.exp(-self.dt/32)*l+(1-np.exp(-self.dt/32))*self.exponent(ca,w,j)
  return ca,lp
 def stationary(self):
  def fun(x):
   c,l,lam=x[:self.n],x[self.n:-1],x[-1];w=np.exp(l)
   return np.r_[((c-2)**3-(c-2))-self.b@(w*(self.b.T@c))/64-lam,l-self.exponent(c,w,np.zeros(self.m)),np.sum(c)-21]
  x=np.r_[[3+2/15 if z in ['p','sc2-positive-module/satellite/2'] else 1+2/15 for z in self.nodes],np.zeros(self.m),0]
  out=root(fun,x,tol=1e-11);assert out.success;return out.x[:-1]

if args.source_proposal:
 s=Model(v['source'],args.duration)
 desired=np.array([float(F(v['declaration']['prepared_source']['reset'][z])) for z in s.nodes])
 L=np.full(s.m,np.log(4097/4096));E=np.vstack((np.eye(s.n-1),-np.ones(s.n-1)))
 def full(c):return desired+E@(c-desired[:-1])
 proposal=root(lambda x:s.step(full(x),L)[0][:-1]-desired[:-1],desired[:-1],tol=1e-12)
 if not proposal.success:raise ValueError('source proposal did not converge')
 c=full(proposal.x);exact=[F(round(x*2**48),2**48) for x in c[:-1]];exact.append(F(21)-sum(exact))
 Path(args.output).write_text(json.dumps(dict(status='untrusted_source_proposal',
  current=dict(zip(s.nodes,map(str,exact))),reference_residual=float(max(abs(s.step(c,L)[0]-desired)))),indent=2)+'\n')
 raise SystemExit(0)

from scipy.linalg import solve
from scipy.interpolate import BarycentricInterpolator
from numpy.polynomial.chebyshev import chebfit,chebval
import time
DT=args.duration;SCALE=64;entry=args.entry;rho=.999
s=Model(v['source'],DT);m=Model(v['targets']['1']['graph'],DT);n=m.n;dof=n-1+m.m
E=np.zeros((n+m.m,dof));E[:n-1,:n-1]=np.eye(n-1);E[n-1,:n-1]=-1;E[n:,n-1:]=np.eye(m.m)
R=np.delete(np.eye(n+m.m),n-1,axis=0)
eq=m.stationary();center=eq.copy();center[n:]*=SCALE
centerr=[F(round(z*2**48),2**48) for z in center];centerr[n-1]=21-sum(centerr[:n-1]);center=np.array(list(map(float,centerr)))
def step(x):
 c,l=m.step(x[:n],x[n:]/SCALE);return np.r_[c,SCALE*l]
def jac(x):
 out=np.zeros((len(x),len(x)))
 for i in range(len(x)):
  y=x.astype(complex);y[i]+=1e-20j;out[:,i]=step(y).imag/1e-20
 return out
D=R@jac(center)@E
lam,T=np.linalg.eig(D);order=np.argsort(-abs(lam));lam,T=lam[order],T[:,order]
assert max(abs(lam.imag))<1e-10 and np.all(lam.real>0)
lam,T=lam.real,T.real;T/=np.linalg.norm(E@T,axis=0);V=E@T;U=np.linalg.inv(T)@R
print('spectrum',min(lam),max(lam),flush=True)
proposals=[]
for role in ['reset']:
 c=np.array([float(F(v['declaration']['prepared_source'][role][z])) for z in s.nodes]);l=np.ones(s.m)*np.log(4097/4096 if role=='current' else 8191/8192)
 if role=='current':c,l=s.step(c,l)
 vals=dict(zip(s.nodes,c));cw={e['edge_id']:l[k] for k,e in enumerate(s.edges)};mod=v['targets']['1']['module'];vals[mod[0]]=0
 for z,w in zip(mod[1:],v['declaration']['allocation_shares']):vals[z]=vals['v']*float(F(w))
 c=np.array([vals[z] for z in m.nodes]);l=np.array([cw.get(e['edge_id'],0) for e in m.edges])
 for k in range(entry):c,l=m.step(c,l)
 endpoint=np.r_[c,SCALE*l];y=U@(endpoint-center)
 for degree in [args.degree]:
  start=time.monotonic();grid=(1-np.cos(np.arange(degree+1)*np.pi/degree))/2
  W=BarycentricInterpolator(grid,np.eye(degree+1),axis=0)(rho*grid[1:-1])
  initial=center[None,:]+(grid[:,None]**(np.log(lam)/np.log(rho))[None,:]*y[None,:])@V.T
  z=(initial@R.T)[1:-1].copy()
  for iteration in range(12):
   cc=np.vstack((R@center,z,R@endpoint));C=center[None,:]+(cc-R@center)@E.T
   flow=np.array([step(row) for row in C])@R.T
   residual=flow[1:-1]-W@cc;error=np.max(abs(residual))
   if error<1e-13:break
   J=-np.kron(W[:,1:-1],np.eye(dof))
   for j in range(degree-1):J[j*dof:(j+1)*dof,j*dof:(j+1)*dof]+=R@jac(C[j+1])@E
   delta=solve(J,-residual.ravel()).reshape(-1,dof);z+=delta
  coeff=chebfit(2*grid-1,C-center,degree)
  sg=np.linspace(0,1,2001);curve=chebval(2*sg-1,coeff).T+center;shift=chebval(2*rho*sg-1,coeff).T+center
  defect=np.array([step(x) for x in curve])-shift
  print(role,degree,'iters',iteration,'collocation',error,'sampled_defect',np.max(abs(defect)),'seconds',time.monotonic()-start,flush=True)
  exact=[[F(0)]*(degree+1) for _ in range(n+m.m)]
  for i in range(n+m.m):
   if i==n-1:continue
   for k in range(1,degree+1):exact[i][k]=F(round(coeff[k,i]*2**60),2**60)
   exact[i][0]=centerr[i]-sum((-1)**k*exact[i][k] for k in range(1,degree+1))
  for k in range(degree+1):exact[n-1][k]=F(21 if k==0 else 0)-sum(exact[i][k] for i in range(n-1))
  proposals.append(dict(role=role,degree=degree,chebyshev_coefficients=[[str(x) for x in row] for row in exact],sampled_defect=float(np.max(abs(defect))),endpoint=endpoint.tolist()))
Path(args.output).write_text(json.dumps(dict(status='untrusted_floating_proposal_no_future_trajectory_input',entry=entry,center=list(map(str,centerr)),rho='999/1000',proposals=proposals),indent=2))
