"""Exploratory successor to SC2Continuation: exact source admission predicates,
independent floating-point full C_OS recurrence, both charts and both roles.
This is NOT an interval trajectory, native event, or completion certificate.
"""
from __future__ import annotations
import json
import lzma
from fractions import Fraction as Q
from pathlib import Path
import numpy as np

PARENT=Path(__file__).parent
SOURCE_NODES=[f'n{i}' for i in range(1,10)]+['p','v','private']
TARGET_NODES=[f'n{i}' for i in range(1,10)]+['p','core','s1','s2','s3','private']
PARAMS=dict(eta=Q(1,1024),h=Q(32),kappa=Q(1,64),chi=Q(1,2),zeta=Q(1,2),kappa_H=Q(1,2),split=Q(1,10**11))
SHARES=(Q(1,64),Q(31,32),Q(1,64))
BASE={'v':Q(21,10),'p':Q(14,5),'n1':Q(11,5),'n2':Q(33,20),'n3':Q(209,100),
      'n5':Q(3,2),'n9':Q(3,2),'private':Q(1),**{x:Q(77,50) for x in ('n4','n6','n7','n8')}}

def edges(source: bool,chirality: int=1):
    b=[('v' if source else f's{(i-1)%3+1}',i,f'n{i}',1) for i in range(1,10)]
    b += [('p',port,f'n{i}',4) for port,i in zip((1,4,7),(1,5,9))]
    if not source:b += [('core',port,f's{j}',port) for j,port in enumerate((2,6,7) if chirality==1 else (3,4,8),1)]
    return b+[('p',2,'private',1)]

