"""G7-R certified research reference, not a pygrc model or native policy.

Full incidence equations on the two reviewed source/target graph classes.
Exact-real enclosures remain separate from a proposed binary64-publication
experiment. No runtime registration, production owner, target search or I/O.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
from types import MappingProxyType

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_atc_sector_channels as mathref

p, I, GRID = mathref.p, mathref.I, mathref.GRID
NATIVE = False
TAU64 = '0x1.71547652b82fep-3'
PARAMS = MappingProxyType(dict(alpha=F(3,8192),beta=F(3,8192),gamma=F(3,4096),
              chi=F(3,64),kh=F(3,4),kah=F(3,4),a=F(19,4),nu=F(1,65536)))
GRAPHS = MappingProxyType(dict(mathref.GRAPHS))


class AdmissionError(ValueError):
    pass


def require(ok,reason):
    if not ok:
        raise AdmissionError(reason)


def digest(value):
    return hashlib.sha256(p.canonical(value)).hexdigest()


def encode(value):
    return p.encode(value)


def bound(x):
    return F(x.lo,GRID),F(x.hi,GRID)


def project(x):
    """Certify one rounded binary64 result for the entire exact enclosure."""
    low,high=map(float,bound(x))
    require(low==high,'unresolved binary64 rounding')
    return I(F(low))


def profile_payload():
    return dict(schema='atc_g7_research_reference_v1',candidate='A',realization='OS',
        law='p(c)=a*c+nu*c*c/2',params={k:str(v) for k,v in PARAMS.items()},
        tau_exact='1/(8*log(2))',tau_binary64=TAU64,
        graphs={k:dict(vertices=n,edges=edges,positions=pos,reference_weights=1,ridge=1)
                for k,(n,edges,pos) in GRAPHS.items()},
        exact_numerics='outward_2**256_interval_full_stage',
        represented_numerics='exact_input_enclosed_stage_then_binary64_C_W_publication',
        native_authority=False)


PROFILE_ID=digest(profile_payload())


class RetainedInterval(I):
    """Detach immutable state endpoints; arithmetic still returns ordinary I."""
    def __init__(self,value):
        require(isinstance(value,I),'typed retained interval')
        object.__setattr__(self,'endpoints',(value.lo,value.hi))

    @property
    def lo(self):return self.endpoints[0]

    @property
    def hi(self):return self.endpoints[1]

    def __setattr__(self,name,value):
        raise AttributeError('retained interval is immutable')


@dataclass(frozen=True)
class State:
    C: tuple
    W: tuple
    source_exact: tuple | None = None

    def __post_init__(self):
        require(type(self.C) is tuple and type(self.W) is tuple,'ordered retained state')
        object.__setattr__(self,'C',tuple(RetainedInterval(v) for v in self.C))
        object.__setattr__(self,'W',tuple(RetainedInterval(v) for v in self.W))
        require(self.source_exact is None or
                (type(self.source_exact) is tuple and len(self.source_exact)==2 and
                 all(type(row) is tuple and all(type(v) is F for v in row) for row in self.source_exact)),
                'immutable exact source preimage')

    def payload(self):
        return encode(dict(C=self.C,W=self.W,source_exact=self.source_exact))

    @classmethod
    def load(cls,value):
        require(type(value) is dict and set(value)=={'C','W','source_exact'},'state schema')
        def vector(rows):
            require(type(rows) is list,'ordered state vector')
            out=[]
            for row in rows:
                require(type(row) is dict and set(row)=={'lo','hi'},'interval schema')
                require(all(type(v) is str and str(int(v))==v for v in row.values()),'canonical endpoint')
                require(int(row['lo'])<=int(row['hi']),'interval order')
                out.append(I.bounds(int(row['lo']),int(row['hi'])))
            return tuple(out)
        exact=value['source_exact']
        if exact is not None:
            require(type(exact) is list and len(exact)==2,'source exact preimage')
            exact=tuple(tuple(F(x) for x in row) for row in exact)
        return cls(vector(value['C']),vector(value['W']),exact)

    def represented(self):
        return State(tuple(map(project,self.C)),tuple(map(project,self.W)))


def validate(graph,state):
    require(graph in GRAPHS and type(state) is State,'research graph/state')
    n,edges,_=GRAPHS[graph]
    require(len(state.C)==n and len(state.W)==len(edges),'complete coordinate coverage')
    require(all(0<x.lo<=x.hi<=9*GRID for x in state.C),'resource domain not certified')
    require(all(GRID//2<=x.lo<=x.hi<=GRID for x in state.W),'history domain not certified')


def descriptor(graph,C):
    return p.mv(mathref.wls_matrix(*GRAPHS[graph]),C)


def conductance(graph,C,D,current):
    _,edges,_=GRAPHS[graph]
    exponents=tuple(PARAMS['alpha']*(C[u]+C[v])/2+
        PARAMS['beta']*(D[u]-D[v]).square()/2+PARAMS['gamma']*j.square()/2
        for (u,v),j in zip(edges,current,strict=True))
    require(all(e.lo>=0 for e in exponents),'nonnegative exponent')
    target=tuple((-e).exp_nonpositive() for e in exponents)
    require(all(t.lo>GRID//2 for t in target),'floor inactivity uncertified')
    return target


def read(graph,state,H):
    """No reduction by paired coordinates: full graph and actual potential."""
    validate(graph,state)
    n,edges,_=GRAPHS[graph]; B=p.incidence(n,edges); BT=tuple(zip(*B))
    C,W=state.C,state.W;d=p.mv(BT,C)
    lap=p.mv(B,tuple(w*x for w,x in zip(W,d,strict=True)))
    potential=tuple(PARAMS['a']*c+PARAMS['nu']*c.square()/2 for c in C)
    delta=tuple(tuple(h-int(i==j) for j,h in enumerate(row)) for i,row in enumerate(H))
    geometry=p.mv(B,p.mv(delta,d))
    phi=tuple(l-v+PARAMS['kah']*g for l,v,g in zip(lap,potential,geometry,strict=True))
    baseline=tuple(-w*x for w,x in zip(W,p.mv(BT,phi),strict=True))
    D=descriptor(graph,C);drive=conductance(graph,C,D,baseline)
    q=tuple((w-t)/(w+t) for w,t in zip(W,drive,strict=True))
    denom=tuple(1-PARAMS['chi']*x for x in q)
    require(all(x.lo>0 for x in denom),'read denominator')
    J=tuple(b/d for b,d in zip(baseline,denom,strict=True))
    readback=tuple(PARAMS['chi']*x*j for x,j in zip(q,J,strict=True))
    flat=p.solve(H,readback)
    return dict(potential=potential,phi=phi,baseline=baseline,descriptor=D,
                drive=drive,current=J,readback=readback,flat=flat)


def identity(m):
    return tuple(tuple(I(int(i==j)) for j in range(m)) for i in range(m))


def evaluate(graph,state,h,represented_tau=False):
    require(type(h) is F and F(3,25)<=h<=F(1,8),'request outside G6 domain')
    n,edges,_=GRAPHS[graph];B=p.incidence(n,edges);H0=identity(len(edges))
    ref=read(graph,state,H0);S=p.star(ref['flat'],B)
    H=tuple(tuple(a+PARAMS['kh']*s for a,s in zip(row,srow,strict=True))
            for row,srow in zip(H0,S,strict=True))
    fresh=read(graph,state,H);S1=p.star(fresh['flat'],B)
    residual2=PARAMS['kh']**2*p.norm2(tuple(a-b for row,other in zip(S,S1,strict=True)
                                         for a,b in zip(row,other,strict=True)))
    require(residual2.hi<GRID*F(1,512**2),'OS residual not admitted')
    Cn=tuple(c-h*j for c,j in zip(state.C,p.mv(B,fresh['current']),strict=True))
    minimum=p.minimum(Cn)
    if minimum.hi<=0:
        raise AdmissionError('resource rejection before writer')
    require(minimum.lo>0 and all(c.hi<=9*GRID for c in Cn),'resource positivity uncertain')
    Dn=descriptor(graph,Cn)
    drives=conductance(graph,Cn,Dn,fresh['current'])
    rho=(-I(h)/I(F(float.fromhex(TAU64)))).exp_nonpositive() if represented_tau else mathref.decay(I(h))
    Wn=tuple((rho*mathref.log_nonpositive(w)+(1-rho)*mathref.log_nonpositive(t)).exp_nonpositive()
             for w,t in zip(state.W,drives,strict=True))
    out=State(Cn,Wn);validate(graph,out)
    return out,dict(reference=ref,generated_H=H,fresh=fresh,writer_descriptor=Dn,
                    writer_drive=drives,rho=rho,residual_squared=residual2)


def rounded_share(activity_u,activity_v):
    require(activity_u.lo>0 and activity_v.lo>0,'positive parent inflows')
    share=activity_u/(activity_u+activity_v)
    lo,hi=bound(share);kl,kh=round(65536*lo),round(65536*hi)
    require(kl==kh and 0<kl<65536,'unresolved dyadic allocation')
    return kl,share


def source_domain(graph,state,current):
    validate(graph,state);C,W=state.C,state.W
    # Exact pairing is structural. Interval endpoints agree because this
    # local reference transports the declared decorated symmetric states.
    def equal(a,b):return (a.lo,a.hi)==(b.lo,b.hi)
    require(type(state.source_exact) is tuple and len(state.source_exact)==2,'exact source preimage required')
    exactC,exactW=state.source_exact
    require(len(exactC)==len(C) and len(exactW)==len(W),'source preimage coverage')
    require(all(type(v) is F and equal(I(v),enclosed)
                for values,enclosures in ((exactC,C),(exactW,W))
                for v,enclosed in zip(values,enclosures,strict=True)), 'source enclosure/preimage mismatch')
    require(exactC[0]==exactC[1] and exactC[2]==exactC[3] and
            exactW[0]==exactW[1] and exactW[2]==exactW[3],'exact source pairing, not interval equality')
    require(equal(C[0],C[1]) and equal(C[2],C[3]) and equal(W[0],W[1]) and equal(W[2],W[3]),'source sectors not exact')
    if graph=='paired_source':
        x=C[4]-(C[0]+C[2])/2;y=(C[0]-C[2])/2
        require(x.lo>=3*GRID and x.hi<=GRID*F(7,2),'paired source x domain')
        require(y.lo>=GRID*(0 if current else -F(1,50)) and y.hi<=GRID*F(1,50),'paired source y domain')
        require(all(w.lo>=GRID*F(24,25) for w in W),'paired history domain')
        require(sum(exactC)==9,'paired exact source charge')
        if current:require(W[0].hi<W[2].lo,'current sector order')
    elif graph=='embedded_source':
        eps=F(1,10000)
        require(exactC[5]==exactC[6] and exactW[4]==exactW[5],'exact environment pairing')
        require(equal(C[5],C[6]) and equal(W[4],W[5]),'environment symmetry')
        require(all(c.lo>=GRID*(1-eps) and c.hi<=GRID*(1+eps) for c in (C[0],C[2],C[5])),'embedded state box')
        require(GRID*(F(99,100)-eps)<=W[0].lo<=W[0].hi<=GRID*(F(99,100)+eps),'embedded u')
        require(all(w.lo>=GRID*(1-eps) for w in (W[2],W[4])),'embedded v/w')
        require(sum(exactC)==F(41,5),'embedded exact source charge')
        if current:require(C[0].lo>=C[2].hi,'current ru >= rv')
    else:
        raise AdmissionError('no research fission authority on this graph')


def prescribe(graph,state):
    source_domain(graph,state,True)
    rd=read(graph,state,identity(len(state.W)))
    bu,bv=rd['baseline'][0],rd['baseline'][2]
    if graph=='paired_source':
        require(bu.lo>0 and bv.lo>0,'actual potential parent baselines')
        diff=bu-bv
        require(max(abs(diff.lo),abs(diff.hi))*64<=(bu+bv).lo,'actual-p balance')
    k,share=rounded_share(rd['current'][0]+rd['current'][1],rd['current'][2]+rd['current'][3])
    low,high=(F(31,64),F(33,64)) if graph=='paired_source' else (F(15,32),F(17,32))
    require(low<=F(k,65536)<=high,'share outside reviewed enclosure')
    return dict(k=k,share=share,reference_current=rd['current'],current_only=True)


def transfer(graph,state,k):
    """One source-selected recipe, both roles independently, no history reset."""
    source_domain(graph,state,False)
    share=F(k,65536);C,W=state.C,state.W
    left,right=share*C[4],(1-share)*C[4]
    require((left-C[0]).lo>0 and (right-C[2]).lo>0,'child funding not admitted')
    target=graph.replace('source','target')
    result=State(C[:4]+(left,right)+C[5:],W[:4]+(I(1),)+W[4:])
    validate(target,result)
    return target,result


def target_admit(graph,state,h):
    # Paired roles enter the return ball after one admitted target step;
    # embedded roles are already inside it. This check is detached, not a
    # hidden committed step at the event boundary.
    nxt,_=evaluate(graph,state,h)
    checked=nxt if graph=='paired_target' else state
    c,R=(F(3,2),F(2,3)) if graph=='paired_target' else (F(41,40),F(1,4))
    require(p.norm2(tuple(x-c for x in checked.C)).hi<GRID*R*R,'target return entry')
    require(all(w.lo>=GRID*F(24,25) for w in checked.W),'target history entry')


@dataclass(frozen=True)
class Publication:
    graph: str
    current: State
    reset: State
    parent: str | None = None
    event: tuple | None = None
    profile: str = PROFILE_ID

    def payload(self):
        return dict(graph=self.graph,current=self.current.payload(),reset=self.reset.payload(),
                    parent=self.parent,event=self.event,profile=self.profile)

    @property
    def identity(self):return digest(self.payload())


class ResearchOwner:
    """Small local transaction experiment, not a replacement native owner."""
    def __init__(self,publication):
        require(publication.profile==PROFILE_ID,'research profile binding')
        validate(publication.graph,publication.current);validate(publication.graph,publication.reset)
        self.publication=publication

    def split(self,h,after_readmission=None):
        before=self.publication
        require(before.parent is None and before.event is None,'unsupported descendant fission')
        selected=prescribe(before.graph,before.current)
        graph,cur=transfer(before.graph,before.current,selected['k'])
        _,rst=transfer(before.graph,before.reset,selected['k'])
        target_admit(graph,cur,h);target_admit(graph,rst,h)
        lineage=tuple((i,i if i<4 else i+1) for i in range(len(before.current.W)))
        event=(selected['k'],lineage,4,str(h))
        candidate=Publication(graph,cur,rst,before.identity,event)
        if after_readmission is not None:after_readmission(candidate)
        self.publication=candidate
        return selected

    def step(self,h):
        before=self.publication
        nxt,details=evaluate(before.graph,before.current,h)
        self.publication=replace(before,current=nxt)
        return details

    def reset(self):
        self.publication=replace(self.publication,current=self.publication.reset)


def replay_event(source,snapshot):
    """Re-execute physical selection/transfer/readmission, don't trust a digest."""
    require(type(snapshot) is dict and set(snapshot)=={'payload','digest'},'event snapshot schema')
    body=snapshot['payload'];require(digest(body)==snapshot['digest'],'snapshot digest')
    require(body['profile']==PROFILE_ID and body['parent']==source.identity,'profile or source lineage absent')
    require(body['event'] is not None and len(body['event'])==4,'event contract')
    h=F(body['event'][3]);owner=ResearchOwner(source);owner.split(h)
    require(p.canonical(owner.publication.payload())==p.canonical(body),'event replay differs')
    return owner.publication


def snapshot(publication):
    # JSON roundtrip detaches all containers for the local mutation checks.
    return json.loads(json.dumps(dict(payload=publication.payload(),digest=publication.identity)))


def replay_sequence(source,record):
    """Recompute a bounded split/ordinary/reset sequence from its pinned root."""
    require(type(record) is dict and set(record)=={'source','actions','final'},'sequence schema')
    require(record['source']==source.identity and type(record['actions']) is list,'sequence root')
    require(len(record['actions'])<=64,'bounded replay work')
    owner=ResearchOwner(source)
    for action in record['actions']:
        require(type(action) is dict and set(action)=={'kind','h','before','after'},'action schema')
        require(action['before']==owner.publication.identity,'missing action predecessor')
        if action['kind']=='split':owner.split(F(action['h']))
        elif action['kind']=='step':owner.step(F(action['h']))
        elif action['kind']=='reset':
            require(action['h'] is None,'reset has no duration');owner.reset()
        else:raise AdmissionError('unknown research action')
        require(action['after']==owner.publication.identity,'action replay diverged')
    require(p.canonical(snapshot(owner.publication))==p.canonical(record['final']),'final replay snapshot diverged')
    return owner.publication
