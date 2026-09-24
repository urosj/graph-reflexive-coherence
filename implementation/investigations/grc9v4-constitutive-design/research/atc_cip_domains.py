"""CIP-0 sufficient coupled-root box; no event/trajectory or native authority.

Import CI's fixed-H lemmas, not its realization-specific root certificate.
The persistent tensor is a fixed, signed, decorated root parameter.
"""
from fractions import Fraction as F
from types import MappingProxyType
import atc_ci_domains as ci

require = ci.require
RZ, KHMAX = F(1, 5000), F(3, 5)
PARAMETER_BOX = MappingProxyType({**ci.PARAMETER_BOX, 'kh': (F(1, 2), KHMAX)})


def root_certificate(kind, *, carrier_radius=RZ, kh_max=KHMAX):
    """Exact sufficient inequalities; a rejected box is not a no-root proof."""
    require(type(carrier_radius) is F and type(kh_max) is F, 'exact rational bounds')
    require(carrier_radius > 0 and F(1, 2) <= kh_max <= 1, 'within fixed-H lemma scope')
    lemma = ci.root_certificate(kind)
    # The imported displacement was evaluated at kh=1, hence equals F_flat².
    source = lemma['flat_bound']**2
    lip = 2 * lemma['flat_bound'] * lemma['flat_lipschitz'] * kh_max
    displacement = kh_max * (carrier_radius + source)
    require(source < carrier_radius, 'held-source carrier-ball invariant')
    require(displacement < ci.RHO, 'combined geometry budget')
    require(lip < 1, 'uniform contraction')
    return dict(kind=kind, fixed_H_lemma=lemma, carrier_radius=carrier_radius,
        kh_max=kh_max, instantaneous_source_bound=source,
        total_displacement_bound=displacement, geometry_slack=ci.RHO-displacement,
        carrier_slack=carrier_radius-source, contraction_bound=lip,
        reduced_inverse_bound=1/(1-lip), carrier_to_root_lipschitz=kh_max/(1-lip),
        current_block_inverse_bound=lemma['current_block_inverse_bound'],
        uniform_in_fixed_Z=True, other_roots_outside_ball_claimed=False)


def domain_certificate():
    source, target = (root_certificate(kind) for kind in ('source', 'target'))
    # Negative controls are proof-budget rejections, not physics failures.
    rejected = []
    for label, radius, gain in (
        ('standalone_PC_radius_at_half_gain', F(1, 3072), F(1, 2)),
        ('standalone_CI_gain_upper', RZ, F(1)),
        ('carrier_smaller_than_source_bound', F(1, 10000), KHMAX),
    ):
        try:
            root_certificate('source', carrier_radius=radius, kh_max=gain)
        except ci.anchor.a.AdmissionError as exc:
            rejected.append(dict(case=label, reason=str(exc)))
        else:
            raise AssertionError('negative proof-budget control unexpectedly passed: ' + label)
    require(F(1, 8192) < RZ, 'preregistered nonzero carrier is interior')
    return dict(parameters=dict(PARAMETER_BOX), geometry_radius=ci.RHO,
        carrier_radius=RZ, requests=(ci.HMIN, ci.HMAX), rho_inst=1, zeta_A=1,
        tau_A='1/(8 log 2)', tau_PC='1/(8 log 2)', source=source, target=target,
        negative_budget_controls=rejected,
        Z_domain='exact decorated signed symmetric star-supported Frobenius ball',
        writer='convex old-Z / same-selected-root-S update; fixed positive tau_PC',
        regularity='invertible current block and reduced H Schur complement',
        acceptance=False, complete_causal_chain=False, native_authority=False)
