"""CIP-1 coupled paired research chain; no production/ATC registration.

Reuse fixed-H algebra and constructive C/W predicates, never standalone
CI/PC evolution. Public step/event calls execute their own roots and writes;
no supplied numerical output or serialized receipt can certify a successor.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import atc_cip_domains as domains
import atc_ci_reference as ci
import atc_ci_state as predicates
import atc_pc_relational_lift as lift
from atc_pc_reference import decorated_tensor

r, a, p, I, GRID = ci.r, ci.a, ci.p, ci.I, ci.GRID
require = r.require


def bounds():
    """CIP roots satisfy the hypotheses of geometry-uniform CI lemmas."""
    root = domains.domain_certificate()
    shared = domains.ci.domain_bounds()
    q, s, b = (shared[k] for k in
        ('target_return_factor','target_geometry_per_X_squared','writer_decay_upper'))
    require(s*F(9,4) == root['target']['instantaneous_source_bound'], 'same full-H source bound')
    require(q*q > b and q < 1, 'variable-request carrier convolution')
    return dict(coupled_roots=root, geometry_uniform_lemmas=shared,
        source_multiplier=shared['source_multiplier'], source_failure_by=71,
        target_first_X_upper=shared['target_first_X_upper'], target_return_factor=q,
        funding_lower=shared['funding_lower'], source_per_X_squared=s, decay_upper=b,
        recurrence='X_next<=q X; z_next<=a_k z+(1-a_k)s X^2, with 0<a_k<=b',
        carrier_convolution='z_n<=b^n z_0+s X_0^2*(q^(2n)-b^n)/(q^2-b)',
        limits=dict(C='(3/2)*1',J='zero',Z='zero',H='identity',W='exp(-3 alpha/2)'),
        entire_box_event_formation=False, native_authority=False)


@dataclass(frozen=True)
class Profile:
    parameters: tuple

    def __post_init__(self):
        ci.Profile(self.parameters)  # parameter validation only, not CI dynamics
        require(self.values['kh'] <= domains.KHMAX, 'CIP joint gain domain')

    @property
    def values(self): return dict(self.parameters)

    @property
    def identity(self):
        return a.digest(a.encode(dict(realization='CI+PC',parameters=self.parameters,
            rho_inst=1,zeta_A=1,tau_A='1/(8 log 2)',tau_PC='1/(8 log 2)',
            RZ=domains.RZ,RHO=domains.ci.RHO)))


@dataclass(frozen=True)
class Role:
    state: predicates.State
    carrier: r.Carrier

    def __post_init__(self):
        require(type(self.state) is predicates.State and type(self.carrier) is r.Carrier,
                'constructive C/W and Z inputs required, not numerical boxes/receipts')
        predicates.root_domain(self.state)
        require(self.carrier.graph == self.state.graph, 'role graph identity')
        require(r.norm_upper(x for row in self.carrier.values for x in row) <= domains.RZ,
                'narrower CIP carrier ball')

    @property
    def graph(self): return self.state.graph

    def payload(self):
        return dict(graph=self.graph,state=self.state.payload(),Z=a.encode(self.carrier.values),
                    carrier_basis=self.carrier.basis)

    @property
    def identity(self): return a.digest(self.payload())


def exact_role(C,W,z):
    state = predicates.exact_state('paired_source',tuple(C),tuple(W))
    return Role(state,r.diagonal_z(z))


def root(role,profile):
    require(type(role) is Role and type(profile) is Profile, 'typed CIP role/profile')
    state, graph, Z = role.state, role.graph, role.carrier.values
    cert = domains.root_certificate('source' if graph=='paired_source' else 'target')
    m = len(state.W); identity = a.identity(m); center = identity
    spread = max(F(v.hi-v.lo,GRID) for v in (*state.C,*state.W,*(x for row in Z for x in row)))
    stop = max(F(1,10**35),1000*spread)
    def evaluate(H):
        value = ci.fixed_read(graph,state.data,H,profile)
        # These intersections implement exact proved decoration, not inference
        # from overlapping numerical intervals.
        value['current'] = r.paired_enclosures(value['current'])
        value['source'] = decorated_tensor(value['source'])
        return value
    def generated(rd):
        return tuple(tuple(I(int(i==j))+profile.values['kh']*(z+s)
            for j,(z,s) in enumerate(zip(zrow,srow,strict=True)))
            for i,(zrow,srow) in enumerate(zip(Z,rd['source'],strict=True)))
    for iteration in range(32):
        rd = evaluate(center); trial = generated(rd)
        displacement = r.norm_upper(x-y for row,other in zip(center,identity,strict=True)
                                    for x,y in zip(row,other,strict=True))
        residual = r.norm_upper(x-y for row,other in zip(trial,center,strict=True)
                                for x,y in zip(row,other,strict=True))
        error = residual/(1-cert['contraction_bound'])
        require(displacement < domains.ci.RHO, 'coupled iterate in proved H ball')
        if error < stop:
            require(displacement+m*error < domains.ci.RHO, 'coupled enclosure in H ball')
            H = tuple(tuple(x+I.bounds(I(-error).lo,I(error).hi) for x in row) for row in center)
            rd = evaluate(H); fresh = generated(rd)
            fj = tuple(j-b-rb for j,b,rb in zip(rd['current'],rd['baseline'],rd['readback'],strict=True))
            fh = tuple(tuple(x-y for x,y in zip(row,other,strict=True)) for row,other in zip(H,fresh,strict=True))
            require(all(x.contains(F(0)) for x in (*fj,*(x for row in fh for x in row))), 'full joint residual')
            result = dict(graph=graph,H=H,generated_H=fresh,read=rd,
                joint_current_residual=fj,joint_geometry_residual=fh,
                residual_at_center=residual,root_error=error,iterations=iteration+1,
                certificate=cert,certificate_digest=a.digest(a.encode(cert)),
                role_binding=role.identity,profile_binding=profile.identity,
                old_Z_binding=a.digest(a.encode(Z)))
            result['selected_joint_root_digest'] = a.digest(a.encode(result))
            return result
        center = tuple(tuple(I(F(x.lo+x.hi,2*GRID)) for x in row) for row in trial)
    raise a.AdmissionError('coupled root enclosure unresolved; do not retune witness')


def step(before,h,profile):
    """Execute root/C/W/Z/restart before returning any certified successor."""
    ci.request(h)
    selected = root(before,profile)
    state,graph = before.state,before.graph
    n,edges,_ = a.GRAPHS[graph]; J = selected['read']['current']
    C = r.paired_enclosures(tuple(c-h*j for c,j in zip(state.C,p.mv(p.incidence(n,edges),J),strict=True)))
    require(all(0<c.lo<=c.hi<=9*GRID for c in C), 'resource positivity before either writer')
    descriptor = a.descriptor(graph,C)
    drive = ci.conductance(graph,C,descriptor,J,profile)
    decay = I(F(1,2)) if h==F(1,8) else a.mathref.decay(I(h))
    W = r.paired_enclosures(tuple((decay*a.mathref.log_nonpositive(w)+(1-decay)*a.mathref.log_nonpositive(g)).exp_nonpositive()
        for w,g in zip(state.W,drive,strict=True)))
    data = a.State(C,W)
    theorem = bounds()
    x,y,rad = predicates._interval_facts(graph,data)
    if graph=='paired_source' and state.predicates.x[0]>=3:
        x = (max(x[0],theorem['source_multiplier']*state.predicates.x[0]),min(x[1],F(9)))
    elif graph=='paired_target':
        proved = (theorem['target_first_X_upper']**2 if state.predicates.transfer_entry else
                  theorem['target_return_factor']**2*state.predicates.radius_squared_upper)
        rad = min(rad,proved)
    provenance = predicates.StepProvenance(before.identity,selected['selected_joint_root_digest'],h,
        profile.identity,a.digest(data.payload()),a.digest(a.encode(theorem)))
    facts = predicates.Predicates(None,max(domains.ci.M,min(F(w.lo,GRID) for w in W)),x,y,rad,
        W[0].hi<W[2].lo,False,'CIP1_executed_step:'+before.identity,step_provenance=provenance)
    following_state = predicates.State(graph,data,facts,token=predicates._TOKEN)
    Z = decorated_tensor(tuple(tuple(decay*z+(1-decay)*s for z,s in zip(row,other,strict=True))
        for row,other in zip(before.carrier.values,selected['read']['source'],strict=True)))
    carrier = r.Carrier(graph,Z,'CIP1_same_root_held_source:'+selected['selected_joint_root_digest'],token=r._DOMAIN_TOKEN)
    following = Role(following_state,carrier)
    restart = root(following,profile)
    return following,dict(selected=selected,restart=restart,decay=decay,
        writer_descriptor=descriptor,writer_drive=drive,old_role=before.identity,new_role=following.identity,
        continuity_evaluations=1,W_writes=1,Z_writes=1)


def select(role,profile):
    x,y = predicates.transfer_domain(role.state,current=True)
    selected = root(role,profile)
    J = selected['read']['current']
    k,share = a.rounded_share(J[0]+J[1],J[2]+J[3])
    require(F(31,64)<=F(k,65536)<=F(33,64), 'combined source-only share interval')
    return dict(k=k,share=share,x=x,y=y,selected=selected,reset_or_target_input=False)


def event(current,reset,profile,*,policy_id=lift.POLICY):
    require(policy_id==lift.POLICY, 'sole selected lossless carrier law; no fallback')
    chosen = select(current,profile)
    roles = {}
    for name,role in (('current',current),('reset',reset)):
        predicates.transfer_domain(role.state)
        source_read = root(role,profile)
        state = predicates.transfer(role.state,chosen['k']) # geometry-independent C/W map only
        carrier,receipt = lift.event_carrier(role.carrier)
        target = Role(state,carrier)
        admitted = root(target,profile)
        roles[name] = dict(role=target,source_read=source_read,read=admitted,receipt=receipt)
    return chosen,roles


def control(role,*,reset_W=False,reset_Z=False):
    """One-time lawful intervention, not a profile change or repeated clamp."""
    state = role.state
    if reset_W:
        f = state.predicates
        data = a.State(state.C,(I(1),)*len(state.W))
        exact = (f.exact[0],(F(1),)*len(state.W)) if f.exact is not None else None
        facts = predicates.Predicates(exact,F(1),f.x,f.y,f.radius_squared_upper,False,
            f.transfer_entry,'CIP1_one_time_W_reset:'+role.identity)
        state = predicates.State(role.graph,data,facts,token=predicates._TOKEN)
    carrier = r.exact_carrier(role.graph,tuple((0,)*len(state.W) for _ in state.W)) if reset_Z else role.carrier
    return Role(state,carrier)
