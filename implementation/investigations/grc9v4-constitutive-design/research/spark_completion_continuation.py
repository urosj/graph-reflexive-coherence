"""Bounded exact-equation SC-2 continuation, not native spark execution.

Fixed 512-bit Arb, 128 steps, mobility 1/1024, duration 32, split tolerance
1/10**11. No fallback, clipping, parameter search or early success selection.
"""
from fractions import Fraction as F
from math import ceil, floor
from flint import arb, ctx, fmpq
import spark_completion_basins as basins
from spark_completion_os_reference import COSReference

PRECISION, HORIZON = 512, 128
ETA, DT, TOL = F(1,1024), F(32), F(1,10**11)
POLICY = dict(sign=-1, gradient=F(4), hessian=F(1,4),
              contrast=F(1,2), core_resource=F(1,2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bound(x):
    """Outward rational bounds, never rounded decimal evidence."""
    scale = 2**128
    lo,hi = F(str(x.lower().fmpq())),F(str(x.upper().fmpq()))
    return [str(F(floor(lo*scale),scale)),str(F(ceil(hi*scale),scale))]


def frob(x):
    return sum(x[i,j]**2 for i in range(x.nrows()) for j in range(x.ncols())).sqrt()


def infnorm(x):
    return max(sum(abs(x[i,j]) for j in range(x.ncols())) for i in range(x.nrows()))


def defect_bounds(s):
    d=s['defect']
    return dict(operator_norm_lower=bound(max(abs(d[i,j]).lower()
                    for i in range(d.nrows()) for j in range(d.ncols()))),
                frobenius_upper=bound(frob(d)))


def geometric_roster(graph, C, order):
    """Certify every row flag, neighbor barrier and strict descent in Arb boxes."""
    low={n:F(str(C[i,0].lower().fmpq())) for i,n in enumerate(order)}
    high={n:F(str(C[i,0].upper().fmpq())) for i,n in enumerate(order)}
    edges=[(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],
            e['head']['port'],F(1)) for e in graph['edges']]
    adj=basins.neighbors(order,edges)
    rows=basins.row_intervals(order,edges,low,high)
    seeds={n for n in order if basins.seed_status(rows[n],POLICY)}
    anchors=set()
    for n in seeds:
        if low[n]>POLICY['core_resource'] and all(low[n]-high[v]>POLICY['contrast'] for v in adj[n]):
            anchors.add(n)
        else:
            need(high[n]<=POLICY['core_resource'] or any(high[n]-low[v]<=POLICY['contrast'] for v in adj[n]),
                 'unresolved anchor barrier')
    down={n:set() for n in order}
    for n in order:
        for v in adj[n]:
            if low[v]>high[n]:down[n].add(v)
            else:need(low[n]>high[v], 'unresolved edge order; no assumed tie')
    destinations={}
    def visit(n):
        if n not in destinations:
            destinations[n]=set().union(*(visit(v) for v in down[n])) if down[n] else {n}
        return destinations[n]
    for n in order:visit(n)
    domains={a:sorted(n for n in order if destinations[n]=={a}) for a in sorted(anchors)}
    return {a:b for a,b in domains.items() if len(b)>1}


def scaling_bound(model, C):
    """Exact Neumann upper bound for the companion's O(eta^4) split."""
    q=model.q; eta=q(1,1024)
    M0=q(3,4)*model.I+model.Le
    mi=M0.inv()
    base=model.read(C,model.I)
    u=q(2)*base['causal_flat']
    G=model.geometry(base['causal_flat'])-model.I
    M2=G*model.Le
    p2=-q(1,64)*model.Bt*model.B*G*model.Bt*C
    a,b=eta**2*infnorm(mi*M2),eta**2*infnorm(G)
    need(a<1 and b<1,'Neumann domain not proved')
    df=q(1,2)*eta**3/(1-b)*(infnorm(G)*infnorm(u)+infnorm(mi)*infnorm(p2-M2*u)/(1-a))
    coefficient=max(sum(model.overlap[i][j] for j in range(model.m)) for i in range(model.m))
    residual=q(coefficient,8)*(2*eta*infnorm(base['causal_flat'])*df+df**2)
    need(residual<q(1,10**11),'derived companion bound exceeds tolerance')
    return dict(neumann_current=str(a),neumann_hodge=str(b),
                split_operator_upper=str(residual))


def mechanism_pressure(model,C):
    q=model.q;eta=q(1,1024);dt=q(32);s=model.step(C,eta=eta,dt=dt);H=s['geometry']
    # Keep full physical closure, but wrongly freeze the potential at reference.
    j0=-eta*model.Bt*(q(1,64)*model.B*model.Bt*C-model.site(C))
    y=(q(3,4)*model.I+H*model.Le).solve(j0)
    frozen=C-dt*model.B*(j0+q(1,4)*y)
    # Keep generated potential, but wrongly use retained response as physical response.
    R=(model.I+model.Le*H).inv()
    wrong=(model.I-q(1,4)*R).solve(s['corrector']['baseline'])
    alternatives=dict(frozen_corrector_potential=frozen,
                      omitted_physical_similarity=C-dt*model.B*wrong,
                      predictor_used_for_continuity=C-dt*model.B*s['predictor']['current'])
    result={}
    for name,value in alternatives.items():
        separation=max(abs(value[i,0]-s['after'][i,0]).lower() for i in range(model.n))
        need(separation>0,'mechanism alternative not distinguished: '+name)
        result[name]=bound(separation)
    return result


def spectral_domain(graph):
    nodes=graph['live_node_ids'];adj={n:set() for n in nodes}
    for e in graph['edges']:
        a,b=e['tail']['node_id'],e['head']['node_id'];adj[a].add(b);adj[b].add(a)
    diameter=0
    for n in nodes:
        distances={n:0};todo=[n]
        for v in todo:
            for w in sorted(adj[v]-distances.keys()):
                distances[w]=distances[v]+1;todo.append(w)
        need(len(distances)==len(nodes),'disconnected research graph')
        diameter=max(diameter,max(distances.values()))
    lower=F(2,(len(nodes)-1)*diameter)
    need(lower>F(1,64),'selector cutoff not separated')
    return dict(diameter=diameter,nonconstant_eigenvalue_lower=str(lower),cutoff='1/64')


def checks(preflight):
    with ctx.workprec(PRECISION):
        target=preflight['targets']['1']
        # The two chiral charts have exactly the same ordered incidence, so
        # reuse numerical evolution, but certify each chart's fixed rows.
        negative=preflight['targets']['-1']['target_graph']
        for graph in (negative,target['target_graph']):
            need(graph['live_node_ids']==target['target_graph']['live_node_ids'],'chiral node order')
        pair=lambda g:[(e['tail']['node_id'],e['head']['node_id']) for e in g['edges']]
        need(pair(negative)==pair(target['target_graph']),'chiral incidence differs')
        initial={};exact_controls={};spectra={}
        for name,graph,roles in (('source',preflight['source_graph'],preflight['source_roles']),
                                 ('target',target['target_graph'],target['roles'])):
            exact=COSReference(graph,'rational');m=COSReference(graph,'arb')
            spectra[name]=spectral_domain(graph)
            need(all(sum(exact.B[i,j] for i in range(exact.n))==0 for j in range(exact.m)),
                 'incidence charge identity')
            for role,values in roles.items():
                C=exact.vector(values['resources']);E=exact.step(C)
                J,flat=exact.direct_similarity_read(C,E['geometry'])
                need(J==E['corrector']['current'] and flat==E['corrector']['causal_flat'],
                     'exact physical similarity disagreement')
                # Literal sum of vertex-star outer products, separate from overlap assembly.
                literal=exact.matrix(exact.m,exact.m)
                f=E['predictor']['causal_flat']
                for v in exact.nodes:
                    for i,e in enumerate(exact.edges):
                        for j,g in enumerate(exact.edges):
                            if v in e and v in g:literal[i,j]+=exact.q(1,8)*f[i,0]*f[j,0]
                need(exact.I+literal==E['geometry'],'literal star assembly disagreement')
                Cball=m.vector(values['resources']);s=m.step(Cball)
                for key in ('geometry','defect','after'):
                    need(all(s[key][i,j].contains(arb(E[key][i,j])) for i in range(E[key].nrows())
                             for j in range(E[key].ncols())), 'exact/Arb disagreement: '+key)
                original=defect_bounds(s)
                need(F(original['operator_norm_lower'][0])>TOL,'original strict-control rejection absent')
                companion=m.step(Cball,eta=m.q(1,1024),dt=m.q(32))
                need(frob(companion['defect'])<m.q(1,10**11),'companion split rejected')
                ec=exact.step(C,eta=exact.q(1,1024),dt=exact.q(32))
                jc,fc=exact.direct_similarity_read(C,ec['geometry'],eta=exact.q(1,1024))
                need(jc==ec['corrector']['current'] and fc==ec['corrector']['causal_flat'],
                     'companion full similarity disagreement')
                need(all(companion['after'][i,0].contains(arb(ec['after'][i,0])) for i in range(m.n)),
                     'companion exact/Arb disagreement')
                initial[name+'/'+role]=dict(original=original,companion=defect_bounds(companion),
                                            analytic_scaling=scaling_bound(exact,C))
                exact_controls[name+'/'+role]=dict(full_similarity=True,literal_star=True,
                                                   exact_rational_enclosed=True)
        histories={};pressure={}
        for role,values in target['roles'].items():
            m=COSReference(target['target_graph'],'arb');C=m.vector(values['resources'])
            pressure[role]=mechanism_pressure(m,C)
            rows=[];snapshots={};worst_split=m.q(0);max_radius=m.q(0);min_C=m.q(100)
            max_hodge=m.q(1);max_condition=m.q(1)
            for step in range(1,HORIZON+1):
                s=m.step(C,eta=m.q(1,1024),dt=m.q(32));C=s['after']
                split=frob(s['defect']);positive=min(C[i,0].lower() for i in range(m.n))
                need(split<m.q(1,10**11) and positive>0, 'finite continuation rejected')
                need(sum(C[i,0] for i in range(m.n)).contains(20),'charge enclosure lost')
                # Final-C read at consumed geometry and separate reference
                # restart. Neither read feeds another continuity update.
                final=m.read(C,s['geometry'],eta=m.q(1,1024))
                fresh=m.read(C,m.I,eta=m.q(1,1024))
                need(all(point['current'][i,0].is_finite() for point in (final,fresh)
                         for i in range(m.m)), 'poststate read failed')
                # H=I+sum positive star outer products, for the exact state
                # enclosed here. Bound its spectrum without assuming that a
                # midpoint or an independently rounded matrix is PSD.
                hmax=(1+sum(s['geometry'][i,i]-1 for i in range(m.m))).upper()
                # A conservative 2-norm bound through H^(1/2) similarity;
                # using cond(H), rather than sqrt(cond(H)), only weakens it.
                physical_condition=hmax/m.q(3,4)
                resolvent_condition=hmax*(1+hmax*infnorm(m.Le))
                need(physical_condition<10**12 and resolvent_condition<10**12,'conditioning guard')
                max_hodge=max(max_hodge,hmax);max_condition=max(max_condition,resolvent_condition)
                rosters={chi:geometric_roster(preflight['targets'][chi]['target_graph'],C,m.nodes)
                         for chi in ('1','-1')}
                descendants={chi:{a:b for a,b in r.items() if a in target['module'] or a=='p'}
                             for chi,r in rosters.items()}
                need(all(len(r)<2 for r in descendants.values()), 'unexpected organizational gain; review result')
                rows.append(dict(step=step,split_upper=bound(split)[1],minimum_resource=bound(positive)[0],
                                 basin_anchors={chi:sorted(r) for chi,r in rosters.items()}))
                worst_split=max(worst_split,split.upper());min_C=min(min_C,positive)
                max_radius=max(max_radius,max(C[i,0].rad().upper() for i in range(m.n)))
                if step in (1,16,64,HORIZON):
                    snapshots[str(step)]=dict(resources={n:bound(C[i,0]) for i,n in enumerate(m.nodes)},
                                             qualified_basins=rosters)
            alternate={n:3 if n in ('p','n1','n5') else 1 for n in m.nodes}
            distance=max(abs(C[i,0]-alternate[n]).upper() for i,n in enumerate(m.nodes))
            need(distance<m.q(1,8),'alternative branch box not reached')
            # Whole alternative equilibrium box has no qualified anchors:
            # the two high exterior nodes have missing rows, p has high
            # neighbors, and every low candidate fails extremum or contrast.
            for chi in ('1','-1'):
                g=preflight['targets'][chi]['target_graph']
                edges=[(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],e['head']['port'],F(1)) for e in g['edges']]
                lo={n:F(c)-F(1,8) for n,c in alternate.items()};hi={n:F(c)+F(1,8) for n,c in alternate.items()}
                adj=basins.neighbors(m.nodes,edges);rs=basins.row_intervals(m.nodes,edges,lo,hi)
                for n in m.nodes:
                    row_failure=any(-l<=POLICY['hessian'] for l,h in rs[n])
                    barrier_failure=any(hi[n]-lo[v]<=POLICY['contrast'] for v in adj[n])
                    need(row_failure or barrier_failure,'alternative no-anchor box not certified')
            histories[role]=dict(steps=rows,checkpoints=snapshots,minimum_resource=bound(min_C),
                maximum_split=bound(worst_split),maximum_resource_ball_radius=bound(max_radius),
                hodge_spectrum_lower='1',maximum_hodge_spectrum_upper=bound(max_hodge),
                maximum_resolvent_condition_upper=bound(max_condition),
                final_consumed_geometry_and_reference_restart_reads=HORIZON,
                alternate_branch_upper_nodes=['n1','n5','p'],alternate_box_distance=bound(distance),
                alternate_box_radius='1/8',alternate_box_has_no_qualified_basins=True,
                physical_trapping_of_alternate_box_proved=False,organized_branch_entry=False)
        # The scientific classifier must fail explicitly when row signs cannot
        # be certified. No arbitrary midpoint/tie resolution is permitted.
        try:basins.seed_status([(F(-3),F(3))]*3,POLICY)
        except basins.Uncertified:pass
        else:raise ValueError('ambiguous row flag accepted')
        return dict(parameters=dict(precision_bits=PRECISION,horizon=HORIZON,mobility=str(ETA),
                    timestep=str(DT),split_tolerance=str(TOL),kappa_H='1/2',chi_C='1/2',zeta_C='1/2',
                    kappa_M_C='0',kappa_Phi_C='1/64',tau_C='1',site_c0='2',site_a='1',site_mu='1'),
                    initial_reads=initial,exact_controls=exact_controls,mechanism_pressure=pressure,
                    selector_domains=spectra,
                    histories=histories,chiral_incidence_identity=True,
                    ambiguous_classifier_rejected=True,exact_equation_steps=2*HORIZON,
                    native_steps=0,native_events=0,completed_spark=False)
