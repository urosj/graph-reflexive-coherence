"""C_CI_PC quartic research: one selected root, immediate geometry and held writer.

Only midpoint root proposals use a precision ladder. Every physical state and
final residual certificate uses the caller's fixed Arb precision. No native API.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import isqrt
import json
from flint import arb, arb_mat, fmpq, ctx
from spark_completion_os_reference import COSReference
from spark_completion_pc import CPCReference, graph_constants, _graph_constants, TAU_PC, TRAP_WEIGHT
from spark_completion_positive import norm_upper
from spark_completion_continuation import bound, infnorm, need, geometric_roster, spectral_domain

CARRIER_RADIUS = F(1,128)
ROOT_RADIUS = F(1,32)
ROOT_NEWTON_LIMIT = 16


@lru_cache(maxsize=8)
def _root_domain(encoded):
    graph=json.loads(encoded); m=COSReference(graph,'rational')
    const=graph_constants(graph)
    L=F(str(infnorm(m.Le))); b=F(str(infnorm(m.B))); a=F(const['inverse_norm'])
    s=F(max(sum(row) for row in m.overlap),8); r=ROOT_RADIUS
    # ||Z||_infinity <= sqrt(m)||Z||_F, rounded upward exactly.
    z=F(isqrt(m.m-1)+1)*CARRIER_RADIUS/2
    h=z+s*r*r
    need(h<1 and a*h*L<1,'composite Neumann inverse bounds unavailable')
    u=1/(1-h); inverse=a/(1-a*h*L)
    j=F(2,1024)*(b*F(4,64)+6)+F(1,1024*64)*L*h*4
    y=inverse*j; image=u*y/2
    lip=u*(inverse*(F(1,1024*64)*L*4+L*y)/2+image)
    contraction=lip*2*s*r
    source=F(m.m,2)*image**2
    need(image<r and contraction<1 and source<CARRIER_RADIUS,'composite root/writer domain unavailable')
    spectrum=spectral_domain(graph)
    hmin=1-CARRIER_RADIUS/2
    need(hmin*F(spectrum['nonconstant_eigenvalue_lower'])>F(1,64),'selector separation')
    return dict(resource_box=['0','4'],carrier_radius=str(CARRIER_RADIUS),
        carrier_norm='symmetric_star_frobenius',signed_carriers=True,
        causal_flat_radius=str(r),overlap_row_sum=str(s),edge_laplacian_norm=str(L),
        incidence_norm=str(b),reference_inverse_norm=str(a),carrier_hodge_deviation=str(z),
        hodge_deviation=str(h),hodge_inverse_norm=str(u),current_inverse_norm=str(inverse),
        image_bound=str(image),geometry_to_flat_lipschitz=str(lip),contraction=str(contraction),
        source_norm_upper=str(source),H_eigenvalue_lower=str(hmin),
        H_eigenvalue_upper=str(1+CARRIER_RADIUS/2+F(m.m,4)*r*r),selector=spectrum,
        invariant_carrier_ball=True,resource_box_invariance_claimed=False,
        uniqueness='one root in the declared flat ball; no global root uniqueness claim',
        stationary_composite_gain=2)


def global_domain(graph):
    return dict(_root_domain(json.dumps(graph,sort_keys=True,separators=(',',':'))))


class CCIPCReference(CPCReference):
    def __init__(self,graph,*,proposal_policy='precision_ladder'):
        super().__init__(graph)
        need(proposal_policy in ('precision_ladder','full_precision'),'unknown proposal policy')
        self.proposal_policy=proposal_policy
        self.domain=global_domain(graph)
        self.root_q=self.q(fmpq(self.domain['contraction']));self.r=self.q(fmpq(str(ROOT_RADIUS)))
        self.newton_iterations=0;self.proposal_bit_work=0

    def validate(self,C,Z):
        super().validate(C,Z)
        need(norm_upper(Z)<=self.q(fmpq(str(CARRIER_RADIUS))),'composite carrier norm domain')

    def geometry_with_history(self,f,Z):
        return self.I+(Z+self.source(f))/2

    def _root_partials(self,C,Z,f,*,full=False):
        """Independent C/Z/f partials; every derivative includes both H consumers."""
        H=self.geometry_with_history(f,Z);read=self.read(C,H,eta=self.q(1,1024))
        flat=read['causal_flat']; y=2*H*flat; M=self.q(3,4)*self.I+H*self.Le
        dHs=[]
        for k in range(self.m):
            dHs.append(self.matrix([[self.q(self.overlap[i][j],8)*
                ((f[j,0] if i==k else 0)+(f[i,0] if j==k else 0))
                for j in range(self.m)] for i in range(self.m)]))
        if full:
            for i,j in self.pairs:
                d=self.zero();d[i,j]=self.q(1,2) if i==j else 1/(2*arb(2).sqrt());d[j,i]=d[i,j]
                dHs.append(d)
        pack=lambda cols:self.matrix([[col[i,0] for col in cols] for i in range(self.m)])
        dj=[-self.q(1,1024*64)*self.Le*d*self.Bt*C for d in dHs]
        rhs=[j-d*self.Le*y for j,d in zip(dj,dHs)]
        if full:
            curvature=self.matrix([[(3*(C[i,0]-2)**2-1) if i==j else 0
                for j in range(self.n)] for i in range(self.n)])
            jC=-self.q(1,1024)*self.Bt*(self.q(1,64)*self.B*H*self.Bt-curvature)
            for k in range(self.n):
                col=self.matrix([[jC[i,k]] for i in range(self.m)]);dj.append(col);rhs.append(col)
        dy=M.solve(pack(rhs)); dhf=[d*flat for d in dHs]
        if full: dhf += [self.matrix(self.m,1) for _ in range(self.n)]
        df=H.solve(dy/2-pack(dhf)); dJ=pack(dj)+dy/4
        block=lambda A,start,count:self.matrix([[A[i,j] for j in range(start,start+count)]for i in range(self.m)])
        out=dict(read=read,Ff=block(df,0,self.m),Jf=block(dJ,0,self.m))
        if full:
            z=len(self.pairs)
            out.update(FZ=block(df,self.m,z),JZ=block(dJ,self.m,z),
                       FC=block(df,self.m+z,self.n),JC=block(dJ,self.m+z,self.n))
        return out

    def root(self,C,Z):
        self.validate(C,Z)
        point=lambda A:self.matrix([[A[i,j].mid() for j in range(A.ncols())] for i in range(A.nrows())])
        proposal_C,proposal_Z=point(C),point(Z);f=self.matrix(self.m,1)
        stages=[];bits=min(128,self.precision)
        if self.proposal_policy=='full_precision': stages=[self.precision]
        else:
            while bits<self.precision: stages.append(bits);bits=min(2*bits,self.precision)
            stages.append(self.precision)
        iterations=0;work=0
        for bits in stages:
            with ctx.workprec(bits):
                threshold=arb(2)**(-bits+32)
                for iteration in range(ROOT_NEWTON_LIMIT):
                    p=self._root_partials(proposal_C,proposal_Z,f)
                    residual=p['read']['causal_flat']-f
                    iterations+=1;work+=bits
                    if infnorm(residual)<threshold: break
                    delta=(self.I-p['Ff']).solve(residual)
                    f=point(f+delta)
                    need(infnorm(f)<self.r,'composite root proposal outside selected domain')
                else: raise ValueError('explicit composite root-proposal iteration limit reached')
        # Whole input enclosure, at fixed physical precision. The midpoint is
        # merely a proposal; Banach bounds certify the true root for every C/Z.
        read=self.read(C,self.geometry_with_history(f,Z),eta=self.q(1,1024))
        residual=infnorm(read['causal_flat']-f);error=(residual/(1-self.root_q)).upper()
        need(infnorm(f)+error<self.r,'composite root enclosure leaves selected domain')
        enclosed=self.matrix([[arb(f[i,0].fmpq(),error.fmpq())]for i in range(self.m)])
        source=self.source(enclosed);H=self.I+(Z+source)/2
        selected=self.read(C,H,eta=self.q(1,1024))
        need(norm_upper(source)<self.q(fmpq(str(CARRIER_RADIUS))),'composite source envelope')
        self.newton_iterations+=iterations;self.proposal_bit_work+=work
        return dict(flat=enclosed,geometry=H,selected=selected,source=source,
                    error=error,residual=residual,proposal=f,iterations=iterations,
                    proposal_bit_work=work,proposal_stages=stages)

    def ccipc_read(self,C,Z):
        root=self.root(C,Z);self.read_count+=1
        return dict(**root,subject_C=self.matrix(C),subject_Z=self.matrix(Z))

    # Inherit only same-subject continuity and the exact exponential held-source
    # writer. Geometry and root selection above are the composite realization.
    pc_read=ccipc_read

    def ccipc_step(self,C,Z):
        read=self.ccipc_read(C,Z);C1,Z1=self.advance(C,Z,read)
        return dict(read=read,after=C1,carrier_after=Z1)

    def partials(self,C,Z):
        root=self.ccipc_read(C,Z);p=self._root_partials(C,Z,root['flat'],full=True)
        cols=self.matrix([[p['FC'][i,j] for j in range(self.n)]+
                          [p['FZ'][i,j] for j in range(len(self.pairs))]for i in range(self.m)])
        implicit=(self.I-p['Ff']).solve(cols)
        fC=self.matrix([[implicit[i,j]for j in range(self.n)]for i in range(self.m)])
        fZ=self.matrix([[implicit[i,self.n+j]for j in range(len(self.pairs))]for i in range(self.m)])
        JC=p['JC']+p['Jf']*fC;JZ=p['JZ']+p['Jf']*fZ;flat=root['flat']
        def writer(df):
            return self.matrix([[(1 if i==j else arb(2).sqrt())*self.q(self.overlap[i][j],4)*
                (flat[i,0]*df[j,k]+flat[j,0]*df[i,k]) for k in range(df.ncols())]for i,j in self.pairs])
        In=self.matrix([[int(i==j)for j in range(self.n)]for i in range(self.n)])
        return dict(CC=In-32*self.B*JC,CZ=-32*self.B*JZ,SC=writer(fC),SZ=writer(fZ),
                    fC=fC,fZ=fZ,root_derivative=p['Ff'],read=root)

def trap_certificate(target, predecessor):
    m = CCIPCReference(target['graph']); e = COSReference(target['graph'], 'rational')
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
    step = m.ccipc_step(C, m.zero())
    defect_C = norm_upper(step['after']-C)*arb(trace).sqrt()
    defect_Z = norm_upper(step['carrier_after'])*TRAP_WEIGHT
    defect = max(defect_C.upper(), defect_Z.upper())
    margin = (1-q)*r-defect
    need(q < 1 and margin > 0, 'full C/Z trapping certificate failed')
    reference_D = m.matrix([[(3*(box[i,0]-2)**2-1) if i == j else 0
                             for j in range(m.n)] for i in range(m.n)])-arb_mat(L)/64
    reference_J = m.matrix([[int(i==j)for j in range(m.n)]for i in range(m.n)])-arb_mat(A)*reference_D/32
    reference_q = arb(q0)+norm_upper(reference_J-arb_mat(J0))*(arb(amax)*arb(trace)).sqrt()
    reference_read = m.read(C,m.I,eta=m.q(1,1024))
    reference_defect = norm_upper(32*m.B*reference_read['current'])*arb(trace).sqrt()
    reference_margin = (1-reference_q)*r-reference_defect
    need(reference_margin > 0, 'reference stationary resource existence failed')
    rosters = {}
    for chi, t in target['charts'].items():
        chart = CCIPCReference(t['graph'])
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
                domain=global_domain(target['graph']), stationary_composite_gain=2,
                actual_root_derivative_upper=bound(infnorm(partials['root_derivative']).upper()),
                same_selected_source_for_geometry_and_writer=True, native_conformance=False), P
