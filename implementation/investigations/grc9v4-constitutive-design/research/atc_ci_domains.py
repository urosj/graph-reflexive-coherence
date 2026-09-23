"""CI-2 rational paired-domain bounds, not sampled CI solver estimates."""
from fractions import Fraction as F
from types import MappingProxyType
import atc_ci_pc_anchor as anchor

require = anchor.require
M, K, RHO = F(24, 25), F(1, 2048), F(1, 4096)
HMIN, HMAX = F(3, 25), F(1, 8)
PARAMETER_BOX = MappingProxyType(dict(
    alpha=(F(1,4096), F(1,2048)), beta=(F(1,4096), F(1,2048)),
    gamma=(F(1,2048), F(1,1024)), chi=(F(1,32), F(1,16)),
    kh=(F(1,2), F(1)), kah=(F(1,2), F(1)),
    a=(F(19,4)-F(1,4096), F(19,4)+F(1,4096)),
    nu=(F(1,131072), F(1,65536))))
CONTRACT = MappingProxyType(dict(
    schema='atc_ci2_paired_domain_v1', candidate='A', realization='CI',
    source='paired positive Q=9, x>=29/10, W in [24/25,1]',
    obstruction='same domain with x>=3, including W-reset control',
    current_event='3<=x<=7/2; 0<=y<=1/50; ordered distinct sectors; positive root inflows and resolved share',
    reset_event='independent state; 3<=x<=7/2; abs(y)<=1/50; no allocator vote',
    share='round-even 2**16 current-root share in [31/64,33/64]',
    target='paired target; Q=9; X=norm(C-3/2)<=3/2; W in [24/25,1]',
    root='unique joint J,H on symmetric star ball ||H-I||_F<=1/4096',
    event_operand='fresh committed C,W and complete selected joint CI root',
    history='old W follows exact edge lineage; bridge W=1; no Z coordinate',
    potential_theorem='common C1 p on [0,9]; |p_prime-19/4|<=1/2048',
    executable_potential='quadratic p(c)=a*c+nu*c*c/2',
    requests=('3/25','1/8'), tau_A='1/(8 log 2)',
    profile_variation='choose fixed profile; only ordinary requests vary between beats',
    whole_box_event_formation=False, active_environment=False, native_authority=False))


def root_certificate(kind):
    """Uniform self-map, Banach and Schur-complement constants, before iteration."""
    require(kind in ('source','target'), 'CI domain kind')
    chi, gamma, kh = F(1,16), F(1,1024), F(1)
    rr, margin = F(1,783), 1-chi/49
    if kind == 'source':
        # Fixed-potential paired incidence bound, enlarged only to x>=2.9.
        require(F(29,40)+F(387,100)*F(61,50)+9*K < F(11,2), 'source baseline lemma')
        b0, lb, count = F(11,2), F(90), F(2)
        budget_base = F(1,2048)*(F(9,2)+F(27,10)**2/2)
    else:
        b0, lb, count = (4+F(5,2)*K)*F(3,2), F(125,8)*F(3,2), F(1)
        budget_base = F(1,2048)*(3+2*F(3,2)**2)
    b = b0 + lb*RHO
    budget = budget_base + gamma*(b/margin)**2/2
    flat = count*rr*b/(1-RHO)
    flux_lip = (rr+chi*gamma*b*b/(2*margin**2))*lb
    flat_lip = flux_lip/(1-RHO) + count*rr*b/(1-RHO)**2
    displacement, contraction = kh*flat**2, 2*kh*flat*flat_lip
    require(budget < 1-M, 'read and post-C writer history invariant')
    require(displacement < RHO and contraction < F(1,100), 'strict root self-map and contraction')
    return dict(kind=kind, radius=RHO, H_min=1-RHO, b0_bound=b0,
        b_bound=b, baseline_geometry_lipschitz=lb, component_to_vector=count,
        read_writer_exponent_budget=budget, current_margin=margin,
        readback_relative_bound=rr, flat_bound=flat, flat_lipschitz=flat_lip,
        displacement_bound=displacement, contraction_bound=contraction,
        current_block_inverse_bound=1/margin, reduced_block_inverse_bound=1/(1-contraction),
        reference_connected_unique_branch=True, other_roots_outside_ball_claimed=False)


def domain_bounds():
    source, target = root_certificate('source'), root_certificate('target')
    rr = F(1,783)
    err = 90*RHO + rr*(F(11,2)+90*RHO)
    growth = F(5,2)*HMIN*(F(19,250)-6*K-F(2,3)*err)
    multiplier, horizon = F(65,64), 71
    require(growth > multiplier-1 and 3*multiplier**horizon > 9, 'uniform positive-source obstruction')
    # Transfer geometry and bare polynomial identities do not depend on realization.
    t, y, eps, amin = F(2,5), F(1,50), F(23,320), F(7,4)
    initial2 = 12*t*t + 4*y*y + 2*eps*eps
    # min(s,1-s)*parent - max(leaf); increasing in x, so x=3
    # is worst. This is shared by the independent current and reset roles.
    funding_lower = F(31,64)*F(9+4*3,5) - (F(9-3,5)+F(1,50))
    require(funding_lower == F(1303,1600) and funding_lower > 0, 'uniform both-role child funding')
    leaf = (1-3*HMIN*amin)*t + (1-HMIN*amin)*y + HMAX*eps/4
    parent = (2-6*HMIN*(amin-F(1,25)))*t + HMAX*y/2 + (1-HMIN)*eps
    bare2 = 4*leaf*leaf+2*parent*parent
    require(initial2 < F(3,2)**2 and bare2 < F(5,8)**2, 'uniform both-role transfer and bare entry')
    lo, hi = M*F(7,16), F(73,16)
    require(1-HMAX*F(19,4)**2/4 > 0, 'positive bare spectral multiplier')
    q0 = max(1+HMIN*z*(z-F(19,4)) for z in (lo, hi))
    bcoef = 4+F(5,2)*K+F(125,8)*RHO
    correction = HMAX*F(5,2)*(F(5,2)*K+F(125,8)*RHO+rr*bcoef)
    q, entry = q0+correction, F(5,8)+F(3,2)*correction
    require(q < F(91,100) and entry < F(2,3), 'actual CI entry and return')
    require(F(1,4096)+9*F(1,65536) < K, 'quadratic subclass inside C1 slope envelope')
    return dict(contract=dict(CONTRACT), parameters=dict(PARAMETER_BOX), source_root=source,
        target_root=target, source_error=err, source_growth_excess_lower=growth,
        source_multiplier=multiplier, source_failure_by=horizon,
        initial_target_X_squared_upper=initial2, bare_first_X_squared_upper=bare2,
        funding_lower=funding_lower,
        resource_error_per_X=correction, target_first_X_upper=entry,
        target_return_factor=q, target_resource_floor=F(5,6),
        target_geometry_per_X_squared=(rr*bcoef/(1-RHO))**2,
        writer_decay_upper=F(25,37),
        limits=dict(C='(3/2)*1', J='zero', H='identity', W='exp(-3 alpha/2)'),
        proof='uniform rational sufficient inequalities, not a parameter sweep',
        event_premise='admitted source event with certified unique source-only share',
        native_authority=False)
