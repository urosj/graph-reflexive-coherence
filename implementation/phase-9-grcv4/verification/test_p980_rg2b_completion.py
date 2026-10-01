"""Nine-port RG2b research: new completion, not an ATC fixture or native backend.

All graph, fixed-row, signed-resource, inverse and section constants are derived
here for the source/D52 graphs. The abstract graph-transform proof is stated in
the companion note. No ATC package or accepted native completion is imported.
"""
from fractions import Fraction as Q
import json
import unittest
from unittest.mock import patch

import test_p980_revised_realization_bounds as physical
from test_p980_os_effect_witness import (
    IV, PARAMS, HISTORY_OFFSET, RESOURCE_RADIUS, HISTORY_RADIUS,
    IntervalRows, bounds, vector, number, endpoint, upper_abs, infinity,
)


# Frozen proposed auxiliary recipe. Physical inputs lie strictly inside it.
SCALE = Q(512)
C_LOW, C_HIGH = Q(-1), Q(5)
Y_LOW, Y_HIGH = Q(-1), Q(1)
RHO = Q(1, 2**12)
SECTION_LIP = Q(1, 1024)
INVERSE_ERROR = Q(1, 2**36)  # research query enclosure, not native tolerance
DEGREE, EDGE_GRAM, MASK_NORM = Q(9), Q(10), Q(5)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def global_bounds(candidate):
    """Rational value and Lipschitz bounds on the ENTIRE signed clamp chart.

    State norm = max(||C||inf, ||Y||inf), Y=512 log W for A. Geometry norm
    is induced infinity throughout. Exp bounds use 1-x <= exp(-x) and
    exp(x) <= 1/(1-x); no physical E>=0 assumption enters the A estimates.
    """
    require(candidate in ('A', 'C'), 'unknown candidate')
    dt, kh, eps = bounds.DT, bounds.KAPPA_H, PARAMS.coefficient
    bmax, hinv = C_HIGH-C_LOW, 1/(1-RHO)
    if candidate == 'A':
        wl, wu = 1-1/SCALE, 1/(1-1/SCALE)
        j0 = wu*EDGE_GRAM*(wu+bounds.KAPPA_AH*RHO)*bmax
        j0x = wu*EDGE_GRAM*((wu+bounds.KAPPA_AH*RHO)*2
                           +(2*wu+bounds.KAPPA_AH*RHO)*bmax/SCALE)
        j0h = wu*bounds.KAPPA_AH*EDGE_GRAM*bmax
        row_x = 2+2*bmax/SCALE
        emax = eps*(2*C_HIGH+12*bmax**2+j0**2)/2
        emin = eps*C_LOW
        gl, gu = 1-emax, 1/(1+emin)
        require(gl > Q(1, 2) and -emin < 1, 'read floor/exp bound unresolved')
        qmax = max(abs((wl-gu)/(wl+gu)), abs((wu-gl)/(wu+gl)))
        ex = eps*(2+24*bmax*row_x+2*j0*j0x)/2
        eh = eps*j0*j0h
        # q=tanh((Y/scale + E)/2) on the certified inactive-floor chart.
        qx, qh = (1/SCALE+ex)/2, eh/2
        chi, zeta = PARAMS.chi_a, PARAMS.zeta_a
        theta = chi*zeta*qmax
        j = j0/(1-theta)
        jx = (j0x+chi*zeta*qx*j)/(1-theta)
        jh = (j0h+chi*zeta*qh*j)/(1-theta)
        causal = chi*qmax*j
        causal_x, causal_h = chi*(qx*j+qmax*jx), chi*(qh*j+qmax*jh)
        # Fresh-resource writer: rows use incoming W and the selected read J.
        advance = dt*DEGREE*j
        post_span = bmax+2*advance
        post_x, post_h = 1+dt*DEGREE*jx, dt*DEGREE*jh
        post_row_x, post_row_h = 2*post_x+2*post_span/SCALE, 2*post_h
        writer_emax = eps*(2*(C_HIGH+advance)+12*post_span**2+j**2)/2
        writer_emin = eps*(C_LOW-advance)
        require(1-writer_emax > Q(1, 2), 'writer floor bound unresolved')
        writer_ex = eps*(2*post_x+24*post_span*post_row_x+2*j*jx)/2
        writer_eh = eps*(2*post_h+24*post_span*post_row_h+2*j*jh)/2
        # 0 < 1-exp(-dt) < dt. In Y coordinates the increment is explicit.
        ax = max(dt*DEGREE*jx, dt*(1+SCALE*writer_ex))
        ah = max(dt*DEGREE*jh, dt*SCALE*writer_eh)
        my = dt*(1+SCALE*max(writer_emax, -writer_emin))
        mf = max(advance, my)
        extra = dict(read_exponent_upper=emax, writer_exponent_upper=writer_emax,
                     read_drive_upper=gu, weight_lower=wl, weight_upper=wu,
                     M_C=advance, M_Y=my)
    else:
        chi, zeta = PARAMS.chi_c, PARAMS.zeta_c
        t = 1/(1-bounds.KAPPA_M)
        tx = t*bounds.KAPPA_M  # mean has norm 1; |tanh'| <= 1 also for signed C
        response = 4*(1+RHO)/(1-RHO)  # sqrt(m)<=4, SPD similarity
        theta = chi*zeta*response
        j0 = t*EDGE_GRAM*(1+RHO)*bmax
        j0x = EDGE_GRAM*(1+RHO)*(2*t+tx*bmax)
        j0h = t*EDGE_GRAM*bmax
        rx = response**2*tx*(1+RHO)*EDGE_GRAM
        rh = response**2*t*EDGE_GRAM
        j = j0/(1-theta)
        jx = (j0x+chi*zeta*rx*j)/(1-theta)
        jh = (j0h+chi*zeta*rh*j)/(1-theta)
        # R J0=(R-I)b - R t(DH-HD)b. This avoids the much looser R*J0
        # value bound; R and (I-pR)^-1 commute. No simultaneous diagonalization
        # of H and D is assumed. ||DH-HD||inf <= 2*||D||inf*rho.
        causal = chi*response*(1+2*t*EDGE_GRAM*RHO)*bmax/(1-theta)
        causal_x = chi*(rx*j+response*jx)
        causal_h = chi*(rh*j+response*jh)
        ax, ah, mf = dt*DEGREE*jx, dt*DEGREE*jh, dt*DEGREE*j
        extra = dict(response_bound=response, modulation_upper=t, M_C=mf, M_Y=Q(0))
    require(0 <= theta < Q(1, 2), 'current inverse unresolved')
    v, vx = hinv*causal, hinv*causal_x
    vh = hinv*causal_h+hinv**2*causal
    ms = zeta*MASK_NORM*v**2
    bx, bh = 2*zeta*MASK_NORM*v*vx, 2*zeta*MASK_NORM*v*vh
    return dict(A_X=ax, A_H=ah, M_f=mf, M_S=ms, B_X=bx, B_H=bh,
                J=j, J_X=jx, J_H=jh, current_margin=1-theta, **extra)


