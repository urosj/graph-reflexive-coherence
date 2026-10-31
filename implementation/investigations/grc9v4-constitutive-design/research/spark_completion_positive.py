"""Frozen supplied constructive candidate; rigorous local checks, no native claim."""
from fractions import Fraction as F
from math import ceil, floor
import hashlib
import json
from flint import arb, arb_mat, fmpq, fmpq_mat, ctx
from pygrc.models.grc_9_v4_expansion import _allocate
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph as Graph, GRC9V4PortEdge as Edge, GRC9V4PortEndpoint as End
import positive_candidate as supplied
import spark_completion_basins as basins
from spark_completion_os_reference import COSReference
from spark_completion_continuation import (
    POLICY, need, bound, frob, infnorm, geometric_roster, spectral_domain, mechanism_pressure,
)

NAMESPACE='sc2-positive-module'
PRECISION=8192  # selected for a 1024-step enclosure, not automatic escalation
HORIZON=1024
TRAP_RADIUS=F(1,2**20)


def norm_upper(matrix):
    """Frobenius upper bound; do not sqrt a zero-centered interval sum."""
    return sum(abs(matrix[i,j]).upper()**2 for i in range(matrix.nrows())
               for j in range(matrix.ncols())).sqrt().upper()


def compact_box(m,C):
    cells=[]
    for i in range(m.n):
        lo,hi=map(F,bound(C[i,0]))
        cells.append([arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))])
    return m.matrix(cells)


