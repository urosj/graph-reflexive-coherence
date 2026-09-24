"""CIP-2 research reference: closed carrier predicates and atomic owner.

Exact C/W/Z witnesses are distinct from outward boxes and represented
diagnostics. Only executing operations mint derived authority. No native API.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
import atc_cip_chain as chain

domains, ci, predicates, lift = chain.domains, chain.ci, chain.predicates, chain.lift
r,a,p,I,GRID,require = chain.r,chain.a,chain.p,chain.I,chain.GRID,chain.require
Profile, bounds, decorated_tensor = chain.Profile,chain.bounds,chain.decorated_tensor
_TOKEN=object()
CONTRACT=dict(schema='atc_cip2_reference_v1',realization='CI+PC',
    exact_domain='C/W constructive predicates plus exact/proved Z Frobenius bound',
    represented_domain='point-valued paired target C/W/Z; no charge-nine predicate',
    raw_result_promotion=False,finite_schedule=('1/8','3/25','31/250','121/1000'),
    finite_error_bound='1/10000000000',intermediate_binary64_rounding=False,
    native_authority=False,whole_box_formation=False)


@dataclass(frozen=True,init=False)
class Carrier:
    graph: str
    values: tuple
    norm_squared_upper: F
    exact: tuple | None
    basis: str

    def __init__(self,graph,values,norm_squared_upper,basis,exact=None,*,token=None):
        require(token is _TOKEN,'use exact_carrier or executing carrier operation')
        require(type(norm_squared_upper) is F and 0<=norm_squared_upper<=domains.RZ**2,'proved CIP carrier bound')
        # Existing wider PC structural checks, not its radius as CIP authority.
        validated=r.Carrier(graph,values,basis,token=r._DOMAIN_TOKEN)
        require(F(p.norm2(tuple(x for row in values for x in row)).lo,GRID)<=norm_squared_upper,
                'carrier bound contradicts enclosure')
        if exact is not None:
            require(sum(x*x for row in exact for x in row)==norm_squared_upper,
                    'exact carrier norm witness')
            require(all(v.contains(x) for row,other in zip(values,exact,strict=True)
                        for v,x in zip(row,other,strict=True)),'exact carrier preimage contradicts enclosure')
        for name,value in dict(graph=graph,values=validated.values,norm_squared_upper=norm_squared_upper,
                               exact=exact,basis=basis).items():object.__setattr__(self,name,value)

    def payload(self):
        return a.encode(dict(graph=self.graph,values=self.values,norm_squared_upper=self.norm_squared_upper,
                             exact=self.exact,basis=self.basis))


def exact_carrier(graph,values):
    require(type(values) is tuple and all(type(row) is tuple for row in values),'immutable exact carrier')
    require(all(type(x) in (int,F) for row in values for x in row),'rational carrier preimage')
    exact=tuple(tuple(F(x) for x in row) for row in values)
    norm2=sum(x*x for row in exact for x in row)
    require(norm2<=domains.RZ**2,'exact CIP carrier radius')
    valid=r.exact_carrier(graph,exact) # exact symmetry/support before enclosure
    return Carrier(graph,valid.values,norm2,'exact:'+a.digest(a.encode(exact)),exact,token=_TOKEN)


@dataclass(frozen=True)
class Role:
    state: predicates.State
    carrier: Carrier

    def __post_init__(self):
        require(type(self.state) is predicates.State and type(self.carrier) is Carrier,'typed exact CIP role')
        predicates.root_domain(self.state)
        require(self.state.graph==self.carrier.graph,'C/W/Z graph identity')

    @property
    def graph(self):return self.state.graph

    def payload(self):return dict(graph=self.graph,state=self.state.payload(),carrier=self.carrier.payload())

    @property
    def identity(self):return a.digest(self.payload())


def exact_role(graph,C,W,Z):
    return Role(predicates.exact_state(graph,tuple(C),tuple(W)),exact_carrier(graph,tuple(tuple(row) for row in Z)))


def _root(graph,data,Z,profile,binding):
    require(type(profile) is Profile,'CIP profile')
    cert=domains.root_certificate('source' if graph=='paired_source' else 'target')
    m=len(data.W);identity=a.identity(m);center=identity
    spread=max(F(v.hi-v.lo,GRID) for v in (*data.C,*data.W,*(x for row in Z for x in row)))
    stop=max(F(1,10**35),1000*spread)
    def evaluate(H):
        read=ci.fixed_read(graph,data,H,profile)
        read['current']=r.paired_enclosures(read['current'])
        read['source']=decorated_tensor(read['source'])
        return read
    def generated(read):
        return tuple(tuple(I(int(i==j))+profile.values['kh']*(z+s) for j,(z,s) in enumerate(zip(row,other,strict=True)))
                     for i,(row,other) in enumerate(zip(Z,read['source'],strict=True)))
    for iteration in range(32):
        read=evaluate(center);trial=generated(read)
        displacement=r.norm_upper(x-y for row,other in zip(center,identity,strict=True) for x,y in zip(row,other,strict=True))
        residual=r.norm_upper(x-y for row,other in zip(trial,center,strict=True) for x,y in zip(row,other,strict=True))
        error=residual/(1-cert['contraction_bound'])
        require(displacement<domains.ci.RHO,'root center in certified H ball')
        if error<stop:
            require(displacement+m*error<domains.ci.RHO,'root enclosure in H ball')
            H=tuple(tuple(x+I.bounds(I(-error).lo,I(error).hi) for x in row) for row in center)
            read=evaluate(H);fresh=generated(read)
            fj=tuple(j-b-rb for j,b,rb in zip(read['current'],read['baseline'],read['readback'],strict=True))
            fh=tuple(tuple(x-y for x,y in zip(row,other,strict=True)) for row,other in zip(H,fresh,strict=True))
            require(all(x.contains(F(0)) for x in (*fj,*(x for row in fh for x in row))),'full joint residual')
            value=dict(H=H,generated_H=fresh,read=read,joint_current_residual=fj,joint_geometry_residual=fh,
                graph=graph,role_binding=binding,profile_binding=profile.identity,
                Z_binding=a.digest(a.encode(Z)),certificate=cert,certificate_digest=a.digest(a.encode(cert)),
                residual_at_center=residual,root_error=error,iterations=iteration+1)
            value['selected_joint_root_digest']=a.digest(a.encode(value))
            return value
        center=tuple(tuple(I(F(x.lo+x.hi,2*GRID)) for x in row) for row in trial)
    raise a.AdmissionError('coupled reference root unresolved')


def root(role,profile):
    require(type(role) is Role,'exact role witness required')
    return _root(role.graph,role.state.data,role.carrier.values,profile,role.identity)


def _advance(graph,data,Z,h,profile,selected,represented=False):
    ci.request(h)
    J=selected['read']['current'];n,edges,_=a.GRAPHS[graph]
    C=r.paired_enclosures(tuple(c-h*j for c,j in zip(data.C,p.mv(p.incidence(n,edges),J),strict=True)))
    require(all(0<c.lo<=c.hi<=9*GRID for c in C),'resource admission before writers')
    desc=a.descriptor(graph,C);drive=ci.conductance(graph,C,desc,J,profile)
    decay=((-I(h)/I(F(float.fromhex(a.TAU64)))).exp_nonpositive() if represented else
           I(F(1,2)) if h==F(1,8) else a.mathref.decay(I(h)))
    W=r.paired_enclosures(tuple((decay*a.mathref.log_nonpositive(w)+(1-decay)*a.mathref.log_nonpositive(g)).exp_nonpositive()
                               for w,g in zip(data.W,drive,strict=True)))
    newZ=decorated_tensor(tuple(tuple(decay*z+(1-decay)*s for z,s in zip(row,other,strict=True))
                                for row,other in zip(Z,selected['read']['source'],strict=True)))
    return a.State(C,W),newZ,dict(selected=selected,writer_descriptor=desc,writer_drive=drive,decay=decay)


def step(before,h,profile):
    ci.request(h);selected=root(before,profile)
    data,Z,details=_advance(before.graph,before.state.data,before.carrier.values,h,profile,selected)
    theorem=bounds();state=before.state
    x,y,rad=predicates._interval_facts(before.graph,data)
    if before.graph=='paired_source' and state.predicates.x[0]>=3:
        x=(max(x[0],theorem['source_multiplier']*state.predicates.x[0]),min(x[1],F(9)))
    elif before.graph=='paired_target':
        rad=min(rad,theorem['target_first_X_upper']**2 if state.predicates.transfer_entry else
                theorem['target_return_factor']**2*state.predicates.radius_squared_upper)
    proof=predicates.StepProvenance(before.identity,selected['selected_joint_root_digest'],h,
        profile.identity,a.digest(data.payload()),a.digest(a.encode(theorem)))
    facts=predicates.Predicates(None,max(domains.ci.M,min(F(w.lo,GRID) for w in data.W)),x,y,rad,
        data.W[0].hi<data.W[2].lo,False,'CIP2_executed_step:'+before.identity,step_provenance=proof)
    following=predicates.State(before.graph,data,facts,token=predicates._TOKEN)
    # Convex invariant is an operation theorem. Interval norm upper bounds
    # may straddle its exact closed boundary; do not widen that boundary.
    norm2=min(domains.RZ**2,F(p.norm2(tuple(v for row in Z for v in row)).hi,GRID))
    carrier=Carrier(before.graph,Z,norm2,'CIP2_held_source:'+selected['selected_joint_root_digest'],token=_TOKEN)
    result=Role(following,carrier)
    details['restart']=root(result,profile)
    return result,details


def select(role,profile):
    predicates.transfer_domain(role.state,current=True)
    selected=root(role,profile);J=selected['read']['current']
    k,share=a.rounded_share(J[0]+J[1],J[2]+J[3])
    require(F(31,64)<=F(k,65536)<=F(33,64),'source-only transfer share')
    return dict(k=k,share=share,root=selected)


def transfer(role,k,profile):
    predicates.transfer_domain(role.state);root(role,profile)
    state=predicates.transfer(role.state,k)
    values,c=lift.lift(role.carrier.values,token=r._DOMAIN_TOKEN,**lift.CANONICAL)
    lift.sign_fidelity(role.carrier.values,values,token=r._DOMAIN_TOKEN,**lift.CANONICAL)
    recovered=lift.inverse(values,token=r._DOMAIN_TOKEN,**lift.CANONICAL)
    require(all(r.same(x,y) for row,other in zip(role.carrier.values,recovered,strict=True)
                for x,y in zip(row,other,strict=True)),'carrier exact-image roundtrip')
    carrier=Carrier('paired_target',values,role.carrier.norm_squared_upper,
                    'CIP2_lossless:'+role.identity,token=_TOKEN)
    result=Role(state,carrier)
    return result,root(result,profile),dict(policy=lift.POLICY,c=c,source=role.identity,target=result.identity,
                                          loss='zero_on_declared_decorated_domain')


@dataclass(frozen=True)
class Publication:
    current: Role
    reset: Role
    profile: Profile
    parent: str | None=None
    event: tuple | None=None

    def __post_init__(self):
        require(type(self.current) is Role and type(self.reset) is Role and type(self.profile) is Profile,'typed publication')
        require(self.current.graph==self.reset.graph,'both-role graph')

    def payload(self):
        return a.encode(dict(current=self.current.payload(),reset=self.reset.payload(),profile=self.profile.identity,
                             parent=self.parent,event=self.event))

    @property
    def identity(self):return a.digest(self.payload())


class ResearchOwner:
    def __init__(self,publication):
        require(type(publication) is Publication,'typed source publication')
        root(publication.current,publication.profile);root(publication.reset,publication.profile)
        self.publication=publication

    def ordinary(self,h,after_readmission=None):
        ci.request(h);before=self.publication;root(before.reset,before.profile)
        following,details=step(before.current,h,before.profile)
        candidate=replace(before,current=following)
        if after_readmission is not None:after_readmission(candidate)
        self.publication=candidate
        return details

    def split(self,after_readmission=None):
        before=self.publication
        require(before.current.graph=='paired_source' and before.parent is None and before.event is None,'single bounded fission')
        chosen=select(before.current,before.profile)
        current,cr,receipt=transfer(before.current,chosen['k'],before.profile)
        reset,rr,reset_receipt=transfer(before.reset,chosen['k'],before.profile)
        event=(chosen['k'],tuple((i,i) for i in range(4)),4,lift.POLICY,
               chosen['root']['selected_joint_root_digest'],a.digest(a.encode((receipt,reset_receipt))))
        candidate=Publication(current,reset,before.profile,before.identity,event)
        if after_readmission is not None:after_readmission(candidate)
        self.publication=candidate
        return dict(choice=chosen,current_root=cr,reset_root=rr)

    def reset(self):
        before=self.publication;root(before.reset,before.profile)
        self.publication=replace(before,current=before.reset)


def snapshot(publication):return dict(payload=publication.payload(),digest=publication.identity)


def replay(source,record):
    require(type(record) is dict and set(record)=={'source','actions','final'},'replay schema')
    require(record['source']==source.identity and type(record['actions']) is list and 0<len(record['actions'])<=16,'replay lineage')
    owner=ResearchOwner(source)
    for action in record['actions']:
        require(type(action) is dict and set(action)=={'kind','h','before','after'},'action schema')
        require(action['before']==owner.publication.identity,'action predecessor')
        if action['kind']=='ordinary':owner.ordinary(F(action['h']))
        elif action['kind']=='split':
            require(action['h'] is None,'zero-time event');owner.split()
        elif action['kind']=='reset':
            require(action['h'] is None,'reset is not beat');owner.reset()
        else:raise a.AdmissionError('unknown replay action')
        require(action['after']==owner.publication.identity,'action result')
    require(record['final']==snapshot(owner.publication),'full replay snapshot')
    return owner.publication


def represented_admission(data,Z):
    predicates.represented_pairing(data)
    require(all(x.lo==x.hi for row in Z for x in row),'point-valued represented carrier')
    exact=tuple(tuple(F(x.lo,GRID) for x in row) for row in Z)
    exact_carrier('paired_target',exact) # exact dyadic radius/support/symmetry
    require(all(w.lo>=domains.ci.M*GRID for w in data.W),'represented history floor')
    require(r.norm_upper(c-F(3,2) for c in data.C)<=F(3,2),'represented target radius')
    a.validate('paired_target',data)


def represented_root(data,Z,profile):
    represented_admission(data,Z)
    result=_root('paired_target',data,Z,profile,None)
    return result


def represented_step(data,Z,h,profile):
    ci.request(h);selected=represented_root(data,Z,profile)
    new,newZ,details=_advance('paired_target',data,Z,h,profile,selected,represented=True)
    rounded=new.represented()
    roundedZ=tuple(tuple(a.project(x) for x in row) for row in newZ)
    details['restart']=represented_root(rounded,roundedZ,profile)
    return rounded,roundedZ,details
