"""Direct curved SC-1 domain; no trajectory after the completion window.

K = {p(s)+v: 0<=s<=1, 1^T v=0, ||v||_P<=R}.  Exact Chebyshev
algebra bounds F_I(p(s))-p(rho*s); a separately proved local Lipschitz
section bound restores BOTH physical H consumers.  Bernstein ranges certify
the whole continuum, not sampled points.  No derivative of Gamma is used.
"""
from math import comb
import time
from flint import arb, arb_mat, fmpq, fmpq_mat, ctx
from spark_completion_c_rg2b import (CRG2bReference, F, ETA, DT, LIP,
    PRECISION, PROPOSAL_BITS, PARAMETERS, ball, maxnorm, exact_bounds)
from spark_completion_c_rg2b_faster import (BASE, ROOT, ENTRY, WINDOW,
    prepare, section_reuse, fresh_check, cached_payload, seal, load)
from spark_completion_c_rg2b_campaign import state_payload, decode, section_payload
from spark_completion_positive import fixture, norm_upper
from spark_completion_a_os_earlier import positive_definite_exact
from spark_completion_continuation import need, geometric_roster, POLICY
import spark_completion_basins as basins

DOMAIN = BASE+'CRG2bDirectDomain.json'
DECLARATION = BASE+'CRG2bDirectDeclaration.json'
RADIUS = F(1,4096)
DECAY = F(999,1000)
DEGREE = 40
SUBDIVISIONS = 6
QUERY_RADIUS = F(7,50)
INVERSE_RADIUS = F(1,5)
EXPECTED = {'p':['p','private'],
    'sc2-positive-module/satellite/2':['n2','n8','sc2-positive-module/satellite/2']}