def section_budgets(b, rho=RHO, lip=SECTION_LIP):
    require(rho > 0 and lip >= 0 and all(b[k] >= 0 for k in ('A_X', 'A_H', 'M_S', 'B_X', 'B_H')),
            'invalid section bounds')
    kh = bounds.KAPPA_H
    ell = b['A_X']+b['A_H']*lip
    require(ell < 1, 'completed inverse contraction unresolved')
    inv = 1/(1-ell)
    value = kh*b['M_S']
    image_lip = kh*(b['B_X']+b['B_H']*lip)*inv
    q = kh*(b['B_H']+(b['B_X']+b['B_H']*lip)*inv*b['A_H'])
    require(value < rho, 'section image escapes geometry ball')
    require(image_lip <= lip, 'section Lipschitz class not preserved')
    require(q < 1, 'graph transform contraction unresolved')
    return dict(ell=ell, inverse_lip=inv, value_radius=value, image_lip=image_lip, q_section=q)


def clipped(x, lower, upper):
    lo, hi = endpoint(x, 0), endpoint(x, 1)
    return IV.mpf([number(max(lower, min(upper, lo))).a,
                   number(max(lower, min(upper, hi))).b])


class AuxiliaryRows(IntervalRows):
    """Literal signed-C extension on positive W; no physical publication path."""
    def conductance(self, c, w, j):
        rows = self.rows(c, w)
        out = []
        for k, edge in enumerate(self.edges):
            u, v = self.index[edge['tail']['node_id']], self.index[edge['head']['node_id']]
            contrast = sum((x-y)**2 for x, y in zip(rows[u], rows[v]))
            exponent = number(self.params.coefficient)*(c[u]+c[v]+contrast+j[k]**2)/2
            drive = IV.exp(-exponent)
            # Global proof certifies this floor inactive even at signed C.
            # Negative E and G>1 are allowed here; do not clip them to 0/1.
            require(endpoint(drive, 0) > Q(1, 2), 'auxiliary floor inactivity unresolved')
            out.append(drive)
        return IV.matrix(out)

    def increment(self, candidate, x, h):
        n, m = len(self.nodes), len(self.edges)
        require(candidate in ('A', 'C') and x.rows == n+(m if candidate == 'A' else 0)
                and x.cols == 1, 'auxiliary state shape/candidate mismatch')
        c = IV.matrix([clipped(x[i], C_LOW, C_HIGH) for i in range(n)])
        y = IV.matrix([clipped(x[n+i], Y_LOW, Y_HIGH) for i in range(m)]) if candidate == 'A' else None
        w = IV.matrix([IV.exp(z/number(SCALE)) for z in y]) if y is not None else None
        read = self.read(candidate, c, w, h)
        dc = -number(bounds.DT)*self.B*read['J']
        if y is None:
            increment = dc
        else:
            drive = self.conductance(c+dc, w, read['J'])
            a = IV.exp(-number(bounds.DT))
            dy = [(1-a)*(number(SCALE)*IV.ln(g)-z) for g, z in zip(drive, y, strict=True)]
            increment = IV.matrix(list(dc)+dy)
        return increment, read['source']


