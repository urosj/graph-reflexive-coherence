#!/usr/bin/env python3
"""Exact outward enclosures of the fixed CAN-LSF enabled research point.

Integer-directed dyadic interval arithmetic; rational alternating-series exp;
integer-square-root enclosures. No binary/Decimal transcendental evaluation,
native execution, new parameter search, file writes or predecessor reruns.
"""
from fractions import Fraction as F
from math import isqrt
import hashlib
import json
from pathlib import Path

BITS = 256
GRID = 1 << BITS
ROOT = Path(__file__).resolve().parents[4]
INV = Path('implementation/investigations/grc9v4-constitutive-design')
REFS = INV / 'evidence/autonomous-topology-change'
SOURCE = ((0, 4), (1, 4), (2, 4), (3, 4))
TARGET = ((0, 4), (1, 4), (2, 5), (3, 5), (4, 5))


def ceil_div(n, d):
    return -((-n)//d)


class I:
    """[lo/GRID,hi/GRID], with integer endpoints and outward operations."""

    def __init__(self, value=0):
        q = F(value)
        self.lo = q.numerator*GRID//q.denominator
        self.hi = ceil_div(q.numerator*GRID, q.denominator)

    @classmethod
    def bounds(cls, lo, hi):
        assert isinstance(lo, int) and isinstance(hi, int) and lo <= hi
        out = cls.__new__(cls)
        out.lo, out.hi = lo, hi
        return out

    @staticmethod
    def coerce(value):
        return value if isinstance(value, I) else I(value)

    def __add__(self, other):
        other = I.coerce(other)
        return I.bounds(self.lo+other.lo, self.hi+other.hi)

    __radd__ = __add__

    def __neg__(self):
        return I.bounds(-self.hi, -self.lo)

    def __sub__(self, other):
        return self+-I.coerce(other)

    def __rsub__(self, other):
        return I.coerce(other)+-self

    def __mul__(self, other):
        other = I.coerce(other)
        products = [a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return I.bounds(min(products)//GRID, ceil_div(max(products), GRID))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = I.coerce(other)
        assert not other.lo <= 0 <= other.hi, 'uncertain or zero divisor'
        pairs = [(a*GRID, b) for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return I.bounds(min(n//d for n, d in pairs), max(ceil_div(n, d) for n, d in pairs))

    def square(self):
        lo = 0 if self.lo <= 0 <= self.hi else min(self.lo*self.lo, self.hi*self.hi)
        hi = max(self.lo*self.lo, self.hi*self.hi)
        return I.bounds(lo//GRID, ceil_div(hi, GRID))

    def sqrt(self):
        assert self.lo >= 0, 'sqrt domain uncertified'
        lo, hi = isqrt(self.lo*GRID), isqrt(self.hi*GRID)
        hi += hi*hi < self.hi*GRID
        assert lo*lo <= self.lo*GRID and hi*hi >= self.hi*GRID
        return I.bounds(lo, hi)

    def exp_nonpositive(self):
        assert self.hi <= 0, 'exp helper is restricted to nonpositive arguments'
        def endpoint(n):
            t, squarings = F(-n, GRID), 0
            while t > F(1, 8):
                t /= 2
                squarings += 1
            # 0<=t<=1/8: decreasing alternating terms bracket exp(-t).
            term, partial = F(1), F(1)
            for k in range(1, 49):
                term *= -t/k
                partial += term
            lower = partial+term*(-t)/49  # odd partial sum, 49 terms beyond 1
            upper = partial             # even partial sum, 48 terms beyond 1
            assert 0 < lower <= upper <= 1
            out = I.bounds(I(lower).lo, I(upper).hi)
            for _ in range(squarings):
                out = out.square()
            return out
        return I.bounds(endpoint(self.lo).lo, endpoint(self.hi).hi)

    def contains(self, rational):
        q = F(rational)*GRID
        return self.lo <= q <= self.hi


def mv(matrix, vector):
    return tuple(sum((a*b for a, b in zip(row, vector, strict=True)), I()) for row in matrix)


def solve(matrix, vector):
    """Interval Gaussian elimination; every pivot interval must be positive."""
    rows = [list(row)+[v] for row, v in zip(matrix, vector, strict=True)]
    n = len(vector)
    for i in range(n):
        pivot = rows[i][i]
        assert pivot.lo > 0, 'uncertain SPD elimination pivot'
        rows[i] = [x/pivot for x in rows[i]]
        for j in range(i+1, n):
            factor = rows[j][i]
            rows[j] = [x-factor*y for x, y in zip(rows[j], rows[i], strict=True)]
    out = [I()]*n
    for i in reversed(range(n)):
        out[i] = rows[i][-1]-sum((rows[i][j]*out[j] for j in range(i+1, n)), I())
    return tuple(out)


def incidence(n, edges):
    B = tuple(tuple(int(i == u)-int(i == v) for u, v in edges) for i in range(n))
    assert all(sum(column) == 0 for column in zip(*B))
    return B


def norm2(vector):
    return sum((v.square() for v in vector), I())


def star(f, B):
    return tuple(tuple(sum(bool(row[i] and row[j]) for row in B)*f[i]*f[j]/2
                       for j in range(len(f))) for i in range(len(f)))


def stage(C, W, H, B):
    BT = tuple(zip(*B))
    d = mv(BT, C)
    stiffness = mv(B, tuple(w*v for w, v in zip(W, d, strict=True)))
    delta = tuple(tuple(v-int(i == j) for j, v in enumerate(row)) for i, row in enumerate(H))
    geometry_phi = mv(B, mv(delta, d))
    phi = tuple(v-F(19, 4)*c+g for c, v, g in zip(C, stiffness, geometry_phi, strict=True))
    baseline = tuple(-w*v for w, v in zip(W, mv(BT, phi), strict=True))
    target = tuple((-v.square()/2048).exp_nonpositive() for v in baseline)
    assert all(t.lo > GRID//2 for t in target), 'pre-read floor inactivity uncertified'
    q = tuple((w-t)/(w+t) for w, t in zip(W, target, strict=True))
    denom = tuple(1-x/16 for x in q)
    assert all(x.lo > 0 for x in denom)
    J = tuple(v/x for v, x in zip(baseline, denom, strict=True))
    read = tuple(x*v/16 for x, v in zip(q, J, strict=True))
    flat = solve(H, read)
    return dict(baseline=baseline, current=J, flat=flat, geometry_phi=geometry_phi)


def minimum(vector):
    return I.bounds(min(v.lo for v in vector), min(v.hi for v in vector))


def step(C, W, B):
    identity = tuple(tuple(I(int(i == j)) for j in range(len(W))) for i in range(len(W)))
    pred = stage(C, W, identity, B)
    S = star(pred['flat'], B)
    H = tuple(tuple(a+b for a, b in zip(row, other, strict=True)) for row, other in zip(identity, S, strict=True))
    corr = stage(C, W, H, B)
    S1 = star(corr['flat'], B)
    residual2 = norm2(tuple(a-b for row, other in zip(S, S1, strict=True) for a, b in zip(row, other, strict=True)))
    assert residual2.hi < GRID*F(1, 512**2), 'OS residual admission uncertified'
    Cnext = tuple(c-v/8 for c, v in zip(C, mv(B, corr['current']), strict=True))
    min_C = minimum(Cnext)
    if min_C.lo > 0:
        writer = tuple((-j.square()/2048).exp_nonpositive() for j in corr['current'])
        assert all(t.lo > GRID//2 and t.hi <= GRID for t in writer)
        Wnext = tuple((w*t).sqrt() for w, t in zip(W, writer, strict=True))
        assert all(w.lo >= GRID//2 and w.hi <= GRID for w in Wnext)
        status = 'admitted_positive'
    elif min_C.hi < 0:
        writer, Wnext, status = None, None, 'certified_negative_resource_proposal'
    else:
        raise AssertionError('resource admission unresolved by enclosure')
    return dict(C_next=Cnext, W_next=Wnext, status=status, minimum_C=min_C,
                split_residual_squared=residual2, reference=pred, fresh=corr, writer=writer,
                readback_change_squared=norm2(tuple(a-b for a, b in zip(pred['current'], pred['baseline'], strict=True))),
                fresh_change_squared=norm2(tuple(a-b for a, b in zip(corr['current'], pred['current'], strict=True))),
                geometry_increment_squared=norm2(tuple(x for row in S for x in row)),
                geometry_consumption_squared=norm2(corr['geometry_phi']))


def guard(C, W):
    B = incidence(5, SOURCE)
    H = tuple(tuple(I(int(i == j)) for j in range(4)) for i in range(4))
    J = stage(C, W, H, B)['current']
    return dict(sector_separation=W[2]-W[0], old_source_spectral_guard=F(5, 2)*(W[0]+W[2])-F(19, 4),
                inward=minimum(J), x=C[4]-(C[0]+C[2])/2, y=(C[0]-C[2])/2,
                reference_current=J)


def rounding_bin(ratio):
    k = (ratio.lo+ratio.hi+GRID)//(2*GRID)
    assert (F(k)-F(1, 2))*GRID < ratio.lo and ratio.hi < (F(k)+F(1, 2))*GRID, 'rounding bin unresolved'
    return k


def kernel_checks():
    probes = (F(-7, 3), F(-1, 7), F(0), F(1, 9), F(3, 2))
    for a in probes:
        for b in probes:
            assert (I(a)+I(b)).contains(a+b)
            assert (I(a)-I(b)).contains(a-b)
            assert (I(a)*I(b)).contains(a*b)
            if b:
                assert (I(a)/I(b)).contains(a/b)
        assert I(a).square().contains(a*a)
    crossing = I.bounds(-GRID, 2*GRID)
    assert crossing.square().lo == 0 and crossing.square().hi == 4*GRID
    assert I().exp_nonpositive().lo == I().exp_nonpositive().hi == GRID
    for a in (F(0), F(1, 7), F(2), F(4)):
        r = I(a).sqrt()
        assert F(r.lo, GRID)**2 <= a <= F(r.hi, GRID)**2
    for operation in (lambda: I(1)/crossing, lambda: rounding_bin(I(F(3, 2)))):
        try:
            operation()
        except AssertionError:
            pass
        else:
            raise AssertionError('uncertain decision was silently resolved')
    return dict(arithmetic_probe_pairs=25, exact_sqrt_checks=4,
                zero_crossing_square=True, uncertain_division_and_rounding_rejected=True)


def symmetry_checks():
    # Automorphisms of the fully homogeneous reference data, not near equality.
    for n, edges in ((5, SOURCE), (6, TARGET)):
        for pair in ((0, 1), (2, 3)):
            perm = list(range(n)); perm[pair[0]], perm[pair[1]] = pair[1], pair[0]
            assert sorted((perm[u], perm[v]) for u, v in edges) == sorted(edges)
    return dict(group='independent leaf swaps (0 1), (2 3)',
                data='paired initial C/W, unit vertex/edge references, common scalar parameters',
                argument='equivariance of every staged operation preserves the fixed subspace in exact reals',
                interval_overlap_used_as_equality_proof=False)


def compact(row):
    return {k: row[k] for k in ('status', 'minimum_C', 'split_residual_squared', 'C_next', 'W_next')}


def evidence():
    C0 = (I(1),)*4+(I(5),)
    W0 = (I(F(361, 400)),)*2+(I(F(5929, 6400)),)*2
    B = incidence(5, SOURCE)
    initial = guard(C0, W0)
    assert initial['old_source_spectral_guard'].hi < 0
    first = step(C0, W0, B)
    assert first['status'] == 'admitted_positive'
    C1, W1 = first['C_next'], first['W_next']
    selected = guard(C1, W1)
    assert all(selected[k].lo > 0 for k in ('sector_separation', 'old_source_spectral_guard', 'inward', 'x', 'y'))
    nonvacuity = {k: first[k] for k in ('readback_change_squared', 'fresh_change_squared',
                                        'geometry_increment_squared', 'geometry_consumption_squared')}
    assert all(value.lo > 0 for value in nonvacuity.values())
    assert all(value.hi < GRID for value in first['writer'])
    J = selected['reference_current']
    activities = (J[0]+J[1], J[2]+J[3])
    ratio = 65536*activities[0]/sum(activities, I())
    k = rounding_bin(ratio)
    assert k == 30779
    shares = (F(k, 65536), F(65536-k, 65536))
    assert sum(shares) == 1  # Exact column-conservative resource transfer.
    funding = (shares[0]*C1[4]-C1[0], shares[1]*C1[4]-C1[2])
    assert all(v.lo > 0 for v in funding)
    tie_margin = minimum((ratio-(F(k)-F(1, 2)), F(k)+F(1, 2)-ratio))
    selected.update(k=k, grid_coordinate=ratio, distance_to_nearest_tie=tie_margin, funding=funding)
    controls = {}
    # Reuse the certified initial ordinary beat as the no-split prefix.
    for name, C, W, start, expected in (
            ('no_split', C1, W1, 2, 10),
            ('history_reset_without_split', C1, (I(1),)*4, 1, 7)):
        rows = [dict(attempt=1, **compact(first))] if name == 'no_split' else []
        for attempt in range(start, 17):
            row = step(C, W, B)
            rows.append(dict(attempt=attempt, **compact(row)))
            if row['status'] == 'certified_negative_resource_proposal':
                assert attempt == expected and row['W_next'] is None
                break
            C, W = row['C_next'], row['W_next']
        else:
            raise AssertionError('no certified failure within the declared horizon')
        controls[name] = dict(rows=rows, failed_attempt=attempt, rejection='resource_positivity',
                              all_OS_residuals_admitted=True, failed_proposal_not_published=True)
    history_lower = I(F(-1, 8)).exp_nonpositive()
    roles = {}
    for name, C, W in (('current', C1, W1), ('reset', C0, W0)):
        target_C = C[:4]+(shares[0]*C[4], shares[1]*C[4])
        target_W = W+(I(1),)
        row = step(target_C, target_W, incidence(6, TARGET))
        assert row['status'] == 'admitted_positive'
        X2 = norm2(tuple(c-F(3, 2) for c in row['C_next']))
        assert X2.hi < GRID*F(4, 9)
        assert all(w.lo > history_lower.hi and w.hi <= GRID for w in row['W_next'])
        roles[name] = dict(**compact(row), squared_deviation=X2,
                           first_entry_certified=True, incoming_C=target_C, incoming_W=target_W)
    return dict(initial_C=C0, initial_W=W0, initial_guard=initial, first_ordinary=compact(first),
                nonvacuity=nonvacuity, writer_targets=first['writer'], source_selection=selected,
                no_event_controls=controls, target_entries=roles, exp_minus_one_eighth=history_lower,
                exact_charge_reason='initial sum nine; incidence columns sum zero; transfer columns sum one',
                scope='fixed prepared point and its one source-selected prescription, not all guard-positive states',
                full_parameter_box_source_or_entry_certified=False)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def encode(value):
    if isinstance(value, I):
        return {'lo': str(value.lo), 'hi': str(value.hi)}
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def main():
    prior_path = REFS/'ATCSectorReadBackLiftChecks.json'
    prior = json.loads((ROOT/prior_path).read_text())
    body = dict(prior); digest = body.pop('record_digest')
    assert hashlib.sha256(canonical(body)).hexdigest() == digest == '4f12d56fd3cccf87925613b021eaed34ecc3087a3403c06b3e7c6023e23fa4a3'
    for binding in prior['source_bindings']:
        assert hashlib.sha256((ROOT/binding['path']).read_bytes()).hexdigest() == binding['sha256'], binding['path']
    assert prior['conditional_target_bounds']['resource_contraction'] == '9209/10240'
    paths = [Path(__file__).relative_to(ROOT), prior_path,
             INV/'decisions/ATCSectorReadBackPointCertification.md',
             REFS/'review/CAN-LSF-ReadBack-Qualified-Pass.md']
    result = encode(dict(schema='grcv4_atc_sector_readback_point_certificate_v1',
        status='fixed_point_enclosure_certificate_pending_independent_review',
        predecessor_record_digest=digest, arithmetic=dict(endpoint_encoding='integer / 2^256',
            bits=BITS, exp='range-reduced rational alternating partial sums N=48,49; outward squaring',
            sqrt='integer isqrt outward endpoints', transcendental_library_used=False),
        kernel_checks=kernel_checks(), symmetry=symmetry_checks(), point=evidence(),
        target_theorem_composition=dict(resource_contraction='9209/10240', resource_floor='5/6',
            history_limit='log W tends to zero', proof='certified both-role entry followed by reviewed uniform conditional theorem'),
        accepted_nonzero_feedback_scope=False, second_adjudication=False, native_execution=False,
        graph_admission=False, ATC2_closed=False,
        source_bindings=[dict(path=str(p), sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]))
    result['record_digest'] = hashlib.sha256(canonical(result)).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