def exact_classify(c: dict[str,Q],ee):
    adj={u:set() for u in c}; rows={u:[[] for _ in range(3)] for u in c};occ=set()
    for u,pu,v,pv in ee:
        assert (u,pu) not in occ and (v,pv) not in occ
        occ.update(((u,pu),(v,pv)));adj[u].add(v);adj[v].add(u)
        rows[u][(pu-1)//3].append(v);rows[v][(pv-1)//3].append(u)
    gg={u:[sum((c[v]-c[u] for v in rr),Q(0))/len(rr) if rr else Q(0) for rr in rows[u]] for u in c}
    targets={}
    def terminals(u):
        if u not in targets:
            nxt=[v for v in adj[u] if c[v]>c[u]]
            targets[u]=set().union(*(terminals(v) for v in nxt)) if nxt else {u}
        return targets[u]
    for u in c:terminals(u)
    basins={};margins={}
    for s in c:
        if not adj[s]:continue
        ms={'positive_resource':c[s]-Q(1,2),
            'gradient_square':16-sum(x*x for x in gg[s]),
            'hessian':min(-x for x in gg[s])-Q(1,4),
            'barrier':min(c[s]-c[v] for v in adj[s])-Q(1,2)}
        dom=[u for u in c if targets[u]=={s}]
        if min(ms.values())>0 and len(dom)>=2:basins[s]=sorted(dom);margins[s]=ms
    return dict(basins=basins,rows=gg,margins=margins)

class Equations:
    def __init__(self,nodes,ee):
        self.nodes=list(nodes); self.ee=ee;ix={u:i for i,u in enumerate(nodes)}
        self.B=np.zeros((len(nodes),len(ee)))
        for k,(u,_,v,__) in enumerate(ee):self.B[ix[u],k]=1;self.B[ix[v],k]=-1
        ends=[{u,v} for u,_,v,__ in ee]
        self.N=np.array([[len(x&y) for y in ends] for x in ends]);self.I=np.eye(len(ee));self.D=self.B.T@self.B
    def read(self,c,H):
        phi=self.B@H@self.B.T@c/64-((c-2)**3-(c-2))
        j0=-float(PARAMS['eta'])*self.B.T@phi
        y=np.linalg.solve(.75*self.I+H@self.D,j0)
        return j0+y/4,np.linalg.solve(H,y)/2
    def stage(self,c):
        jp,fp=self.read(c,self.I); H=self.I+self.N*np.outer(fp,fp)/8
        j,f=self.read(c,H);HH=self.I+self.N*np.outer(f,f)/8
        cp=c-float(PARAMS['h'])*self.B@j
        return cp,float(np.linalg.norm(H-HH,'fro')),float(np.max(np.abs(H-self.I)))

def main():
    result={'status':'exploratory_numerical_positive_not_completion',
        'parameters':PARAMS,'source':BASE,'shares':SHARES,
        'source_edges':edges(True),'target_positive_edges':edges(False,1),'target_negative_edges':edges(False,-1),
        'changes_from_retained_case':['one private exterior leaf at old parent port 2',
        'source resource preparation, total charge 21','explicit event shares 1/64,31/32,1/64'],
        'unchanged':['homogeneous quartic site law','C_OS staging and all coefficients',
        'SC1 thresholds and gain definition','D11 boundary/spine rule and exact zero core','split tolerance'],
        'discovery':'small exploratory source/transfer probes; not preregistered or autonomous selection',
        'claims_not_established':['interval-enclosed trajectory','native source/event admission',
        'postbeat source formation','actual allocator execution','full-map trapping certificate','completed spark'],
        'roles':{}}
    for role in ('current','reset'):
        s=BASE.copy()
        if role=='reset':s['n1']+=Q(1,64);s['n2']-=Q(1,128);s['n3']-=Q(1,128)
        sx=exact_classify(s,edges(True));assert set(sx['basins'])=={'p'} and set(sx['basins']['p'])==set(s)
        gv=sx['rows']['v'];assert sum(x*x for x in gv)<16 and min(-x for x in gv)<Q(1,8)
        assert sum(s.values())==21
        source_model=Equations(SOURCE_NODES,edges(True))
        _,source_split,_=source_model.stage(np.array([float(s[u]) for u in SOURCE_NODES]))
        tc={u:s.get(u,Q(0)) for u in TARGET_NODES};tc['core']=Q(0)
        for j,p in enumerate(SHARES,1):tc[f's{j}']=p*s['v']
        assert sum(tc.values())==21
        initial={str(ch):exact_classify(tc,edges(False,ch)) for ch in (1,-1)}
        assert all(set(d['basins'])=={'p'} for d in initial.values())
        model=Equations(TARGET_NODES,edges(False));c=np.array([float(tc[u]) for u in TARGET_NODES])
        observations=[];mn=float('inf');maxsplit=0.;maxgeo=0.; maxcharge=0.
        first={str(ch):None for ch in (1,-1)};last_nonpositive={str(ch):0 for ch in (1,-1)}
        for k in range(1,513):
            c,sp,geo=model.stage(c)
            assert np.isfinite(c).all() and min(c)>0
            mn=min(mn,float(min(c)));maxsplit=max(maxsplit,sp);maxgeo=max(maxgeo,geo);maxcharge=max(maxcharge,abs(float(sum(c))-21))
            oq={u:Q(float(x)) for u,x in zip(TARGET_NODES,c)}
            bychart={str(ch):exact_classify(oq,edges(False,ch)) for ch in (1,-1)}
            for ch,d in bychart.items():
                gain=len(d['basins'])-1 if any(x.startswith('s') or x=='core' for x in d['basins']) else 0
                if gain>=1 and first[ch] is None:first[ch]=k
                if gain<1:last_nonpositive[ch]=k
            observations.append(dict(step=k,basins={ch:d['basins'] for ch,d in bychart.items()},
               margins={ch:d['margins'] for ch,d in bychart.items()}))
        result['roles'][role]=dict(exact_source=s,source_predicates=sx,trigger_rows=gv,
            trigger_margin=Q(1,8)-min(-x for x in gv),source_read_split_floating=source_split,
            initial_target=tc,initial_basins={ch:d['basins'] for ch,d in initial.items()},
            first_gain_step=first,last_step_without_gain=last_nonpositive,
            steps=512,minimum_resource=mn,max_frobenius_split=maxsplit,max_geometry_change=maxgeo,
            max_floating_charge_drift=maxcharge,final_resources=dict(zip(TARGET_NODES,c)),observations=observations)
    # Exact hand checks are independent of rounded float sums.
    path=PARENT/'positive_candidate_results.json.xz'
    path.write_bytes(lzma.compress((json.dumps(result,indent=2,default=lambda x:str(x) if isinstance(x,Q) else float(x))+'\n').encode()))
    for role,r in result['roles'].items():
        print(role, {k:r[k] for k in ('trigger_rows','trigger_margin','source_read_split_floating','first_gain_step','last_step_without_gain','minimum_resource','max_frobenius_split','max_floating_charge_drift')})
if __name__=='__main__':main()
