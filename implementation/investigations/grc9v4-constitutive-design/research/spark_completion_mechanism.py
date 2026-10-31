"""Exact checks of the SC-2 proposed site mechanism; no native model execution.

The analytic proof is SparkCompletionSC2MechanismAnalysis.md. These identities
and rational bounds neither execute an event nor provide a numerical OS
trapping radius. No potential is registered in the substrate.
"""
from fractions import Fraction as F
from itertools import combinations

NODES = ('p','x','y','m','a','b','d','f','e','g')
EDGES = (('p','a'),('p','b'),('p','m'),('x','d'),('x','f'),('x','m'),
         ('y','e'),('y','g'),('y','m'))


def matmul(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def transpose(a):
    return list(map(list,zip(*a)))


def inverse(a):
    n=len(a)
    rows=[list(row)+[F(i==j) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        pivot=next(i for i in range(k,n) if rows[i][k])
        rows[k],rows[pivot]=rows[pivot],rows[k]
        d=rows[k][k];rows[k]=[x/d for x in rows[k]]
        for i in range(n):
            if i!=k:
                d=rows[i][k];rows[i]=[x-d*y for x,y in zip(rows[i],rows[k])]
    return [row[n:] for row in rows]


def positive(a):
    """Exact symmetric elimination, not a floating eigenvalue decision."""
    n=len(a);a=[list(row) for row in a]
    assert a==transpose(a)
    for k in range(n):
        assert a[k][k]>0
        for i in range(k+1,n):
            for j in range(k+1,n):
                a[i][j]-=a[i][k]*a[k][j]/a[k][k]
    return True


def incidence(nodes,edges):
    return [[F((i==a)-(i==b)) for a,b in edges] for i in nodes]


def bounds(kappa=F(1,64),radius=F(1,8),forcing=F(6)):
    # c0=2, a=mu=1; ||L||inf=6, forcing=||L C0||inf, ||P||inf=9/5.
    p=F(9,5)
    image=kappa*(forcing+6*radius)/2+p*(3*radius**2+radius**3)/2
    q=3*kappa+p*(6*radius+3*radius**2)/2
    return image,q


def checks():
    n=len(NODES);m=len(EDGES)
    ports={v:[] for v in NODES};port_edges=[]
    for u,v in EDGES:
        pu,pv=1+3*len(ports[u]),1+3*len(ports[v])
        ports[u].append(pu);ports[v].append(pv)
        assert pu<=9 and pv<=9
        port_edges.append([u,pu,v,pv])
    assert all(ports[v]==[1,4,7] for v in ('p','x','y','m'))
    b=incidence(NODES,EDGES);bt=transpose(b);lap=matmul(b,bt)
    sig=[F(1) if v in ('p','x','y') else F(-1) for v in NODES]
    c0=[2+x for x in sig]
    apply=lambda a,x:[row[0] for row in matmul(a,[[v] for v in x])]
    assert sum(c0)==16
    assert max(sum(abs(v) for v in row) for row in lap)==6
    assert max(abs(v) for v in apply(lap,c0))==6
    distances={}
    adjacent={v:{w for a,z in EDGES for w in ([z] if a==v else [a] if z==v else [])} for v in NODES}
    for root in NODES:
        dist={root:0};todo=[root]
        for v in todo:
            for w in adjacent[v]-dist.keys():
                dist[w]=dist[v]+1;todo.append(w)
        assert len(dist)==n
        distances[root]=dist
    diameter=max(v for row in distances.values() for v in row.values())
    assert diameter==4

    r=F(1,8);kappa=F(1,64);image,q=bounds(kappa,r)
    assert image==F(99,1024) and r-image==F(29,1024) and q==F(489,640)
    assert image<r and q<1
    assert not (bounds(F(1))[0]<r and bounds(F(1))[1]<1)
    def vprime(c):
        z=c-2
        return z**3-z
    assert all(vprime(c)==0 for c in c0)
    assert any(kappa*x for x in apply(lap,c0))  # C0 is NOT the coupled equilibrium.
    def equilibrium_map(y):
        nonlinear=[3*s*x*x+x**3 for s,x in zip(sig,y)]
        average=sum(nonlinear)/n
        lc=apply(lap,[c+x for c,x in zip(c0,y)])
        return [kappa*z/2-(v-average)/2 for z,v in zip(lc,nonlinear)]
    for i in range(n-1):
        y=[F(0)]*n;y[i]=r;y[-1]=-r
        out=equilibrium_map(y)
        assert sum(out)==0 and max(map(abs,out))<=image
    # This finite pressure checks implementation identities; the uniform
    # polynomial/mean-value inequalities in the note prove the whole box.
    local_slacks=dict(resource_minimum=F(7,8),gradient_square=16-3*F(9,4)**2,
                      signed_hessian=F(7,4)-F(1,4),neighbor_barrier=F(7,4)-F(1,2))
    assert local_slacks['gradient_square']==F(13,16)
    assert min(local_slacks.values())>0

    # Actual reference C read law at the declared control slice: beta=1/4,
    # tau=1, unit pairings and transport. Retained deformation is off.
    eye=[[F(i==j) for j in range(m)] for i in range(m)]
    edge_lap=matmul(bt,b)
    resolvent=inverse([[eye[i][j]+edge_lap[i][j] for j in range(m)] for i in range(m)])
    block=[[eye[i][j]-F(1,4)*resolvent[i][j] for j in range(m)] for i in range(m)]
    assert positive(block)
    mobility=matmul(matmul(b,inverse(block)),bt)
    assert mobility==transpose(mobility) and all(sum(row)==0 for row in mobility)
    e=[[F(i==j)-F(i==n-1) for j in range(n-1)] for i in range(n)]
    project=[[F(i==j)-F(1,n) for j in range(n)] for i in range(n)]
    amin=F(2,(n-1)*diameter);amax=F(8)
    for matrix in (
        [[mobility[i][j]-amin*project[i][j] for j in range(n)] for i in range(n)],
        [[amax*project[i][j]-mobility[i][j] for j in range(n)] for i in range(n)]):
        assert positive(matmul(matmul(transpose(e),matrix),e))
    dmin=3*(1-r)**2-1-6*kappa;dmax=3*(1+r)**2-1
    h=F(1,32)
    assert dmin==F(77,64) and dmax==F(179,64)
    assert h*amax*dmax==F(179,256)<1
    derivative_bound=1-h*amin*dmin
    assert derivative_bound==F(36787,36864)<1
    # Review corollary: same global law and charge, 120 disjoint branch boxes.
    # Existence and physical local attraction follow from the analytic uniform
    # bounds, not from a root/trajectory search. The selected pattern is not unique.
    branch_bounds=[]
    for high in combinations(NODES,3):
        center=[F(3 if v in high else 1) for v in NODES]
        forcing=max(map(abs,apply(lap,center)))
        branch_image,branch_q=bounds(kappa,r,forcing)
        assert sum(center)==16 and forcing<=6
        assert branch_image<r and branch_q==q<1
        branch_bounds.append((high,branch_image))
    assert len(branch_bounds)==120 and 2-2*r>0
    no_basin_high={'a','b','d'}
    negative_image=next(value for high,value in branch_bounds if set(high)==no_basin_high)
    assert negative_image==F(83,1024)
    # Uniform no-anchor proof: upper nodes miss rows; each lower node has an
    # upper neighbor (wrong extremum) or a lower neighbor within 2r<barrier.
    for v in NODES:
        if v in no_basin_high:
            assert len(ports[v])==1
        else:
            assert adjacent[v]
            assert adjacent[v] & no_basin_high or 2*r<F(1,2)
    # Suppressing geometry leaves the equilibrium derivative unchanged.
    # Suppressing explicit Read-Back gives A=L and still contracts locally;
    # enabled feedback is compatible, not shown necessary for this organization.
    assert h*6*dmax<1 and 1-h*amin*dmin<1
    # Necessary charge compatibility for a future event/branch pairing, not
    # sufficiency for equilibrium existence, admission or branch reachability.
    def charge_compatible(charge,n,k,radius):
        return abs(charge-(n+2*k))<=n*radius  # fixed c0=2,a=1
    assert charge_compatible(F(16),10,3,r)
    assert charge_compatible(F(69,4),10,3,r)  # equality is not excluded
    assert not charge_compatible(F(69,4)+F(1,1024),10,3,r)
    # A 2-node mode shows the ordinary step cannot be arbitrarily large.
    mode_rate=F(48,11)  # beta=1/4,tau=1,lambda=2,V''=2,kappa=0
    assert abs(1-mode_rate)>1
    assert 1+h*mode_rate>1  # opposite sign has an expanding mode.

    def source(j):
        flat=apply(resolvent,j)
        # zeta=chi=1/2, two endpoints per edge, star assembly coefficient 1/2.
        return [[sum(F(1,16)*flat[i]*flat[k] for v in NODES
                     if v in EDGES[i] and v in EDGES[k]) for k in range(m)] for i in range(m)]
    j=[F(i+1,32) for i in range(m)];t=F(1,8)
    s=source(j);st=source([t*x for x in j])
    assert source([F(0)]*m)==[[F(0)]*m for _ in range(m)]
    assert st==[[t*t*x for x in row] for row in s]
    assert any(x for row in s for x in row)  # nonzero off-equilibrium read/source.

    # A derivative at one point is not a whole-box contraction certificate.
    nonlinear=lambda x:F(1,2)*x+x*x
    assert nonlinear(F(0))==0 and nonlinear(F(1))>1
    # Graph relabel/order/orientation changes preserve the potential law.
    perm=list(reversed(range(n)))
    bp=incidence(tuple(NODES[i] for i in perm),tuple((v,u) for u,v in reversed(EDGES)))
    assert matmul(bp,transpose(bp))==[[lap[i][j] for j in perm] for i in perm]
    return dict(
        scope='exact conditional equilibrium and C_OS local-stability mechanism; proposed nonlinear site binding',
        parameters=dict(c0='2',a='1',mu='1',kappa='1/64',eta_C='1',kappa_M_C='0',
                        tau_C='1',chi_C='1/2',zeta_C='1/2',kappa_H='1/2',dt='1/32'),
        graph=dict(nodes=list(NODES),edges=[list(e) for e in EDGES],port_edges=port_edges,
                   diameter=diameter,maximum_degree=3),
        equilibrium=dict(charge='16',radius=str(r),image_bound=str(image),strict_image_margin=str(r-image),
                         solver_lipschitz_bound=str(q),C0_is_not_the_coupled_equilibrium=True),
        basin_margins={k:str(v) for k,v in local_slacks.items()},
        physical_derivative=dict(norm='A_inverse_on_fixed_charge',mobility_lower=str(amin),
                                 mobility_upper=str(amax),curvature_lower=str(dmin),
                                 curvature_upper=str(dmax),operator_norm_bound=str(derivative_bound),
                                 uniform_whole_box_bound=False),
        review_pressure=dict(
            same_charge_branch_boxes=len(branch_bounds),
            branch_box_separation=str(2-2*r),
            largest_branch_image_bound=str(max(value for _,value in branch_bounds)),
            stable_no_basin_branch=dict(upper_nodes=sorted(no_basin_high),
                                       image_bound=str(negative_image),qualified_basins=0,
                                       uniform_box_argument=True),
            local_stability_survives_feedback_suppression=True,
            charge_preflight_is_necessary_only=True,
            reported_full_OS_box_escape_reexecuted=False),
        controls=dict(large_stiffness_not_certified=True,excessive_step_expands=True,wrong_sign_expands=True,
                      read_and_source_nonzero_off_equilibrium=True,source_quadratic_at_zero=True,
                      point_derivative_not_whole_box=True,label_orientation_covariance=True,
                      exact_charge_equilibrium_map=True),
        C_OS_local_exact_trapping_neighborhood_exists_conditionally=True,
        quantified_full_OS_trapping_radius=None,represented_numerical_certificate=False,
        native_evaluator_implemented=False,native_steps=0,native_events=0,
        parent_event_entry_proved=False,completed_spark=False,policy_admitted=False)
