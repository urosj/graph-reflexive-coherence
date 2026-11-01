"""Earlier A_OS witnesses on immutable trajectories, using full-state domains.

The anisotropic domain is an exact rational parallelotope in C/logW coordinates.
Floating-point eigendata propose its basis only; Arb verifies the actual full
map on the entire domain. No physical parameter, allocation or SC-1 rule changes.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,lzma
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_a_os import AOSReference,graph_constants,geometric_roster
from spark_completion_positive import norm_upper,content_id
from spark_completion_ci_campaign import exact_bounds
from spark_completion_continuation import need,POLICY,infnorm,spectral_domain
import spark_completion_basins as basins

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
BASE=INV+'evidence/spark-completion/applicability/'
EARLIER=BASE+'earlier-closure/'
PRECISION=512


def read_json(path):
    raw=(ROOT/path).read_bytes()
    return json.loads(lzma.decompress(raw) if path.endswith('.xz') else raw)


def sealed(value):return {**value,'record_digest':content_id(value)}


def need_seal(value):
    need(value['record_digest']==content_id({k:v for k,v in value.items() if k!='record_digest'}),'record digest')


def originals():
    """Authenticate the accepted producer and operands before any reuse."""
    acceptance=read_json(BASE+'AOSScientificAcceptance.json');need_seal(acceptance)
    authority=read_json(INV+'decisions/spark-completion-a-os/Authority.json');need_seal(authority)
    need(authority['acceptance']['record_digest']==acceptance['record_digest'] and
         hashlib.sha256((ROOT/BASE/'AOSScientificAcceptance.json').read_bytes()).hexdigest()==authority['acceptance']['sha256'],
         'accepted scientific subject')
    refs={r['path']:r['sha256'] for r in acceptance['subjects']};runs={}
    for role in ('current','reset'):
        path=BASE+'AOS-'+role+'.json.xz';raw=(ROOT/path).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==refs[path],'accepted trajectory bytes')
        value=json.loads(lzma.decompress(raw));need_seal(value)
        need(value['record_digest']==acceptance['execution_record_digests'][role],'accepted execution identity')
        for ref in value['sources']:
            need(hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256'],'producer/operand source drift')
        c=value['checks'];need(c['role']==role and c['proof']['relative_dimension']==30,'original full state')
        runs[role]=c
    need(runs['current']['proof']==runs['reset']['proof'],'different original centers')
    return runs


def interval(pair):
    a,b=map(F,pair);need(0<=b-a<=F(1,2**110),'retained interval shape/width')
    return arb(fmpq(str((a+b)/2)),fmpq(str((b-a)/2)))


def decode(m,row):
    need(set(row['C'])==set(m.nodes) and len(row['logW'])==m.m,'all retained coordinates')
    return arb_mat([[interval(row['C'][x])] for x in m.nodes]),arb_mat([[interval(x)] for x in row['logW']])


def stack(C,L):return arb_mat(C.tolist()+L.tolist())


def uniform_geometry(m,Cbox,Lbox,center,edge_radius):
    """Rows use an outer box; every edge comparison uses the actual domain."""
    W=m.exp(Lbox);rv,_=m.rows(Cbox,W)
    seeds={node for i,node in enumerate(m.nodes)
           if basins.seed_status([tuple(map(F,exact_bounds(x))) for x in rv[i]],POLICY)}
    adj={x:set() for x in m.nodes};down={x:set() for x in m.nodes};comparisons={};edges=[]
    for k,(i,j) in enumerate(m.pairs):
        gap=arb(fmpq(center[m.nodes[i]])-fmpq(center[m.nodes[j]]));radius=edge_radius(i,j)
        lower=abs(gap)-radius;need(lower>0,'domain crosses an edge-order hyperplane')
        a,b=m.nodes[i],m.nodes[j];adj[a].add(b);adj[b].add(a)
        down[a if gap<0 else b].add(b if gap<0 else a)
        comparisons[i,j]=(gap-radius,gap+radius);comparisons[j,i]=(-gap-radius,-gap+radius)
        edges.append(dict(edge_id=m.edge_ids[k],orientation=1 if gap>0 else -1,
                          strict_margin=exact_bounds(lower),half_width=exact_bounds(radius)))
    anchors=set()
    for x in seeds:
        i=m.nodes.index(x);neighbors=[m.nodes.index(y) for y in adj[x]]
        if Cbox[i,0]>m.q(1,2) and all(comparisons[i,j][0]>m.q(1,2) for j in neighbors):anchors.add(x)
        else:need(Cbox[i,0]<=m.q(1,2) or any(comparisons[i,j][1]<=m.q(1,2) for j in neighbors),'unresolved anchor')
    destinations={}
    def visit(x):
        if x not in destinations:destinations[x]=set().union(*(visit(y) for y in down[x])) if down[x] else {x}
        return destinations[x]
    for x in m.nodes:visit(x)
    roster={a:sorted(x for x in m.nodes if destinations[x]=={a}) for a in sorted(anchors)}
    roster={a:b for a,b in roster.items() if len(b)>1}
    need(all(Cbox[i,0]>0 for i in range(m.n)),'positive resource domain')
    need(all(m.q(99,100)<w<m.q(101,100) for w in W.entries()),'weighted selector W domain')
    selector=spectral_domain(m.graph)
    need(F(selector['nonconstant_eigenvalue_lower'])*F(99,100)>F(1,64),'weighted selector cutoff')
    return dict(complete_basins=roster,seeds=sorted(seeds),edges=edges,
        minimum_order_margin=exact_bounds(min(arb(fmpq(e['strict_margin'][0])) for e in edges)),
        minimum_resource=exact_bounds(min(Cbox[i,0].lower() for i in range(m.n))),
        W_bounds=[exact_bounds(min(x.lower() for x in W.entries()))[0],exact_bounds(max(x.upper() for x in W.entries()))[1]],
        weighted_selector_lower=str(F(selector['nonconstant_eigenvalue_lower'])*F(99,100)))


def charge_maps(m):
    n=m.n;d=n-1+m.m
    E=fmpq_mat([[int(i==j) if i<n-1 else -int(j<n-1) if i==n-1 else int(j==i-1)
                 for j in range(d)] for i in range(n+m.m)])
    R=fmpq_mat([[int(i==j) if i<n-1 else int(j==i+1) for j in range(n+m.m)] for i in range(d)])
    need(R*E==fmpq_mat([[int(i==j) for j in range(d)] for i in range(d)]),'charge chart identity')
    need(all(sum(E[i,j] for i in range(n))==0 for j in range(d)),'all tangent directions conserve charge')
    return E,R


def anisotropic_certificate(runs,proposal):
    need_seal(proposal)
    need(proposal['schema']=='spark-completion-aos-anisotropic-domain-v1' and
         proposal['relative_dimension']==30 and not proposal['accepted_authority'],'domain scope')
    for ref in proposal['sources']:
        need(hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256'],'domain source drift')
    with ctx.workprec(PRECISION):
        original=runs['current'];proof=original['proof'];m=AOSReference(original['targets']['1']['graph'])
        n=m.n;d=n-1+m.m;E,R=charge_maps(m)
        need(len(proposal['basis'])==d and all(len(row)==d for row in proposal['basis']),'full basis dimensions')
        T=fmpq_mat([[fmpq(x) for x in row] for row in proposal['basis']]);r=list(map(fmpq,proposal['axis_radii']))
        need(len(r)==d and all(x>0 for x in r),'positive independent axis radii')
        try:ti=T.inv()
        except (ZeroDivisionError,ValueError) as error:raise ValueError('rank-deficient full-state domain') from error
        diagonal=lambda xs:fmpq_mat([[xs[i] if i==j else 0 for j in range(d)] for i in range(d)])
        S=E*T*diagonal(r);U=diagonal([1/x for x in r])*ti*R
        need(U*S==fmpq_mat([[int(i==j) for j in range(d)] for i in range(d)]),'exact domain inverse')
        C=m.vector(proof['center']);L=arb_mat([[arb(fmpq(x))] for x in proof['logW_center']])
        need(sum(fmpq(x) for x in proof['center'].values())==21,'exact center charge')
        radii=[sum(abs(S[i,j]) for j in range(d)) for i in range(n+m.m)]
        Cbox=arb_mat([[arb(fmpq(proof['center'][x]),radii[i])] for i,x in enumerate(m.nodes)])
        Lbox=arb_mat([[arb(fmpq(x),radii[n+i])] for i,x in enumerate(proof['logW_center'])])
        derivative=arb_mat(U)*m.jacobian(Cbox,Lbox)*arb_mat(S)
        rows=[sum(abs(derivative[i,j]).upper() for j in range(d)) for i in range(d)]
        q=max(rows);need(q<1,'full transformed derivative does not contract')
        step=m.step(C,L);delta=arb_mat(U)*stack(step['after']-C,step['logW_after']-L)
        defect=max(abs(x).upper() for x in delta.entries());margin=1-q-defect
        need(margin>0,'no strict full-domain self-map margin')
        geo={}
        edge_radius=lambda i,j:arb(sum(abs(S[i,k]-S[j,k]) for k in range(d)))
        for chi,target in original['targets'].items():
            chart=AOSReference(target['graph'])
            need(chart.nodes==m.nodes and chart.pairs==m.pairs and chart.terms==m.terms,'chiral equation identity')
            geo[chi]=uniform_geometry(chart,Cbox,Lbox,proof['center'],edge_radius)
            need(geo[chi]['complete_basins']==proof['complete_basins'][chi],'uniform complete basin roster')
        # The actual domain succeeds even when its coordinate-box enclosure does not preserve edge order.
        box_margins=[abs(fmpq(proof['center'][m.nodes[i]])-fmpq(proof['center'][m.nodes[j]]))-radii[i]-radii[j] for i,j in m.pairs]
        interior=1/max(sum(abs(U[i,j]) for j in range(n+m.m)) for i in range(d))
        result=dict(schema='spark-completion-aos-anisotropic-proof-v1',relative_dimension=d,
            resource_dimension=n-1,conductance_dimension=m.m,exact_charge='21',domain_record_digest=proposal['record_digest'],
            norm='||diag(r)^-1 T^-1 R (C-center,logW-logW_center)||_infinity',unit_radius='1',
            contraction=exact_bounds(q),derivative_row_bounds=[exact_bounds(x) for x in rows],
            center_defect=exact_bounds(defect),strict_image_margin=exact_bounds(margin),
            all_independent_directions_included=True,positive_relative_neighborhood_lower=str(interior),
            coordinate_half_widths=list(map(str,radii)),geometry=geo,
            enclosing_coordinate_box_minimum_edge_margin=str(min(box_margins)),
            split_upper=exact_bounds(m.os_read(Cbox,Lbox)['split_upper']),proof_precision_bits=PRECISION,
            actual_full_map_trapping=True,accepted_authority=False,native_completion=False)
        return result,dict(model=m,center_C=C,center_L=L,S=S,U=U,Cbox=Cbox,Lbox=Lbox,derivative=derivative)


def positive_definite_exact(M):
    """Exact rational LDL elimination; every pivot must be strictly positive."""
    need(M==M.transpose(),'symmetric spectral inequality');n=M.nrows();a=M.tolist();pivots=[]
    for k in range(n):
        pivot=a[k][k];need(pivot>0,'exact spectral inequality not positive definite');pivots.append(str(pivot))
        for i in range(k+1,n):
            for j in range(i,n):a[j][i]=a[i][j]=a[i][j]-a[i][k]*a[k][j]/pivot
    return pivots


def enlarged_ball_certificate(runs):
    """Reproduce the attached 1/5000, weight-256 comparison in original Arb."""
    with ctx.workprec(PRECISION):
        original=runs['current'];proof=original['proof'];m=AOSReference(original['targets']['1']['graph']);n=m.n
        B=graph_constants(json.dumps(m.graph,sort_keys=True))[0];weights=list(map(fmpq,proof['reference_W']))
        A=B*fmpq_mat([[weights[i] if i==j else 0 for j in range(m.m)] for i in range(m.m)])*B.transpose()
        pi=fmpq_mat([[fmpq(1,n) for j in range(n)] for i in range(n)]);P=(A+pi).inv()
        curvature=[3*(fmpq(proof['center'][x])-2)**2-1 for x in m.nodes]
        D=fmpq_mat([[curvature[i] if i==j else 0 for j in range(n)] for i in range(n)])-A/64
        E=fmpq_mat([[int(i==j) if i<n-1 else -1 for j in range(n-1)] for i in range(n)])
        low=positive_definite_exact(E.transpose()*(D-fmpq(2,5)*P)*E)
        high=positive_definite_exact(E.transpose()*(14*P-D)*E)
        J0=arb_mat(fmpq_mat([[int(i==j) for j in range(n)] for i in range(n)])-A*D/32)
        r=arb(fmpq(1,5000));weight=256;amax=arb(infnorm(A));trace=arb(sum(P[i,i] for i in range(n))-1)
        C=m.vector(proof['center']);L=arb_mat([[arb(fmpq(x))] for x in proof['logW_center']])
        cr=(r*amax.sqrt()).upper();lr=r/weight
        Cbox=arb_mat([[arb(fmpq(proof['center'][x]),cr)] for x in m.nodes])
        Lbox=arb_mat([[arb(fmpq(x),lr.upper())] for x in proof['logW_center']])
        J=m.jacobian(Cbox,Lbox)
        block=lambda a,b,c,d:arb_mat([[J[i,j] for j in range(c,d)] for i in range(a,b)])
        cc=arb(fmpq(79,80))+norm_upper(block(0,n,0,n)-J0)*(amax*trace).sqrt()
        cw=norm_upper(block(0,n,n,n+m.m))*trace.sqrt()/weight
        wc=norm_upper(block(n,n+m.m,0,n))*amax.sqrt()*weight
        ww=m.decay+norm_upper(block(n,n+m.m,n,n+m.m)-m.decay*m.I)
        q=max((cc+cw).upper(),(wc+ww).upper());need(q<1,'enlarged full C/W ball does not contract')
        step=m.step(C,L);defect=max((norm_upper(step['after']-C)*trace.sqrt()).upper(),(weight*norm_upper(step['logW_after']-L)).upper())
        margin=(1-q)*r-defect;need(margin>0,'enlarged ball image margin')
        edge_radius=lambda i,j:r*arb(A[i,i]+A[j,j]-2*A[i,j]).sqrt()
        geo={chi:uniform_geometry(AOSReference(t['graph']),Cbox,Lbox,proof['center'],edge_radius) for chi,t in original['targets'].items()}
        need(all(g['complete_basins']==proof['complete_basins'][chi] for chi,g in geo.items()),'enlarged ball basin roster')
        return dict(schema='spark-completion-aos-enlarged-ball-proof-v1',radius='1/5000',weight=weight,
            exact_reference_spectral_bounds=['2/5','14'],reference_contraction='79/80',
            positive_definite_pivots={'lower':low,'upper':high},contraction=exact_bounds(q),
            center_defect=exact_bounds(defect),strict_image_margin=exact_bounds(margin),geometry=geo,
            split_upper=exact_bounds(m.os_read(Cbox,Lbox)['split_upper']),relative_dimension=30,
            proof_precision_bits=PRECISION,accepted_authority=False),P


def entry_checks(runs,anisotropic,operands,ball,P):
    """Actual interval coordinates, never stored scalar distances or point probes."""
    result={};m=operands['model'];C0=operands['center_C'];L0=operands['center_L']
    with ctx.workprec(PRECISION):
        U=arb_mat(operands['U']);Pa=arb_mat(P)
        for role,run in runs.items():
            charts={chi:AOSReference(t['graph']) for chi,t in run['targets'].items()}
            rows=[];an_entry=None;ball_entry=None;changes=[];previous=None;first_gain=None
            for step,row in enumerate(run['observations'],1):
                need(row['step']==step,'retained consecutive coverage');C,L=decode(m,row)
                need(sum(C.entries()).contains(21),'charge interval consistency')
                z=U*stack(C-C0,L-L0);an=max(abs(x).upper() for x in z.entries())
                an_lower=max(abs(x).lower() for x in z.entries())
                diff=C-C0;resource=(diff.transpose()*Pa*diff)[0,0].upper().sqrt().upper()
                history=ball['weight']*norm_upper(L-L0);bn=max(resource,history.upper())/arb(fmpq(ball['radius']))
                if an_entry is None:
                    if an<1:an_entry=step
                    else:need(an_lower>1,'earlier anisotropic membership unresolved')
                if ball_entry is None and bn<1:ball_entry=step
                signs=[]
                for i,j in m.pairs:
                    gap=C[i,0]-C[j,0];need(gap>0 or gap<0,'retained edge order unresolved');signs.append(1 if gap>0 else -1)
                if previous is not None:
                    for k,(old,new) in enumerate(zip(previous,signs)):
                        if old!=new:changes.append(dict(edge_id=m.edge_ids[k],before_step=step-1,after_step=step,before_sign=old,after_sign=new))
                previous=signs
                roster={chi:geometric_roster(chart,C,L) for chi,chart in charts.items()}
                if first_gain is None and roster==run['proof']['complete_basins']:first_gain=step
                if an_entry is not None:
                    need(an<1 and all(roster[chi]==anisotropic['geometry'][chi]['complete_basins'] for chi in roster),'anisotropic suffix leaves domain/roster')
                if ball_entry is not None:
                    need(bn<1 and all(roster[chi]==ball['geometry'][chi]['complete_basins'] for chi in roster),'enlarged-ball suffix leaves domain/roster')
                rows.append(dict(step=step,anisotropic_distance=[exact_bounds(an_lower)[0],exact_bounds(an)[1]],ball_distance=exact_bounds(bn),
                    resource_P_distance=exact_bounds(resource),weighted_logW_distance=exact_bounds(history),
                    complete_basins=roster))
            need(an_entry is not None and ball_entry is not None and an_entry+2<=len(rows) and ball_entry+2<=len(rows),'two-beat completion window')
            last=changes[-1] if changes else None
            need(last is None or an_entry>=last['after_step'],'entry before a later fixed-order reversal')
            checkpoints={str(k):dict(original_state=run['observations'][k-1],recomputed=rows[k-1])
                         for k in sorted({an_entry-1,an_entry,an_entry+1,an_entry+2,ball_entry-1,ball_entry,ball_entry+1,ball_entry+2,
                                          *([] if last is None else [last['before_step'],last['after_step']])}) if k>=1}
            result[role]=dict(role=role,original_entry=run['decision']['first_certified_entry'],original_window_end=run['decision']['target_completion_step'],
                anisotropic_entry=an_entry,anisotropic_window_end=an_entry+2,ball_entry=ball_entry,ball_window_end=ball_entry+2,
                window_beats=2,window_elapsed='64',first_spatial_gain=first_gain,last_order_reversal=last,
                all_order_reversals=changes,retained_states_checked=len(rows),two_chart_classifications_checked=2*len(rows),
                additional_event_gain=0,inherited_event_gain=int(role=='current'),reset_earns_live_gain=False,
                same_event_certificate_successor=True,numerical_trajectory_steps=0,
                interval_checks=rows,checkpoints=checkpoints)
    return result


def recompute():
    """Deterministic proof/check replay; never integrates a trajectory."""
    runs=originals();proposal=read_json(EARLIER+'AOSAnisotropicDomain.json')
    anisotropic,operands=anisotropic_certificate(runs,proposal)
    ball,P=enlarged_ball_certificate(runs)
    entries=entry_checks(runs,anisotropic,operands,ball,P)
    return sealed(dict(schema='spark-completion-aos-earlier-checks-v1',
        status='demonstrated_bounded_pending_review',family='A_OS',
        anisotropic=anisotropic,enlarged_ball=ball,runs=entries,
        original_execution_digests={r:read_json(BASE+'AOS-'+r+'.json.xz')['record_digest'] for r in runs},
        accepted_authority=False,native_completion=False,G4_accepted=False,
        additional_event_gain=0,trajectory_reruns=0,physical_parameters_changed=False))