def midpoint_vector(v):
    return vector([(endpoint(x, 0)+endpoint(x, 1))/2 for x in v])


def auxiliary(model):
    return AuxiliaryRows(physical.StagedRows(model.nodes, model.edges, PARAMS))


def state(candidate, c, w=None):
    return IV.matrix(list(c)+([number(SCALE)*IV.ln(x) for x in w] if candidate == 'A' else []))


def reference_inverse(model, candidate, target):
    """Certify inverse for Gamma_0=I, NOT a numerical RG section evaluator."""
    ax = global_bounds(candidate)['A_X']
    x = midpoint_vector(target)
    for iteration in range(1, 21):
        f, _ = model.increment(candidate, x, model.I)
        x = midpoint_vector(target-f)
        f, _ = model.increment(candidate, x, model.I)
        residual = infinity(x+f-target)
        error = residual/(1-ax)
        if error < INVERSE_ERROR:
            return x, error, residual, iteration
    raise ValueError('reference inverse did not meet the research error budget')


def assert_reference_inverse_certificate(model, candidate, target, point, error, residual):
    """RG-F2: re-evaluate every RETURNED coordinate before consuming its error.

    Adapted from the supplied independent review control. This certifies a
    Gamma_0=I query, not a numerical invariant-section evaluation.
    """
    expected = len(model.nodes)+(len(model.edges) if candidate == 'A' else 0)
    if candidate not in ('A', 'C') or any(
            getattr(v, 'rows', None) != expected or getattr(v, 'cols', None) != 1
            for v in (target, point)):
        raise AssertionError('reference inverse point/target shape mismatch')
    try:
        error, residual = Q(error), Q(residual)
    except (TypeError, ValueError, OverflowError) as exc:
        raise AssertionError('nonfinite or invalid inverse certificate scalar') from exc
    if not (0 <= residual and 0 <= error < INVERSE_ERROR):
        raise AssertionError('invalid inverse certificate bounds or query budget')
    for v in (target, point):
        for z in v:
            if endpoint(z, 0) > endpoint(z, 1):
                raise AssertionError('reversed inverse point/target enclosure')
    increment, _ = model.increment(candidate, point, model.I)
    if getattr(increment, 'rows', None) != expected or getattr(increment, 'cols', None) != 1:
        raise AssertionError('inverse increment shape mismatch')
    checked = infinity(point+increment-target)
    if residual < checked:
        raise AssertionError('inverse residual is not bound to the returned complete point')
    ax = global_bounds(candidate)['A_X']
    if error < checked/(1-ax):
        raise AssertionError('inverse error does not enclose the returned-point residual')
    return checked


