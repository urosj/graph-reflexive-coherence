"""Full C/W direct curved domains, independent of any later trajectory.

The reference is the full fixed-H=I physical map, including the writer.
Adaptive rational Bernstein cells and interval directional derivatives bound
F_I(p(s))-p(rho*s) on the entire continuum. A fresh global Lipschitz section
bound restores both H consumers. Each curve has a full 30-dimensional tube.
"""
import time
from math import comb
from flint import arb,arb_mat,arb_series,fmpq,fmpq_mat,ctx
from spark_completion_a_rg2b import *
from spark_completion_c_rg2b_direct import (curve_at,bernstein_cells,split_bernstein,
    cheb_times_x,CurveBounds,EXPECTED)
from spark_completion_a_os_earlier import positive_definite_exact
from spark_completion_positive import fixture,norm_upper
from spark_completion_continuation import POLICY
import spark_completion_basins as basins

RADIUS=F(1,4096)
DECAY=F(999,1000)
ENTRY=300
WINDOW=2
DEGREE=40
GEOMETRY_DEPTH=6
RESIDUAL_LIMIT=F(1,10**7)
MAX_RESIDUAL_DEPTH=16
REFERENCE_LOWER=F(1,4)
TAYLOR_ORDER=4


def metric(m):
    B=graph_constants(m.key)[0];A=B*B.transpose();n=m.n
    pi=fmpq_mat([[fmpq(1,n) for _ in range(n)] for _ in range(n)])
    P=(A+pi).inv();trace=sum(P[i,i] for i in range(n))-1
    need(A*P*A==A and trace>0,'exact charge metric')
    m.algebra=dict(A=A,P=P);m.A=arb_mat(A);m.P=arb_mat(P)
    m.trace=arb(trace);m.amax=arb(infnorm(A))
    return A,P


def metric_norm(m,X):
    C=arb_mat([[X[i,0]] for i in range(m.n)])
    Y=arb_mat([[X[m.n+i,0]] for i in range(m.m)])
    square=(C.transpose()*m.P*C)[0,0]
    return max(square.nonnegative_part().sqrt().upper(),norm_upper(Y).upper())


def ranges(rows):
    return arb_mat([[arb((min(row)+max(row))/2,(max(row)-min(row))/2)] for row in rows])


def composition(Q,rho):
    d=Q.ncols()-1;rows=[[fmpq(1)],[rho-1,rho]]
    for _ in range(1,d):
        old=rows[-1];new=cheb_times_x(old)
        for j in range(len(new)):
            new[j]=2*rho*new[j]+(2*(rho-1)*old[j] if j<len(old) else 0)-(rows[-2][j] if j<len(rows[-2]) else 0)
        rows.append(new)
    return Q*fmpq_mat([[rows[i][j] if j<len(rows[i]) else 0 for j in range(d+1)] for i in range(d+1)])


def curve_jets(cell,width,*,at_midpoint):
    """Exact Bernstein derivatives/k! at the midpoint or over the whole cell."""
    degree=len(cell[0])-1;out=[]
    for row in cell:
        coefficients=[];differences=list(row)
        for k in range(TAYLOR_ORDER+1):
            factor=fmpq(comb(degree,k))/width**k
            if at_midpoint:
                d=len(differences)-1
                value=sum(fmpq(comb(d,i),2**d)*z for i,z in enumerate(differences))*factor
                coefficients.append(arb(value))
            else:
                lo,hi=min(differences)*factor,max(differences)*factor
                coefficients.append(arb((lo+hi)/2,(hi-lo)/2))
            differences=[b-a for a,b in zip(differences,differences[1:])]
        out.append(arb_series(coefficients,prec=TAYLOR_ORDER+1))
    return out


def reference_jets(m,X):
    """Independent scalar edge equations for the complete fixed-I map."""
    zero=lambda:arb_series([0],prec=TAYLOR_ORDER+1)
    C=X[:m.n];Y=X[m.n:];W=[(v/ball(SCALE)).exp() for v in Y]
    lap=[zero() for _ in C]
    for k,(i,j) in enumerate(m.pairs):
        z=W[k]*(C[i]-C[j]);lap[i]+=z;lap[j]-=z
    phi=[l/64-((c-2)**3-(c-2)) for l,c in zip(lap,C)]
    j0=[-W[k]*(phi[i]-phi[j])/1024 for k,(i,j) in enumerate(m.pairs)]
    def exponent(c,current):
        rows=[[sum((W[k]*(c[j]-c[i]) for k,j in terms),zero())/
            sum((W[k] for k,j in terms),zero()) if terms else zero() for terms in node]
            for i,node in enumerate(m.terms)]
        values=[-(c[i]+c[j]+sum(((a-b)**2 for a,b in zip(rows[i],rows[j])),zero())+current[k]**2)/65536
            for k,(i,j) in enumerate(m.pairs)]
        need(all(v[0]>m.floor_log for v in values),'jet floor branch')
        return values
    G=[v.exp() for v in exponent(C,j0)]
    q=[(w-g)/(w+g) for w,g in zip(W,G)]
    J=[j/(1-v/4) for j,v in zip(j0,q)]
    after=list(C)
    for k,(i,j) in enumerate(m.pairs):
        after[i]=after[i]-ball(DT)*J[k];after[j]=after[j]+ball(DT)*J[k]
    ex=exponent(after,J)
    return after+[m.decay*y+(1-m.decay)*ball(SCALE)*v for y,v in zip(Y,ex)]


