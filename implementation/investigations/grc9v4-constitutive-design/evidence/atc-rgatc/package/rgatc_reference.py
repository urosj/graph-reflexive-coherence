"""Bounded RGATC-E/R reference; exact frozen T/A profile, no native authority.

A finite forward ladder evaluates a graph-transform iterate at a certified
inverse output. It starts with H=I afresh on every section query. No CI root,
previous geometry, source geometry transport, or persistent Z is used.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction as F
from functools import lru_cache
from math import factorial, isqrt
from pathlib import Path
from types import MappingProxyType
from collections.abc import Mapping
import hashlib
import json
import sys

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'predecessor'))
import check_rgatc_ta as ta
I,GRID,p=ta.I,ta.GRID,ta.p
DELTA,KH,RHO,M=ta.H,ta.KH,ta.RHO,ta.M
PARAMS=MappingProxyType(dict(ta.PARAMS))
R=F(1,16384); Q=F(2,47); L=F(1,2)
DEPTH=24; MAX_SHOOTS=16; SECTION_TOL=F(1,10**34)
_TOKEN=object()

class AdmissionError(ValueError):pass

def need(ok:bool,msg:str):
    if not ok:raise AdmissionError(msg)

def enc(x):
    if isinstance(x,I):return {'lo':str(F(x.lo,GRID)),'hi':str(F(x.hi,GRID))}
    if isinstance(x,F):return str(x)
    if isinstance(x,Graph):return x.payload()
    if 'Box' in globals() and isinstance(x,Box):return x.payload()
    if isinstance(x,Mapping):return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [enc(v) for v in x]
    return x

def digest(x):return hashlib.sha256(json.dumps(enc(x),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def mid(x):return F(x.lo+x.hi,2*GRID)
def upper(x):return F(x.hi,GRID)
def lower(x):return F(x.lo,GRID)
def absup(x):return F(max(abs(x.lo),abs(x.hi)),GRID)
def span(lo,hi):return I.bounds(I(lo).lo,I(hi).hi)
def flat(A):return tuple(x for row in A for x in row)
def sqrtup(q):
    q=F(q);need(q>=0,'nonnegative exact square norm')
    n=isqrt(q.numerator*GRID*GRID//q.denominator)
    if n*n*q.denominator<q.numerator*GRID*GRID:n+=1
    return F(n,GRID)
def normup(xs):return sqrtup(sum(absup(x)**2 for x in xs))
def ballnorm(xs):return sqrtup(sum(F(x)**2 for x in xs))
def identity(m):return tuple(tuple(I(int(i==j)) for j in range(m)) for i in range(m))
def same(a,b):return a.lo==b.lo and a.hi==b.hi

def intersect(xs):
    return I.bounds(max(x.lo for x in xs),min(x.hi for x in xs))

@dataclass(frozen=True)
class Graph:
    name:str
    n:int
    edges:tuple
    positions:tuple
    def __post_init__(self):
        need(type(self.edges) is tuple and type(self.positions) is tuple,'immutable graph')
        need(self.n in (5,6) and len(self.edges)==self.n-1 and len(self.positions)==self.n,'paired graph dimensions')
        need(all(type(e) is tuple and len(e)==2 and 0<=e[0]<self.n and 0<=e[1]<self.n and e[0]!=e[1] for e in self.edges),'simple edges')
        need(len({frozenset(e) for e in self.edges})==len(self.edges),'no parallel edge in declared graph')
        deg=[sum(i in e for e in self.edges) for i in range(self.n)]
        need(sorted(deg)==([1,1,1,1,4] if self.n==5 else [1,1,1,1,3,3]),'paired topology only')
        need(all(self.positions[i]==(1 if deg[i]==1 else 0) for i in range(self.n)),'declared host data')
        # Connectedness, not merely the degree sequence.
        seen={0}
        for _ in range(self.n):seen|={v for u,v in self.edges if u in seen}|{u for u,v in self.edges if v in seen}
        need(len(seen)==self.n,'connected paired graph')
    def payload(self):return dict(name=self.name,n=self.n,edges=self.edges,positions=self.positions)
    @property
    def B(self):return p.incidence(self.n,self.edges)

SOURCE=Graph('source',5,p.SOURCE,(1,1,1,1,0))
TARGET=Graph('target',6,p.TARGET,(1,1,1,1,0,0))
GRAPHS={'source':SOURCE,'target':TARGET}
PROFILE=MappingProxyType(dict(schema='rgatc_er_frozen_profile_v1',completion='rgatc_paired_floor_preserving_completion_v1_proposed',
             delta=DELTA,kappa_H=KH,tau='1/(8*log(2))',parameters=PARAMS,
             native_authority=False))
PROFILE_ID=digest(PROFILE)
EVALUATOR=MappingProxyType(dict(algorithm='finite_forward_ladder_output_residual_v1',arithmetic_bits=256,
    default_depth=DEPTH,maximum_depth=40,maximum_inverse_shoots=MAX_SHOOTS,default_tolerance=SECTION_TOL))

# Outward fixed-grid elementary functions. The retained I kernel is unchanged.
# Taylor remainder at |t|<=1/8 is <(1/8)^51/51!/(1-1/(8*52)).
_EXP_TAIL=F(1,8)**51/F(factorial(51))/(1-F(1,8*52))
@lru_cache(maxsize=20000)
def _exp_endpoint(integer):
    x=F(integer,GRID);s=0
    while abs(x)>F(1,8):x/=2;s+=1
    xx=I(x);term=I(1);total=I(1)
    for k in range(1,51):term=term*xx/k;total+=term
    total+=span(-_EXP_TAIL,_EXP_TAIL)
    need(total.lo>0,'positive reduced exponential')
    for _ in range(s):total=total.square()
    return total.lo,total.hi

def expi(x):
    x=I.coerce(x)
    return I.bounds(_exp_endpoint(x.lo)[0],_exp_endpoint(x.hi)[1])

_LOG_TAIL=2*F(1,3)**193/(193*(1-F(1,9)))
@lru_cache(maxsize=20000)
def _log_endpoint(integer):
    x=I.bounds(integer,integer)
    need(GRID//2<=integer<=3*GRID//2,'log positive support interval')
    z=(x-1)/(x+1);term=z;total=I(0);z2=z.square()
    for k in range(96):total+=term/(2*k+1);term=term*z2
    out=2*total+span(-_LOG_TAIL,_LOG_TAIL)
    return out.lo,out.hi

def logi(x):
    need(x.lo>=GRID//2 and x.hi<=3*GRID//2,'log support range')
    return I.bounds(_log_endpoint(x.lo)[0],_log_endpoint(x.hi)[1])

LOG2=-logi(I(F(1,2)))
DECAY=expi(-8*DELTA*LOG2)
TAU64='0x1.71547652b82fep-3' # verified against independent 110-digit Decimal below

def smooth_value(q,A,a,b,B):
    if q<=A or q>=B:return F(0)
    if a<=q<=b:return F(1)
    t=(q-A)/(a-A) if q<a else (B-q)/(B-b)
    return 3*t*t-2*t*t*t

def cutoff1(x,A,a,b,B):
    lo,hi=lower(x),upper(x)
    vals=[smooth_value(lo,A,a,b,B),smooth_value(hi,A,a,b,B)]
    vals += [smooth_value(q,A,a,b,B) for q in (A,a,b,B) if lo<=q<=hi]
    return span(min(vals),max(vals))

def cutoff(C,W):
    out=I(1)
    for c in C:out*=cutoff1(c,F(-2),F(-1),F(10),F(11))
    for w in W:out*=cutoff1(w,F(1,2),F(3,4),F(5,4),F(3,2))
    return out

def descriptor(g,C):
    ans=[]
    for i in range(g.n):
        num=I(0);den=1
        for u,v in g.edges:
            if i not in (u,v):continue
            j=v if i==u else u;dx=g.positions[j]-g.positions[i]
            num+=dx*(C[j]-C[i]);den+=dx*dx
        ans.append(num/den)
    return tuple(ans)

def conductance(g,C,D,J):
    es=[];gs=[]
    for (u,v),j in zip(g.edges,J,strict=True):
        e=(PARAMS['alpha']*(C[u]+C[v])+PARAMS['beta']*(D[u]-D[v]).square()+PARAMS['gamma']*j.square())/2
        # effective exponent min(E,log2) preserves the auxiliary floor.
        cap=I.bounds(min(e.lo,LOG2.lo),min(e.hi,LOG2.hi))
        gg=expi(-cap)
        # Exact floor is a fact of the formula, not an admission tolerance.
        gg=I.bounds(max(gg.lo,GRID//2),gg.hi)
        es.append(cap);gs.append(gg)
    return tuple(gs),tuple(es)

def fixed_read(g,C,W,H):
    B=g.B;BT=tuple(zip(*B));diff=p.mv(BT,C)
    lap=p.mv(B,tuple(w*d for w,d in zip(W,diff,strict=True)))
    inc=tuple(tuple(x-int(i==j) for j,x in enumerate(row)) for i,row in enumerate(H))
    geo=p.mv(B,p.mv(inc,diff))
    pot=tuple(PARAMS['a']*c+PARAMS['nu']*c.square()/2 for c in C)
    phi=tuple(l-v+PARAMS['kah']*z for l,v,z in zip(lap,pot,geo,strict=True))
    b=tuple(-w*d for w,d in zip(W,p.mv(BT,phi),strict=True))
    D=descriptor(g,C);drive,expo=conductance(g,C,D,b)
    q=tuple((w-v)/(w+v) for w,v in zip(W,drive,strict=True))
    denom=tuple(1-PARAMS['chi']*v for v in q)
    need(all(x.lo>0 for x in denom),'fixed-current regularity')
    J=tuple(bb/dd for bb,dd in zip(b,denom,strict=True))
    rb=tuple(PARAMS['chi']*v*j for v,j in zip(q,J,strict=True))
    vv=p.solve(H,rb);S=p.star(vv,B)
    return dict(H=H,descriptor=D,potential=pot,geometry_phi=geo,phi=phi,baseline=b,drive=drive,
                effective_exponent=expo,q=q,denominator=denom,current=J,readback=rb,flat=vv,source=S)

def raw_step(g,C,W,H,decay=DECAY,physical=False):
    selected=fixed_read(g,C,W,H)
    outC=tuple(c-DELTA*v for c,v in zip(C,p.mv(g.B,selected['current']),strict=True))
    if physical:need(all(c.lo>0 for c in outC),'positive resource proposal before W writer')
    D=descriptor(g,outC);drive,expo=conductance(g,outC,D,selected['current'])
    outW=tuple(expi(decay*logi(w)-(1-decay)*e) for w,e in zip(W,expo,strict=True))
    return outC,outW,dict(selected=selected,writer_descriptor=D,writer_drive=drive,writer_exponent=expo,decay=decay)

def completed(g,C,W,H):
    beta=cutoff(C,W)
    if beta.hi==0:return C,W,identity(len(W)),beta
    # Clip an enclosure at auxiliary support boundaries. beta=0 on the
    # exterior part; beta*f_raw(clipped support) encloses the full extension.
    cc=tuple(I.bounds(max(x.lo,-2*GRID),min(x.hi,11*GRID)) for x in C)
    ww=tuple(I.bounds(max(x.lo,GRID//2),min(x.hi,3*GRID//2)) for x in W)
    outC,outW,details=raw_step(g,cc,ww,H)
    S=details['selected']['source']
    return (tuple(x+beta*(y-z) for x,y,z in zip(C,outC,cc,strict=True)),
            tuple(x+beta*(y-z) for x,y,z in zip(W,outW,ww,strict=True)),
            tuple(tuple(I(int(i==j))+KH*beta*s for j,s in enumerate(row)) for i,row in enumerate(S)),beta)

def ladder(g,seed,depth):
    C=tuple(I(x) for x in seed[:g.n]);W=tuple(I(x) for x in seed[g.n:]);HH=identity(len(W))
    cut=[]
    for _ in range(depth):
        C,W,HH,beta=completed(g,C,W,HH);cut.append((beta.lo,beta.hi))
    return C+W,HH,cut

SECTION_QUERIES=0

def section(g,C,W,*,depth=DEPTH,max_shoots=MAX_SHOOTS,tolerance=SECTION_TOL):
    """Certified Gamma on an input box; all numerical work is query-local.

    Exact forward ladder output lies on Gamma_depth at its final state.
    Final inverse residual is converted by Lip(Gamma_depth)<=1/2. Add
    arithmetic ball, uncertain query radius, and the global Banach tail.
    """
    global SECTION_QUERIES
    need(type(depth) is int and 1<=depth<=40,'finite graph-transform depth')
    need(type(max_shoots) is int and 1<=max_shoots<=MAX_SHOOTS,'finite inverse work')
    need(type(tolerance) is F and tolerance>0,'positive error contract')
    SECTION_QUERIES+=1
    vec=tuple(C)+tuple(W)
    need(len(C)==g.n and len(W)==len(g.edges),'section input dimensions')
    query=tuple(mid(x) for x in vec)
    width=max(absup(x-q) for x,q in zip(vec,query,strict=True))
    seed=query
    tail=R*Q**depth
    need(tail+L*width<tolerance,'section tail/input width exceeds budget')
    for shoot in range(max_shoots):
        out,HH,cut=ladder(g,seed,depth)
        residual=max(absup(y-x) for y,x in zip(out,query,strict=True))
        center=tuple(tuple(mid(h) for h in row) for row in HH)
        numerr=ballnorm(tuple(absup(h-c) for row,other in zip(HH,center,strict=True) for h,c in zip(row,other,strict=True)))
        radius=numerr+L*(residual+width)+tail
        if radius<=tolerance:
            need(ballnorm(tuple(center[i][j]-int(i==j) for i in range(len(W)) for j in range(len(W))))+len(W)*radius<RHO,
                 'section numerical enclosure in certified H ball')
            box=tuple(tuple(span(c-radius,c+radius) for c in row) for row in center)
            result=dict(H=box,center=center,radius=radius,arithmetic_error=numerr,inverse_output_residual=residual,
                input_radius=width,banach_tail=tail,depth=depth,inverse_shoots=shoot+1,
                completed_ladder_steps=depth*(shoot+1),query=vec,query_digest=digest(dict(graph=g,values=vec)),
                graph=g,profile_id=PROFILE_ID,proof='finite_ladder_on_Gamma_N_then_Lipschitz_output_residual_v1',
                all_inverse_ladder_cutoffs_one=all(a==b==GRID for a,b in cut),
                previous_geometry_used=False,CI_root_used=False,tolerance=tolerance,max_shoots=max_shoots,
                evaluator_policy_id=digest(dict(contract=EVALUATOR,depth=depth,max_shoots=max_shoots,tolerance=tolerance)))
            result['section_digest']=digest(result)
            return result
        seed=tuple(x-(mid(y)-q) for x,y,q in zip(seed,out,query,strict=True))
    raise AdmissionError('section inverse/error budget exhausted')

@dataclass(frozen=True)
class Box:
    lo:int
    hi:int
    def __post_init__(self):need(type(self.lo) is int and type(self.hi) is int and self.lo<=self.hi,'immutable interval endpoints')
    @classmethod
    def freeze(cls,x):return cls(x.lo,x.hi)
    def thaw(self):return I.bounds(self.lo,self.hi)
    def payload(self):return dict(lo=str(F(self.lo,GRID)),hi=str(F(self.hi,GRID)))

@dataclass(frozen=True,init=False)
class State:
    graph:str
    C:tuple
    W:tuple
    radius2:F|None
    provenance:tuple
    def __init__(self,graph,C,W,radius2,provenance,*,token=None):
        need(token is _TOKEN,'exact_state or executing operation required')
        need(graph in GRAPHS,'physical graph name')
        g=GRAPHS[graph];C=tuple(C);W=tuple(W)
        need(len(C)==g.n and len(W)==len(g.edges),'state dimensions')
        need(all(c.hi>0 for c in C) if provenance[0]=='rational' else all(c.lo>0 for c in C),'positive physical resources')
        need(sum(C,I(0)).contains(F(9)),'charge proof contradicts enclosure')
        need(all(w.hi>=M*GRID and w.lo<=GRID for w in W),'history proof contradicts enclosure')
        for v in (C,W):
            need(same(v[0],v[1]) and same(v[2],v[3]),'paired scientific enclosures')
        if graph=='source' and provenance[0]!='rational':
            need((C[4]-(C[0]+C[2])/2).lo>=F(29,10)*GRID,'certified source read corridor')
        if graph=='target':
            need(type(radius2) is F and 0<=radius2<=F(9,4),'target radius certificate')
            need(lower(p.norm2(tuple(x-F(3,2) for x in C)))<=radius2,'target radius contradiction')
        object.__setattr__(self,'graph',graph)
        object.__setattr__(self,'C',tuple(Box.freeze(x) for x in C));object.__setattr__(self,'W',tuple(Box.freeze(x) for x in W))
        object.__setattr__(self,'radius2',radius2);object.__setattr__(self,'provenance',provenance)
    def values(self):return tuple(x.thaw() for x in self.C),tuple(x.thaw() for x in self.W)
    def payload(self):return enc(dict(graph=self.graph,C=self.C,W=self.W,radius2=self.radius2,provenance=self.provenance))
    @property
    def identity(self):return digest(self.payload())

def paired(v):
    out=list(v)
    for i,j in ((0,1),(2,3)):out[i]=out[j]=intersect((v[i],v[j]))
    return tuple(out)

def exact_state(graph,C,W):
    need(graph in GRAPHS,'graph')
    need(type(C) is tuple and type(W) is tuple,'immutable rational inputs')
    need(all(type(x) in (F,int) for x in C+W),'exact rational state')
    C=tuple(map(F,C));W=tuple(map(F,W));g=GRAPHS[graph]
    need(len(C)==g.n and len(W)==len(g.edges),'input dimensions')
    need(sum(C)==9 and min(C)>0,'exact positive Q9')
    need(min(W)>=M and max(W)<=1,'exact W floor and ceiling')
    for v in (C,W):need(v[0]==v[1] and v[2]==v[3],'exact pairing, not interval overlap')
    if graph=='source':
        need(C[4]-(C[0]+C[2])/2>=F(29,10),'source root corridor')
        rad=None
    else:
        rad=sum((c-F(3,2))**2 for c in C);need(rad<=F(9,4),'exact target radius')
    return State(graph,tuple(map(I,C)),tuple(map(I,W)),rad,('rational',C,W),token=_TOKEN)

def source_state(x,y,u,v):
    C=((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,)
    return exact_state('source',C,(u,u,v,v))

def seeds():
    eps=F(1,2**30)
    return (source_state(3-DELTA,F(1,2**24),F(99,100)-eps,F(99,100)+eps),
            source_state(F(13,4),-F(1,100),F(97,100),F(99,100)))

def read(state):
    need(type(state) is State,'exact state witness required')
    C,W=state.values();g=GRAPHS[state.graph]
    sec=section(g,C,W);rd=fixed_read(g,C,W,sec['H'])
    return dict(section=sec,read=rd,state_binding=state.identity,profile_id=PROFILE_ID)

def ordinary(state,delta=DELTA):
    need(type(delta) is F and delta==DELTA,'frozen positive RG beat')
    need(type(state) is State,'exact state witness required')
    C,W=state.values();g=GRAPHS[state.graph];sel=read(state)
    cc,ww,details=raw_step(g,C,W,sel['section']['H'],physical=True)
    cc,ww=paired(cc),paired(ww)
    need(all(w.hi>=M*GRID and w.lo<=GRID for w in ww),'writer invariant compatibility')
    rad=None
    if state.graph=='target':rad=min(upper(p.norm2(tuple(c-F(3,2) for c in cc))), (1-F(3,4)*DELTA)**2*state.radius2)
    proof=('ordinary',state.identity,digest(dict(C=cc,W=ww)),PROFILE_ID,DELTA)
    nxt=State(state.graph,cc,ww,rad,proof,token=_TOKEN)
    restart=read(nxt)
    gen=tuple(tuple(I(int(i==j))+KH*s for j,s in enumerate(row)) for i,row in enumerate(sel['read']['source']))
    residual=tuple(tuple(x-y for x,y in zip(row,other,strict=True)) for row,other in zip(restart['section']['H'],gen,strict=True))
    need(all(x.contains(F(0)) for x in flat(residual)),'independent next-section/generated invariance enclosures')
    details.update(selected=sel,restart=restart,generated_H=gen,invariance_residual=residual,
                   resource_writes=1,history_writes=1,geometry_state_writes=0)
    return nxt,details

def transfer_guard(state,current=False):
    need(type(state) is State and state.graph=='source','source transfer graph')
    C,W=state.values()
    if state.provenance[0]=='rational':
        c=state.provenance[1];w=state.provenance[2];x=c[4]-(c[0]+c[2])/2;y=(c[0]-c[2])/2
        need(3<=x<=F(7,2) and abs(y)<=F(1,50),'exact transfer domain')
        if current:need(y>=0 and w[0]<w[2],'current decorated sector order')
    else:
        x=C[4]-(C[0]+C[2])/2;y=(C[0]-C[2])/2
        need(x.lo>=3*GRID and x.hi<=F(7,2)*GRID and y.lo>=-F(1,50)*GRID and y.hi<=F(1,50)*GRID,'certified transfer domain')
        if current:need(y.lo>=0 and W[0].hi<W[2].lo,'current decorated sector order')

def select(state):
    transfer_guard(state,True);ev=read(state);J=ev['read']['current'];u=J[0]+J[1];v=J[2]+J[3]
    need(u.lo>0 and v.lo>0,'positive event inflows')
    raw=65536*u/(u+v);k=round(mid(raw))
    need((F(k)-F(1,2))*GRID<raw.lo and raw.hi<(F(k)+F(1,2))*GRID,'unique dyadic cell')
    need(F(31,64)<=F(k,65536)<=F(33,64),'funded share domain')
    return dict(k=k,raw_index=raw,event_read=ev)

def transfer(state,k):
    transfer_guard(state)
    need(type(k) is int and F(31,64)<=F(k,65536)<=F(33,64),'typed admitted share')
    C,W=state.values();share=F(k,65536)
    cc=C[:4]+(share*C[4],(1-share)*C[4]);ww=W+(I(1),)
    rad=upper(p.norm2(tuple(c-F(3,2) for c in cc)))
    nxt=State('target',cc,ww,rad,('transfer',state.identity,k,PROFILE_ID),token=_TOKEN)
    admitted=read(nxt)
    return nxt,admitted

def history_reset(state):
    need(type(state) is State,'state history intervention')
    C,W=state.values()
    return State(state.graph,C,tuple(I(1) for _ in W),state.radius2,('W_reset_only',state.identity,PROFILE_ID),token=_TOKEN)

@dataclass(frozen=True)
class Publication:
    current:State
    reset:State
    last:str='initial'
    parent:str|None=None
    event:tuple|None=None
    clock:F=F(0)
    def __post_init__(self):
        need(type(self.current) is State and type(self.reset) is State,'typed independent roles')
        need(self.current.graph==self.reset.graph,'both-role topology')
        need(type(self.clock) is F and self.clock>=0,'exact lifecycle clock')
    def payload(self):return dict(current=self.current.payload(),reset=self.reset.payload(),profile_id=PROFILE_ID,last=self.last,parent=self.parent,event=self.event,clock=self.clock)
    @property
    def identity(self):return digest(self.payload())

class Owner:
    def __init__(self,publication):
        need(type(publication) is Publication,'publication required')
        read(publication.current);read(publication.reset);self.publication=publication
    def ordinary(self,delta=DELTA,after=None):
        before=self.publication;read(before.reset)
        nxt,details=ordinary(before.current,delta)
        candidate=replace(before,current=nxt,last='ordinary',clock=before.clock+DELTA)
        if after:after(candidate)
        self.publication=candidate
        return details
    def split(self,after=None):
        before=self.publication
        need(before.last=='ordinary' and before.current.provenance[0]=='ordinary' and before.current.graph=='source' and before.event is None,'post-positive-beat single fission boundary')
        choice=select(before.current)
        cur,cr=transfer(before.current,choice['k']);rst,rr=transfer(before.reset,choice['k'])
        event=(choice['k'],tuple((i,i) for i in range(4)),4,'W_bridge_one_no_H_transport',choice['event_read']['section']['section_digest'])
        candidate=Publication(cur,rst,'split',before.identity,event,before.clock)
        if after:after(candidate)
        self.publication=candidate
        return dict(choice=choice,current_target=cr,reset_target=rr)
    def reset(self):
        before=self.publication;read(before.reset)
        self.publication=replace(before,current=before.reset,last='reset')

def snapshot(pub):return dict(payload=pub.payload(),digest=pub.identity)

def replay(source,record):
    need(type(record) is dict and set(record)=={'source','actions','final'},'replay schema')
    need(record['source']==source.identity,'replay source lineage')
    need(type(record['actions']) is list and 0<len(record['actions'])<=16,'bounded replay actions')
    owner=Owner(source)
    for act in record['actions']:
        need(type(act) is dict and set(act)=={'kind','delta','before','after'},'replay action schema')
        need(act['before']==owner.publication.identity,'replay predecessor')
        if act['kind']=='ordinary':owner.ordinary(F(act['delta']))
        elif act['kind']=='split':
            need(act['delta'] is None,'zero-time event');owner.split()
        elif act['kind']=='reset':
            need(act['delta'] is None,'zero-time reset');owner.reset()
        else:raise AdmissionError('unknown replay action')
        need(act['after']==owner.publication.identity,'replay result identity')
    need(record['final']==snapshot(owner.publication),'full physics-replay snapshot')
    return owner.publication

# Representation is a diagnostic path, never a constructive exact-charge role.
def project(x):
    lo,hi=float(lower(x)),float(upper(x))
    need(lo==hi,'binary64 rounding not resolved by enclosure')
    return F(lo)

def point_admission(C,W):
    need(type(C) is tuple and type(W) is tuple and len(C)==6 and len(W)==5,'target-only represented points')
    need(all(type(x) is F and F(float(x))==x for x in C+W),'exact binary64 point operands')
    need(min(C)>0 and min(W)>=M and max(W)<=1,'represented positivity/history domain')
    need(C[0]==C[1] and C[2]==C[3] and W[0]==W[1] and W[2]==W[3],'represented exact pairing')
    need(sum((c-F(3,2))**2 for c in C)<=F(9,4),'represented target radius')

def represented_read(C,W):
    point_admission(C,W)
    cc,ww=tuple(map(I,C)),tuple(map(I,W))
    sec=section(TARGET,cc,ww)
    return dict(section=sec,read=fixed_read(TARGET,cc,ww,sec['H']),state_binding=None,
                profile_id=PROFILE_ID,exact_charge_authority=False)

def represented_step(C,W,delta=DELTA):
    need(type(delta) is F and delta==DELTA,'represented frozen dyadic beat')
    selected=represented_read(C,W)
    d64=expi(-I(DELTA)/I(F(float.fromhex(TAU64))))
    cc,ww,details=raw_step(TARGET,tuple(map(I,C)),tuple(map(I,W)),selected['section']['H'],d64,physical=True)
    cpoint,wpoint=tuple(project(x) for x in cc),tuple(project(x) for x in ww)
    restart=represented_read(cpoint,wpoint)
    exactC,exactW,_=raw_step(TARGET,tuple(map(I,C)),tuple(map(I,W)),selected['section']['H'],DECAY,physical=True)
    local_error=max(absup(x-y) for x,y in zip(exactC+exactW,cpoint+wpoint,strict=True))
    defect_bound=L*local_error
    generated=tuple(tuple(I(int(i==j))+KH*v for j,v in enumerate(row)) for i,row in enumerate(selected['read']['source']))
    generated_center=tuple(tuple(mid(x) for x in row) for row in generated)
    generated_error=ballnorm(absup(x-y) for row,other in zip(generated,generated_center,strict=True) for x,y in zip(row,other,strict=True))
    center_gap=ballnorm(x-y for row,other in zip(restart['section']['center'],generated_center,strict=True) for x,y in zip(row,other,strict=True))
    need(center_gap<=defect_bound+restart['section']['radius']+generated_error,'represented RG defect bridge')
    # This path approximates the original frozen exact-tau profile. It does
    # NOT silently redefine Gamma to the tau64 ordinary-map completion.
    details.update(selected=selected,restart=restart,rounded_tau=F(float.fromhex(TAU64)),
                   section_profile_tau='exact 1/(8 log 2)',writer_tau='binary64 approximation',
                   exact_charge_authority=False,local_exact_map_error=local_error,
                   invariance_defect_bound=defect_bound,invariance_center_gap=center_gap,generated_error=generated_error)
    return cpoint,wpoint,details

def eligible_event(state):
    """Sufficient bounded event guard only; no target inspection."""
    try:transfer_guard(state,True)
    except AdmissionError:return False
    return True

def autonomous_beat(owner,delta=DELTA,after_event=None):
    """One ordinary transaction followed by a conditional separate event.

    An event failure leaves the already successful ordinary commit intact.
    This is a bounded research dispatcher, not a general/native K0 scheduler.
    """
    need(type(owner) is Owner,'research owner')
    details=owner.ordinary(delta)
    if owner.publication.current.graph!='source' or not eligible_event(owner.publication.current):
        return dict(ordinary=details,event_status='outside_sufficient_event_domain',event=None)
    event=owner.split(after_event)
    return dict(ordinary=details,event_status='committed_fission',event=event)
