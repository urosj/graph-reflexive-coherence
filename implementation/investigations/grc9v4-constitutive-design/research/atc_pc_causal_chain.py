"""PC-3 fixed full-feedback causal chain; investigation only, never native ATC.

Sole carrier policy and source profile fixed before target evaluation.
No CI solve, OS corrector, PSD fallback, target search or parameter sweep.
"""
from fractions import Fraction as F
from types import MappingProxyType
import atc_pc_relational_lift as lift
r=lift.r

PC3_CONTRACT=MappingProxyType(dict(
    schema='atc_pc3_fixed_causal_contract_v1',
    carrier_policy='pc_star_fission_relational_lift_lossless_v1',
    relational_continuity='c_target=c_source',PSD_fallback_allowed=False,
    failure_disposition='retain genuine failure; any PSD successor needs a preregistered new PC-2b investigation',
    source='unchanged PC1 paired-star ordinary onset and independent reset',
    profile='unchanged active nonlinear PC1 profile',h='1/8',tau_PC='1/(8 log 2)',
    event_read='fresh committed PC read using postbeat C/W/Z',
    event_duration=0,carrier_domain='seven-dimensional decorated signed target-star ball',
    event_image='five-dimensional subset, not an invariant ordinary-step requirement'))


def bounds():
    """Uniform fixed-H estimates plus PC-specific carrier induction.

    Shared read estimates were proved for every H in the radius, not just a
    CI root. No implicit solver/contraction is used to select a PC current.
    """
    inherited=r.dynamical_bounds();entry=r.uniform_certificate('target')
    bcoef=4+F(5,2)*r.K+F(375,32)*r.RHO
    scoef=(r.RREAD*bcoef/(1-r.RHO))**2
    r.require(entry['source_bound']==scoef*F(3,2)**2,'source bound scales with target resource radius')
    r.require(entry['source_bound']<r.Z_RADIUS,'entry-ball held source inside carrier ball')
    q=inherited['target_return_factor'];entryX=inherited['target_entry_upper']
    r.require(entryX<F(2,3) and q<F(9,10),'resource entry and contraction independent of Z sign')
    r.require(q*q>F(1,2),'geometric carrier-decay bound denominator positive')
    # Both role transfer domains use |y|<=1/50 and either sign of v-u.
    t,y,e=F(2,5),F(1,50),F(23,320);amin=F(7,4)
    leaf=F(11,32)*t+F(25,32)*y+e/32
    parent=(2-F(3,4)*(amin-F(1,25)))*t+F(1,4)*(2-amin)*y+F(7,8)*e
    bare_squared=4*leaf**2+2*parent**2
    initial_squared=12*t*t+4*y*y+2*e*e
    r.require(bare_squared<F(3,5)**2 and initial_squared<F(3,2)**2,'bare transfer-entry lemma rechecked exactly')
    return dict(source_growth=inherited['source_growth'],source_failure_by=67,
        geometry_radius=r.RHO,carrier_radius=r.Z_RADIUS,H_min=1-r.RHO,
        initial_target_X_squared_upper=initial_squared,bare_first_X_squared_upper=bare_squared,
        first_target_X_upper=entryX,return_X_radius=F(2,3),return_factor=q,
        target_resource_floor=F(5,6),target_read_writer_exponent_budget=entry['read_writer_exponent_budget'],
        current_denominator_lower=entry['current_margin'],baseline_per_X=bcoef,
        structural_source_per_X_squared=scoef,entry_source_norm_upper=entry['source_bound'],
        next_carrier_norm_upper=(r.Z_RADIUS+entry['source_bound'])/2,
        signed_carrier_invariant=True,PSD_assumed=False,
        limits=dict(C='(3/2) * 1',W='exp(-3 alpha/2) on every edge',Z='zero',H='identity'),
        recurrence='z_(n+1) <= z_n/2 + (scoef/2) X_n^2; X_(n+1) <= q X_n after entry')


def role_transfer_domain(state):
    x=r.source_check(state);y=(state.C[0]-state.C[2])/2
    r.require(x.hi<=r.GRID*F(7,2) and r.absolute(y)<=F(1,50),'both-role transfer domain')
    return x,y


def select_event(state,carrier):
    """Only current source enters; target and reset are not arguments."""
    x,y=role_transfer_domain(state)
    r.require(y.lo>=0 and state.W[0].hi<state.W[2].lo,'current event region and ordered exact sectors')
    read=r.pc_read(state,carrier)
    j=read['read']['current']
    k,share=r.a.rounded_share(j[0]+j[1],j[2]+j[3])
    r.require(F(31,64)<=F(k,65536)<=F(33,64),'source-selected dyadic share inside proved transfer interval')
    return dict(k=k,share=share,x=x,y=y,
        selector='fresh postbeat fixed-H PC inward sector currents',
        source_state_digest=r.a.digest(state.payload()),source_carrier_digest=r.a.digest(r.a.encode(carrier.values))),read


def target_step(state,carrier):
    """One actual PC target beat: old-Z read, continuity/W, held-S Z, reread."""
    r.require(state.graph==carrier.graph=='paired_target','fixed target PC step')
    selected=r.pc_read(state,carrier)
    nxt=r.advance('paired_target',state,selected)
    values=tuple(tuple((z+s)/2 for z,s in zip(row,other))
                 for row,other in zip(carrier.values,selected['source']))
    Zn=r.Carrier('paired_target',values,'PC3-held-source-half-writer:'+carrier.basis,token=r._DOMAIN_TOKEN)
    restart=r.pc_read(nxt,Zn)
    return nxt,Zn,selected,restart


def event(current,currentZ,reset,resetZ,*,policy_id=PC3_CONTRACT['carrier_policy']):
    r.require(policy_id==PC3_CONTRACT['carrier_policy']==lift.POLICY,'PC3 sole carrier policy; no fallback')
    choice,read=select_event(current,currentZ)
    roles={}
    for name,state,carrier in (('current',current,currentZ),('reset',reset,resetZ)):
        role_transfer_domain(state)
        r.pc_read(state,carrier)  # independent actual source role admission
        target=r.transfer(state,choice['k'])
        targetZ,receipt=lift.event_carrier(carrier)
        admitted=r.pc_read(target,targetZ)
        roles[name]=dict(state=target,carrier=targetZ,read=admitted,receipt=receipt)
    return choice,read,roles
