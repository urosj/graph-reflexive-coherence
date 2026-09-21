#!/usr/bin/env python3
"""Exact zero-feedback binary-partition mathematics, not a topology policy.

Stdlib rational arithmetic only. No native imports, events or trajectories.
The all-integer classification is proved in ATCPartitionDependentStability.md;
the finite roster here pressures its identities against independently built
Laplacians and certifies the smallest affine restorative example.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def laplacian(size, edges):
    value = [[F() for _ in range(size)] for _ in range(size)]
    for i, j in edges:
        value[i][i] += 1
        value[j][j] += 1
        value[i][j] -= 1
        value[j][i] -= 1
    return value


def double_star(m, n):
    if type(m) is not int or type(n) is not int or min(m, n) < 1:
        raise ValueError('two nonempty integer blocks are required')
    d = m + n
    edges = [(i, d) for i in range(m)]
    edges += [(i, d + 1) for i in range(m, d)] + [(d, d + 1)]
    return laplacian(d + 2, edges)


def shifted(L, t):
    return [[(t if i == j else F()) - v for j, v in enumerate(row)]
            for i, row in enumerate(L)]


def mv(matrix, vector):
    return tuple(sum((a*b for a, b in zip(row, vector, strict=True)), F())
                 for row in matrix)


def mm(a, b):
    return [list(mv(list(zip(*b)), row)) for row in a]


def determinant(matrix):
    a = [list(map(F, row)) for row in matrix]
    result = F(1)
    for i in range(len(a)):
        pivot = next((j for j in range(i, len(a)) if a[j][i]), None)
        if pivot is None:
            return F()
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            result = -result
        value = a[i][i]
        result *= value
        for j in range(i+1, len(a)):
            ratio = a[j][i] / value
            for k in range(i+1, len(a)):
                a[j][k] -= ratio*a[i][k]
            a[j][i] = F()
    return result


def ldlt_pivots(matrix):
    a = [list(map(F, row)) for row in matrix]
    pivots = []
    for i in range(len(a)):
        value = a[i][i]
        if value == 0:
            raise ValueError('zero exact pivot')
        pivots.append(value)
        for j in range(i+1, len(a)):
            for k in range(j, len(a)):
                a[k][j] -= a[j][i]*a[k][i]/value
                a[j][k] = a[k][j]
    return pivots


def field(L, C, p, kappa=F(1), eta=F(1)):
    LC = mv(L, C)
    gradient = tuple(p(c)-kappa*l for c, l in zip(C, LC, strict=True))
    return tuple(-eta*v for v in mv(L, gradient))


def run():
    predecessor_path = REFS / 'ATCAddressabilityConditions.json'
    predecessor = json.loads(predecessor_path.read_text())
    assert predecessor['record_digest'] == '6f6e7b8b681e8d560338f26d1da4a062e5726ca0590ea57c220e12be50da64c7'
    assert predecessor['record_digest'] == sha(canonical(
        {k: v for k, v in predecessor.items() if k != 'record_digest'}))

    rows = []
    determinant_checks = 0
    for d in range(2, 9):
        for m in range(1, d//2+1):
            n = d-m
            L = double_star(m, n)
            size = d+2
            # N+1 exact values identify the two degree-N polynomials.
            for t in map(F, range(size+1)):
                cubic = t**3-(d+4)*t**2+(m*n+2*d+5)*t-(d+2)
                assert determinant(shifted(L, t)) == (t-1)**(d-2)*t*cubic
                determinant_checks += 1
            matrix = shifted(L, F(d+1))
            pivots = ldlt_pivots(matrix)
            delta = (d+1)*(m-1)*(n-1)-1
            expected_det = F(d)**(d-2)*(d+1)*delta
            assert determinant(matrix) == expected_det
            assert all(v > 0 for v in pivots[:-1])
            assert (pivots[-1] > 0) == (m >= 2)

            L2, L3 = mm(L, L), mm(mm(L, L), L)
            for index, block in ((d, m), (d+1, n)):
                degree = block+1
                assert L2[index][index] == degree*(degree+1)
                assert L3[index][index] == degree**3+2*degree**2+d+1
            assert L2[d][d+1] == -(d+2)
            gram = [[L2[i][j] for j in (d, d+1)] for i in (d, d+1)]
            assert determinant(gram) > 0
            corner_bound = m*m+n*n+5*d+8
            assert gram[0][0]+gram[1][1]-2*gram[0][1] == corner_bound

            # Direct source Laplacian, independently of the quotient formulas.
            source = laplacian(d+1, [(i, d) for i in range(d)])
            r, s = F(1), F(2*d)
            p = lambda c: c**3/F(7)-c/F(3)
            js = (d+1)*(s-r)+p(r)-p(s)
            assert field(source, (r,)*d+(s,), p) == (-js,)*d+(d*js,)
            child_resources = (F(m, d)*s, F(n, d)*s)
            assert sum(child_resources) == s and min(child_resources) > r
            rows.append(dict(m=m, n=n, degree=d, vertices=size,
                threshold_determinant=str(expected_det),
                threshold_ldlt_pivots=list(map(str, pivots)),
                affine_window_exists_for_positive_kappa=m >= 2,
                load_gram=[list(map(str, row)) for row in gram],
                load_gram_determinant=str(determinant(gram)),
                joint_load_squared_coefficient=corner_bound))

    # Minimal admissible partition: 2+2. Coefficients are declared mathematical
    # data, not a replacement for any content-addressed runtime potential.
    m = n = 2
    d = 4
    L = double_star(m, n)
    kappa, eta, h, a, epsilon = F(1), F(1), F(1, 8), F(19, 4), F(1, 64)
    r, s = F(1), F(3)
    p = lambda c: a*c
    C0 = (r,)*4+(s/2,)*2
    charge = sum(C0)
    mean = charge/6
    source = laplacian(5, [(i, 4) for i in range(4)])
    js = eta*(5*kappa-a)*(s-r)
    assert js == F(1, 2)
    assert field(source, (r,)*4+(s,), p) == (-js,)*4+(4*js,)
    target_field = field(L, C0, p)
    assert target_field == (F(7, 8),)*4+(F(-7, 4),)*2
    assert field(L, (mean,)*6, p) == (F(),)*6

    # The balanced target spectrum is 0,1,1,3,(5+-sqrt(17))/2.
    for t in map(F, range(7)):
        assert determinant(shifted(L, t)) == t*(t-1)**2*(t-3)*(t*t-5*t+2)
    lower, upper = F(3, 8), F(37, 8)
    qpoly = lambda t: t*t-5*t+2
    assert lower < F(5, 2) < upper
    assert qpoly(lower) == qpoly(upper) == F(17, 64) > 0
    assert all(v > 0 for v in ldlt_pivots(shifted(L, upper)))
    mu = a-kappa*upper
    rate_lower, rate_upper = lower*mu, a*a/(4*kappa)
    multiplier_lower = 1-h*eta*rate_upper
    contraction = 1-h*eta*rate_lower
    assert mu == F(1, 8)
    assert 0 < multiplier_lower <= contraction < 1

    initial_radius_squared = sum((c-mean)**2 for c in C0)
    radius_bound, joint_load_bound, R = F(3, 5), 6*epsilon, F(3, 4)
    assert initial_radius_squared == F(1, 3) < radius_bound**2
    assert radius_bound+joint_load_bound < R < mean
    resource_lower = mean-R
    assert resource_lower == F(5, 12)

    L2, L3 = mm(L, L), mm(mm(L, L), L)
    directions = [tuple(-L[j][i] for j in range(6)) for i in (4, 5)]
    base = field(L, C0, p)
    responses = []
    for i, w in zip((4, 5), directions, strict=True):
        loaded = tuple(c+epsilon*z for c, z in zip(C0, w, strict=True))
        response = h/(3*epsilon)*(field(L, loaded, p)[i]-base[i])
        assert response == h*eta/3*(a*L2[i][i]-kappa*L3[i][i]) == F(7, 24)
        responses.append(str(response))
    for aa in (-epsilon, epsilon):
        for bb in (-epsilon, epsilon):
            load = tuple(aa*u+bb*v for u, v in zip(*directions, strict=True))
            assert sum(load) == 0
            assert sum(v*v for v in load) <= joint_load_bound**2

    # Funded/inward negative control: a singleton block still fails curvature.
    negative = double_star(1, 3)
    negative_pivots = ldlt_pivots(shifted(negative, a))
    assert negative_pivots[-1] < 0
    negative_s = F(5)
    assert (5-a)*(negative_s-r) == 1
    assert min(negative_s/4, 3*negative_s/4)-r == F(1, 4) > 0
    for bad in ((0, 2), (-1, 2), (1, 0), (True, 2), (1, 2.0)):
        try:
            double_star(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid partition was admitted')

    paths = [Path(__file__).resolve(), predecessor_path,
             INV/'scripts/probe_atc_source_fission.py']
    record = dict(schema='grcv4_atc_partition_stability_certificate_v1',
        status='passed_exact_algebra_and_affine_return_bounds',
        scientific_status='proposed_mathematical_result_pending_independent_review',
        scope='symmetric unit-weight star source; supplied binary nonempty half-edge blocks; one unit child bridge; fixed zero-feedback law',
        predecessor_digest=predecessor['record_digest'],
        classification=dict(source_threshold='(m+n+1)*kappa',
            target_characteristic='(t-1)^(m+n-2)*t*(t^3-(m+n+4)*t^2+(m*n+2*(m+n)+5)*t-(m+n+2))',
            affine_window='kappa*lambda_max(L_target)<a<kappa*(m+n+1)',
            exists_iff='kappa>0 and m>=2 and n>=2',
            exact_proof='Schur complement: det S=(d+1)/d^2*((d+1)*(m-1)*(n-1)-1)',
            all_integer_proof_in='implementation/investigations/grc9v4-constitutive-design/decisions/ATCPartitionDependentStability.md',
            finite_roster_role='identity/negative-control pressure, not proof by enumeration'),
        finite_checks=dict(degrees=[2, 8], unordered_partitions=len(rows),
            characteristic_determinant_evaluations=determinant_checks,
            rejected_invalid_partitions=5, rows=rows),
        affine_example=dict(m=2, n=2, p='(19/4)*c', kappa=str(kappa), eta=str(eta),
            h=str(h), epsilon=str(epsilon), source_C=list(map(str, (r,)*4+(s,))),
            source_inward_current=str(js), target_C=list(map(str, C0)),
            target_field=list(map(str, target_field)), conserved_charge=str(charge),
            child_funding_margin='1/2', equilibrium_C=[str(mean)]*6,
            spectral_lower=str(lower), spectral_upper=str(upper), curvature_lower=str(mu),
            decay_rate_lower=str(rate_lower), decay_rate_upper=str(rate_upper),
            step_multiplier_lower=str(multiplier_lower), contraction_upper=str(contraction),
            initial_radius_squared=str(initial_radius_squared), initial_radius_upper=str(radius_bound),
            joint_load_norm_upper=str(joint_load_bound), invariant_radius=str(R),
            resource_lower=str(resource_lower), directions=[list(map(str, w)) for w in directions],
            individual_response=responses, response_normalization='h*delta_f_i/(degree_i*epsilon)',
            return_scope='exact-arithmetic one signed joint encounter at any unencountered age; not arbitrary repeated encounters or rounded execution'),
        negative_control=dict(m=1, n=3, source_C=['1', '1', '1', '1', '5'],
            source_inward_current='1', child_funding_margin='1/4',
            a=str(a), curvature_ldlt_pivots=list(map(str, negative_pivots)),
            outcome='inward and funded but target affine curvature indefinite'),
        unestablished=['autonomous_partition_selection', 'higher_degree_F2',
            'nonzero_geometry_or_history_feedback', 'generic_graphs', 'nonuniform_sources',
            'all_ten_families', 'independent_identity', 'general_functional_differentiation',
            'runtime_potential_or_initializer_admission', 'rounded_infinite_return'],
        trajectory_updates=0, native_steps=0, topology_events=0, production_changes=False,
        source_bindings=[dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path.read_bytes()))
                         for path in paths])
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))
