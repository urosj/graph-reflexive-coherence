"""Bounded full-feedback CI/PC research laws; no production registration.

Uses the accepted fixed-geometry A evaluator and outward interval primitives,
not its OS pass, event current, target admission or lifecycle owner.
"""
from fractions import Fraction as F
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import atc_sector_reference as a

p, I, GRID = a.p, a.I, a.GRID
require = a.require
RHO = F(1,4096)
Z_RADIUS = F(1,3072)
H = F(1,8)
M = F(24,25)
K = F(1,2048)
RREAD = F(3,3133)  # chi/(49-chi), not an OS approximation

# Constructive domain witnesses, not equality inferred from interval overlap.
# Public inputs are exact rationals. Only the proved equivariant operations
# below may retain the charge/pairing witness through non-point enclosures.
_DOMAIN_TOKEN = object()


@dataclass(frozen=True, init=False)
class DomainState:
    graph: str
    data: a.State
    basis: str

    def __init__(self, graph, data, basis, *, token=None):
        require(token is _DOMAIN_TOKEN, 'use exact_state or a certified state operation')
        a.validate(graph, data)
        require(graph in ('paired_source','paired_target'), 'paired domain graph')
        require(all(same(v[i],v[j]) for v in (data.C,data.W) for i,j in ((0,1),(2,3))),
                'domain witness requires paired enclosures')
        q=sum(data.C,I(0))
        require(q.lo<=9*GRID<=q.hi, 'charge witness inconsistent with enclosure')
        object.__setattr__(self,'graph',graph)
        object.__setattr__(self,'data',data)
        object.__setattr__(self,'basis',basis)

    @property
    def C(self): return self.data.C

    @property
    def W(self): return self.data.W

    def payload(self): return self.data.payload()


def same(x,y):
    return (x.lo,x.hi)==(y.lo,y.hi)


def exact_state(graph,C,W):
    require(all(type(x) in (int,F) for x in (*C,*W)), 'exact rational state input')
    C,W=tuple(map(F,C)),tuple(map(F,W))
    require(graph in ('paired_source','paired_target'), 'paired exact graph')
    require(len(C)==a.GRAPHS[graph][0] and len(W)==len(a.GRAPHS[graph][1]), 'exact coverage')
    require(sum(C)==9, 'exact Q=9 required')
    require(all(v[i]==v[j] for v in (C,W) for i,j in ((0,1),(2,3))), 'exact pairing required')
    return DomainState(graph,a.State(tuple(map(I,C)),tuple(map(I,W))),
                       a.digest(a.encode(dict(exact_C=C,exact_W=W))),token=_DOMAIN_TOKEN)


def domain_state(graph,state):
    require(type(state) is DomainState and state.graph==graph, 'constructive charge/pairing witness required')
    a.validate(graph,state.data)


def reset_history(state):
    domain_state(state.graph,state)
    return DomainState(state.graph,a.State(state.C,(I(1),)*len(state.W)),
                       'W-reset:'+state.basis,token=_DOMAIN_TOKEN)


@dataclass(frozen=True, init=False)
class Carrier:
    graph: str
    values: tuple
    basis: str

    def __init__(self,graph,values,basis,*,token=None):
        require(token is _DOMAIN_TOKEN, 'use exact_carrier or a certified carrier operation')
        require(graph in ('paired_source','paired_target'), 'carrier graph')
        edges=a.GRAPHS[graph][1];n=len(edges)
        require(len(values)==n and all(len(row)==n for row in values), 'carrier dimensions')
        require(all(same(values[i][j],values[j][i]) for i in range(n) for j in range(n)),
                'symmetric carrier required')
        require(all(values[i][j].lo==values[i][j].hi==0 for i in range(n) for j in range(n)
                    if not set(edges[i]) & set(edges[j])), 'carrier star support')
        for i,j in ((0,1),(2,3)):
            perm=list(range(n));perm[i],perm[j]=perm[j],perm[i]
            require(all(same(values[k][l],values[perm[k]][perm[l]]) for k in range(n) for l in range(n)),
                    'decorated carrier sector symmetry')
        require(norm_upper(x for row in values for x in row)<=Z_RADIUS, 'PC carrier ball')
        object.__setattr__(self,'graph',graph)
        object.__setattr__(self,'values',tuple(tuple(a.RetainedInterval(x) for x in row) for row in values))
        object.__setattr__(self,'basis',basis)