def continuous_residual(m,Q):
    """Fourth-order Taylor enclosure on an exact partition; no sampling proof."""
    start=time.monotonic()
    shift=composition(Q,fmpq(str(DECAY)))
    initial=6;count=2**initial
    cells=bernstein_cells(Q,initial);shiftcells=bernstein_cells(shift,initial)
    pending=[(fmpq(i,count),fmpq(i+1,count),cells[i],shiftcells[i],initial) for i in reversed(range(count))]
    leaves=[];evaluations=0;maximum=arb(0)
    while pending:
        need(time.monotonic()-start<3600,'explicit one-hour continuous certificate limit')
        lo,hi,cell,shiftcell,depth=pending.pop();mid=(lo+hi)/2;width=hi-lo
        cb=ranges(cell);need(m.in_agreement(cb),'reference curve leaves agreement')
        point=reference_jets(m,curve_jets(cell,width,at_midpoint=True))
        point_shift=curve_jets(shiftcell,width,at_midpoint=True)
        whole=reference_jets(m,curve_jets(cell,width,at_midpoint=False))
        whole_shift=curve_jets(shiftcell,width,at_midpoint=False)
        bound=arb(0)
        for k in range(TAYLOR_ORDER+1):
            a,b=(whole,whole_shift) if k==TAYLOR_ORDER else (point,point_shift)
            coefficient=arb_mat([[x[k]-y[k]] for x,y in zip(a,b)])
            bound+=metric_norm(m,coefficient)*arb(width/2)**k
        bound=bound.upper()
        evaluations+=1
        if evaluations%128==0:print('continuous-domain',evaluations,'accepted',len(leaves),'seconds',round(time.monotonic()-start,1),flush=True)
        if bound<ball(RESIDUAL_LIMIT):
            maximum=max(maximum,bound)
            leaves.append(dict(interval=[str(lo),str(hi)],residual_upper=exact_bounds(bound)))
        else:
            need(depth<MAX_RESIDUAL_DEPTH,'functional residual subdivision limit')
            a=[split_bernstein(row) for row in cell];b=[split_bernstein(row) for row in shiftcell]
            pending.append((mid,hi,[v[1] for v in a],[v[1] for v in b],depth+1))
            pending.append((lo,mid,[v[0] for v in a],[v[0] for v in b],depth+1))
    need(sum(fmpq(row['interval'][1])-fmpq(row['interval'][0]) for row in leaves)==1,'partition length')
    need(leaves[0]['interval'][0]=='0' and leaves[-1]['interval'][1]=='1' and
        all(a['interval'][1]==b['interval'][0] for a,b in zip(leaves,leaves[1:])),'exact gap-free partition')
    return maximum,dict(method='rational_Bernstein_derivatives_and_full_writer_order4_interval_Taylor',
        evaluations=evaluations,cells=leaves,uniform_bound=exact_bounds(maximum),continuous_parameter=True)