def cheb_product(a,b):
    out=[fmpq(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j]+=x*y/2
            out[abs(i-j)]+=x*y/2
    return out


def cheb_times_x(a):
    out=[fmpq(0)]*(len(a)+1)
    for i,x in enumerate(a):
        out[i+1]+=x/2
        out[abs(i-1)]+=x/2
    return out


def curve_at(Q,s):
    """Exact rational evaluation, including charge, at a rational parameter."""
    x=2*fmpq(str(s))-1
    t=[fmpq(1),x]
    for _ in range(2,Q.ncols()):t.append(2*x*t[-1]-t[-2])
    return Q*fmpq_mat([[v] for v in t[:Q.ncols()]])


def reference_residual(m,Q,rho):
    """Uniform P norm via the sum of exact Chebyshev coefficient norms."""
    d=Q.ncols()-1
    composition=[[fmpq(1)],[rho-1,rho]]
    for _ in range(1,d):
        old=composition[-1];new=cheb_times_x(old)
        for j in range(len(new)):
            new[j]=2*rho*new[j]+(2*(rho-1)*old[j] if j<len(old) else 0)-(composition[-2][j] if j<len(composition[-2]) else 0)
        composition.append(new)
    K=fmpq_mat([[composition[i][j] if j<len(composition[i]) else 0 for j in range(d+1)] for i in range(d+1)])
    h=fmpq(str(ETA*DT));A=m.algebra['A'];L=m.algebra['L']
    linear=Q+h*A*L*Q/64-Q*K
    site=[]
    for i in range(m.n):
        a=[Q[i,k] for k in range(d+1)];a[0]-=2
        cubic=cheb_product(cheb_product(a,a),a)
        for k,z in enumerate(a):cubic[k]-=z
        site.append(cubic)
    residual=-h*A*fmpq_mat(site)
    for i in range(m.n):
        for k in range(d+1):residual[i,k]+=linear[i,k]
    bound=arb(0)
    for k in range(residual.ncols()):
        v=fmpq_mat([[residual[i,k]] for i in range(m.n)])
        need(sum(v.entries())==0,'functional residual leaves exact charge tangent')
        squared=(v.transpose()*m.algebra['P']*v)[0,0]
        need(squared>=0,'negative exact metric square')
        bound+=arb(squared).sqrt()
    return bound.upper(),residual


def split_bernstein(row):
    row=list(row);left=[row[0]];right=[row[-1]]
    while len(row)>1:
        row=[(a+b)/2 for a,b in zip(row,row[1:])]
        left.append(row[0]);right.append(row[-1])
    return left,right[::-1]


def bernstein_cells(Q,depth):
    d=Q.ncols()-1;powers=[[1],[-1,2]]
    for _ in range(1,d):
        old=powers[-1];new=[0]*(len(old)+1)
        for j,z in enumerate(old):new[j]-=2*z;new[j+1]+=4*z
        for j,z in enumerate(powers[-2]):new[j]-=z
        powers.append(new)
    T=fmpq_mat([[powers[k][j] if j<len(powers[k]) else 0 for j in range(d+1)] for k in range(d+1)])
    B=fmpq_mat([[fmpq(comb(i,j),comb(d,j)) if i>=j else 0 for i in range(d+1)] for j in range(d+1)])
    cells=[(Q*T*B).tolist()]
    for _ in range(depth):
        new=[]
        for cell in cells:
            halves=[split_bernstein(row) for row in cell]
            new.extend(([x[0] for x in halves],[x[1] for x in halves]))
        cells=new
    return cells


class CurveBounds:
    """Exact Bernstein linear forms plus exact charge-tangent dual norm.

For arbitrary w, sup_{1^T v=0, ||v||_P<=R} |w^T v| =
R sqrt(w^T A w).  Correlation matters for small edge differences.
    """
    def __init__(self,m,Q,radius,depth):
        self.m=m;self.cells=bernstein_cells(Q,depth);self.radius=ball(radius);self.cache={}

    def linear(self,weights):
        key=tuple(map(str,weights))
        if key in self.cache:return self.cache[key]
        w=[fmpq(str(x)) for x in weights];terms=[(i,x) for i,x in enumerate(w) if x]
        values=[sum(x*cell[i][k] for i,x in terms) for cell in self.cells for k in range(len(cell[0]))]
        vector=fmpq_mat([w]);sq=(vector*self.m.algebra['A']*vector.transpose())[0,0]
        need(sq>=0,'negative dual metric square')
        width=self.radius*arb(sq).sqrt()
        result=((arb(min(values))-width).lower(),(arb(max(values))+width).upper())
        self.cache[key]=result
        return result

    def coordinate(self,i):return self.linear([int(j==i) for j in range(self.m.n)])
    def difference(self,i,j):return self.linear([int(k==i)-int(k==j) for k in range(self.m.n)])

    def box(self):
        ranges=[self.coordinate(i) for i in range(self.m.n)]
        return arb_mat([[arb((a.fmpq()+b.fmpq())/2,(b.fmpq()-a.fmpq())/2)] for a,b in ranges])


def uniform_roster(m,graph,bounds):
    """Every row flag, anchor barrier and directed edge on the entire K."""
    nodes=m.nodes
    need(graph['live_node_ids']==nodes,'chiral node order differs')
    need([(e['tail']['node_id'],e['head']['node_id']) for e in graph['edges']]==m.edges,'chiral incidence differs')
    edges=[(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],e['head']['port'],F(1)) for e in graph['edges']]
    adj=basins.neighbors(nodes,edges);terms={n:[[],[],[]] for n in nodes}
    for a,pa,b,pb,_ in edges:
        for here,port,there in ((a,pa,b),(b,pb,a)):terms[here][(port-1)//3].append(there)
    seeds=set();rows={}
    for n in nodes:
        rows[n]=[]
        for neighbors in terms[n]:
            weights=[F(neighbors.count(v),len(neighbors))-int(v==n) if neighbors else F(0) for v in nodes]
            lo,hi=bounds.linear(weights)
            rows[n].append((F(str(lo.fmpq())),F(str(hi.fmpq()))))
        if basins.seed_status(rows[n],POLICY):seeds.add(n)
    anchors=set()
    for n in seeds:
        lo,hi=bounds.coordinate(nodes.index(n))
        contrasts=[bounds.difference(nodes.index(n),nodes.index(v)) for v in adj[n]]
        if lo>ball(POLICY['core_resource']) and all(a>ball(POLICY['contrast']) for a,_ in contrasts):anchors.add(n)
        else:need(hi<=ball(POLICY['core_resource']) or any(b<=ball(POLICY['contrast']) for _,b in contrasts),'unresolved curve anchor')
    down={n:set() for n in nodes};margin=arb(1);directions=[]
    for a,b in m.edges:
        lo,hi=bounds.difference(nodes.index(a),nodes.index(b))
        need(lo>0 or hi<0,'curve changes an edge direction')
        below,above=(b,a) if lo>0 else (a,b)
        down[below].add(above);margin=min(margin,lo if lo>0 else -hi)
        directions.append([below,above])
    destinations={}
    def visit(n):
        if n not in destinations:destinations[n]=set().union(*(visit(v) for v in down[n])) if down[n] else {n}
        return destinations[n]
    for n in nodes:visit(n)
    roster={a:sorted(n for n in nodes if destinations[n]=={a}) for a in sorted(anchors)}
    roster={a:v for a,v in roster.items() if len(v)>1}
    need(roster==EXPECTED,'curve complete basin roster differs')
    return dict(complete_basins=roster,seeds=sorted(seeds),anchors=sorted(anchors),
        edge_directions=directions,minimum_edge_margin=exact_bounds(margin),
        row_bounds={n:[[str(a),str(b)] for a,b in rs] for n,rs in rows.items()})


def local_section(m,center,box):
    """Local inverse cube and section differences, using only global Lip(Gamma).

The inverse cube is independently closed by Banach iteration.  Global inverse
uniqueness identifies it with the frozen completion inverse.  Thus local G
partial bounds imply local section value/Lipschitz bounds without D Gamma.
    """
    C=m.vector(center);a=m.algebra;s0=m.section(C)
    w=max(abs(box[i,0]-C[i,0]).upper() for i in range(m.n))
    need(w<ball(QUERY_RADIUS),'query cube does not contain curve hull')
    R=ball(INVERSE_RADIUS);V=m.bounds['section_value_radius'];ell=ball(a['ell']);b=ball(a['b']);ss=ball(a['s']);a0=ball(a['a0'])
    need(a0*V*ell<1 and V<1,'local resolvent premises')
    inverse=a0/(1-a0*V*ell);hinv=1/(1-V);M=arb_mat(a['M']);MD=M*m.Le
    cb=arb_mat([[arb(z.fmpq(),fmpq(str(INVERSE_RADIUS)))] for z in C.entries()])
    need(all(ball(m.lo)<x<ball(m.hi) for x in cb.entries()),'inverse footprint crosses argument retraction')
    curv=arb_mat([[3*(cb[i,0]-2)**2-1 if i==j else 0 for j in range(m.n)] for i in range(m.n)])
    D=arb_mat(a['L'])/64-curv;h=ball(ETA*DT)
    reference=maxnorm(h*m.A*D);dmax=max(abs(curv[i,i]).upper() for i in range(m.n))
    qdiff=inverse*V*ell*a0/4
    perturb=h*b*2*(qdiff*(dmax+2*b/64)+(1+inverse/4)*2*b*V/64)
    ell_local=reference+perturb+m.bounds['A_H']*ball(LIP)
    f0=maxnorm(s0['read']['increment']);inverse_margin=R-ball(QUERY_RADIUS)-f0-ell_local*R
    need(ell_local<1 and inverse_margin>0,'local inverse cube not a strict contraction/self-map')
    inverse_lip=1/(1-ell_local)
    YX0=maxnorm(-ball(ETA)*M*m.Bt*D)
    read0=m.lag(C,m.operators(m.I));Y0=maxnorm(read0['causal_flat']*2);z=maxnorm(m.Bt*cb);eps=a0*V*ell
    Y=(Y0+YX0*R+ball(ETA)*maxnorm(MD)*V*z/64)/(1-eps)
    YX=(YX0+ball(ETA)*maxnorm(MD)*V*2/64)/(1-eps)
    j0x=maxnorm(-ball(ETA)*m.Bt*D)
    j0=maxnorm(read0['baseline'])+j0x*R+ball(ETA)*ell*V*z/64
    DY=min(ell*Y,hinv*(j0+3*Y/4))
    YH=inverse*(ball(ETA)*ell*z/64+DY)
    flat=hinv*Y/2;flatX=hinv*YX/2;flatH=hinv*(YH/2+flat)
    GX=2*ss*flat*flatX;GH=2*ss*flat*flatH
    lip=((GX+GH*ball(LIP))*inverse_lip).upper();value=(ss*flat**2).upper()
    need(0<lip<ball(LIP) and 0<value<V,'local section bounds do not improve global ones')
    record=dict(query_cube_radius=str(QUERY_RADIUS),inverse_cube_radius=str(INVERSE_RADIUS),
        hull_width=exact_bounds(w),inverse_cube_margin=exact_bounds(inverse_margin),
        inverse_increment_lipschitz=exact_bounds(ell_local),inverse_lipschitz=exact_bounds(inverse_lip),
        geometry_X=exact_bounds(GX),geometry_H=exact_bounds(GH),
        current_value=exact_bounds(Y),current_X=exact_bounds(YX),current_H=exact_bounds(YH),
        section_lipschitz=exact_bounds(lip),section_value_radius=exact_bounds(value),
        global_section_lipschitz_used=str(LIP),global_section_value_radius=exact_bounds(V),
        section_C1_claimed=False,inverse_is_frozen_completion_inverse=True)
    return lip,value,record


def physical_bounds(m,box,lip,value):
    """Common full-state difference bound and absolute F-Gamma versus F-I error."""
    n=m.n;curv=[3*(x-2)**2-1 for x in box.entries()]
    low=fmpq_mat([[curv[i].lower().fmpq() if i==j else 0 for j in range(n)] for i in range(n)])-m.algebra['L']/64
    high=fmpq_mat([[curv[i].upper().fmpq() if i==j else 0 for j in range(n)] for i in range(n)])-m.algebra['L']/64
    E=fmpq_mat([[int(i==j) if i<n-1 else -1 for j in range(n-1)] for i in range(n)]);P=m.algebra['P']
    pl=positive_definite_exact(E.transpose()*(low-P/3)*E)
    ph=positive_definite_exact(E.transpose()*(64*P-high)*E)
    ell=ball(m.algebra['ell']);h=ball(ETA*DT);V=value
    a2=(1+V)/(1-V)*m.q(4,3);q2=1+a2/4
    D0=max(abs(x).upper() for x in curv)+ell/64
    partial=h*ell*(a2*V*ell/3*D0+q2*ell*V/64)
    z=norm_upper(m.Bt*box);phi=m.B*m.Bt*box/64-m.site(box)
    j0=ball(ETA)*norm_upper(m.Bt*phi)+ball(ETA)*ell*V*z/64;y=a2*j0
    hslope=ball(DT)*ell.sqrt()*(ball(ETA)*ell*z*q2/64+a2*ell*y/4)
    convert=(m.amax*m.trace).sqrt();reference=max(abs(1-h/3),abs(1-64*h))
    fixed=partial*convert;section=hslope*lip*convert
    q=(reference+fixed+section).upper();error=(m.trace.sqrt()*hslope*V).upper()
    need(0<fixed and 0<section and 0<error and q<1,'full physical curve contraction fails')
    return q,error,dict(contraction=exact_bounds(q),reference_contraction=exact_bounds(reference),
        fixed_geometry_correction=exact_bounds(fixed),section_difference_correction=exact_bounds(section),
        geometry_value_correction=exact_bounds(error),H_slope=exact_bounds(hslope),
        charge_tangent_rayleigh_bounds=['1/3','64'],exact_ldl_pivots=dict(lower=pl,upper=ph),
        relative_dimension=n-1,all_independent_coordinates=True,both_H_consumers=True,section_C1_claimed=False)


def direct_certificate(domain):
    """All domain premises are recomputed; no executed trajectory is an input."""
    with ctx.workprec(PRECISION):
        _,_,targets=fixture();m=CRG2bReference(targets['1']['graph'])
        need(domain['schema']=='spark-completion-crg2b-direct-domain-v1' and domain['nodes']==m.nodes,'direct domain subject')
        need(domain['degree']==DEGREE and domain['radius']==str(RADIUS) and domain['parameter_decay']==str(DECAY) and domain['bernstein_subdivision_depth']==SUBDIVISIONS,'direct domain parameters')
        need(domain['parameters']==PARAMETERS and domain['relative_dimension']==m.n-1,'physical domain parameters/dimension')
        Q=fmpq_mat([[fmpq(v) for v in row] for row in domain['chebyshev_coefficients']])
        need(Q.nrows()==m.n and Q.ncols()==DEGREE+1 and RADIUS>0,'full-dimensional positive-radius curve')
        need(all(sum(Q[i,k] for i in range(m.n))==(21 if k==0 else 0) for k in range(DEGREE+1)),'curve exact charge identity')
        need(curve_at(Q,0)==fmpq_mat([[fmpq(domain['center'][n])] for n in m.nodes]),'curve origin differs')
        A,P=m.algebra['A'],m.algebra['P']
        need(A*P*A==A and all(sum(A[i,j] for j in range(m.n))==0 for i in range(m.n)),'charge-tangent dual metric identity')
        bounds=CurveBounds(m,Q,RADIUS,SUBDIVISIONS);box=bounds.box();km=list(map(ball,m.domain['K_minus']))
        need(all(x>0 and km[0]<x<km[1] for x in box.entries()),'curve leaves physical domain')
        geometry={chi:uniform_roster(m,t['graph'],bounds) for chi,t in targets.items()}
        reference,residual=reference_residual(m,Q,fmpq(str(DECAY)))
        lip,value,local=local_section(m,domain['center'],box)
        q,correction,physical=physical_bounds(m,box,lip,value)
        defect=(reference+correction).upper();margin=((1-q)*ball(RADIUS)-defect).lower()
        need(0<DECAY<1 and margin>0,'direct curve lacks a strict self-map margin')
        return dict(schema='spark-completion-crg2b-direct-certificate-v1',
            domain='continuous polynomial curve plus full charge-tangent metric ball',
            domain_digest=domain['record_digest'],entry_step=ENTRY,completion_step=ENTRY+WINDOW,
            ordinary_duration=str(DT),elapsed_from_event=str(DT*(ENTRY+WINDOW)),
            metric='(A0 + 11^T/n)^-1 on exact charge-21 tangent space',
            radius=str(RADIUS),relative_dimension=m.n-1,curve_degree=DEGREE,parameter_decay=str(DECAY),
            bernstein_cells=2**SUBDIVISIONS,reference_functional_defect=exact_bounds(reference),
            residual_degree=residual.ncols()-1,full_physical_functional_defect=exact_bounds(defect),
            strict_image_margin=exact_bounds(margin),common_contraction=physical,local_section=local,
            hull={n:exact_bounds(box[i,0]) for i,n in enumerate(m.nodes)},geometry=geometry,
            complete_basins={chi:g['complete_basins'] for chi,g in geometry.items()},
            future_trajectory_required=False,supporting_trajectory_steps_after_completion=0,
            trajectory_inputs_to_domain_checker=0,all_parameters_certified_continuously=True,
            original_SC1_contract_unchanged=True,full_return_difference_bound=True,
            full_physical_state=['C'],section_C1_claimed=False,completion_relative=True,
            accepted_authority=False,native_completion=False,reset_earns_live_gain=False)


def membership(m,Q,row):
    need(ENTRY<=row['step']<=ENTRY+WINDOW,'membership outside declared completion window')
    C,r=decode(m,row)
    need(sum(C.entries())==21 and r>0,'entry tube is not full-dimensional exact charge')
    parameter=DECAY**(row['step']-ENTRY);delta=C-arb_mat(curve_at(Q,parameter))
    distance=((delta.transpose()*m.P*delta)[0,0].nonnegative_part().sqrt()+r).upper()
    margin=(ball(RADIUS)-distance).lower()
    need(margin>0,'executed tube is outside the direct domain')
    return dict(step=row['step'],parameter=str(parameter),distance_upper=exact_bounds(distance),strict_membership_margin=exact_bounds(margin))


def campaign(role,declaration,domain):
    """Fresh physical prefix only.  No terminal trap or later-state read."""
    start=time.monotonic()
    with ctx.workprec(PRECISION):
        m,C,r,record,targets=prepare(role,declaration)
        initial=state_payload(m,C,r);s=m.section(C,retain_chain=True)
        event=section_payload(s,m,C,r);rows=[];fresh={};first=None;window=[];gap=arb(1)
        Q=fmpq_mat([[fmpq(v) for v in row] for row in domain['chebyshev_coefficients']])
        for step in range(1,ENTRY+WINDOW+1):
            need(time.monotonic()-start<3600,'direct prefix one-hour cap')
            oldC,oldr=C,r;C,r,diag=m.advance_tube(C,r,s)
            strict=r-(diag['lipschitz']*oldr+diag['defect'])
            need(strict>0,'prefix successor tube lacks strict image margin');gap=min(gap,strict.lower())
            s=section_reuse(m,oldC,s,C);cb=m.box(C,r);km=list(map(ball,m.domain['K_minus']))
            need(sum(C.entries())==21 and all(km[0]<x<km[1] and x>0 for x in cb.entries()),'prefix physical admission')
            roster={chi:geometric_roster(t['graph'],cb,m.nodes) for chi,t in targets.items()}
            if first is None and all(v==EXPECTED for v in roster.values()):first=step
            if step in (1,ENTRY,ENTRY+WINDOW):fresh[str(step)]=fresh_check(m,C,r,s)
            row=dict(step=step,**state_payload(m,C,r),section=cached_payload(s),complete_basins=roster,
                tube=dict(lipschitz=exact_bounds(diag['lipschitz']),defect=exact_bounds(diag['defect'],256),strict_image_margin=exact_bounds(strict,256)))
            rows.append(row)
            if step>=ENTRY:
                need(all(v==EXPECTED for v in roster.values()),'completion window roster differs')
                window.append(membership(m,Q,row))
        return dict(role=role,source=record,targets=targets,initial_target=initial,event_section=event,
            observations=rows,fresh_section_checks=fresh,first_spatial_gain=first,
            entry=ENTRY,completion=ENTRY+WINDOW,last_executed_step=ENTRY+WINDOW,
            domain_digest=domain['record_digest'],window_membership=window,
            minimum_tube_image_margin=exact_bounds(gap,256),
            section_reuse=dict(initial_section_fresh=True,each_transfer_from_invariance=True,
                center_shifts_enclosed=True,physical_state=['C'],geometry_history_transported_at_event=False,
                geometry_is_independent_physical_state=False,fresh_rebuild_count=len(fresh),forward_reuse_steps=len(rows)),
            arithmetic=dict(precision_bits=PRECISION,proposal_bits=PROPOSAL_BITS,radius_bits=160,
                horizon=ENTRY+WINDOW,time_limit_seconds=3600,automatic_fallback=False),
            elapsed_seconds=time.monotonic()-start)