def exact_carrier(graph,values):
    require(all(type(x) in (int,F) for row in values for x in row), 'exact rational carrier input')
    require(graph in ('paired_source','paired_target'), 'carrier graph')
    edges=a.GRAPHS[graph][1];n=len(edges)
    require(len(values)==n and all(len(row)==n for row in values), 'carrier dimensions')
    require(all(values[i][j]==values[j][i] for i in range(n) for j in range(n)), 'exact carrier symmetry')
    require(all(values[i][j]==0 for i in range(n) for j in range(n)
                if not set(edges[i]) & set(edges[j])), 'exact carrier star support')
    for i,j in ((0,1),(2,3)):
        perm=list(range(n));perm[i],perm[j]=perm[j],perm[i]
        require(all(values[k][l]==values[perm[k]][perm[l]] for k in range(n) for l in range(n)),
                'exact decorated carrier symmetry')
    return Carrier(graph,tuple(tuple(I(x) for x in row) for row in values),
                   a.digest(a.encode(values)),token=_DOMAIN_TOKEN)


def absolute(x):
    return F(max(abs(x.lo), abs(x.hi)), GRID)


def norm_upper(values):
    return F(p.norm2(tuple(values)).sqrt().hi, GRID)


def point(q):
    return I(F(q))


def uniform_certificate(kind):
    """Rational Banach/envelope bounds at the fixed, fully active profile.

    Source: paired nonnegative Q=9, x>=29/10, m<=W<=1.
    Target: Q=9, ||C-3/2||<=3/2, m<=W<=1. Read the companion
    proof for derivation; these constants are not estimated from iterations.
    """
    chi, gamma, kh = (a.PARAMS[k] for k in ('chi','gamma','kh'))
    if kind == 'source':
        # The source quotient bound decreases with x; the small enlargement
        # below x=3 is for one successful beat reaching the event region.
        require(F(29,40)+F(387,100)*F(61,50)+9*K < F(11,2), 'bare source bound')
        b0, lb, count = F(11,2), F(135,2), F(2)
        budget_const = a.PARAMS['alpha']*F(9,2)+a.PARAMS['beta']*F(27,10)**2/2
    else:
        require(kind == 'target', 'known domain')
        b0, lb, count = (4+F(5,2)*K)*F(3,2), F(375,32)*F(3,2), F(1)
        budget_const = a.PARAMS['alpha']*3+2*a.PARAMS['beta']*F(3,2)**2
    b = b0+lb*RHO
    margin = 1-chi/49
    j = b/margin
    budget = budget_const+gamma*j*j/2
    require(budget < 1-M, 'read and post-resource writer targets stay above m')
    flat = count*RREAD*b/(1-RHO)
    flux_lip = (RREAD+chi*gamma*b*b/(2*margin**2))*lb
    flat_lip = flux_lip/(1-RHO)+count*RREAD*b/(1-RHO)**2
    source_bound = flat**2
    displacement = kh*source_bound
    contraction = 2*kh*flat*flat_lip
    require(displacement < RHO and contraction < F(1,100), 'strict self-map and contraction')
    require(kind != 'source' or source_bound < Z_RADIUS, 'PC source-ball invariance')
    return dict(kind=kind, radius=RHO, current_margin=margin, b0_bound=b0,
        b_bound=b, baseline_geometry_lipschitz=lb, read_writer_exponent_budget=budget,
        flat_bound=flat, flat_lipschitz=flat_lip, source_bound=source_bound,
        displacement_bound=displacement, contraction_bound=contraction)