def content_id(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()


def fixture():
    source=Graph(tuple(supplied.SOURCE_NODES),tuple(
        Edge(f'positive-{i}','boundary',End(a,pa),End(b,pb))
        for i,(a,pa,b,pb) in enumerate(supplied.edges(True))))
    values={};targets={}
    for role in ('current','reset'):
        c=dict(supplied.BASE)
        if role=='reset':c['n1']+=F(1,64);c['n2']-=F(1,128);c['n3']-=F(1,128)
        edges=[(a,pa,b,pb,F(1))for a,pa,b,pb in supplied.edges(True)]
        rows=basins.row_intervals(source.live_node_ids,edges,c,c)
        gv=[x[0] for x in rows['v']]
        need(gv==[F(-3,25),F(-43,75),F(-43,75)],'source rows')
        need(sum(x*x for x in gv)==F(3779,5625)<16 and F(1,8)-min(-x for x in gv)==F(1,200),'trigger')
        need(basins.classify(source.live_node_ids,edges,c,POLICY)['basins']=={'p':set(c)},'parent')
        need(sum(c.values())==21,'source charge');values[role]=c
    for chirality in (-1,1):
        g,module,_=_allocate(source,'v',NAMESPACE,chirality,(0,0,0))
        aliases={module[0]:'core',**{v:f's{i}' for i,v in enumerate(module[1:],1)}}
        label=lambda v:aliases.get(v,v)
        actual={(label(e.tail.node_id),e.tail.port,label(e.head.node_id),e.head.port)for e in g.edges}
        need(actual==set(supplied.edges(False,chirality)),'literal D11 allocation mismatch')
        need(len(g.live_node_ids)==15 and len(g.edges)==16,'target dimensions')
        states={}
        for role,c in values.items():
            t={n:x for n,x in c.items() if n!='v'};t[module[0]]=F(0)
            t.update({n:p*c['v']for n,p in zip(module[1:],supplied.SHARES)})
            need(sum(t.values())==21 and t[module[2]]==F(651,320),'target charge/allocation')
            edges=[(e.tail.node_id,e.tail.port,e.head.node_id,e.head.port,F(1))for e in g.edges]
            need(set(basins.classify(g.live_node_ids,edges,t,POLICY)['basins'])=={'p'},'event-only gain')
            states[role]=t
        targets[str(chirality)]=dict(graph=g.to_payload(),module=list(module),aliases=aliases,states=states)
    return source.to_payload(),values,targets


def full_jacobian(model,C):
    """Analytic interval derivative of every predictor/geometry/corrector term."""
    m=model;q=m.q;n=m.n
    In=m.matrix([[int(i==j)for j in range(n)]for i in range(n)])
    curvature=m.matrix([[(3*(C[i,0]-2)**2-1) if i==j else 0 for j in range(n)]for i in range(n)])
    dp=q(1,64)*m.B*m.Bt-curvature
    yp=(q(3,4)*m.I+m.Le).solve(-q(1,1024)*m.Bt*dp)
    dfp=q(1,2)*yp
    step=m.step(C,eta=q(1,1024),dt=q(32))
    fp=step['predictor']['causal_flat'];H=step['geometry']
    y=q(2)*H*step['corrector']['causal_flat']
    M=q(3,4)*m.I+H*m.Le
    columns=[]
    for k in range(n):
        dH=m.matrix([[q(m.overlap[i][j],8)*(dfp[i,k]*fp[j,0]+fp[i,0]*dfp[j,k])
                      for j in range(m.m)]for i in range(m.m)])
        ek=m.matrix([[int(i==k)]for i in range(n)])
        dphi=q(1,64)*m.B*(dH*m.Bt*C+H*m.Bt*ek)-curvature*ek
        dj0=-q(1,1024)*m.Bt*dphi
        dy=M.solve(dj0-dH*m.Le*y)
        columns.append(ek-q(32)*m.B*(dj0+dy/4))
    return m.matrix([[columns[j][i,0]for j in range(n)]for i in range(n)])


def propose_center(m):
    """Newton proposes a rational center. The subsequent full-map proof certifies it."""
    with ctx.workprec(512):
        C=m.matrix([[m.q(3 if n in ('p',NAMESPACE+'/satellite/2') else 1)+m.q(2,15)]for n in m.nodes])
        lam=m.q(0);L=m.B*m.Bt
        for _ in range(10):
            D=m.matrix([[(3*(C[i,0]-2)**2-1 if i==j else 0)-L[i,j]/64
                          for j in range(m.n)]for i in range(m.n)])
            M=m.matrix([[D[i,j] if i<m.n and j<m.n else -1 if i<m.n else 1 if j<m.n else 0
                          for j in range(m.n+1)]for i in range(m.n+1)])
            r=m.site(C)-L*C/64
            delta=M.solve(m.matrix([[r[i,0]-lam]for i in range(m.n)]+[[sum(C[i,0]for i in range(m.n))-21]]))
            C=m.matrix([[(C[i,0]-delta[i,0]).mid()]for i in range(m.n)]);lam=(lam-delta[m.n,0]).mid()
        # Exact fixed charge, with dyadic coordinates and no trajectory normalization.
        vals=[F(floor(F(str(C[i,0].mid().fmpq()))*2**160),2**160)for i in range(m.n-1)]
        vals.append(F(21)-sum(vals))
        return {n:str(x) for n,x in zip(m.nodes,vals)}


def trap(target):
    with ctx.workprec(512):
        m=COSReference(target['graph'],'arb');e=COSReference(target['graph'],'rational');n=m.n
        center=propose_center(m);C=m.vector(center)
        A=e.B*(e.I+(e.q(3,4)*e.I+e.Le).inv()/4)*e.Bt
        pi=e.matrix([[e.q(1,n)for j in range(n)]for i in range(n)])
        P=(A+pi).inv();trace=sum(P[i,i]for i in range(n))-1
        amax=infnorm(A);amin=1/trace
        r=m.q(1,2**20)
        # Rational outward coordinate enclosure of the metric ball on E.
        R=F(ceil(F(str((arb(amax).sqrt()*r).upper().fmpq()))*2**80),2**80)
        box=m.matrix([[arb(fmpq(center[node]),fmpq(str(R)))]for node in m.nodes])
        D=e.matrix([[(3*(e.q(1)*fmpq(center[m.nodes[i]])-2)**2-1 if i==j else 0)
                     -(e.B*e.Bt)[i,j]/64 for j in range(n)]for i in range(n)])
        L=e.B*e.Bt
        dmin=min(3*(fmpq(center[v])-2)**2-1 for v in m.nodes)-infnorm(L)/64
        dmax=max(3*(fmpq(center[v])-2)**2-1 for v in m.nodes)
        need(dmin>0 and amax*dmax/32<2,'reference contraction domain')
        q0=max(1-amin*dmin/32,amax*dmax/32-1)
        J0=e.matrix([[int(i==j)for j in range(n)]for i in range(n)])-A*D/32
        J=full_jacobian(m,box)
        perturb=norm_upper(J-arb_mat(J0))*(arb(amax)*arb(trace)).sqrt()
        contraction=arb(q0)+perturb
        need(contraction<1,f'full OS metric contraction unproved: q0={arb(q0).str(12)}, perturbation={perturb.str(12)}')
        T=m.step(C,eta=m.q(1,1024),dt=m.q(32))['after'];delta=T-C
        center_defect=frob(delta)*arb(trace).sqrt()
        margin=(1-contraction)*r-center_defect
        need(margin>0,'strict full-map invariant ball unproved')
        in_box_step=m.step(box,eta=m.q(1,1024),dt=m.q(32))
        need(norm_upper(in_box_step['defect'])<m.q(1,10**11),'trap split unproved')
        rosters=geometric_roster(target['graph'],box,m.nodes)
        expected={'p':['p','private'],NAMESPACE+'/satellite/2':['n2','n8',NAMESPACE+'/satellite/2']}
        need({a:sorted(b)for a,b in rosters.items()}=={a:sorted(b)for a,b in expected.items()},'trap complete basin roster')
        # Full derivative pressure: use the fundamental theorem on finite
        # charge-preserving segments; difference quotients must be enclosed.
        exact_center=e.vector(center);Jcenter=full_jacobian(e,exact_center)
        need(all(J[i,j].contains(arb(Jcenter[i,j]))for i in range(n)for j in range(n)), 'rational Jacobian not enclosed')
        need(all(sum(Jcenter[i,j]for i in range(n))==1 for j in range(n)), 'derivative charge identity')
        for index in (0,4,9):
            v=e.matrix([[int(i==index)-int(i==n-1)]for i in range(n)])
            h=e.q(1,2**40)
            difference=(e.step(exact_center+h*v,eta=e.q(1,1024),dt=e.q(32))['after']
                        -e.step(exact_center,eta=e.q(1,1024),dt=e.q(32))['after'])/h
            enclosure=J*arb_mat(v)
            need(all(enclosure[i,0].contains(arb(difference[i,0]))for i in range(n)), 'Jacobian finite-segment control')
        return dict(center=center,radius=str(TRAP_RADIUS),coordinate_radius=str(R),
                    metric='(A0 + 11^T/n)^-1 restricted to exact charge-21 tangent space',
                    A_max=str(amax),A_min=str(amin),inverse_trace=str(trace),
                    q_reference=str(q0),derivative_perturbation=bound(perturb),
                    contraction=bound(contraction),center_defect=bound(center_defect),
                    strict_image_margin=bound(margin),split_upper=bound(norm_upper(in_box_step['defect'])),
                    complete_basins=rosters,relative_dimension=n-1,
                    actual_full_map_trapping=True,represented_conservation_lift=False),P


def checks(exploratory):
    source,source_values,targets=fixture()
    proof,P=trap(targets['1'])
    roles={};initial={};t=targets['1']
    with ctx.workprec(PRECISION):
        model=COSReference(t['graph'],'arb');m=model
        center=m.vector(proof['center']);trace=m.q(fmpq(proof['inverse_trace']))
        # Same numerical graph in both charts, but separately certify all rows
        # and full domains throughout the complete trapping neighborhood.
        neg=COSReference(targets['-1']['graph'],'rational')
        need(m.nodes==neg.nodes and m.edges==neg.edges,'chiral numerical graph mismatch')
        box=m.matrix([[arb(fmpq(proof['center'][n]),fmpq(proof['coordinate_radius']))]for n in m.nodes])
        for chi,target in targets.items():
            need(geometric_roster(target['graph'],box,m.nodes)==proof['complete_basins'],'chiral trap roster')
        proof['selector_domain']=spectral_domain(t['graph'])
        proof['minimum_edge_order_gap']=bound(min(abs(box[m.nodes.index(a),0]-box[m.nodes.index(b),0]).lower()for a,b in m.edges))
        need(F(proof['minimum_edge_order_gap'][0])>0,'fixed full descent DAG not proved')
        for label,g,states in (('source',source,source_values),('target',t['graph'],t['states'])):
            e=COSReference(g,'rational');b=COSReference(g,'arb')
            spectral_domain(g)
            for role,state in states.items():
                vals={n:str(x)for n,x in state.items()};C=e.vector(vals)
                es=e.step(C,eta=e.q(1,1024),dt=e.q(32))
                current,flat=e.direct_similarity_read(C,es['geometry'],eta=e.q(1,1024))
                need(current==es['corrector']['current'] and flat==es['corrector']['causal_flat'],'exact closure')
                bs=b.step(b.vector(vals),eta=b.q(1,1024),dt=b.q(32))
                need(norm_upper(bs['defect'])<b.q(1,10**11),'source/target split')
                need(all(bs['after'][i,0].contains(arb(es['after'][i,0]))for i in range(b.n)),'rational first-update enclosure')
                initial[label+'/'+role]=dict(split_upper=bound(norm_upper(bs['defect'])),
                    exact_similarity_and_first_update=True,scientific_input_id=content_id(dict(graph=g,resources=vals,parameters=supplied.PARAMS)))
        aliases=t['aliases'];alias=lambda n:aliases.get(n,n)
        for role,state in t['states'].items():
            C=m.vector({n:str(x)for n,x in state.items()})
            snapshots={};trace_rows=[];first_gain=None;minimum=m.q(100);max_split=m.q(0)
            max_condition=m.q(0);max_radius=m.q(0);pressure=mechanism_pressure(m,C)
            expected=exploratory['roles'][role]
            for k in range(1,HORIZON+1):
                step=m.step(C,eta=m.q(1,1024),dt=m.q(32));C=step['after']
                split=norm_upper(step['defect']);positive=min(C[i,0].lower()for i in range(m.n))
                need(split<m.q(1,10**11) and positive>0,'continuation domain')
                need(sum(C[i,0]for i in range(m.n)).contains(21),'exact-charge enclosure')
                for H in (step['geometry'],m.I):
                    point=m.read(C,H,eta=m.q(1,1024))
                    need(all(point['current'][i,0].is_finite()for i in range(m.m)),'final/restart read')
                hmax=(1+sum(step['geometry'][i,i]-1 for i in range(m.m))).upper()
                condition=hmax*(1+hmax*infnorm(m.Le))
                need(condition<10**12,'research conditioning limit')
                rounded=compact_box(m,C)
                rosters={chi:geometric_roster(target['graph'],rounded,m.nodes)for chi,target in targets.items()}
                # Parent footprint is the whole allocated graph; only surviving
                # parent and module anchors are eligible descendants.
                gains={chi:len({a for a in r if a=='p' or a in t['module']})-1
                       if any(a in t['module']for a in r) else 0 for chi,r in rosters.items()}
                gain=all(x>=1 for x in gains.values())
                if gain and first_gain is None:first_gain=k
                if first_gain is not None:need(gain,'spatial gain lost before trap')
                if k<=512:
                    mapped={chi:{alias(a):sorted(alias(v)for v in members)for a,members in r.items()}
                            for chi,r in rosters.items()}
                    need(mapped==expected['observations'][k-1]['basins'],'supplied numerical classification disagreement')
                distance=norm_upper(C-center)*trace.sqrt()  # conservative P-norm upper bound on E
                entry=distance<m.q(1,2**20)
                minimum=min(minimum,positive);max_split=max(max_split,split)
                max_condition=max(max_condition,condition.upper())
                max_radius=max(max_radius,max(C[i,0].rad().upper()for i in range(m.n)))
                trace_rows.append(dict(step=k,minimum_resource=bound(positive)[0],split_upper=bound(split)[1],
                    qualified_basins=rosters,trap_distance_upper=bound(distance)[1]))
                if k in (1,40,42,128,512) or entry:
                    snapshots[str(k)]={n:bound(C[i,0])for i,n in enumerate(m.nodes)}
                if entry:break  # full-map contraction certifies every later exact step
            need(entry,'no certified trap entry within the fixed horizon')
            need(first_gain==expected['first_gain_step']['1']==expected['first_gain_step']['-1'],'first gain disagreement')
            roles[role]=dict(first_gain_step=first_gain,certified_trap_entry_step=k,
                trap_distance_upper=bound(distance),minimum_resource=bound(minimum),maximum_split=bound(max_split),
                maximum_condition_upper=bound(max_condition),maximum_ball_radius=bound(max_radius),
                observations=trace_rows,checkpoints=snapshots,mechanism_pressure=pressure,
                all_subsequent_exact_steps_certified_by_trap=True)
        return dict(status='positive_exact_equation_entry_and_full_map_trap_not_native_completion',
            parameters={k:str(v)for k,v in supplied.PARAMS.items()},precision_bits=PRECISION,
            maximum_steps_per_role=HORIZON,stop_rule='first certified trap entry; no numerical continuation needed thereafter',
            source_graph=source,source_resources={r:{n:str(x)for n,x in v.items()}for r,v in source_values.items()},
            shares=[str(x)for x in supplied.SHARES],targets={chi:dict(graph=v['graph'],module=v['module'],
                resources={r:{n:str(x)for n,x in state.items()}for r,state in v['states'].items()},
                research_identity=content_id(v))for chi,v in targets.items()},
            initial_reads=initial,trap=proof,roles=roles,
            source_postbeat_formation_proved=False,native_admission=False,native_steps=0,native_events=0,
            completed_spark=False,SC1_closed=True,SC2_closed=False,debts_closed=[])
