"""C_CI quartic completion applicability, investigation only.

A root is a fixed point in causal-flat coordinates, not an OS corrector.
FLINT/Arb at an explicit precision; midpoint operations propose roots only.
Every returned read encloses the exact joint root for every input in C.
"""
from fractions import Fraction as F
from flint import arb, arb_mat, fmpq, ctx
from spark_completion_os_reference import COSReference
from spark_completion_positive import norm_upper
from spark_completion_continuation import infnorm, bound, need

ROOT_RADIUS = F(1,32)
ROOT_NEWTON_LIMIT = 16


def rational(x):
    return F(str(x))


def global_root_domain(graph):
    """Exact uniform Banach bounds for all C in [0,4]^V, for this graph."""
    m=COSReference(graph,'rational')
    L=rational(infnorm(m.Le)); b=rational(infnorm(m.B))
    a=rational(infnorm((m.q(3,4)*m.I+m.Le).inv()))
    S=F(max(sum(row) for row in m.overlap),8)
    r=ROOT_RADIUS; h=S*r*r
    need(h<1 and a*h*L<1,'Neumann inverse bounds unavailable')
    u=1/(1-h); inverse=a/(1-a*h*L)
    j0=F(2,1024)*(b*F(4,64)+6)+F(1,1024*64)*L*h*4
    y=inverse*j0; image=u*y/2
    H_lip=u*(inverse*(F(1,1024*64)*L*4+L*y)/2+image)
    contraction=H_lip*2*S*r
    need(image<r and contraction<1,'joint-root self-map/contraction not established')
    return dict(resource_box=['0','4'],causal_flat_radius=str(r),overlap_row_sum=str(S),
        edge_laplacian_norm=str(L),incidence_norm=str(b),reference_inverse_norm=str(a),
        hodge_deviation=str(h),hodge_inverse_norm=str(u),current_inverse_norm=str(inverse),
        current_baseline_bound=str(j0),y_bound=str(y),image_bound=str(image),
        geometry_to_flat_lipschitz=str(H_lip),contraction=str(contraction),
        uniqueness='one root in the declared flat ball; no global root uniqueness claim')


class CCIReference(COSReference):
    def __init__(self,graph):
        super().__init__(graph,'arb')
        self.domain=global_root_domain(graph)
        self.root_q=self.q(fmpq(self.domain['contraction']))
        self.r=self.q(1,32)

    def partials(self,C,f):
        """Partial derivatives at independent C,f, including both H consumers."""
        H=self.geometry(f);read=self.read(C,H,eta=self.q(1,1024))
        y=2*H*read['causal_flat'];M=self.q(3,4)*self.I+H*self.Le
        curvature=self.matrix([[(3*(C[i,0]-2)**2-1) if i==j else 0 for j in range(self.n)]for i in range(self.n)])
        jC=-self.q(1,1024)*self.Bt*(self.q(1,64)*self.B*H*self.Bt-curvature)
        yC=M.solve(jC); FC=H.solve(yC)/2; JC=jC+yC/4
        # One multi-RHS solve per inverse, algebraically the same partials.
        dHs=[];djcols=[];rhs=[]
        for k in range(self.m):
            dH=self.matrix([[self.q(self.overlap[i][j],8)*
                ((f[j,0] if i==k else 0)+(f[i,0] if j==k else 0))
                for j in range(self.m)]for i in range(self.m)])
            dj=-self.q(1,1024*64)*self.Le*dH*self.Bt*C
            dHs.append(dH);djcols.append(dj);rhs.append(dj-dH*self.Le*y)
        pack=lambda cols:self.matrix([[cols[j][i,0]for j in range(self.m)]for i in range(self.m)])
        dy=M.solve(pack(rhs))
        dHf=pack([dH*read['causal_flat']for dH in dHs])
        ff=H.solve(dy/2-dHf)
        jf=pack(djcols)+dy/4
        return read,ff,FC,jf,JC

    def root(self,C):
        need(all(C[i,0]>=0 and C[i,0]<=4 for i in range(self.n)), 'C outside declared root domain')
        proposal_C=self.matrix([[C[i,0].mid()]for i in range(self.n)])
        f=self.matrix([[0]for _ in range(self.m)])
        threshold=arb(2)**(-ctx.prec+64)
        for iteration in range(ROOT_NEWTON_LIMIT):
            read,df,_,_,_=self.partials(proposal_C,f)
            residual=read['causal_flat']-f
            if infnorm(residual)<threshold:
                break
            delta=(self.I-df).solve(residual)
            f=self.matrix([[(f[i,0]+delta[i,0]).mid()]for i in range(self.m)])
            need(infnorm(f)<self.r,'root proposal outside selected domain')
        else:
            raise ValueError('explicit root-proposal iteration limit reached')
        # Banach a-posteriori estimate on the actual input enclosure, not its midpoint.
        read=self.read(C,self.geometry(f),eta=self.q(1,1024))
        residual=infnorm(read['causal_flat']-f)
        error=(residual/(1-self.root_q)).upper()
        need(infnorm(f)+error<self.r,'root enclosure leaves selected domain')
        enclosed=self.matrix([[arb(f[i,0].fmpq(),error.fmpq())]for i in range(self.m)])
        H=self.geometry(enclosed);selected=self.read(C,H,eta=self.q(1,1024))
        return dict(flat=enclosed,geometry=H,selected=selected,error=error,
            residual=residual,proposal=f,iterations=iteration+1)

    def ci_step(self,C):
        root=self.root(C)
        return dict(root=root,after=C-self.q(32)*self.B*root['selected']['current'])

    def full_jacobian(self,C,root=None):
        root=self.root(C) if root is None else root
        _,Ff,FC,Jf,JC=self.partials(C,root['flat'])
        df=(self.I-Ff).solve(FC)
        In=self.matrix([[int(i==j)for j in range(self.n)]for i in range(self.n)])
        return In-self.q(32)*self.B*(JC+Jf*df),Ff


