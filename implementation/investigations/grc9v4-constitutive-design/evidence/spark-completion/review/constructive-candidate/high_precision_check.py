"""Independent 70-decimal numerical cross-check; not rigorous interval output."""
import json
from pathlib import Path
from fractions import Fraction as Q
import mpmath as mp
import positive_candidate as C
mp.mp.dps=70

def q(x):return mp.mpf(x.numerator)/x.denominator if isinstance(x,Q) else mp.mpf(x)

class MPModel:
 def __init__(self,nodes,ee):
  self.nodes=list(nodes); ix={u:i for i,u in enumerate(nodes)};m=len(ee)
  self.B=mp.matrix(len(nodes),m);self.I=mp.eye(m)
  for k,(u,_,v,__) in enumerate(ee):self.B[ix[u],k]=1;self.B[ix[v],k]=-1
  self.D=self.B.T*self.B; self.R=(mp.mpf(3)/4*self.I+self.D)**-1
  ends=[{u,v} for u,_,v,__ in ee]
  self.N=[[len(x&y) for y in ends] for x in ends]
 def rhs(self,c,H):
  potential=self.B*(H*(self.B.T*c))/64-mp.matrix([(x-2)**3-(x-2) for x in c])
  return -self.B.T*potential/1024
 def stage(self,c):
  j0=self.rhs(c,self.I);yp=self.R*j0;fp=yp/2;m=len(fp)
  H=self.I+mp.matrix([[self.N[i][j]*fp[i]*fp[j]/8 for j in range(m)] for i in range(m)])
  j0c=self.rhs(c,H);y=mp.lu_solve(mp.mpf(3)/4*self.I+H*self.D,j0c);j=j0c+y/4;f=mp.lu_solve(H,y)/2
  dh=mp.matrix([[self.N[i][j]*(fp[i]*fp[j]-f[i]*f[j])/8 for j in range(m)] for i in range(m)])
  return c-32*self.B*j,mp.sqrt(sum(x*x for x in dh))

out={'precision_decimal':70,'kind':'numerical_cross_check_not_interval','roles':{}}
for role in ('current','reset'):
 s=C.BASE.copy()
 if role=='reset':s['n1']+=Q(1,64);s['n2']-=Q(1,128);s['n3']-=Q(1,128)
 t={u:s.get(u,Q(0)) for u in C.TARGET_NODES}
 for i,r in enumerate(C.SHARES,1):t[f's{i}']=r*s['v']
 c=mp.matrix([q(t[u]) for u in C.TARGET_NODES]);fmodel=C.Equations(C.TARGET_NODES,C.edges(False));mpmodel=MPModel(C.TARGET_NODES,C.edges(False)); cf=__import__('numpy').array([float(t[u]) for u in C.TARGET_NODES])
 mxerr=mp.mpf(0);maxsp=mp.mpf(0);first={};mismatches=[];saved={}
 for k in range(1,129):
  c,sp=mpmodel.stage(c);cf,_,_=fmodel.stage(cf);maxsp=max(maxsp,sp)
  mxerr=max(mxerr,max(abs(c[i]-mp.mpf(float(cf[i]))) for i in range(len(cf))))
  vals={u:Q(mp.nstr(x,72)) for u,x in zip(C.TARGET_NODES,c)}
  for ch in (1,-1):
   bs=C.exact_classify(vals,C.edges(False,ch))['basins'];bf=C.exact_classify({u:Q(float(x)) for u,x in zip(C.TARGET_NODES,cf)},C.edges(False,ch))['basins']
   if bs!=bf:mismatches.append([k,ch])
   if len(bs)>=2 and str(ch) not in first:first[str(ch)]=k
  if k in (40,42,64,128):saved[str(k)]={u:mp.nstr(x,35) for u,x in zip(C.TARGET_NODES,c)}
 out['roles'][role]={'first_gain':first,'classification_mismatches':mismatches,'max_difference_binary64':mp.nstr(mxerr,12),'max_frobenius_split':mp.nstr(maxsp,16),'checkpoints':saved}
 print(role,out['roles'][role]['first_gain'],out['roles'][role]['max_difference_binary64'],flush=True)
Path(__file__).with_name('high_precision_results.json').write_text(json.dumps(out,indent=2)+'\n')
