"""SC-2 full exact-equation C_OS reference on the kappa_M=0 unit slice.

Investigation only: the homogeneous quartic site binding is not native authority.
FLINT rationals or explicitly selected Arb balls; no precision/fallback switching.
The generated Hodge enters BOTH the corrector potential and physical Read-Back.
"""
from flint import arb, arb_mat, fmpq, fmpq_mat


class COSReference:
    def __init__(self, graph, backend):
        if backend not in ('rational', 'arb'):
            raise ValueError('explicit rational or arb backend required')
        self.scalar = fmpq if backend == 'rational' else arb
        self.matrix = fmpq_mat if backend == 'rational' else arb_mat
        self.nodes = graph['live_node_ids']
        self.edges = [(e['tail']['node_id'],e['head']['node_id']) for e in graph['edges']]
        if any(a == b for a,b in self.edges):
            raise ValueError('this unit-pairing reference requires loop-free graphs')
        self.n,self.m = len(self.nodes),len(self.edges)
        self.B = self.matrix([[(i==a)-(i==b) for a,b in self.edges] for i in self.nodes])
        self.Bt = self.B.transpose()
        self.Le = self.Bt*self.B
        self.I = self.matrix([[int(i==j) for j in range(self.m)] for i in range(self.m)])
        self.overlap = [[sum(v in e and v in f for v in self.nodes) for f in self.edges]
                        for e in self.edges]

    def q(self, numerator, denominator=1):
        return self.scalar(fmpq(numerator,denominator))

    def vector(self, values):
        return self.matrix([[self.scalar(fmpq(values[v]))] for v in self.nodes])

    def site(self, C):
        return self.matrix([[(C[i,0]-2)**3-(C[i,0]-2)] for i in range(self.n)])

    def read(self, C, H, eta=None):
        eta = self.q(1) if eta is None else eta
        phi = self.q(1,64)*self.B*H*self.Bt*C-self.site(C)
        j0 = -eta*self.Bt*phi
        # R_phys=(I+H B^T B)^-1; y=R_phys J. This direct solve is
        # algebraically identical to the full physical similarity closure.
        y = (self.q(3,4)*self.I+H*self.Le).solve(j0)
        J = j0+self.q(1,4)*y
        flat = self.q(1,2)*H.solve(y)
        return dict(potential=phi,baseline=j0,current=J,causal_flat=flat)

    def geometry(self, flat):
        # kappa_H*zeta=1/4; star overlap is count/2 on loop-free graphs.
        return self.I+self.matrix([[self.q(self.overlap[i][j],8)*flat[i,0]*flat[j,0]
                                   for j in range(self.m)] for i in range(self.m)])

    def step(self, C, *, eta=None, dt=None):
        dt = self.q(1,32) if dt is None else dt
        predictor = self.read(C,self.I,eta)
        H = self.geometry(predictor['causal_flat'])
        corrector = self.read(C,H,eta)
        regenerated = self.geometry(corrector['causal_flat'])
        defect = H-regenerated
        after = C-dt*self.B*corrector['current']
        return dict(predictor=predictor,geometry=H,corrector=corrector,
                    regenerated=regenerated,defect=defect,after=after)

    def direct_similarity_read(self, C, H, eta=None):
        """Separate literal resolvent/similarity route for exact cross-checks."""
        eta = self.q(1) if eta is None else eta
        ih = H.inv()
        retained = (self.I+self.Le*H).inv()
        physical = H*retained*ih
        phi = self.q(1,64)*self.B*H*self.Bt*C-self.site(C)
        j0 = -eta*self.Bt*phi
        J = (self.I-self.q(1,4)*physical).solve(j0)
        return J,self.q(1,2)*retained*ih*J
