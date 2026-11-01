"""Investigation-only quartic C_PC map and full C/Z contraction certificate.

FLINT exact graph constants; Arb enclosures at the caller's declared precision.
The carrier is a symmetric, star-supported bilinear form, with signed entries.
All independent carrier directions occur in the derivative; no Z=0 restriction.
"""
from fractions import Fraction as F
from functools import lru_cache
import json

from flint import arb, arb_mat, fmpq, ctx
from spark_completion_os_reference import COSReference
from spark_completion_positive import norm_upper
from spark_completion_continuation import bound, infnorm, need, geometric_roster, spectral_domain

TAU_PC = 32
CARRIER_RADIUS = F(1, 64)
TRAP_WEIGHT = 1024


@lru_cache(maxsize=8)
def _graph_constants(encoded):
    """Only exact immutable incidence/metric operands are cached, by full graph."""
    graph = json.loads(encoded)
    e = COSReference(graph, 'rational')
    inverse = (e.q(3, 4)*e.I + e.Le).inv()
    A = e.B*(e.I + inverse/4)*e.Bt
    pi = e.matrix([[e.q(1, e.n) for _ in range(e.n)] for _ in range(e.n)])
    P = (A + pi).inv()
    pack = lambda M: tuple(tuple(str(M[i, j]) for j in range(M.ncols())) for i in range(M.nrows()))
    return dict(A=pack(A), P=pack(P), reference_inverse=pack(inverse),
                inverse_norm=str(infnorm(inverse)), A_max=str(infnorm(A)),
                inverse_trace=str(sum(P[i, i] for i in range(e.n))-1))


def graph_constants(graph):
    return _graph_constants(json.dumps(graph, sort_keys=True, separators=(',', ':')))


def global_domain(graph):
    """Uniform read/source envelope on C in [0,4], ||Z||_F <= 1/64.

    H=I+Z/2 is symmetric positive definite. Euclidean/Frobenius bounds
    avoid assuming nonnegative carrier entries. M is similar to a symmetric
    positive matrix through H^(1/2), bounding its inverse by sqrt(cond(H))/0.75.
    """
    m = COSReference(graph, 'arb')
    R = m.q(1, 64)
    hmin, hmax = 1-R/2, 1+R/2
    ell = infnorm(m.Le).upper()
    # ||B^T C||_2 <= 4 sqrt(m); ||B^T V'(C)||_2 <= 12 sqrt(m).
    j0 = m.q(1, 1024)*arb(m.m).sqrt()*(ell*hmax/16 + 12)
    inverse = (hmax/hmin).sqrt()*m.q(4, 3)
    flat = inverse*j0/(2*hmin)
    # |O_ij/4| <= 1/2, hence ||S||_F <= ||f||_2^2/2.
    source = flat**2/2
    need(source < R, 'uniform carrier source envelope exceeds radius')
    spectrum = spectral_domain(graph)
    need(hmin*arb(fmpq(spectrum['nonconstant_eigenvalue_lower'])) > m.q(1, 64),
         'carrier geometry loses selector separation')
    return dict(resource_box=['0', '4'], carrier_radius=str(CARRIER_RADIUS),
                carrier_norm='symmetric_star_frobenius', signed_carriers=True,
                H_eigenvalue_lower=bound(hmin), H_eigenvalue_upper=bound(hmax),
                current_inverse_norm_upper=bound(inverse), source_norm_upper=bound(source),
                flat_norm_upper=bound(flat), selector=spectrum,
                invariant_carrier_ball=True, resource_box_invariance_claimed=False)