def literal_signed_increment(model, candidate, evaluation_state, h):
    """RG-F1 oracle: unprojected signed law, never increment() or clipped().

    Reuses the reviewed read/conductance kernels, but independently assembles
    the continuity and fresh-C/selected-J log-history increments. This isolates
    completion binding; it is not an independent oracle for those kernels.
    """
    n, m = len(model.nodes), len(model.edges)
    expected = n+(m if candidate == 'A' else 0)
    if candidate not in ('A', 'C') or evaluation_state.rows != expected or evaluation_state.cols != 1:
        raise AssertionError('literal signed-law shape/candidate mismatch')
    c = IV.matrix([evaluation_state[i] for i in range(n)])
    y = IV.matrix([evaluation_state[n+i] for i in range(m)]) if candidate == 'A' else None
    w = IV.matrix([IV.exp(z/number(SCALE)) for z in y]) if y is not None else None
    read = model.read(candidate, c, w, h)
    dc = -number(bounds.DT)*model.B*read['J']
    if y is None:
        return dc, read['source']
    a = IV.exp(-number(bounds.DT))
    drive = model.conductance(c+dc, w, read['J'])
    dy = [(1-a)*(number(SCALE)*IV.ln(g)-z) for g, z in zip(drive, y, strict=True)]
    return IV.matrix(list(dc)+dy), read['source']


def assert_frozen_retraction_agreement(model, candidate, x, h):
    """Independently project to the FROZEN faces, not producer constants.

    Adapted from the supplied review control. Calling increment(PX, H) for the
    expected result would repeat, rather than detect, a wrong retraction.
    """
    projected = []
    for i, z in enumerate(x):
        lo, hi = (Q(-1), Q(5)) if i < len(model.nodes) else (Q(-1), Q(1))
        left = max(lo, min(hi, endpoint(z, 0)))
        right = max(lo, min(hi, endpoint(z, 1)))
        projected.append(IV.mpf([number(left).a, number(right).b]))
    expected_f, expected_s = literal_signed_increment(model, candidate, IV.matrix(projected), h)
    actual_f, actual_s = model.increment(candidate, x, h)
    for label, actual, expected in (('increment', actual_f, expected_f), ('source', actual_s, expected_s)):
        if (getattr(actual, 'rows', None), getattr(actual, 'cols', None)) != (expected.rows, expected.cols):
            raise AssertionError('completed increment/source shape mismatch')
        # Existing point-enclosure comparison allowance; not a solver tolerance.
        if infinity(actual-expected) >= Q(1, 10**50):
            raise AssertionError(f'completed {label} does not match the frozen argument-only retraction')


class RGCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        physical.RevisedRealizationBoundTests.setUpClass()
        cls.source, cls.target = physical.RevisedRealizationBoundTests.source, physical.RevisedRealizationBoundTests.target

    def test_signed_global_and_section_budgets(self):
        for model in (self.source, self.target):
            n, m = len(model.nodes), len(model.edges)
            self.assertEqual(m, n-1)
            seen = {model.nodes[0]}
            for _ in model.nodes:
                seen |= {end['node_id'] for e in model.edges
                         if e['tail']['node_id'] in seen or e['head']['node_id'] in seen
                         for end in (e['tail'], e['head'])}
            self.assertEqual(seen, set(model.nodes))
            self.assertLessEqual(infinity(model.B), DEGREE)
            self.assertLessEqual(infinity(model.D), EDGE_GRAM)
            self.assertLessEqual(max(sum(Q(float(x)) for x in row) for row in model.mask), MASK_NORM)
            self.assertLessEqual(len(model.edges), 16)
            self.assertGreater(Q(1, len(model.nodes)*(len(model.nodes)-1)), Q(1, 512))
        for candidate in ('A', 'C'):
            b = global_bounds(candidate)
            s = section_budgets(b)
            self.assertLess(s['ell'], Q(1, 20))
            self.assertLess(s['q_section'], Q(1, 200))
            self.assertLess(s['value_radius'], Q(1, 2**15))
            self.assertGreater(b['current_margin'], Q(999, 1000))
            # F(K_-) subset interior K, F^{-1}(K) subset U, including Y.
            self.assertLess(b['M_C'], Q(1, 4))
            self.assertLess(b['M_Y'], Q(1, 8))
        b = global_bounds('A')
        for changed, kw, message in (
                (dict(b, A_X=Q(1)), {}, 'inverse'),
                (dict(b, M_S=2*RHO), {}, 'image'),
                (b, dict(lip=Q(0)), 'Lipschitz')):
            with self.assertRaisesRegex(ValueError, message):
                section_budgets(changed, **kw)
        # Supplied exact boundary controls isolate the final contraction gate.
        synthetic = dict(A_X=Q(0), A_H=Q(0), M_S=Q(0), B_X=Q(0), B_H=Q(2))
        with self.assertRaisesRegex(ValueError, 'graph transform'):
            section_budgets(synthetic)  # q=1, earlier image-Lipschitz gate passes
        near = section_budgets(dict(synthetic, B_H=Q(2)-Q(1, 2**50)))
        self.assertEqual(near['q_section'], 1-Q(1, 2**51))
        equal = section_budgets(dict(synthetic, B_X=SECTION_LIP, B_H=Q(1)))
        self.assertEqual(equal['image_lip'], SECTION_LIP)
        self.assertEqual(equal['q_section'], Q(1, 2))

    def test_signed_extension_and_physical_agreement(self):
        for model in (self.source, self.target):
            aux, n, m = auxiliary(model), len(model.nodes), len(model.edges)
            c, w, j = vector([-1]*n), vector([1]*m), vector([0]*m)
            self.assertTrue(all(endpoint(g, 0) > 1 for g in aux.conductance(c, w, j)))
            with self.assertRaisesRegex(ValueError, 'physical inactive-floor'):
                model.conductance(c, w, j)
            c = vector([Q(2)+Q(i % 3, 64) for i in range(n)])
            w = vector([1-HISTORY_OFFSET]*m)
            for candidate in ('A', 'C'):
                history = w if candidate == 'A' else None
                x = state(candidate, c, history)
                f, s = aux.increment(candidate, x, model.I)
                r = model.read(candidate, c, history, model.I)
                after = c-number(bounds.DT)*model.B*r['J']
                wp = model.write(after, w, r['J']) if history is not None else None
                # Independent physical W writer vs auxiliary log-W increment.
                # This tiny point-evaluation allowance is not solver tolerance.
                self.assertLess(infinity(x+f-state(candidate, after, wp)), Q(1, 10**50))
                self.assertLess(infinity(s-r['source']), Q(1, 10**50))
                outside = vector([7]*n+([2]*m if candidate == 'A' else []))
                boundary = vector([C_HIGH]*n+([Y_HIGH]*m if candidate == 'A' else []))
                fo, so = aux.increment(candidate, outside, model.I)
                fb, sb = aux.increment(candidate, boundary, model.I)
                # Equal interval objects still have width on subtraction.
                self.assertEqual([z._mpi_ for z in fo], [z._mpi_ for z in fb])
                self.assertEqual([z._mpi_ for z in so], [z._mpi_ for z in sb])
                # Completion is X+f(PX), not a projection of the returned state.
                self.assertGreater(endpoint((outside+fo)[0], 0), C_HIGH)
            self.assertEqual(endpoint(clipped(number(-2), C_LOW, C_HIGH), 0), C_LOW)
            self.assertEqual(endpoint(clipped(number(6), C_LOW, C_HIGH), 1), C_HIGH)
            with self.assertRaisesRegex(ValueError, 'shape/candidate'):
                aux.increment('X', c, model.I)
            with self.assertRaisesRegex(ValueError, 'shape/candidate'):
                aux.increment('A', c, model.I)
        # Outward intervals must retain both endpoints across all four faces.
        for lo, hi in ((Q(-1), Q(5)), (Q(-1), Q(1))):
            for left, right in ((lo-2, lo-1), (lo-1, lo+Q(1, 2)), (lo, hi),
                                (hi-Q(1, 2), hi+1), (hi+1, hi+2), (lo-1, hi+1)):
                z = IV.mpf([number(left).a, number(right).b])
                result = clipped(z, lo, hi)
                self.assertEqual(endpoint(result, 0), max(lo, min(hi, left)))
                self.assertEqual(endpoint(result, 1), max(lo, min(hi, right)))

    def test_frozen_retraction_agreement_and_mutations(self):
        cases = []
        for graph, base in (('source', self.source), ('D52', self.target)):
            model, n, m = auxiliary(base), len(base.nodes), len(base.edges)
            h = model.I.copy()
            i, j = next((i, j) for i in range(m) for j in range(i+1, m) if model.mask[i, j])
            h[i, j] = h[j, i] = number(RHO/2)
            for candidate in ('A', 'C'):
                for kind, resources, history in (
                        ('signed_near_faces', [Q(-3, 4) if i % 2 == 0 else Q(19, 4) for i in range(n)],
                         [Q((-1)**i)*Q(7, 8) for i in range(m)]),
                        ('physical_near_faces', [Q(7, 4) if i % 2 == 0 else Q(19, 4) for i in range(n)],
                         [Q((-1)**i)*Q(7, 8) for i in range(m)]),
                        ('mixed_exterior', [Q(-2) if i % 3 == 0 else Q(6) if i % 3 == 1 else Q(2) for i in range(n)],
                         [Q((-1)**i)*2 for i in range(m)])):
                    x = vector(resources+(history if candidate == 'A' else []))
                    with self.subTest(graph=graph, candidate=candidate, kind=kind):
                        assert_frozen_retraction_agreement(model, candidate, x, h)
                    cases.append((graph, candidate, kind, model, x, h))
        self.assertEqual(len(cases), 12)

        original_increment, original_clip = AuxiliaryRows.increment, clipped
        for mutation in ('nonnegative_C', 'narrow_Y'):
            def changed_increment(model, candidate, x, h):
                def changed_clip(value, lo, hi):
                    if mutation == 'nonnegative_C' and (lo, hi) == (C_LOW, C_HIGH):
                        lo = Q(0)
                    if mutation == 'narrow_Y' and (lo, hi) == (Y_LOW, Y_HIGH):
                        lo, hi = Q(-5, 8), Q(5, 8)
                    return original_clip(value, lo, hi)
                # Change only the argument retraction in the real increment.
                # The independent expected projection never calls clipped().
                with patch(__name__+'.clipped', changed_clip):
                    return original_increment(model, candidate, x, h)

            rejected = 0
            with patch.object(AuxiliaryRows, 'increment', changed_increment):
                for graph, candidate, kind, model, x, h in cases:
                    if (mutation == 'narrow_Y' and candidate != 'A'
                            or mutation == 'nonnegative_C' and kind == 'physical_near_faces'):
                        continue
                    with self.subTest(mutation=mutation, graph=graph, candidate=candidate, kind=kind):
                        with self.assertRaisesRegex(AssertionError, 'frozen argument-only retraction'):
                            assert_frozen_retraction_agreement(model, candidate, x, h)
                    rejected += 1
            self.assertEqual(rejected, 6 if mutation == 'narrow_Y' else 8)

    def test_signed_inverse_and_no_resource_clipping(self):
        model, report = auxiliary(self.target), {}
        old = {e['edge_id'] for e in self.source.edges}
        for candidate in ('A', 'C'):
            b = global_bounds(candidate)
            s = section_budgets(b)
            # Compare the actual section inverse with Gamma_0=I. The extra
            # uncertainty is analytical, not a claim to have evaluated Gamma.
            section_shift = b['A_H']*s['value_radius']/(1-b['A_X'])
            for role, center in (('current', Q(3)), ('reset', Q(2))):
                c = vector([bounds.resources(model.nodes, center)[n] for n in model.nodes])
                w = vector([1-HISTORY_OFFSET if e['edge_id'] in old else 1 for e in model.edges])
                target = state(candidate, c, w)
                x, error, residual, iterations = reference_inverse(model, candidate, target)
                assert_reference_inverse_certificate(model, candidate, target, x, error, residual)
                total = error+section_shift
                core = model.index['core']
                self.assertLess(endpoint(x[core], 1)+total, 0)
                # K_- strictly contains the signed preimage and its uncertainty.
                self.assertTrue(all(endpoint(z, 0)-total > Q(-1, 4)
                                    and endpoint(z, 1)+total < Q(17, 4) for z in list(x)[:len(model.nodes)]))
                self.assertTrue(all(endpoint(z, 0)-total > Q(-5, 8)
                                    and endpoint(z, 1)+total < Q(5, 8) for z in list(x)[len(model.nodes):]))
                clipped_x = x.copy()
                for i in range(len(model.nodes)):
                    clipped_x[i] = clipped(x[i], Q(0), C_HIGH)
                f, _ = model.increment(candidate, clipped_x, model.I)
                bad = clipped_x+f-target
                # Lower bound, not an overestimating norm mistaken for failure.
                self.assertGreater(endpoint(bad[core], 0), INVERSE_ERROR)
                report[candidate+'_'+role] = dict(iterations=iterations, residual=float(residual),
                    inverse_error=float(error), section_inverse_shift=float(section_shift),
                    actual_section_inverse_core_upper=float(endpoint(x[core], 1)+total),
                    clipped_reference_residual_lower=float(endpoint(bad[core], 0)))
        type(self).inverse_report = report

    def test_reference_inverse_certificate_pressure(self):
        model = auxiliary(self.target)
        old = {e['edge_id'] for e in self.source.edges}
        for candidate in ('A', 'C'):
            for role, center in (('current', Q(3)), ('reset', Q(2))):
                c = vector([bounds.resources(model.nodes, center)[n] for n in model.nodes])
                w = vector([1-HISTORY_OFFSET if e['edge_id'] in old else 1 for e in model.edges])
                target = state(candidate, c, w)
                visited, increment = [], model.increment

                def capture(candidate, point, h):
                    visited.append(point.copy())
                    return increment(candidate, point, h)

                with patch.object(model, 'increment', side_effect=capture):
                    x, error, residual, _ = reference_inverse(model, candidate, target)
                self.assertGreaterEqual(len(visited), 2)
                self.assertEqual([z._mpi_ for z in x], [z._mpi_ for z in visited[-1]])
                checked = assert_reference_inverse_certificate(model, candidate, target, x, error, residual)
                self.assertEqual(checked, residual)
                stale = visited[-2]  # actual previous iterate, new residual/error
                tail = x.copy()
                tail[tail.rows-1] += number(8*INVERSE_ERROR)
                for mutation, point, e, r in (
                        ('stale_point', stale, error, residual),
                        ('zero_residual', x, error, Q(0)),
                        ('zero_error', x, Q(0), residual),
                        ('last_coordinate', tail, error, residual)):
                    with self.subTest(candidate=candidate, role=role, mutation=mutation):
                        with self.assertRaisesRegex(AssertionError, 'inverse (residual|error)'):
                            assert_reference_inverse_certificate(model, candidate, target, point, e, r)
                # Interval LOWER bound proves that this is a false certificate,
                # not just a wider recomputed residual or an acceptable iterate.
                f, _ = model.increment(candidate, stale, model.I)
                residual_lower = max(max(Q(0), endpoint(z, 0), -endpoint(z, 1)) for z in stale+f-target)
                self.assertGreater(residual_lower/(1+global_bounds(candidate)['A_X']), INVERSE_ERROR)

        # Pressure malformed scalars/shapes using the last genuine certificate.
        for e, r in ((Q(-1), residual), (INVERSE_ERROR, residual), (error, Q(-1)),
                     (float('nan'), residual), (error, float('inf'))):
            with self.assertRaises(AssertionError):
                assert_reference_inverse_certificate(model, candidate, target, x, e, r)
        for malformed in ([], vector([0]), IV.matrix([[0, 0]])):
            with self.assertRaisesRegex(AssertionError, 'shape'):
                assert_reference_inverse_certificate(model, candidate, target, malformed, error, residual)
            with self.assertRaisesRegex(AssertionError, 'shape'):
                assert_reference_inverse_certificate(model, candidate, malformed, x, error, residual)
        bad = x.copy()
        bad[bad.rows-1] = IV.mpf('inf')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            assert_reference_inverse_certificate(model, candidate, target, bad, error, residual)

    def test_inverse_consumer_rejects_false_certificates(self):
        # Protect the actual evidence-consuming path, not just a helper called
        # by new tests. Removing its returned-point validation must fail here.
        original = reference_inverse
        for mutation in ('stale_point', 'zero_residual', 'zero_error', 'last_coordinate'):
            def forged(model, candidate, target):
                visited, increment = [], model.increment

                def capture(candidate, point, h):
                    visited.append(point.copy())
                    return increment(candidate, point, h)

                with patch.object(model, 'increment', side_effect=capture):
                    x, error, residual, iterations = original(model, candidate, target)
                if mutation == 'stale_point':
                    x = visited[-2]
                elif mutation == 'zero_residual':
                    residual = Q(0)
                elif mutation == 'zero_error':
                    error = Q(0)
                else:
                    x = x.copy()
                    x[x.rows-1] += number(8*INVERSE_ERROR)
                return x, error, residual, iterations

            with self.subTest(mutation=mutation), patch(__name__+'.reference_inverse', forged):
                with self.assertRaisesRegex(AssertionError, 'inverse (residual|error)'):
                    self.test_signed_inverse_and_no_resource_clipping()

    def test_global_bounds_against_signed_chart_perturbations(self):
        # These controls pressure the analytic inequalities; finitely many
        # evaluations are not substituted for their uniform derivation.
        delta = Q(1, 2**16)
        for base in (self.source, self.target):
            model, n, m = auxiliary(base), len(base.nodes), len(base.edges)
            for candidate in ('A', 'C'):
                b = global_bounds(candidate)
                # Both signed and physical C; alternating near-boundary Y.
                x = vector([Q(-1, 2)+Q(i % 4) for i in range(n)]
                           +([Q((-1)**i, 2) for i in range(m)] if candidate == 'A' else []))
                f, s = model.increment(candidate, x, model.I)
                self.assertLess(infinity(f), b['M_f'])
                self.assertLess(infinity(s), b['M_S'])
                shifted = x+vector([delta*(-1)**i for i in range(x.rows)])
                fx, sx = model.increment(candidate, shifted, model.I)
                self.assertLess(infinity(fx-f), b['A_X']*delta)
                self.assertLess(infinity(sx-s), b['B_X']*delta)
                h = model.I.copy()
                i, j = next((i, j) for i in range(m) for j in range(i+1, m) if model.mask[i, j])
                h[i, j] = h[j, i] = number(delta)
                fh, sh = model.increment(candidate, x, h)
                self.assertLess(infinity(fh-f), b['A_H']*delta)
                self.assertLess(infinity(sh-s), b['B_H']*delta)

    def test_rg_uniform_geometry_continuation_both_roles(self):
        report = {}
        for candidate in ('A', 'C'):
            radius = section_budgets(global_bounds(candidate))['value_radius']
            for role, center in (('current', Q(3)), ('reset', Q(2))):
                src, dst = self.source, self.target
                desired = {n: center if n == 'source-s' else center+bounds.OUTSIDE_OFFSET for n in src.nodes}
                initial = bounds.preimage(src.edges, desired) if role == 'current' else desired
                c = vector([initial[n] for n in src.nodes], RESOURCE_RADIUS)
                w = vector([1-HISTORY_OFFSET]*len(src.edges), HISTORY_RADIUS) if candidate == 'A' else None
                records = []

                def admit(model, c, w, stage):
                    # Independent geometry-coordinate coverage is enforced by
                    # read_bounds. The RG theorem, NOT a CI solve/OS predictor,
                    # supplies this candidate's new global section-value bound.
                    r, budget = physical.read_bounds(model, candidate, c, w, radius=radius)
                    physical.assert_current_frobenius_aggregation(r['source'], budget['source_frobenius_squared'])
                    self.assertLess(budget['source_infinity'], global_bounds(candidate)['M_S'])
                    self.assertTrue(all(Q(-1, 4) < endpoint(x, 0) <= endpoint(x, 1) < Q(17, 4) for x in c))
                    if w is not None:
                        self.assertTrue(all(Q(-5, 8) < endpoint(number(SCALE)*IV.ln(x), 0)
                                            <= endpoint(number(SCALE)*IV.ln(x), 1) < Q(5, 8) for x in w))
                    records.append(dict(stage=stage, resource_lower=float(min(endpoint(x, 0) for x in c)),
                                        resource_upper=float(max(endpoint(x, 1) for x in c)),
                                        regularity=float(budget['regularity'])))
                    return r

                r = admit(src, c, w, 'source')
                if role == 'current':
                    c = c-number(bounds.DT)*src.B*r['J']
                    w = src.write(c, w, r['J']) if w is not None else None
                    admit(src, c, w, 'source_poststate')
                    row = src.rows(c, w if w is not None else vector([1]*len(src.edges)))[src.index['source-s']]
                    self.assertTrue(all(endpoint(x, 0) > 0 for x in row))
                    self.assertLess(sum(upper_abs(x)**2 for x in row), Q(1, 4))
                lineage = dict(zip((e['edge_id'] for e in src.edges), w, strict=True)) if w is not None else {}
                c = IV.matrix([c[src.index[n]] if n.startswith('outside-') else
                               c[src.index['source-s']]/3 if n.startswith('satellite/') else number(0)
                               for n in dst.nodes])
                w = IV.matrix([lineage.get(e['edge_id'], number(1)) for e in dst.edges]) if w is not None else None
                for k in range(bounds.HORIZON):
                    r = admit(dst, c, w, f'target_{k}')
                    c = c-number(bounds.DT)*dst.B*r['J']
                    w = dst.write(c, w, r['J']) if w is not None else None
                    self.assertGreater(min(endpoint(x, 0) for x in c), bounds.RESOURCE_MARGIN/2)
                    self.assertLess(max(endpoint(x, 1) for x in c), 4)
                admit(dst, c, w, f'target_{bounds.HORIZON}')
                report[candidate+'_'+role] = records
        type(self).continuation_report = report


if __name__ == '__main__':
    import sys
    reporting = '--report' in sys.argv
    if reporting:
        sys.argv.remove('--report')
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(json.dumps(dict(bounds={a: {k: float(v) for k, v in (global_bounds(a)|section_budgets(global_bounds(a))).items()}
                                      for a in ('A', 'C')},
                              inverse=getattr(RGCompletionTests, 'inverse_report', None),
                              continuation=getattr(RGCompletionTests, 'continuation_report', None)), indent=2))
    sys.exit(not result.result.wasSuccessful())
