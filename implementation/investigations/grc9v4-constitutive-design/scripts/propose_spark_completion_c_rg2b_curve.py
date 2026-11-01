"""Optional floating proposal search; SciPy never participates in certification.

Export operands with check_spark_completion_c_rg2b_direct.py, then pass the JSON
as --inputs. Only the current prefix endpoint at 390 and a reference center
are used. The output is an untrusted proposal, never accepted proof evidence.
"""
import json,time,argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--inputs',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
import numpy as np
from pathlib import Path
from fractions import Fraction as F
from scipy.linalg import solve
from scipy.interpolate import BarycentricInterpolator
from numpy.polynomial.chebyshev import chebfit,chebval
v=json.loads(Path(args.inputs).read_text());nodes=v['nodes'];n=len(nodes);d=n-1
A=np.array([[float(F(x))for x in row]for row in v['A']]);L=np.array([[float(F(x))for x in row]for row in v['L']]);c=np.array([float(F(v['center'][x]))for x in nodes]);x=np.array([float(F(v['at390'][s]))for s in nodes]);h=1/128
E=np.vstack((np.eye(d),-np.ones(d)));R=np.eye(n)[:d];B=R@A;D=np.diag(3*(c-2)**2-1)-L/64;lam,T=np.linalg.eig(R@A@D@E);order=np.argsort(lam);lam=lam[order].real;T=T[:,order].real;T/=np.linalg.norm(E@T,axis=0);V=E@T;U=np.linalg.inv(T)@R;y=U@(x-c);rho=.999
best=[]
for degree in (24,40,64,88):
 start=time.monotonic();grid=(1-np.cos(np.arange(degree+1)*np.pi/degree))/2
 W=BarycentricInterpolator(grid,np.eye(degree+1),axis=0)(rho*grid[1:-1]);Dref=np.eye(d)-h*R@A@D@E
 initial=c[None,:]+(grid[:,None]**(np.log(1-h*lam)/np.log(rho))[None,:]*y[None,:])@V.T
 z=initial[1:-1,:d].copy();idx=np.arange(degree-1)
 for iteration in range(12):
  cc=np.vstack((c[:d],z,x[:d]));C=c[None,:]+(cc-c[:d])@E.T
  phi=C@L.T/64-((C-2)**3-(C-2));flow=(C+h*phi@A.T)[:, :d]
  residual=flow[1:-1]-W@cc;error=np.max(abs(residual))
  if error<2e-14:break
  J=-np.kron(W[:,1:-1],np.eye(d))
  for j in idx:
   DF=np.eye(d)+h*B@(L/64-np.diag(3*(C[j+1]-2)**2-1))@E
   J[j*d:(j+1)*d,j*d:(j+1)*d]+=DF
  delta=solve(J,-residual.ravel()).reshape(-1,d);z+=delta
 coeff=chebfit(2*grid-1,C-c,degree)
 sg=np.linspace(0,1,10001);curve=chebval(2*sg-1,coeff).T+c;shift=chebval(2*rho*sg-1,coeff).T+c
 defect=curve+h*(curve@L.T/64-((curve-2)**3-(curve-2)))@A.T-shift
 P=np.array([[float(F(x))for x in row]for row in v['P']]);norms=np.sqrt(np.maximum(0,np.einsum('bi,ij,bj->b',defect,P,defect)))
 print('degree',degree,'iters',iteration,'collocation',error,'defect',max(norms),'seconds',time.monotonic()-start,'endpoint',max(abs(curve[-1]-x)),flush=True)
 exact=[[F(0)]*(degree+1) for _ in range(n)]
 for i in range(n-1):
  for k in range(1,degree+1):exact[i][k]=F(round(coeff[k,i]*2**60),2**60)
  exact[i][0]=F(v['center'][nodes[i]])-sum((-1)**k*exact[i][k] for k in range(1,degree+1))
 for k in range(degree+1):exact[-1][k]=F(21 if k==0 else 0)-sum(exact[i][k] for i in range(n-1))
 best.append(dict(rational_chebyshev_coefficients=[[str(x) for x in row] for row in exact],degree=degree,rho=str(F(rho).limit_denominator()),coefficients=coeff.tolist(),max_sampled_defect=float(max(norms))))
Path(args.output).write_text(json.dumps(dict(status='floating_collocation_proposals_only_no_future_trajectory_input',proposals=best),indent=2))