def trap_certificate(target,os_proof):
    """Fresh full CI derivative/center check on the previously declared metric ball."""
    from math import ceil
    from spark_completion_continuation import geometric_roster, spectral_domain
    m=CCIReference(target['graph']);e=COSReference(target['graph'],'rational');n=m.n
    center=os_proof['center'];r=m.q(fmpq(os_proof['radius']))
    A=e.B*(e.I+(e.q(3,4)*e.I+e.Le).inv()/4)*e.Bt
    pi=e.matrix([[e.q(1,n)for j in range(n)]for i in range(n)])
    P=(A+pi).inv();trace=sum(P[i,i]for i in range(n))-1;amax=infnorm(A);amin=1/trace
    need(str(amax)==os_proof['A_max'] and str(trace)==os_proof['inverse_trace'],'reference metric mismatch')
    R=F(ceil(F(str((arb(amax).sqrt()*r).upper().fmpq()))*2**80),2**80)
    need(str(R)==os_proof['coordinate_radius'],'changed ball enclosure')
    C=m.vector(center);box=m.matrix([[arb(fmpq(center[node]),fmpq(str(R)))]for node in m.nodes])
    L=e.B*e.Bt
    D=e.matrix([[(3*(fmpq(center[m.nodes[i]])-2)**2-1 if i==j else 0)-L[i,j]/64
                  for j in range(n)]for i in range(n)])
    dmin=min(3*(fmpq(center[v])-2)**2-1 for v in m.nodes)-infnorm(L)/64
    dmax=max(3*(fmpq(center[v])-2)**2-1 for v in m.nodes)
    need(dmin>0 and amax*dmax/32<2,'reference metric contraction unavailable')
    q0=max(1-amin*dmin/32,amax*dmax/32-1)
    J0=e.matrix([[int(i==j)for j in range(n)]for i in range(n)])-A*D/32
    root=m.root(box);J,Ff=m.full_jacobian(box,root)
    need(infnorm(Ff)<m.root_q,'actual root derivative outside uniform bound')
    perturb=norm_upper(J-arb_mat(J0))*(arb(amax)*arb(trace)).sqrt()
    q=arb(q0)+perturb
    center_step=m.ci_step(C);defect=norm_upper(center_step['after']-C)*arb(trace).sqrt()
    margin=(1-q)*r-defect
    need(q<1 and margin>0,'full CI trapping not established')
    need(all(sum(J[i,j]for i in range(n)).contains(arb(1))for j in range(n)), 'full derivative charge identity')
    rosters={}
    for chi,t in target['charts'].items():
        need([(z['tail']['node_id'],z['head']['node_id'])for z in t['graph']['edges']]==m.edges,
             'chiral incidence differs')
        rosters[chi]=geometric_roster(t['graph'],box,m.nodes)
        need(rosters[chi]==os_proof['complete_basins'],'complete trap domains differ')
    return dict(center=center,radius=os_proof['radius'],coordinate_radius=str(R),
        metric='(A0 + 11^T/n)^-1 on exact charge-21 tangent space',relative_dimension=n-1,
        A_max=str(amax),inverse_trace=str(trace),reference_contraction=str(q0),
        full_CI_derivative_perturbation=bound(perturb),full_CI_contraction=bound(q),
        center_defect=bound(defect),strict_image_margin=bound(margin),
        root_domain=m.domain,actual_root_derivative_upper=bound(infnorm(Ff).upper()),
        complete_basins=rosters,selector_domain=spectral_domain(target['graph']),
        same_ball_as_OS=True,OS_trajectory_entry_reused=False,full_physical_state=['C'],
        native_conformance=False),P
