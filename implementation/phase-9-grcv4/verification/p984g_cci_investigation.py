"""Exact-real C_CI ball investigation; no native root or staged-error credit."""

import argparse
import hashlib
import json
import subprocess
from flint import arb, ctx, fmpq
import p984g_cos as shared

ROOT, BASE, HERE = shared.ROOT, shared.BASE, shared.HERE
SELF = HERE + 'p984g_cci_investigation.py'
TEST = HERE + 'test_p984g_cci_investigation.py'
PLAN = BASE + 'P9-8.4g-CCIInvestigationPlan.md'
REVIEW = BASE + 'P9-8.4g-CCIInvestigation.md'
PREPARED = BASE + 'larger-graph-examples/C_CI.json'
RESULTS = BASE + 'P9-8.4g-CCIInvestigationResults.json'
BITS = 192
require, read, seal = shared.require, shared.read, shared.seal


def q(value):
    return value if isinstance(value, fmpq) else fmpq(value) if isinstance(value, (int, str)) else shared.q(value)


def upper(value):
    require(value.is_finite(), 'nonfinite scalar enclosure')
    return value.upper().fmpq()


def conditions(n, radius, cutoff, beta, displacement, contraction, condition, limit):
    require(n > 1 and 0 <= radius < 1, 'SPD ball required')
    gap = (1-radius)/q(n*(n-1))-cutoff
    require(cutoff > 0 and gap > 0, 'strict constant-selector separation required')
    require(0 <= beta < 1, 'positive-s nonnegative-feedback domain required')
    require(displacement <= radius, 'self-map unproved')
    require(0 <= contraction < 1, 'strict contraction unproved')
    require(condition <= limit, 'physical conditioning unproved')
    return gap


def certificate(subject, role):
    b, params = shared.graph_data(subject)
    require(subject['profile']['identity_payload']['profile_family_id']=='C_CI', 'C_CI only')
    p, real = params['candidate'], params['realization']
    require(real['schema_version']=='grcv4-ci-params-v1', 'non-composite CI required')
    require(params['geometry']['star_cover_id']=='vertex_star_exact_overlap_v1'
            and params['geometry']['overlap_normalization_id']=='edge_multiplicity_inverse_sqrt_v1', 'star hypothesis')
    require(p['potential_evaluator_id']=='quadratic_site_potential_zero_derivative_v1'
            and p['transport_id']=='C-HM-STIFFNESS-BASELINE-v1', 'transport hypothesis')
    require(p['C_ref']>0 and p['tau_C']>=0, 'positive scale/nonnegative tau required')
    require(real['contraction_domain_id'].startswith('ci_reference_frobenius_ball_v1:'), 'Frobenius ball required')
    radius = q(float.fromhex(real['contraction_domain_id'].split(':',1)[1]))
    c = [q(x) for x in subject['roles'][role]['C']]
    require(len(c)==len(b) and all(x>=0 for x in c), 'resource domain')
    require(subject['roles'][role]['W_A'] is None and subject['roles'][role]['Z_4'] is None, 'unexpected history')
    n, m = b.shape
    beta = q(p['zeta_C'])*q(p['chi_C'])
    # Validate hypotheses before evaluating any denominator or square root.
    conditions(n,radius,q(p['Lambda_C']),beta,0,0,1,q(params['solver']['conditioning_limit']))
    lower, high = 1-radius, 1+radius
    degree = max(sum(abs(int(x)) for x in row) for row in b)
    dnorm = q(2*degree)  # ||B^T B||_2 <= 2 maximum vertex degree
    dc = [sum((q(int(w))*v for w,v in zip(col,c,strict=True)),q(0)) for col in b.T]
    with ctx.workprec(BITS):
        # exp(|kappa_M|) bounds the constant-mode scalar retained Hodge tH.
        t = upper(arb(abs(q(p['kappa_M_C']))).exp())
        similarity = upper(arb(high/lower).sqrt())
        d = upper(arb(sum((x*x for x in dc),q(0))).sqrt())
        inverse = similarity/(1-beta)
        baseline_lip = abs(q(p['eta_C'])*q(p['kappa_Phi_C']))*t*dnorm*d
        baseline = baseline_lip*high
        v = inverse*baseline
        v_lip = inverse*(baseline_lip+q(p['tau_C'])*t*dnorm*v)
        flat = abs(q(p['chi_C']))*v/lower
        flat_lip = abs(q(p['chi_C']))*(v_lip/lower+v/lower**2)
        gain = abs(q(params['geometry']['kappa_H'])*q(p['zeta_C']))
        displacement = gain*flat**2
        contraction = 2*gain*flat*flat_lip
        require(beta*similarity<1, 'physical conditioning Neumann margin')
        physical_condition = (1+beta*similarity)/(1-beta*similarity)
        gap = conditions(n,radius,q(p['Lambda_C']),beta,displacement,contraction,
                         physical_condition,q(params['solver']['conditioning_limit']))
        current_lip = baseline_lip+beta*v_lip
        joint_factor = upper(arb(1+current_lip**2).sqrt())/(1-contraction)
    bounds = dict(radius=radius, selector_gap=gap, hodge_lower=lower, hodge_upper=high,
        incidence_gram_upper=dnorm, retained_scalar_upper=t, inverse_upper=inverse,
        baseline_upper=baseline, current_lipschitz_upper=current_lip,
        flat_upper=flat, flat_lipschitz_upper=flat_lip,
        displacement_upper=displacement, contraction_upper=contraction,
        physical_condition_upper=physical_condition,
        joint_error_per_geometry_residual_upper=joint_factor,
        root_distance_from_reference_upper=displacement,
        tolerance=q(real['tolerance']))
    return dict(vertices=n,edges=m,maximum_degree=degree,
        bounds={k:str(v) for k,v in bounds.items()},
        exact_real_unique_root=True,
        reference_pair_already_within_exact_real_residual_tolerance=displacement<=q(real['tolerance']),
        native_first_iteration_prediction_verified=False)


