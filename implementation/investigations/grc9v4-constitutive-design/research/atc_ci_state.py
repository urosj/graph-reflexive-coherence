"""CI-only constructive predicates, separate from outward numerical boxes.

Exact rational inputs retain their preimage. Derived states carry only facts
proved by their operation (charge/pairing, history invariance, growth/return),
plus conservative interval facts. No epsilon and no alteration of frozen PC
or A_OS state machinery. This is a research proof interface, not a sandbox.
"""
from dataclasses import dataclass, asdict
from fractions import Fraction as F
import atc_ci_domains as domains

r=domains.anchor
a,I,GRID,require=r.a,r.I,r.GRID,r.require
_TOKEN=object()


@dataclass(frozen=True)
class StepProvenance:
    """Diagnostic execution bindings, never an externally redeemable authority."""
    before_witness_digest: str
    selected_joint_root_digest: str
    h: F
    profile_digest: str
    result_numerical_digest: str
    theorem_digest: str


@dataclass(frozen=True)
class Predicates:
    exact: tuple | None
    history_lower: F
    x: tuple | None
    y: tuple | None
    radius_squared_upper: F | None
    ordered_sectors: bool
    transfer_entry: bool
    basis: str
    charge: F=F(9)
    paired: bool=True
    step_provenance: StepProvenance | None=None


@dataclass(frozen=True, init=False)
class State:
    graph: str
    data: a.State
    predicates: Predicates

    def __init__(self,graph,data,predicates,*,token=None):
        require(token is _TOKEN and type(predicates) is Predicates, 'use exact_state or certified CI operations')
        require(graph in ('paired_source','paired_target'), 'CI witness graph')
        a.validate(graph,data)
        require(all(r.same(v[i],v[j]) for v in (data.C,data.W) for i,j in ((0,1),(2,3))),
                'proved pairing inconsistent with numerical enclosures')
        require(predicates.charge==9 and predicates.paired, 'CI exact charge/pairing premises')
        if predicates.exact is not None:
            require(all(box.contains(value) for boxes,values in zip((data.C,data.W),predicates.exact,strict=True)
                        for box,value in zip(boxes,values,strict=True)), 'exact preimage must lie in numerical enclosures')
        require(all(bounds is None or bounds[0]<=bounds[1] for bounds in (predicates.x,predicates.y)),
                'consistent proved scalar bounds')
        # Necessary compatibility checks, not a substitute for operation proof.
        require(sum(c.lo for c in data.C)<=9*GRID<=sum(c.hi for c in data.C),
                'charge witness contradicts numerical enclosure')
        require(F(1,2)<=predicates.history_lower<=1 and
                all(w.hi>=predicates.history_lower*GRID and w.lo<=GRID for w in data.W),
                'history witness contradicts numerical enclosure')
        if graph=='paired_source':
            x,y,_=_interval_facts(graph,data)
            require(predicates.x is not None and predicates.y is not None and
                    all(max(actual[0],proved[0])<=min(actual[1],proved[1])
                        for actual,proved in ((x,predicates.x),(y,predicates.y))),
                    'source coordinate witness contradicts numerical enclosure')
        else:
            radius2=r.p.norm2(tuple(c-F(3,2) for c in data.C))
            require(predicates.radius_squared_upper is not None and
                    F(radius2.lo,GRID)<=predicates.radius_squared_upper,
                    'target radius witness contradicts numerical enclosure')
        if predicates.step_provenance is not None:
            require(type(predicates.step_provenance) is StepProvenance and
                    predicates.step_provenance.result_numerical_digest==a.digest(data.payload()),
                    'step provenance contradicts numerical result')
        object.__setattr__(self,'graph',graph)
        object.__setattr__(self,'data',data)
        object.__setattr__(self,'predicates',predicates)

    @property
    def C(self): return self.data.C

    @property
    def W(self): return self.data.W

    def payload(self):
        return dict(numerical=self.data.payload(),witness=a.encode(asdict(self.predicates)))


def exact_state(graph,C,W):
    require(graph in ('paired_source','paired_target'), 'CI exact graph')
    require(all(type(x) in (int,F) for x in (*C,*W)), 'exact rational CI input')
    C,W=tuple(map(F,C)),tuple(map(F,W))
    require(len(C)==a.GRAPHS[graph][0] and len(W)==len(a.GRAPHS[graph][1]), 'CI exact coverage')
    require(sum(C)==9 and all(v[i]==v[j] for v in (C,W) for i,j in ((0,1),(2,3))),
            'exact charge and pairing before interval conversion')
    require(all(0<c<=9 for c in C) and all(F(1,2)<=w<=1 for w in W), 'exact state range')
    x=C[4]-(C[0]+C[2])/2 if graph=='paired_source' else None
    y=(C[0]-C[2])/2 if graph=='paired_source' else None
    rad=sum((c-F(3,2))**2 for c in C) if graph=='paired_target' else None
    facts=Predicates((C,W),min(W),(x,x) if x is not None else None,
        (y,y) if y is not None else None,rad,W[0]<W[2],False,'exact_rational_preimage')
    return State(graph,a.State(tuple(map(I,C)),tuple(map(I,W))),facts,token=_TOKEN)