def physical_bounds(m,Xbox):
    """P/Euclidean block norm, pointwise self-adjoint reference and section differences."""
    C,L=m.unpack(Xbox);W=m.exp(L);n=m.n;A,P=m.algebra['A'],m.algebra['P']
    curv=[3*(x-2)**2-1 for x in C.entries()]
    low=fmpq_mat([[curv[i].lower().fmpq() if i==j else 0 for j in range(n)] for i in range(n)])-A/64
    high=fmpq_mat([[curv[i].upper().fmpq() if i==j else 0 for j in range(n)] for i in range(n)])-A/64
    E=fmpq_mat([[int(i==j) if i<n-1 else -1 for j in range(n-1)] for i in range(n)])
    lower=positive_definite_exact(E.transpose()*(low-fmpq(str(REFERENCE_LOWER))*P)*E)
    upper=positive_definite_exact(E.transpose()*(64*P-high)*E)
    q0=max(abs(1-ball(DT/1024)*ball(REFERENCE_LOWER)),abs(1-ball(DT/1024)*64))
    value=m.bounds['section_value_radius'];lip=ball(m.domain['image_lipschitz'])
    H=arb_mat([[arb(int(i==j),value.upper().fmpq()) if m.overlap[i][j] else arb(0)
        for j in range(m.m)] for i in range(m.m)])
    read=m.lag(Xbox,H);r=read['selected'];q=r['q'];j0=r['baseline'];G=r['drive']
    den=[1-q[i,0]/4 for i in range(m.m)]
    R=m.diag(arb_mat([[W[i,0]/den[i]] for i in range(m.m)]))
    D0=m.A/64-m.diag(arb_mat([[v] for v in curv]))
    perturb_potential=m.B*(m.diag(W)-m.I+H-m.I)*m.Bt/64
    dc=arb_mat([[int(i==j) for j in range(n)] for i in range(n)])
    dw=arb_mat(m.m,n);dphi=D0+perturb_potential
    dj0=-m.diag(W)*m.Bt*dphi/1024
    _,de=m.exponent(C,W,j0,None,dc,dw,dj0)
    dq=arb_mat([[-2*W[i,0]*G[i,0]*de[i,j]/(W[i,0]+G[i,0])**2 for j in range(n)] for i in range(m.m)])
    difference=ball(DT/1024)*m.B*((R-m.I)*m.Bt*D0+R*m.Bt*perturb_potential)
    difference-=ball(DT)*m.B*m.diag(arb_mat([[j0[i,0]/(4*den[i]**2)] for i in range(m.m)]))*dq
    J=m.fixed_jacobian(Xbox,H,read)
    block=lambda a,b,c,d:arb_mat([[J[i,j] for j in range(c,d)] for i in range(a,b)])
    cc=q0+norm_upper(difference)*(m.amax*m.trace).sqrt()
    cw=norm_upper(block(0,n,n,m.d))*m.trace.sqrt()
    wc=norm_upper(block(n,m.d,0,n))*m.amax.sqrt()
    ww=m.decay+norm_upper(block(n,m.d,n,m.d)-m.decay*m.I)
    fixed=max((cc+cw).upper(),(wc+ww).upper())
    out_convert=max((n*m.trace).sqrt().upper(),arb(m.m).sqrt().upper())
    in_convert=max(m.amax.sqrt().upper(),arb(1))
    section=(out_convert*m.bounds['A_H']*lip*in_convert).upper()
    correction=(out_convert*m.bounds['A_H']*value).upper()
    contraction=(fixed+section).upper()
    need(contraction<1,'full physical C/W curve contraction')
    return contraction,correction,dict(contraction=exact_bounds(contraction),
        reference_contraction=exact_bounds(q0),block_bounds={k:exact_bounds(v) for k,v in dict(CC=cc,CW=cw,WC=wc,WW=ww).items()},
        section_lipschitz=exact_bounds(lip),section_difference_correction=exact_bounds(section),
        geometry_value_correction=exact_bounds(correction),relative_dimension=n-1+m.m,
        resource_dimension=n-1,conductance_dimension=m.m,section_C1_claimed=False,
        exact_ldl_pivots=dict(lower=lower,upper=upper),charge_tangent_rayleigh_bounds=[str(REFERENCE_LOWER),'64'],
        both_H_consumers=True,full_writer_included=True,all_independent_coordinates=True)


def uniform_geometry(m,Q,bounds,Xbox):
    """Weighted rows plus correlated resource comparisons on the continuous tube."""
    C,L=m.unpack(Xbox);W=m.exp(L);wl=min(w.lower() for w in W.entries())
    deviation=max(abs(w-1).upper() for w in W.entries())
    span=max(c.upper() for c in C.entries())-min(c.lower() for c in C.entries())
    correction=2*deviation*span/wl
    seeds=set();rows={}
    for i,node in enumerate(m.nodes):
        values=[]
        for terms in m.terms[i]:
            if not terms:values.append((F(0),F(0)));continue
            coeff=[F(sum(v==j for _,v in terms),len(terms))-int(j==i) for j in range(m.n)]
            lo,hi=bounds.linear(coeff)
            values.append((F(str((lo-correction).lower().fmpq())),F(str((hi+correction).upper().fmpq()))))
        rows[node]=values
        if basins.seed_status(values,POLICY):seeds.add(node)
    adj={n:set() for n in m.nodes};down={n:set() for n in m.nodes};edges=[];minimum=arb(1)
    for k,(i,j) in enumerate(m.pairs):
        a,b=m.nodes[i],m.nodes[j];adj[a].add(b);adj[b].add(a)
        lo,hi=bounds.difference(i,j);need(lo>0 or hi<0,'continuous C/W domain changes edge order')
        below,above=(b,a) if lo>0 else (a,b);margin=lo if lo>0 else -hi
        down[below].add(above);minimum=min(minimum,margin)
        edges.append(dict(edge_id=m.edge_ids[k],below=below,above=above,strict_margin=exact_bounds(margin)))
    anchors=set()
    for node in seeds:
        i=m.nodes.index(node);lo,hi=bounds.coordinate(i)
        contrasts=[bounds.difference(i,m.nodes.index(v)) for v in adj[node]]
        if lo>ball(POLICY['core_resource']) and all(a>ball(POLICY['contrast']) for a,b in contrasts):anchors.add(node)
        else:need(hi<=ball(POLICY['core_resource']) or any(b<=ball(POLICY['contrast']) for a,b in contrasts),'curve anchor unresolved')
    destinations={}
    def visit(node):
        if node not in destinations:destinations[node]=set().union(*(visit(v) for v in down[node])) if down[node] else {node}
        return destinations[node]
    for node in m.nodes:visit(node)
    roster={a:sorted(n for n in m.nodes if destinations[n]=={a}) for a in sorted(anchors)}
    roster={a:v for a,v in roster.items() if len(v)>1}
    need(roster==EXPECTED,'continuous weighted complete basins differ')
    return dict(complete_basins=roster,seeds=sorted(seeds),anchors=sorted(anchors),edges=edges,
        minimum_edge_margin=exact_bounds(minimum),weighted_row_correction=exact_bounds(correction),
        row_bounds={n:[[str(a),str(b)] for a,b in values] for n,values in rows.items()})