def calculate():
    declaration=read(PREPARED)
    require((ROOT/PREPARED).read_bytes()==subprocess.check_output(
        ['git','show','e1d61021:'+PREPARED],cwd=ROOT), 'prepared declaration changed')
    require(declaration['reference_recipe']==dict(unit_vertex_measures=True,unit_edge_weights=True,
        K4_base='exact zero m by m in each graph edge order',
        context=dict(contract_id='constant_zero_context_v1',values={})), 'unit reference hypothesis')
    cases=[dict(graph=g,role=r,**certificate(declaration[g],r)) for g,r in shared.CASES]
    paths=[SELF,TEST,PLAN,REVIEW,PREPARED,shared.SELF,
           HERE+'prepare_p983_all_realizations.py','src/pygrc/models/grc_v4_ci.py',
           'src/pygrc/models/grc_v4_candidate_c.py','specs/grc-v4-spec.md']
    return seal(dict(schema='p984g-cci-investigation-v1',family='C_CI',cases=cases,
        source_bindings={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        scalar_backend='FLINT rational + Arb outward bounds',precision_bits=BITS,
        scope='exact_real_declared_frobenius_ball_not_represented_or_native',
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,
        user_accepted=False,aggregate_closed=False,
        open_obligations=['staged arithmetic and whole joint-root error bridge',
            'CI feedback discrimination under the unchanged residual tolerance',
            'native certificate, both-role roots, charge and final-C readmission']))


def check(value=None):
    value=read(RESULTS) if value is None else value
    require(value==calculate(), 'C_CI investigation/source/scope drift')
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('run','check'))
    args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no evidence overwrite')
        raw=json.dumps(calculate(),indent=2)+'\n'
        require(len(raw.encode())<500000,'retention budget')
        (ROOT/RESULTS).write_text(raw)
    else: check()


if __name__=='__main__': main()