def paired_state(x,y,u,v):
    require(all(type(value) in (int,F) for value in (x,y,u,v)), 'exact rational paired coordinates')
    x,y,u,v=map(F,(x,y,u,v))
    return exact_state('paired_source',((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,), (u,u,v,v))


def root_domain(state):
    require(type(state) is State, 'constructive CI predicate witness required')
    require(state.predicates.history_lower>=domains.M, 'exact/certified CI history lower boundary')
    if state.graph=='paired_source':
        require(state.predicates.x[0]>=F(29,10), 'exact/certified CI source contrast boundary')
    else:
        require(state.predicates.radius_squared_upper<=F(9,4), 'exact/certified CI target radius boundary')


def transfer_domain(state,current=False):
    root_domain(state)
    require(state.graph=='paired_source', 'source transfer graph')
    f=state.predicates
    require(3<=f.x[0]<=f.x[1]<=F(7,2) and -F(1,50)<=f.y[0]<=f.y[1]<=F(1,50),
            'exact/certified both-role event boundaries')
    if current:
        require(f.y[0]>=0 and f.ordered_sectors, 'exact/certified current event boundaries and sector order')
    # Returned enclosures are observations, not the source of predicate truth.
    return (I.bounds(I(f.x[0]).lo,I(f.x[1]).hi),I.bounds(I(f.y[0]).lo,I(f.y[1]).hi))


def _interval_facts(graph,data):
    if graph=='paired_source':
        x=data.C[4]-(data.C[0]+data.C[2])/2;y=(data.C[0]-data.C[2])/2
        return a.bound(x),a.bound(y),None
    return None,None,F(r.p.norm2(tuple(c-F(3,2) for c in data.C)).hi,GRID)


def certified_step(before,h,profile):
    """Execute, then certify: there is no caller-supplied output or proof input.

    The local root, continuity result and writer output cannot be substituted
    through this interface. Raw advance stays numerical-only. As elsewhere in
    this research code, malicious monkeypatching/private-token access is not a
    security boundary; public data and reconstructed receipts are untrusted.
    """
    # Runtime import avoids a module initialization cycle. Calling through the
    # reference keeps its ordinary final-root/rollback pressure effective.
    import atc_ci_reference as reference
    reference.request(h)
    root_domain(before)
    selected=reference.root(before,profile)
    data,details=reference.advance_raw(before.graph,before.data,h,selected,profile,domain_witness=before)
    bounds=domains.domain_bounds()
    x,y,rad=_interval_facts(before.graph,data)
    if before.graph=='paired_source':
        if before.predicates.x[0]>=3:
            x=(max(x[0],bounds['source_multiplier']*before.predicates.x[0]),min(x[1],F(9)))
    else:
        proved=(bounds['target_first_X_upper']**2 if before.predicates.transfer_entry else
                bounds['target_return_factor']**2*before.predicates.radius_squared_upper)
        rad=min(rad,proved)
    provenance=StepProvenance(a.digest(before.payload()),selected['selected_joint_root_digest'],h,
        profile.identity,a.digest(data.payload()),a.digest(a.encode(bounds)))
    facts=Predicates(None,max(domains.M,min(F(w.lo,GRID) for w in data.W)),x,y,rad,
        data.W[0].hi<data.W[2].lo,False,'CI2_certified_step:'+a.digest(a.encode(asdict(provenance))),
        step_provenance=provenance)
    following=State(before.graph,data,facts,token=_TOKEN)
    details['restart']=reference.root(following,profile)
    return following,details


def transfer(before,k):
    transfer_domain(before)
    require(type(k) is int and F(31,64)<=F(k,65536)<=F(33,64), 'exact dyadic transfer interval')
    share=F(k,65536);C,W=before.C,before.W
    data=a.State(C[:4]+(share*C[4],(1-share)*C[4]),W+(I(1),))
    if before.predicates.exact is not None:
        exactC,exactW=before.predicates.exact
        target=exact_state('paired_target',exactC[:4]+(share*exactC[4],(1-share)*exactC[4]),exactW+(F(1),))
        exact=target.predicates.exact;rad=target.predicates.radius_squared_upper
    else:
        exact=None;rad=_interval_facts('paired_target',data)[2]
    # The domain/share lemma proves funding and radius uniformly, including
    # exact endpoints; no target fitting or comparison epsilon is needed.
    rad=min(rad,domains.domain_bounds()['initial_target_X_squared_upper'])
    facts=Predicates(exact,before.predicates.history_lower,None,None,rad,
        before.predicates.ordered_sectors,True,'CI2_transfer:'+a.digest(before.payload())+':'+str(k))
    target=State('paired_target',data,facts,token=_TOKEN)
    root_domain(target)
    return target


def represented_pairing(state):
    """A rounded point has exact dyadic pair equality, never charge-nine credit."""
    require(type(state) is a.State, 'represented numerical state required')
    require(all(x.lo==x.hi for x in (*state.C,*state.W)), 'represented input must be point-valued, not overlapping boxes')
    require(all(v[i].lo==v[j].lo for v in (state.C,state.W) for i,j in ((0,1),(2,3))),
            'represented input must preserve exact paired C and W')
