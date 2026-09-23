"""PC-4 paired-domain research reference. No native code or registration.

Full graph, explicit positive parameter box, variable requests at fixed tau.
Exact-domain owners and publication-rounded diagnostic states stay distinct.
The PC-2 signed lossless law is the sole event carrier policy.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from types import MappingProxyType
import atc_pc_causal_chain as pc3

r=pc3.r
a,p,I,GRID=r.a,r.p,r.I,r.GRID
require=r.require
HMIN,HMAX=F(3,25),F(1,8)
PARAMETER_BOX=MappingProxyType(dict(
    alpha=(F(1,4096),F(1,2048)),beta=(F(1,4096),F(1,2048)),
    gamma=(F(1,2048),F(1,1024)),chi=(F(1,32),F(1,16)),
    kh=(F(1,2),F(1)),kah=(F(1,2),F(1)),
    a=(F(19,4)-F(1,4096),F(19,4)+F(1,4096)),
    nu=(F(1,131072),F(1,65536))))
CONTRACT=MappingProxyType(dict(schema='atc_pc4_paired_reference_v1',
    carrier_policy=pc3.lift.POLICY,relational_continuity='c_target=c_source',
    h_domain=('3/25','1/8'),tau_A='1/(8 log 2)',tau_PC='1/(8 log 2)',
    parameter_variation='choose fixed profile in box; requests alone may vary between beats',
    potential_theorem='common C1 p on [0,9], |p_prime-19/4|<=1/2048',
    executable_potential='quadratic subclass p(c)=a*c+nu*c*c/2',
    graph_scope='decorated paired 2+2 source and double-star target only',
    environment_scope='no active external-edge carrier transport contract claimed',
    represented_recipe='binary64 input and C/W/Z publication; enclosed internal stages, represented h and tau',
    represented_charge='measured drift, never admitted as exact charge-nine state',
    finite_schedule=('1/8','3/25','31/250','121/1000'),finite_steps_per_role=4,
    finite_error_bound='1/10000000000',native_authority=False))


@dataclass(frozen=True)
class Profile:
    parameters: tuple=tuple(sorted(a.PARAMS.items()))

    def __post_init__(self):
        require(type(self.parameters) is tuple and all(type(t) is tuple and len(t)==2 for t in self.parameters),'immutable parameter roster')
        require(tuple(k for k,_ in self.parameters)==tuple(sorted(PARAMETER_BOX)),'exact parameter keys/order')
        for k,v in self.parameters:
            require(type(v) is F and PARAMETER_BOX[k][0]<=v<=PARAMETER_BOX[k][1],'parameter outside declared box: '+k)

    @property
    def values(self):return dict(self.parameters)

    @property
    def identity(self):return a.digest(a.encode(dict(contract=dict(CONTRACT),parameters=self.parameters)))


def domain_bounds():
    """Rational sufficient conditions for entire box; no sampled fitting."""
    M,K=r.M,r.K
    rho=r.Z_RADIUS # max kappa_H=1, not PC3's 3/4
    rr=F(1,783)    # chi_max/(49-chi_max)
    margin=1-F(1,16)/49
    source_b=F(11,2)+90*rho
    source_j=source_b/margin
    source_budget=F(1,2048)*(F(9,2)+F(27,10)**2/2)+source_j**2/2048
    source_S=(2*rr*source_b/(1-rho))**2
    source_error=90*rho+rr*source_b
    growth=F(5,2)*HMIN*(F(19,250)-6*K-F(2,3)*source_error)
    multiplier=F(81,80);horizon=89
    require(growth>multiplier-1 and 3*multiplier**horizon>9,'uniform PC source obstruction')
    B=4+F(5,2)*K+F(125,8)*rho
    s=(rr*B/(1-rho))**2
    target_j=B*F(3,2)/margin
    target_budget=F(1,2048)*(3+2*F(3,2)**2)+target_j**2/2048
    require(max(source_budget,target_budget)<1-M,'whole-box read and post-C W-writer budgets')
    require(max(source_S,s*F(3,2)**2)<r.Z_RADIUS,'both graph PC carrier balls invariant')
    lo,hi=M*F(7,16),F(73,16)
    require(1-HMAX*F(19,4)**2/4>0,'positive spectral multiplier')
    q0=max(1+HMIN*x*(x-F(19,4)) for x in (lo,hi))
    error=HMAX*F(5,2)*(F(5,2)*K+F(125,8)*rho+rr*B)
    q=q0+error
    t,y,eps,amin=F(2,5),F(1,50),F(23,320),F(7,4)
    leaf=(1-3*HMIN*amin)*t+(1-HMIN*amin)*y+HMAX*eps/4
    parent=(2-6*HMIN*(amin-F(1,25)))*t+HMAX*y/2+(1-HMIN)*eps
    require(4*leaf**2+2*parent**2<F(5,8)**2,'variable-request bare transfer entry')
    entry=F(5,8)+F(3,2)*error
    require(entry<F(2,3) and q<F(91,100),'whole-box PC target entry and contraction')
    rho_bar=F(25,37)
    require(q*q>rho_bar,'decay convolution denominator positive')
    require(F(1,4096)+9*F(1,65536)<K,'entire executable quadratic box within C1 envelope')
    return dict(parameters=dict(PARAMETER_BOX),requests=(HMIN,HMAX),fixed_tau='1/(8 log 2)',
        geometry_radius=rho,H_min=1-rho,carrier_radius=r.Z_RADIUS,
        source_baseline_bound=source_b,current_margin=margin,
        source_writer_budget=source_budget,target_writer_budget=target_budget,
        source_held_S_bound=source_S,target_entry_held_S_bound=s*F(3,2)**2,
        source_growth_excess_lower=growth,source_multiplier=multiplier,source_failure_by=horizon,
        target_first_X_upper=entry,target_return_factor=q,target_resource_floor=F(5,6),
        target_S_per_X_squared=s,writer_decay_upper=rho_bar,
        asymptotic='C -> (3/2)1, J -> 0, Z -> 0, H -> I, W -> exp(-3 alpha/2)',
        whole_box_theorem=True,parameter_sweep=False,arbitrary_environment=False)


def request(h):
    require(type(h) is F and HMIN<=h<=HMAX,'request outside PC4 interval')


def conductance(graph,C,D,J,profile):
    par=profile.values;edges=a.GRAPHS[graph][1]
    exponents=tuple(par['alpha']*(C[u]+C[v])/2+par['beta']*(D[u]-D[v]).square()/2+par['gamma']*j.square()/2
                    for (u,v),j in zip(edges,J,strict=True))
    require(all(v.lo>=0 for v in exponents),'nonnegative conductance exponent')
    drive=tuple((-v).exp_nonpositive() for v in exponents)
    require(all(v.lo>=r.M*GRID for v in drive),'conductance invariant interval')
    return drive


def decorated_tensor(matrix):
    """Intersect enclosures only using proved transposition/pair symmetries."""
    n=len(matrix);perms=[]
    for u in (False,True):
        for v in (False,True):
            perm=list(range(n))
            if u:perm[0],perm[1]=1,0
            if v:perm[2],perm[3]=3,2
            perms.append(perm)
    rows=[]
    for i in range(n):
        row=[]
        for j in range(n):
            orbit=[matrix[g[x]][g[y]] for g in perms for x,y in ((i,j),(j,i))]
            low,high=max(x.lo for x in orbit),min(x.hi for x in orbit)
            require(low<=high,'decorated equivariance enclosure inconsistent')
            row.append(I.bounds(low,high))
        rows.append(tuple(row))
    return tuple(rows)


def fixed_read(graph,state,Z,profile):
    """Full fixed-H equations, also used by unadmitted rounding diagnostics."""
    require(type(profile) is Profile and type(Z) is r.Carrier and Z.graph==graph,'profile/carrier binding')
    a.validate(graph,state)
    require(all(w.lo>=r.M*GRID for w in state.W),'history domain')
    par=profile.values;n,edges,_=a.GRAPHS[graph];B=p.incidence(n,edges);BT=tuple(zip(*B))
    C,W=state.C,state.W;d=p.mv(BT,C)
    H=tuple(tuple(I(int(i==j))+par['kh']*v for j,v in enumerate(row)) for i,row in enumerate(Z.values))
    lap=p.mv(B,tuple(w*x for w,x in zip(W,d,strict=True)))
    delta=tuple(tuple(v-int(i==j) for j,v in enumerate(row)) for i,row in enumerate(H))
    geom=p.mv(B,p.mv(delta,d))
    potential=tuple(par['a']*c+par['nu']*c.square()/2 for c in C)
    phi=tuple(l-v+par['kah']*g for l,v,g in zip(lap,potential,geom,strict=True))
    baseline=tuple(-w*x for w,x in zip(W,p.mv(BT,phi),strict=True))
    D=a.descriptor(graph,C);drive=conductance(graph,C,D,baseline,profile)
    q=tuple((w-t)/(w+t) for w,t in zip(W,drive,strict=True))
    denom=tuple(1-par['chi']*x for x in q)
    require(all(x.lo>0 for x in denom),'fixed-H current denominator')
    J=r.paired_enclosures(tuple(b/d for b,d in zip(baseline,denom,strict=True)))
    readback=tuple(par['chi']*x*j for x,j in zip(q,J,strict=True))
    flat=r.paired_enclosures(p.solve(H,readback))
    S=decorated_tensor(p.star(flat,B))
    require(r.norm_upper(v for row in S for v in row)<r.Z_RADIUS,'held structural source in carrier ball')
    return dict(H=H,potential=potential,phi=phi,baseline=baseline,descriptor=D,
        drive=drive,current=J,readback=readback,flat=flat,source=S)


@dataclass(frozen=True)
class Role:
    state: r.DomainState
    carrier: r.Carrier

    def __post_init__(self):
        require(type(self.state) is r.DomainState and type(self.carrier) is r.Carrier,'exact-domain role types')
        require(self.state.graph==self.carrier.graph,'role graph binding')

    def payload(self):
        return a.encode(dict(graph=self.state.graph,state=self.state.payload(),Z=self.carrier.values))


def read(role,profile):
    require(type(role) is Role,'exact role required')
    if role.state.graph=='paired_source':r.source_check(role.state,F(29,10))
    else:r.target_check(role.state)
    return fixed_read(role.state.graph,role.state.data,role.carrier,profile)


def raw_step(graph,state,Z,h,profile,*,represented_tau=False):
    request(h)
    selected=fixed_read(graph,state,Z,profile);n,edges,_=a.GRAPHS[graph]
    C=r.paired_enclosures(tuple(c-h*j for c,j in zip(state.C,p.mv(p.incidence(n,edges),selected['current']),strict=True)))
    require(all(0<c.lo<=c.hi<=9*GRID for c in C),'resource rejection before writers')
    D=a.descriptor(graph,C);drive=conductance(graph,C,D,selected['current'],profile)
    decay=(-I(h)/I(F(float.fromhex(a.TAU64)))).exp_nonpositive() if represented_tau else a.mathref.decay(I(h))
    W=r.paired_enclosures(tuple((decay*a.mathref.log_nonpositive(w)+(1-decay)*a.mathref.log_nonpositive(g)).exp_nonpositive()
                               for w,g in zip(state.W,drive,strict=True)))
    values=decorated_tensor(tuple(tuple(decay*z+(1-decay)*s for z,s in zip(row,other,strict=True))
                                 for row,other in zip(Z.values,selected['source'],strict=True)))
    carrier=r.Carrier(graph,values,'PC4-held-source-writer',token=r._DOMAIN_TOKEN)
    nxt=a.State(C,W);a.validate(graph,nxt)
    restart=fixed_read(graph,nxt,carrier,profile)
    return nxt,carrier,dict(selected=selected,writer_descriptor=D,writer_drive=drive,decay=decay,restart=restart)


def step(role,h,profile):
    read(role,profile)
    state,Z,details=raw_step(role.state.graph,role.state.data,role.carrier,h,profile)
    exact=r.DomainState(role.state.graph,state,'PC4-incidence-equivariance-step',token=r._DOMAIN_TOKEN)
    out=Role(exact,Z);read(out,profile)
    return out,details


def select(role,profile):
    x,y=pc3.role_transfer_domain(role.state)
    require(y.lo>=0 and role.state.W[0].hi<role.state.W[2].lo,'current exact ordered sectors')
    rd=read(role,profile);j=rd['current']
    k,share=a.rounded_share(j[0]+j[1],j[2]+j[3])
    require(F(31,64)<=F(k,65536)<=F(33,64),'source-selected share outside sufficient transfer interval')
    return dict(k=k,share=share,read_digest=a.digest(a.encode(rd)),x=x,y=y)


def transfer(role,k,profile):
    pc3.role_transfer_domain(role.state);read(role,profile)
    state=r.transfer(role.state,k);Z,receipt=pc3.lift.event_carrier(role.carrier)
    out=Role(state,Z);rd=read(out,profile)
    return out,receipt,rd


@dataclass(frozen=True)
class Publication:
    current: Role
    reset: Role
    profile: Profile=Profile()
    parent: str | None=None
    event: tuple | None=None

    def __post_init__(self):
        require(type(self.current) is Role and type(self.reset) is Role and type(self.profile) is Profile,'publication types')
        require(self.current.state.graph==self.reset.state.graph,'both-role graph identity')

    def payload(self):
        return a.encode(dict(profile=self.profile.identity,current=self.current.payload(),reset=self.reset.payload(),
                             parent=self.parent,event=self.event))

    @property
    def identity(self):return a.digest(self.payload())


class ResearchOwner:
    """Bounded exact-real research transaction; not a production API."""
    def __init__(self,publication):
        require(type(publication) is Publication,'typed research publication')
        read(publication.current,publication.profile);read(publication.reset,publication.profile)
        self.publication=publication

    def ordinary(self,h,after_readmission=None):
        before=self.publication
        read(before.reset,before.profile)
        nxt,details=step(before.current,h,before.profile)
        candidate=replace(before,current=nxt)
        if after_readmission is not None:after_readmission(candidate)
        self.publication=candidate
        return details

    def split(self,after_readmission=None):
        before=self.publication
        require(before.current.state.graph=='paired_source' and before.event is None,'bounded single fission only')
        chosen=select(before.current,before.profile)
        cur,c_receipt,c_read=transfer(before.current,chosen['k'],before.profile)
        rst,r_receipt,r_read=transfer(before.reset,chosen['k'],before.profile)
        event=(chosen['k'],pc3.lift.POLICY,tuple((i,i) for i in range(4)),4,0)
        candidate=Publication(cur,rst,before.profile,before.identity,event)
        if after_readmission is not None:after_readmission(candidate)
        self.publication=candidate
        return dict(choice=chosen,current_carrier=c_receipt,reset_carrier=r_receipt,
                    current_read=c_read,reset_read=r_read)

    def reset(self):
        before=self.publication;read(before.reset,before.profile)
        self.publication=replace(before,current=before.reset)


def snapshot(publication):
    return dict(payload=publication.payload(),digest=publication.identity)


def replay(source,record):
    """Recompute physics for the bounded sequence; hashes alone never suffice."""
    require(type(record) is dict and set(record)=={'source','actions','final'},'sequence schema')
    require(record['source']==source.identity,'source lineage binding')
    require(type(record['actions']) is list and 0<len(record['actions'])<=16,'bounded action roster')
    owner=ResearchOwner(source)
    for action in record['actions']:
        require(type(action) is dict and set(action)=={'kind','h','before','after'},'action schema')
        require(action['before']==owner.publication.identity,'action predecessor')
        kind=action['kind']
        if kind=='ordinary':owner.ordinary(F(action['h']))
        elif kind=='split':
            require(action['h'] is None,'zero-time event has no request');owner.split()
        elif kind=='reset':
            require(action['h'] is None,'reset has no request');owner.reset()
        else:raise a.AdmissionError('unknown action')
        require(action['after']==owner.publication.identity,'action successor')
    require(a.encode(snapshot(owner.publication))==record['final'],'final replay contents differ')
    return owner.publication


def represented(role):
    """No exact-charge witness is manufactured from rounded resources."""
    state=role.state.data.represented()
    Z=r.exact_carrier(role.state.graph,tuple(tuple(F(float(a.bound(a.project(x))[0])) for x in row) for row in role.carrier.values))
    return state,Z


def represented_step(graph,state,Z,h,profile):
    state,Z,details=raw_step(graph,state,Z,h,profile,represented_tau=True)
    rounded=state.represented()
    carrier=r.exact_carrier(graph,tuple(tuple(a.bound(a.project(x))[0] for x in row) for row in Z.values))
    fixed_read(graph,rounded,carrier,profile)
    return rounded,carrier,details