def dynamical_bounds():
    source, target = uniform_certificate('source'), uniform_certificate('target')
    err=F(135,2)*RHO+RREAD*(F(11,2)+F(135,2)*RHO)
    growth=F(5,16)*(F(19,250)-6*K-F(2,3)*err)
    require(growth>F(1,60) and 3*F(61,60)**67>9, 'finite unsplit positivity obstruction')
    lo, hi=M*F(7,16),F(73,16)
    require(1-H*F(19,4)**2/4>0, 'positive bare spectral multiplier')
    q0=max(1+H*lo*(lo-F(19,4)),1+H*hi*(hi-F(19,4)))
    correction=H*F(5,2)*(F(5,2)*K+F(375,32)*RHO+
                               RREAD*(4+F(5,2)*K+F(375,32)*RHO))
    entry=F(3,5)+F(3,2)*correction
    require(entry<F(2,3) and q0+correction<F(9,10), 'CI target entry and indefinite return')
    return dict(source=source,target=target,source_error=err,source_growth=growth,
        source_multiplier=F(61,60),source_failure_by=67,
        target_entry_upper=entry,target_return_factor=q0+correction,
        target_radius=F(2,3),target_resource_floor=F(5,6))


def paired_state(x,y,u,v):
    return exact_state('paired_source',((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,),
                       (u,u,v,v))


def source_check(state, minimum_x=F(3)):
    domain_state('paired_source',state)
    x=state.C[4]-(state.C[0]+state.C[2])/2
    require(x.lo>=GRID*minimum_x,'source contrast domain')
    require(all(w.lo>=GRID*M for w in state.W),'source history interval')
    return x


def target_check(state):
    domain_state('paired_target',state)
    require(norm_upper(c-F(3,2) for c in state.C)<=F(3,2),'target ball')
    require(all(w.lo>=GRID*M for w in state.W),'target history interval')


def geometry(source):
    return tuple(tuple(I(int(i==j))+a.PARAMS['kh']*x for j,x in enumerate(row))
                 for i,row in enumerate(source))


def ci_read(graph,state):
    """Banach-certified joint-root enclosure, not convergence-as-proof."""
    kind='source' if graph=='paired_source' else 'target'
    if kind=='source': source_check(state,F(29,10))
    else: target_check(state)
    cert=uniform_certificate(kind);n,edges,_=a.GRAPHS[graph];B=p.incidence(n,edges)
    center=a.identity(len(edges));identity=a.identity(len(edges))
    for iteration in range(24):
        rd=a.read(graph,state.data,center);generated=geometry(p.star(rd['flat'],B))
        displacement=norm_upper(x-y for row,other in zip(center,identity) for x,y in zip(row,other))
        require(displacement<RHO,'root iterate stays in certified domain')
        residual=norm_upper(x-y for row,other in zip(generated,center) for x,y in zip(row,other))
        error=residual/(1-cert['contraction_bound'])
        if error<F(1,10**35):
            enclosure=tuple(tuple(x+I.bounds(I(-error).lo,I(error).hi) for x in row) for row in center)
            result=a.read(graph,state.data,enclosure)
            return dict(H=enclosure,read=result,source=p.star(result['flat'],B),
                root_error=error,iterations=iteration+1,certificate=cert,
                residual_at_center=residual,state_binding=a.digest(state.payload()),graph=graph,
                domain_basis=state.basis)
        center=tuple(tuple(I(F(x.lo+x.hi,2*GRID)) for x in row) for row in generated)
    raise a.AdmissionError('bounded CI root enclosure unresolved')


def pc_read(state,Z):
    require(type(Z) is Carrier and type(state) is DomainState and Z.graph==state.graph,
            'typed carrier and matching domain state required')
    graph=state.graph
    if graph=='paired_source': source_check(state,F(29,10))
    else: target_check(state)
    Hodge=geometry(Z.values);rd=a.read(graph,state.data,Hodge)
    source=p.star(rd['flat'],p.incidence(a.GRAPHS[graph][0],a.GRAPHS[graph][1]))
    require(norm_upper(x for row in source for x in row)<Z_RADIUS,'held source in declared ball')
    return dict(H=Hodge,read=rd,source=source,
                certificate=uniform_certificate('source' if graph=='paired_source' else 'target'),
                state_binding=a.digest(state.payload()),graph=graph,domain_basis=state.basis)


def paired_enclosures(values):
    # Apply a proved symmetry, not a fitted equality tolerance.
    out=list(values)
    for i,j in ((0,1),(2,3)):
        lo=max(values[i].lo,values[j].lo);hi=min(values[i].hi,values[j].hi)
        require(lo<=hi,'equivariance enclosure intersection')
        out[i]=out[j]=I.bounds(lo,hi)
    return tuple(out)


def advance(graph,state,selected):
    """One continuity then post-C descriptor/selected-J log writer."""
    domain_state(graph,state)
    require(selected['graph']==graph and selected['state_binding']==a.digest(state.payload()),
            'selected read must belong to this state and graph')
    B=p.incidence(a.GRAPHS[graph][0],a.GRAPHS[graph][1]);J=selected['read']['current']
    C=paired_enclosures(tuple(c-H*j for c,j in zip(state.C,p.mv(B,J))))
    require(all(c.lo>0 for c in C),'resource positivity rejected before writers')
    drive=a.conductance(graph,C,a.descriptor(graph,C),J)
    # h=tau_A*log(2): log interpolation has exact half coefficient.
    W=paired_enclosures(tuple((w*t).sqrt() for w,t in zip(state.W,drive)))
    out=DomainState(graph,a.State(C,W),'equivariant-step:'+a.digest(a.encode(selected)),token=_DOMAIN_TOKEN)
    require(all(w.lo>=GRID*M for w in W),'post-resource writer invariant')
    return out


def pc_step(state,Z):
    selected=pc_read(state,Z);nxt=advance('paired_source',state,selected)
    # Preregistered tau_PC=1/(8 log 2), h=1/8; held source, not new-state S.
    Zn=Carrier(Z.graph,tuple(tuple((z+s)/2 for z,s in zip(row,other))
                            for row,other in zip(Z.values,selected['source'])),
               'equivariant-held-source-writer:'+Z.basis,token=_DOMAIN_TOKEN)
    restart=pc_read(nxt,Zn)
    return nxt,Zn,selected,restart


def event_select(state,root):
    require(root['graph']=='paired_source' and root['state_binding']==a.digest(state.payload()),
            'event operand must be the fresh joint read of this source')
    x=source_check(state);y=(state.C[0]-state.C[2])/2
    require(x.hi<=GRID*F(7,2) and 0<=y.lo<=y.hi<=GRID*F(1,50),'event region')
    require(state.W[0].hi<state.W[2].lo,'two distinct decorated sectors')
    # CI-native selected root: neither a reference read nor the old root.
    j=root['read']['current'];bu,bv=root['read']['baseline'][0],root['read']['baseline'][2]
    require(bu.lo>0 and bv.lo>0,'positive current baseline activity')
    legacy_balance = absolute(bu-bv)*64<F((bu+bv).lo,GRID)
    k,share=a.rounded_share(j[0]+j[1],j[2]+j[3])
    require(F(31,64)<=F(k,65536)<=F(33,64),'source-only allocation range')
    return dict(k=k,share=share,x=x,y=y,root_current=j,root_H=root['H'],
        auxiliary_OS_style_baseline_balance_passed=legacy_balance,
        selector='positive joint-root inflows; unique dyadic share in declared sufficient transfer interval')


def transfer(state,k):
    domain_state('paired_source',state)
    require(type(k) is int and F(31,64)<=F(k,65536)<=F(33,64),'declared transfer interval')
    share=F(k,65536);C,W=state.C,state.W
    left,right=share*C[4],(1-share)*C[4]
    require((left-C[0]).lo>0 and (right-C[2]).lo>0,'both-role funding')
    out=DomainState('paired_target',a.State(C[:4]+(left,right),W+(I(1),)),
                    'charge-preserving-split:'+state.basis+':'+str(k),token=_DOMAIN_TOKEN)
    target_check(out)
    return out


def fixtures():
    # Declared once before any outcome: a genuine x<3 → x>=3 ordinary onset.
    return (paired_state(F(59,20),F(1,100),F(97,100),F(99,100)),
            paired_state(F(33,10),-F(3,200),F(49,50),F(97,100)))


def diagonal_z(value):
    return exact_carrier('paired_source',tuple(tuple(value if i==j else 0 for j in range(4)) for i in range(4)))
