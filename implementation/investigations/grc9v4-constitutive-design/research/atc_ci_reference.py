"""CI-3 full-graph bounded research reference; no native model or registration.

The mathematical root is joint J,H. Every scientific read carries the full
root, residual, domain/certificate and state/profile identity. Rounded target
diagnostics never acquire the exact-charge/pairing domain witness.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from types import MappingProxyType
import atc_ci_domains as domains
import atc_ci_state as predicates

exact_state, paired_state = predicates.exact_state, predicates.paired_state

r = domains.anchor
a, p, I, GRID = r.a, r.p, r.I, r.GRID
require = r.require
CONTRACT = MappingProxyType(dict(schema='atc_ci3_paired_reference_v1',
    domain_contract=dict(domains.CONTRACT), numerical_root='a-priori Banach residual enclosure of full joint J,H',
    root_stop_budget='max(1e-35,1000*input_enclosure_width); above squared-norm grid resolution',
    state='C,W only; no persistent carrier', event_time=0,
    finite_schedule=('1/8','3/25','31/250','121/1000'), finite_steps_per_role=4,
    finite_error_bound='1/10000000000',
    represented_recipe='binary64 input and C/W publication; enclosed internal stages and joint root; represented h/tau',
    represented_charge='measure drift; never manufacture exact Q=9 witness',
    domain_admission='exact rational predicates or certified operation facts; numerical boxes are enclosures, not exact predicates',
    successor_provenance='certified_step executes its own root/continuity/writer; no raw-data or receipt promotion API',
    represented_pairing='point-valued dyadic C/W with exact pair equality before symmetry intersection',
    native_authority=False))


@dataclass(frozen=True)
class Profile:
    parameters: tuple = tuple(sorted(a.PARAMS.items()))

    def __post_init__(self):
        require(type(self.parameters) is tuple and all(type(row) is tuple and len(row)==2 for row in self.parameters),
                'immutable parameter roster')
        require(tuple(k for k,_ in self.parameters)==tuple(sorted(domains.PARAMETER_BOX)), 'exact parameter keys/order')
        for k,v in self.parameters:
            require(type(v) is F and domains.PARAMETER_BOX[k][0]<=v<=domains.PARAMETER_BOX[k][1],
                    'parameter outside declared box: '+k)

    @property
    def values(self): return dict(self.parameters)

    @property
    def identity(self): return a.digest(a.encode(dict(contract=dict(CONTRACT), parameters=self.parameters)))


def request(h):
    require(type(h) is F and domains.HMIN<=h<=domains.HMAX, 'request outside CI domain')


def conductance(graph,C,D,J,profile):
    v=profile.values;edges=a.GRAPHS[graph][1]
    exponents=tuple(v['alpha']*(C[u]+C[w])/2+v['beta']*(D[u]-D[w]).square()/2+v['gamma']*j.square()/2
                    for (u,w),j in zip(edges,J,strict=True))
    require(all(e.lo>=0 for e in exponents), 'nonnegative conductance exponent')
    values=tuple((-e).exp_nonpositive() for e in exponents)
    require(all(g.lo>=domains.M*GRID for g in values), 'conductance invariant interval')
    return values


def fixed_read(graph,state,H,profile):
    """Full incidence equations, not a paired-coordinate surrogate or OS pass."""
    a.validate(graph,state)
    n,edges,_=a.GRAPHS[graph];B=p.incidence(n,edges);BT=tuple(zip(*B))
    C,W=state.C,state.W;v=profile.values;diff=p.mv(BT,C)
    lap=p.mv(B,tuple(w*x for w,x in zip(W,diff,strict=True)))
    delta=tuple(tuple(x-int(i==j) for j,x in enumerate(row)) for i,row in enumerate(H))
    geo=p.mv(B,p.mv(delta,diff))
    potential=tuple(v['a']*c+v['nu']*c.square()/2 for c in C)
    phi=tuple(l-f+v['kah']*g for l,f,g in zip(lap,potential,geo,strict=True))
    baseline=tuple(-w*x for w,x in zip(W,p.mv(BT,phi),strict=True))
    D=a.descriptor(graph,C);drive=conductance(graph,C,D,baseline,profile)
    q=tuple((w-g)/(w+g) for w,g in zip(W,drive,strict=True))
    denominator=tuple(1-v['chi']*x for x in q)
    require(all(x.lo>0 for x in denominator), 'CI fixed-current block')
    J=tuple(b/d for b,d in zip(baseline,denominator,strict=True))
    readback=tuple(v['chi']*x*j for x,j in zip(q,J,strict=True))
    flat=p.solve(H,readback);source=p.star(flat,B)
    return dict(potential=potential,phi=phi,baseline=baseline,descriptor=D,drive=drive,
                q=q,denominator=denominator,current=J,readback=readback,flat=flat,source=source)


def generated_H(read,profile):
    return tuple(tuple(I(int(i==j))+profile.values['kh']*x for j,x in enumerate(row))
                 for i,row in enumerate(read['source']))


def raw_root(graph,state,profile,*,domain_witness=None):
    """Enclose the root for the certified input with residual/(1-L).

    Target root bounds do not require exact charge. This permits a separately
    labelled represented diagnostic; it does not extend the Q=9 return theorem.
    Source callers must use root() with its constructive exact-domain witness.
    """
    require(type(profile) is Profile and graph in ('paired_source','paired_target'), 'CI root profile/graph')
    a.validate(graph,state)
    if domain_witness is not None:
        require(type(domain_witness) is predicates.State and domain_witness.data is state
                and domain_witness.graph==graph, 'root domain witness binding')
        predicates.root_domain(domain_witness)
    else:
        require(graph=='paired_target', 'source root requires constructive exact-charge witness')
        require(all(w.lo>=domains.M*GRID for w in state.W), 'represented root history interval')
        require(r.norm_upper(c-F(3,2) for c in state.C)<=F(3,2), 'target root ball')
    kind='source' if graph=='paired_source' else 'target'
    cert=domains.root_certificate(kind)
    m=len(state.W);center=a.identity(m);identity=a.identity(m)
    spread=max(F(x.hi-x.lo,GRID) for x in (*state.C,*state.W))
    # A stopping budget, not a proof estimated from observed convergence.
    # The returned radius is always independently bounded by the residual.
    # Squaring on the inherited 2**256 grid imposes a norm floor near 2**-128.
    # A 1e-40 budget would be unresolvable despite a converged, certified root.
    stop=max(F(1,10**35),1000*spread)
    for iteration in range(32):
        rd=fixed_read(graph,state,center,profile);generated=generated_H(rd,profile)
        displacement=r.norm_upper(x-y for row,other in zip(center,identity,strict=True) for x,y in zip(row,other,strict=True))
        residual=r.norm_upper(x-y for row,other in zip(generated,center,strict=True) for x,y in zip(row,other,strict=True))
        error=residual/(1-cert['contraction_bound'])
        require(displacement<domains.RHO, 'root center stays in certified geometry ball')
        if error<stop:
            require(displacement+m*error<domains.RHO, 'root enclosure stays in geometry neighborhood')
            enclosure=tuple(tuple(x+I.bounds(I(-error).lo,I(error).hi) for x in row) for row in center)
            final=fixed_read(graph,state,enclosure,profile);fresh=generated_H(final,profile)
            joint_current=tuple(j-b-z for j,b,z in zip(final['current'],final['baseline'],final['readback'],strict=True))
            joint_geometry=tuple(tuple(x-y for x,y in zip(row,other,strict=True))
                                 for row,other in zip(enclosure,fresh,strict=True))
            require(all(x.contains(F(0)) for x in (*joint_current,*(x for row in joint_geometry for x in row))),
                    'literal joint residual must enclose zero')
            value=dict(H=enclosure,generated_H=fresh,read=final,joint_current_residual=joint_current,
                joint_geometry_residual=joint_geometry,root_error=error,residual_at_center=residual,
                certificate=cert,certificate_digest=a.digest(a.encode(cert)),
                graph=graph,state_binding=a.digest(state.payload()),profile_binding=profile.identity,
                domain_witness_binding=a.digest(domain_witness.payload()) if domain_witness is not None else None,
                iterations=iteration+1,stop_budget=stop)
            value['selected_joint_root_digest']=a.digest(a.encode(value))
            return value
        center=tuple(tuple(I(F(x.lo+x.hi,2*GRID)) for x in row) for row in generated)
    raise a.AdmissionError('bounded joint CI root enclosure unresolved')


def root(state,profile):
    predicates.root_domain(state)
    return raw_root(state.graph,state.data,profile,domain_witness=state)


def advance_raw(graph,state,h,selected,profile,*,represented_tau=False,domain_witness=None):
    request(h)
    if represented_tau:
        require(graph=='paired_target' and domain_witness is None, 'represented target diagnostic only')
        predicates.represented_pairing(state)
    else:
        require(type(domain_witness) is predicates.State and domain_witness.data is state
                and domain_witness.graph==graph, 'paired advance needs its constructive domain witness')
        predicates.root_domain(domain_witness)
    require(selected['domain_witness_binding']==(a.digest(domain_witness.payload()) if domain_witness is not None else None),
            'selected joint root domain witness binding')
    require(selected['graph']==graph and selected['state_binding']==a.digest(state.payload())
            and selected['profile_binding']==profile.identity, 'selected joint root state/profile binding')
    n,edges,_=a.GRAPHS[graph];J=selected['read']['current']
    C=r.paired_enclosures(tuple(c-h*j for c,j in zip(state.C,p.mv(p.incidence(n,edges),J),strict=True)))
    require(all(0<c.lo<=c.hi<=9*GRID for c in C), 'resource rejection before writer')
    D=a.descriptor(graph,C);drive=conductance(graph,C,D,J,profile)
    decay=(-I(h)/I(F(float.fromhex(a.TAU64)))).exp_nonpositive() if represented_tau else a.mathref.decay(I(h))
    W=r.paired_enclosures(tuple((decay*a.mathref.log_nonpositive(w)+(1-decay)*a.mathref.log_nonpositive(g)).exp_nonpositive()
                               for w,g in zip(state.W,drive,strict=True)))
    return a.State(C,W),dict(selected=selected,writer_descriptor=D,writer_drive=drive,decay=decay)


def step(state,h,profile):
    return predicates.certified_step(state,h,profile)


def role_transfer_domain(state):
    return predicates.transfer_domain(state)


def select(state,profile):
    x,y=predicates.transfer_domain(state,current=True)
    selected=root(state,profile);j=selected['read']['current']
    k,share=a.rounded_share(j[0]+j[1],j[2]+j[3])
    require(F(31,64)<=F(k,65536)<=F(33,64), 'source-only share outside transfer domain')
    return dict(k=k,share=share,root=selected,x=x,y=y)


def transfer(state,k,profile):
    role_transfer_domain(state);root(state,profile)
    target=predicates.transfer(state,k)
    return target,root(target,profile)


@dataclass(frozen=True)
class Publication:
    current: predicates.State
    reset: predicates.State
    profile: Profile=Profile()
    parent: str | None=None
    event: tuple | None=None

    def __post_init__(self):
        require(type(self.current) is predicates.State and type(self.reset) is predicates.State and type(self.profile) is Profile,
                'typed exact publication')
        require(self.current.graph==self.reset.graph, 'both-role graph identity')

    def payload(self):
        return a.encode(dict(graph=self.current.graph,profile=self.profile.identity,
            current=self.current.payload(),reset=self.reset.payload(),parent=self.parent,event=self.event))

    @property
    def identity(self): return a.digest(self.payload())


class ResearchOwner:
    """One ordinary commit, then one independent zero-time research event."""
    def __init__(self,publication):
        require(type(publication) is Publication, 'typed research publication')
        root(publication.current,publication.profile);root(publication.reset,publication.profile)
        self.publication=publication

    def ordinary(self,h,after_readmission=None):
        request(h);before=self.publication;root(before.reset,before.profile)
        following,details=step(before.current,h,before.profile)
        candidate=replace(before,current=following)
        if after_readmission is not None: after_readmission(candidate)
        self.publication=candidate
        return details

    def split(self,after_readmission=None):
        before=self.publication
        require(before.current.graph=='paired_source' and before.parent is None and before.event is None,
                'bounded single event; no descendant split')
        chosen=select(before.current,before.profile)
        current,croot=transfer(before.current,chosen['k'],before.profile)
        reset,rroot=transfer(before.reset,chosen['k'],before.profile)
        event=(chosen['k'],tuple((i,i) for i in range(4)),4,0,chosen['root']['selected_joint_root_digest'])
        candidate=Publication(current,reset,before.profile,before.identity,event)
        if after_readmission is not None: after_readmission(candidate)
        self.publication=candidate
        return dict(choice=chosen,current_root=croot,reset_root=rroot)

    def reset(self):
        before=self.publication;root(before.reset,before.profile)
        self.publication=replace(before,current=before.reset)


def snapshot(publication): return dict(payload=publication.payload(),digest=publication.identity)


def replay(source,record):
    require(type(record) is dict and set(record)=={'source','actions','final'}, 'sequence schema')
    require(record['source']==source.identity and type(record['actions']) is list
            and 0<len(record['actions'])<=16, 'source lineage and bounded action roster')
    owner=ResearchOwner(source)
    for action in record['actions']:
        require(type(action) is dict and set(action)=={'kind','h','before','after'}, 'action schema')
        require(action['before']==owner.publication.identity, 'action predecessor')
        if action['kind']=='ordinary': owner.ordinary(F(action['h']))
        elif action['kind']=='split':
            require(action['h'] is None, 'zero-time event has no request');owner.split()
        elif action['kind']=='reset':
            require(action['h'] is None, 'reset has no request');owner.reset()
        else: raise a.AdmissionError('unknown action')
        require(action['after']==owner.publication.identity, 'action successor differs')
    require(a.encode(snapshot(owner.publication))==record['final'], 'final replay contents differ')
    return owner.publication


def represented_step(state,h,profile):
    """Target-only diagnostic, no DomainState or exact-charge claim."""
    predicates.represented_pairing(state)
    selected=raw_root('paired_target',state,profile)
    data,details=advance_raw('paired_target',state,h,selected,profile,represented_tau=True)
    rounded=data.represented()
    predicates.represented_pairing(rounded)
    details['restart']=raw_root('paired_target',rounded,profile)
    return rounded,details