class CPCReference(COSReference):
    def __init__(self, graph):
        super().__init__(graph, 'arb')
        self.graph = graph
        self.precision = ctx.prec
        self.constants = graph_constants(graph)
        self.pairs = [(i, j) for i in range(self.m) for j in range(i, self.m) if self.overlap[i][j]]
        self.decay = (-self.q(32, TAU_PC)).exp()
        self.read_count = 0
        self.writer_count = 0

    def zero(self):
        return self.matrix(self.m, self.m)

    def source(self, flat):
        result = self.zero()
        for i, j in self.pairs:
            result[i, j] = self.q(self.overlap[i][j], 4)*flat[i, 0]*flat[j, 0]
            result[j, i] = result[i, j]
        return result

    def validate(self, C, Z):
        need(ctx.prec == self.precision, 'model precision changed; construct a fresh model')
        need(C.nrows() == self.n and C.ncols() == 1 and Z.nrows() == Z.ncols() == self.m,
             'physical state dimensions')
        need(all(C[i, 0] >= 0 and C[i, 0] <= 4 for i in range(self.n)), 'resource domain')
        need(all(Z[i, j].mid() == Z[j, i].mid() and Z[i, j].rad() == Z[j, i].rad()
                 for i in range(self.m) for j in range(i)), 'carrier enclosure symmetry')
        need(all(Z[i, j] == 0 for i in range(self.m) for j in range(self.m)
                 if not self.overlap[i][j]), 'carrier star support')
        need(norm_upper(Z) <= self.q(1, 64), 'carrier norm domain')

    def pc_read(self, C, Z):
        self.validate(C, Z)
        H = self.I + Z/2
        selected = self.read(C, H, eta=self.q(1, 1024))
        source = self.source(selected['causal_flat'])
        need(norm_upper(source) <= self.q(1, 64), 'carrier source envelope')
        self.read_count += 1
        return dict(geometry=H, selected=selected, source=source,
                    subject_C=self.matrix(C), subject_Z=self.matrix(Z))

    def advance(self, C, Z, read):
        # Reads may be reused only across the identical full (C,Z) enclosure.
        for value, saved in ((C, read['subject_C']), (Z, read['subject_Z'])):
            need(all(a.mid() == b.mid() and a.rad() == b.rad()
                     for a, b in zip(value.entries(), saved.entries())), 'stale physical read')
        after_C = C-self.q(32)*self.B*read['selected']['current']
        after_Z = self.decay*Z+(1-self.decay)*read['source']
        self.writer_count += 1
        return after_C, after_Z

    def pc_step(self, C, Z):
        read = self.pc_read(C, Z)
        C1, Z1 = self.advance(C, Z, read)
        return dict(read=read, after=C1, carrier_after=Z1)

    def partials(self, C, Z):
        """Blocks in C and a Frobenius-orthonormal symmetric star basis.

        Batch each matrix's right-hand sides into a single solve. Offdiagonal
        basis elements have entries 1/sqrt(2); output carrier coordinates use
        sqrt(2). Thus these columns cover the actual Frobenius geometry.
        """
        read = self.pc_read(C, Z)
        H = read['geometry']; flat = read['selected']['causal_flat']
        y = 2*H*flat; M = self.q(3, 4)*self.I+H*self.Le
        curvature = self.matrix([[(3*(C[i, 0]-2)**2-1) if i == j else 0
                                  for j in range(self.n)] for i in range(self.n)])
        jC = -self.q(1, 1024)*self.Bt*(self.q(1, 64)*self.B*H*self.Bt-curvature)
        yC = M.solve(jC); fC = H.solve(yC)/2; JC = jC+yC/4
        dH = []
        for i, j in self.pairs:
            basis = self.zero()
            basis[i, j] = self.q(1, 2) if i == j else 1/(2*arb(2).sqrt())
            basis[j, i] = basis[i, j]
            dH.append(basis)
        jZ = [-self.q(1, 1024*64)*self.Le*d*self.Bt*C for d in dH]
        pack = lambda cols: self.matrix([[col[i, 0] for col in cols] for i in range(self.m)])
        yZ = M.solve(pack([j-d*self.Le*y for j, d in zip(jZ, dH)]))
        fZ = H.solve(yZ/2-pack([d*flat for d in dH]))
        JZ = pack(jZ)+yZ/4
        def writer_derivative(df):
            return self.matrix([[(1 if i == j else arb(2).sqrt())*self.q(self.overlap[i][j], 4)*
                                 (flat[i, 0]*df[j, k]+flat[j, 0]*df[i, k])
                                 for k in range(df.ncols())] for i, j in self.pairs])
        SC, SZ = writer_derivative(fC), writer_derivative(fZ)
        In = self.matrix([[int(i == j) for j in range(self.n)] for i in range(self.n)])
        return dict(CC=In-32*self.B*JC, CZ=-32*self.B*JZ,
                    SC=SC, SZ=SZ, fC=fC, fZ=fZ, read=read)