def curve_certificate(domain,role):
    _,_,targets=fixture();m=ARG2bReference(targets['1']['graph']);metric(m)
    need(domain['schema']=='spark-completion-arg2b-direct-domain-v1' and
        domain['parameters']==PARAMETERS and domain['nodes']==m.nodes and domain['edge_ids']==m.edge_ids,
        'direct domain physical subject')
    need(domain['relative_dimension']==30 and domain['entry']==ENTRY and domain['completion']==ENTRY+WINDOW and
        domain['radius']==str(RADIUS) and domain['parameter_decay']==str(DECAY) and domain['degree']==DEGREE and
        domain['coordinate_system']=='C_then_64_logW' and not domain['accepted_authority'], 'direct domain declaration')
    need(set(domain['curves'])=={'current','reset'} and domain['curves']['current']==domain['curves']['reset'],
        'declared common current/reset domain')
    Q=fmpq_mat([[fmpq(v) for v in row] for row in domain['curves'][role]])
    need(Q.nrows()==m.d and Q.ncols()==DEGREE+1,'full C/W polynomial shape')
    need(all(sum(Q[i,k] for i in range(m.n))==(21 if k==0 else 0) for k in range(DEGREE+1)),'curve exact charge')
    need(curve_at(Q,0)==fmpq_mat([[fmpq(v)] for v in domain['center']]),'curve origin')
    bounds=CurveBounds(m,Q,RADIUS,GEOMETRY_DEPTH);cb=bounds.box()
    cells=bernstein_cells(Q,GEOMETRY_DEPTH);yb=[]
    for i in range(m.n,m.d):
        lo=min(min(cell[i]) for cell in cells)-fmpq(str(RADIUS))
        hi=max(max(cell[i]) for cell in cells)+fmpq(str(RADIUS))
        yb.append([arb((lo+hi)/2,(hi-lo)/2)])
    Xbox=arb_mat(cb.tolist()+yb)
    need(m.in_agreement(Xbox) and all(c>0 for c in cb.entries()),'full curved domain physical agreement')
    geometry={}
    for chi,t in targets.items():
        other=ARG2bReference(t['graph']);need(other.nodes==m.nodes and other.pairs==m.pairs and other.terms==m.terms,'chiral equation identity')
        geometry[chi]=uniform_geometry(other,Q,bounds,Xbox)
    q,correction,physical=physical_bounds(m,Xbox)
    reference,partition=continuous_residual(m,Q)
    defect=(reference+correction).upper();margin=((1-q)*ball(RADIUS)-defect).lower()
    need(margin>0,'direct full-state domain lacks a strict self-map margin')
    return dict(role=role,full_physical_state=['C','W_A'],relative_dimension=m.n-1+m.m,
        radius=str(RADIUS),parameter_decay=str(DECAY),degree=DEGREE,physical=physical,
        reference_functional_defect=exact_bounds(reference),full_physical_functional_defect=exact_bounds(defect),
        strict_image_margin=exact_bounds(margin),residual_partition=partition,geometry=geometry,
        hull=[exact_bounds(x) for x in Xbox.entries()],completion_relative_section=m.domain,
        future_trajectory_required=False,trajectory_inputs_to_domain_checker=0,
        section_C1_claimed=False,accepted_authority=False,native_completion=False)