def trap_certificate(target, predecessor):
    m = CPCReference(target['graph']); e = COSReference(target['graph'], 'rational')
    const = m.constants
    A, P = e.matrix(const['A']), e.matrix(const['P'])
    amax, trace = fmpq(const['A_max']), fmpq(const['inverse_trace'])
    need(str(amax) == predecessor['A_max'] and str(trace) == predecessor['inverse_trace'],
         'inherited exact metric changed')
    center = predecessor['center']; r = m.q(fmpq(predecessor['radius']))
    R = fmpq(predecessor['coordinate_radius']); zrad = r/TRAP_WEIGHT
    C = m.vector(center)
    box = m.matrix([[arb(fmpq(center[node]), R)] for node in m.nodes])
    Z = m.zero()
    for i, j in m.pairs:
        Z[i, j] = arb(0, zrad.fmpq())
        Z[j, i] = Z[i, j]
    # The coordinate enclosure includes the entire Frobenius ball. Extra
    # points only enlarge derivative bounds; they do not redefine the trap.
    partials = m.partials(box, Z)
    L = e.B*e.Bt
    D = e.matrix([[(3*(fmpq(center[m.nodes[i]])-2)**2-1 if i == j else 0)-L[i, j]/64
                   for j in range(m.n)] for i in range(m.n)])
    dmin = min(3*(fmpq(center[v])-2)**2-1 for v in m.nodes)-infnorm(L)/64
    dmax = max(3*(fmpq(center[v])-2)**2-1 for v in m.nodes)
    need(dmin > 0 and amax*dmax/32 < 2, 'reference contraction premise')
    q0 = max(1-dmin/(32*trace), amax*dmax/32-1)
    J0 = e.matrix([[int(i == j) for j in range(m.n)] for i in range(m.n)])-A*D/32
    a = arb(q0)+norm_upper(partials['CC']-arb_mat(J0))*(arb(amax)*arb(trace)).sqrt()
    b = norm_upper(partials['CZ'])*arb(trace).sqrt()
    c = (1-m.decay)*norm_upper(partials['SC'])*arb(amax).sqrt()
    d = m.decay+(1-m.decay)*norm_upper(partials['SZ'])
    q = max((a+b/TRAP_WEIGHT).upper(), (d+TRAP_WEIGHT*c).upper())
    step = m.pc_step(C, m.zero())
    defect_C = norm_upper(step['after']-C)*arb(trace).sqrt()
    defect_Z = norm_upper(step['carrier_after'])*TRAP_WEIGHT
    defect = max(defect_C.upper(), defect_Z.upper())
    margin = (1-q)*r-defect
    need(q < 1 and margin > 0, 'full C/Z trapping certificate failed')
    reference_margin = (1-a)*r-defect_C
    need(reference_margin > 0, 'reference stationary resource existence failed')
    rosters = {}
    for chi, t in target['charts'].items():
        chart = CPCReference(t['graph'])
        need(chart.nodes == m.nodes and chart.edges == m.edges, 'chiral numerical graph mismatch')
        rosters[chi] = geometric_roster(t['graph'], box, m.nodes)
        need(rosters[chi] == predecessor['complete_basins'], 'complete spatial basins changed')
    need(sum(F(v) for v in center.values()) == 21, 'center outside exact charge slice')
    return dict(center=center, carrier_center='zero', resource_radius=predecessor['radius'],
                coordinate_radius=str(R), carrier_radius=str(F(predecessor['radius'])/TRAP_WEIGHT),
                weight=TRAP_WEIGHT, norm='max(||delta_C||_P, weight*||delta_Z||_F)',
                metric='P=(A0+11^T/n)^-1 on exact charge-21 tangent space',
                A_max=str(amax), inverse_trace=str(trace), reference_contraction=str(q0),
                resource_dimension=m.n-1, carrier_dimension=len(m.pairs),
                full_dimension=m.n-1+len(m.pairs), independent_carrier_pairs=m.pairs,
                derivative_blocks={k:bound(v) for k,v in dict(CC=a,CZ=b,ZC=c,ZZ=d).items()},
                weighted_resource_row=bound(a+b/TRAP_WEIGHT), weighted_carrier_row=bound(d+TRAP_WEIGHT*c),
                full_contraction=bound(q), center_defect=bound(defect), strict_image_margin=bound(margin),
                reference_submap_margin=bound(reference_margin),
                complete_basins=rosters, full_physical_state=['C','Z_4'],
                nonzero_carrier_directions_included=True, stationary_carrier_argument=
                'At the unique exact reference equilibrium inside the trap, B^T Phi=0 implies J=f=S=0 and Z=0.',
                domain=global_domain(target['graph']), native_conformance=False), P
