"""Independent SC-1 scientific pressure retained from the supplied review.

The exact graph enumeration, reconstructed example and three countermodels are
reused. Repository adapters replace the supplied package's upload-directory
lookup; native declarations are read from their existing repository artifacts.
Called by scripts/check_spark_completion_sc1.py --check. No native evolution.
"""
from __future__ import annotations
import hashlib, itertools, json, lzma
from fractions import Fraction as F
from pathlib import Path


def reachability(nodes, edges, psi):
    n=len(nodes); pos={v:i for i,v in enumerate(nodes)}
    adj={v:set() for v in nodes}
    for u,v in edges:
        if psi[u]>psi[v]: adj[u].add(v)
        elif psi[v]>psi[u]: adj[v].add(u)
    reach=[[i==j for j in range(n)] for i in range(n)]
    for u in nodes:
        for v in adj[u]: reach[pos[u]][pos[v]]=True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n): reach[i][j] |= reach[k][j]
    terminals={v for v in nodes if not adj[v]}
    ends={u:{v for v in terminals if reach[pos[u]][pos[v]]} for u in nodes}
    regions={s:{u for u in nodes if ends[u]=={s}} for s in terminals}
    return adj,ends,regions


def enumerate_descent():
    total=0; qualified_pairs=0; checked_paths=0
    for n in range(5):
        nodes=tuple(range(n)); pairs=list(itertools.combinations(nodes,2))
        for bits in range(1<<len(pairs)):
            edges=[p for j,p in enumerate(pairs) if (bits>>j)&1]
            nbr={v:set() for v in nodes}
            for u,v in edges: nbr[u].add(v); nbr[v].add(u)
            for values in itertools.product(range(3),repeat=n):
                psi=dict(zip(nodes,values)); adj,ends,regions=reachability(nodes,edges,psi)
                def recursive(v):
                    if not adj[v]: return {v},0
                    children=[recursive(w) for w in adj[v]]
                    return set().union(*(x[0] for x in children)),1+max(x[1] for x in children)
                for v in nodes:
                    terminal_set,length=recursive(v)
                    assert terminal_set==ends[v] and ends[v]
                    assert length<=n-1
                covered=set()
                for s,region in regions.items():
                    assert not (covered&region); covered |= region
                    for v in region: assert adj[v]<=region
                # Strict local minima with barrier 1/2 and nontrivial domains.
                # This is a superset of row-qualified SC-1 anchors, so the graph
                # theorem checks apply in particular to row-qualified anchors.
                anchors=[s for s in regions if len(regions[s])>=2 and nbr[s]
                         and all(psi[j]-psi[s]>F(1,2) for j in nbr[s])]
                for s,t in itertools.combinations(anchors,2):
                    qualified_pairs+=1
                    stack=[(s,(s,))]
                    while stack:
                        v,path=stack.pop()
                        if v==t:
                            assert max(psi[z] for z in path)>max(psi[s],psi[t])+F(1,2)
                            checked_paths+=1
                        else:
                            for w in nbr[v]-set(path): stack.append((w,path+(w,)))
                total+=1
    return dict(graph_landscape_pairs=total,levels=[0,1,2],max_vertices=4,
                row_predicate_scope='graph theorem on a superset of qualified anchors',
                qualified_anchor_pairs=qualified_pairs,connecting_simple_paths=checked_paths,
                all_route_termination_forward_closure_disjointness_and_barriers=True)


def rows(nodes,edges,c):
    out={v:[F(0)]*3 for v in nodes}; den={v:[F(0)]*3 for v in nodes}
    for u,ru,v,rv,w in edges:
        for i,r,j in [(u,ru,v),(v,rv,u)]:
            out[i][r]+=w*(c[j]-c[i]);den[i][r]+=w
    return {i:[out[i][a]/den[i][a] if den[i][a] else F(0) for a in range(3)] for i in nodes}


def classify(nodes,edges,c,sign=-1,eg=F(4),eh=F(1,4),barrier=F(1,2),cmin=F(1,2)):
    psi={v:sign*c[v] for v in nodes}
    adj,ends,regions=reachability(nodes,[(u,v) for u,_,v,_,_ in edges],psi)
    g=rows(nodes,edges,c);nbr={v:set() for v in nodes}
    for u,_,v,_,_ in edges: nbr[u].add(v);nbr[v].add(u)
    return {s:sorted(region) for s,region in regions.items()
            if sum(v*v for v in g[s])<eg*eg and min(sign*v for v in g[s])>eh
            and c[s]>cmin and nbr[s]-{s}
            and all(psi[j]-psi[s]>barrier for j in nbr[s]) and len(region)>=2}


def reconstructed_toy():
    src=('p','v','a','b','d','f','e','g')
    # Endpoint row numbers are 0-based; distinct occupied rows/ports are used.
    se=[('p',0,'a',0,F(1)),('p',1,'b',0,F(1)),('p',2,'v',0,F(1)),
        ('v',1,'d',0,F(1)),('v',1,'f',0,F(1)),('v',2,'e',0,F(1)),('v',2,'g',0,F(1))]
    sc={v:F(3 if v=='p' else 2 if v=='v' else 1) for v in src}
    assert sum(sc.values())==11
    assert classify(src,se,sc)=={'p':sorted(src)}
    nodes=('p','x','y','m','a','b','d','f','e','g')
    te=[('p',0,'a',0,F(1)),('p',1,'b',0,F(1)),('p',2,'m',0,F(1)),
        ('x',0,'d',0,F(1)),('x',1,'f',0,F(1)),('x',2,'m',1,F(1)),
        ('y',0,'e',0,F(1)),('y',1,'g',0,F(1)),('y',2,'m',2,F(1))]
    c={v:sc[v] for v in src if v!='v'};c.update(x=F(3,4),m=F(1,2),y=F(3,4))
    assert sum(c.values())==11 and set(classify(nodes,te,c))=={'p'}
    center={v:F(2) if v in ('p','x','y') else F(5,7) for v in nodes}
    assert sum(center.values())==11
    expected={'p':['a','b','p'],'x':['d','f','x'],'y':['e','g','y']}
    radius=F(1,14); q=F(1,2); eps=F(1,112)
    low=F(5,7)-radius;contrast=(2-radius)-(F(5,7)+radius)
    maxcontrast=(2+radius)-(F(5,7)-radius)
    assert low==F(9,14) and contrast==F(8,7)
    assert 3*maxcontrast**2 < 16 and contrast>F(1,2) and contrast>F(1,4)
    assert radius-q*radius-eps==F(3,112)
    trace=[]
    for k in range(1,8):
        c={v:center[v]+q*(c[v]-center[v]) for v in nodes}
        distance=max(abs(c[v]-center[v]) for v in nodes)
        assert sum(c.values())==11 and classify(nodes,te,c)==expected
        trace.append(dict(step=k,distance=str(distance),in_box=distance<=radius,basins=sorted(expected)))
    assert next(r['step'] for r in trace if r['in_box'])==5
    corners=0
    for plus in itertools.combinations(nodes,5):
        plus=set(plus);x={v:center[v]+(radius if v in plus else -radius) for v in nodes}
        assert sum(x.values())==11 and classify(nodes,te,x)==expected
        corners+=1
    return dict(scope='independent abstract graph reconstruction; compared with the local reference, not a native V4 map',
                nodes=list(nodes),edges=[list(e[:4])+[str(e[4])] for e in te],
                source_parent='p',relative_dimension=9,exact_charge='11',radius=str(radius),
                contraction=str(q),minimum_resource=str(low),edge_order_margin=str(contrast),
                image_margin=str(radius*(1-q)),full_step_error=str(eps),remaining_image_margin=str(radius*(1-q)-eps),
                basins=expected,trace=trace,charge_slice_box_vertices_checked=corners,
                actual_V4_map=False,actual_D11_event=False)


def capacity_counterexample():
    # Continuous positive inflow can coexist with pointwise E_n/T_n < iota
    # when the ratio tends to iota. Error here deliberately cancels the inflow.
    iota=F(1,4);c0=F(1);Q=F(3);rows=[]
    for n in [1,2,8,64,1024]:
        E=(n-1)*iota;cs=c0+iota*n-E
        assert E/n<iota and cs==F(5,4) and 0<cs<Q
        assert iota*n<=Q-c0+E
        rows.append(dict(n=n,error=str(E),error_rate=str(E/n),sink_resource=str(cs)))
    return dict(scope='literal pointwise-below reading, not a counterexample to a uniform-gap premise',
                inflow=str(iota),charge=str(Q),samples=rows,
                valid_exclusion_condition='iota*T_n - E_n eventually exceeds Q_max-C_s0; sufficient: T_n->infinity and limsup E_n/T_n < iota')


def seed_rounding():
    exact=[F(1,3),F(2,3),F(2,3)]
    rounded=[F(float(x)) for x in exact]
    assert sum(x*x for x in exact)==1
    assert sum(x*x for x in rounded)<1
    assert min(rounded)>F(1,4)
    # All row inputs can be exact dyadics: 3 equal weights and these
    # resource differences. Strict neighbor barrier Delta=1/8 holds.
    diffs=[[F(1,4),F(1,4),F(1,2)], [F(1,2),F(1,2),F(1)], [F(1,2),F(1,2),F(1)]]
    assert [sum(r)/3 for r in diffs]==exact
    assert min(x for r in diffs for x in r)>F(1,8)
    return dict(scope='exact row qualification and represented row qualification are distinct; no native completion counterexample',
                exact_rows=list(map(str,exact)),represented_hex=[float(x).hex() for x in exact],
                exact_squared_norm='1',represented_squared_norm=str(sum(x*x for x in rounded)),
                exact_strict_gradient_pass=False,represented_strict_gradient_pass=True,
                row_neighbor_differences=[[str(x) for x in r] for r in diffs])


def constraint_rounding():
    # The relative image margin does not bound errors normal to the charge slice.
    r=F(1,4);q=F(1,2);eps=F(1,32);star=(F(1,2),F(1,2))
    out=(star[0]+eps,star[1]+eps)
    assert eps<(1-q)*r and sum(out)!=1
    return dict(scope='charge-slice counterexample, not a native step',
                K='x1+x2=1, |xi-1/2|<=1/4',q=str(q),relative_image_margin=str((1-q)*r),
                norm_error=str(eps),represented_point=list(map(str,out)),charge=str(sum(out)),in_exact_K=False,
                tolerance_aware_example=dict(error_per_coordinate=str(F(1,2**50)),
                    charge_error=str(F(1,2**49)),charge_tolerance='1e-11',
                    within_tolerance=F(1,2**49)<F(1,10**11),in_exact_charge_slice=False))


def native_bindings(inputs):
    result={}
    for fam in ['C_OS','C_CI','A_CI','A_PC']:
        path=inputs/f'P9-10.1a-Pressure-{fam}.json.xz'
        assert path.is_file(), path
        data=json.loads(lzma.decompress(path.read_bytes()))
        obs=data['evidence']['observations']
        params_seen=[];nchecks=0; topology_sizes=set(); profile_ids=set()
        for case in obs:
            for root in case['selected_roots'].values():
                inp=root['recipe']['inputs']; ref=inp['reference']; p=ref['profile']['params_resolved']
                graph=ref['graph']; ns=graph['live_node_ids']; es=graph['edges']
                assert len(es)==len(ns)-1 and ns
                adjacency={n:set() for n in ns}
                for e in es:
                    u=e['tail']['node_id'];v=e['head']['node_id']
                    assert u!=v
                    adjacency[u].add(v);adjacency[v].add(u)
                reached=set(); stack=[ns[0]]
                while stack:
                    u=stack.pop()
                    if u not in reached:
                        reached.add(u);stack.extend(adjacency[u]-reached)
                assert len(reached)==len(ns)
                assert all(v==0 for row in ref['K4_base'] for v in row)
                assert ref['context']['value']=={}
                topology_sizes.add((len(ns),len(es)))
                identity=ref['profile']['identity_payload']
                assert identity['profile_family_id']==fam
                assert identity['geometry_profile_id']=='affine_reference_relative_v1'
                assert p['common']['measure_profile_id']=='unit_vertex_measure_v1'
                profile_ids.add(identity['params_hash'])
                # Retain exact key contracts rather than inferring native behavior.
                assert p['common']['boundary_policy_id']=='closed_no_flux_v1'
                assert p['common']['context_contract_id']=='constant_zero_context_v1'
                cand=p['candidate'];name='site_potential_id' if fam.startswith('A') else 'potential_evaluator_id'
                assert cand[name]=='quadratic_site_potential_zero_derivative_v1'
                eta=cand.get('eta',cand.get('eta_C'))
                stiffness=cand.get('kappa_c',cand.get('kappa_Phi_C'))
                assert eta>0 and stiffness>0
                if fam.startswith('A'):
                    assert cand['tau_A']>0 and cand['W_floor']>0
                    assert all(w>0 for w in inp['current']['W_A'])
                    assert p['geometry']['candidate_adapter_id']=='candidate_a_exact_star_adapter_v1'
                    # With positive W and W_hat, |q_A|<1. This exact bound
                    # implies positive current denominators throughout that domain.
                    assert abs(F(cand['zeta_A'])*F(cand['chi_A']))<1
                    assert cand['conductance_evaluator_id']=='curvature_disabled_G_W_v1'
                    if fam=='A_PC':
                        assert p['realization']['tau_PC']>0
                        assert p['realization']['writer_id']=='zero_order_hold_exponential_v1'
                else:
                    assert all(w>0 for w in cand['W_C_tr'].values())
                params_seen.append(dict(site_potential=cand[name],eta=cand.get('eta',cand.get('eta_C')),
                                        stiffness=cand.get('kappa_c',cand.get('kappa_Phi_C')),
                                        kappa_H=p['geometry']['kappa_H'],tau_PC=p['realization'].get('tau_PC')))
                nchecks+=1
        result[fam]=dict(source_file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         role_reads=nchecks,topology_sizes=[list(pair) for pair in sorted(topology_sizes)],profile_parameter_ids=sorted(profile_ids),declaration_checks='connected trees; zero structural base; closed boundary; zero context; zero site derivative',
                         unique_parameter_rows=list({json.dumps(x,sort_keys=True):x for x in params_seen}.values()))
    return result


def correction_checks(basins):
    """Turn the review's countermodels into checks of the corrected interface."""
    results={}
    def reject(name, call, expected):
        try:
            call()
        except basins.Uncertified as exc:
            assert str(exc)==expected, (name,str(exc))
        else:
            raise AssertionError(name+': unexpectedly certified')
        results[name]=expected

    policy=dict(sign=1,gradient=F(1),hessian=F(1,4))
    exact=(F(1,3),F(2,3),F(2,3))
    rounded=tuple(F(float(x)) for x in exact)
    errors=tuple(abs(x-y) for x,y in zip(exact,rounded))
    assert basins.seed_status([(x,x) for x in rounded],policy)
    assert not basins.seed_status([(x,x) for x in exact],policy)
    reject('represented_pass_at_exact_boundary',
           lambda:basins.certified_seed_agreement(exact,rounded,errors,policy),
           'unresolved_seed_predicate')
    reject('row_bound_understated',
           lambda:basins.certified_seed_agreement(exact,rounded,(F(0),)*3,policy),
           'invalid_row_bound')
    assert basins.certified_seed_agreement((F(1,2),)*3,(F(1,2),)*3,(F(1,64),)*3,policy)
    assert not basins.certified_seed_agreement((F(1),)*3,(F(1),)*3,(F(1,64),)*3,policy)
    results['strict_positive_and_negative_row_agreement']=True
    for name,error in [('normal_error',F(1,32)),('below_charge_tolerance',F(1,2**50))]:
        reject(name,lambda e=error:basins.require_exact_charge_slice((F(1,2)+e,)*2,F(1)),
               'outside_exact_charge_slice')
    basins.require_exact_charge_slice((F(1,2)+F(1,32),F(1,2)-F(1,32)),F(1))
    results['tangent_error_preserves_charge']=True

    # A charge-preserving map has distinct fixed points on distinct charge
    # slices: making their union a slab does not yield global contraction.
    def charge_family(point):
        mean=sum(point)/len(point)
        return tuple(mean+F(1,2)*(x-mean) for x in point)
    a,b=(F(1,2),)*2,(F(3,4),)*2
    assert charge_family(a)==a and charge_family(b)==b and a!=b
    results['charge_slab_not_one_contraction']=dict(distance_ratio='1')

    # Symbolic affine error budgets E(T)<=a*T+b admit a finite capacity
    # exclusion only with an actual rate gap iota-a>0, not sampled E(T)/T<iota.
    iota,Q,c0=F(1,4),F(3),F(1)
    def horizon(rate,offset):
        basins.need(rate<iota,'no_uniform_error_rate_gap')
        return max(F(0),(Q-c0+offset)/(iota-rate))
    reject('pointwise_below_is_not_uniform_gap',
           lambda:horizon(iota,-iota),'no_uniform_error_rate_gap')
    assert horizon(F(1,8),F(0))==16
    results['uniform_gap_finite_horizon']='16'

    # A loop-free anchor must beat both the Hessian and neighbor margins.
    eg,eh,contrast=F(1),F(1,4),F(3,4)
    assert eg**2>3*eh**2 and eg**2<=3*max(eh,contrast)**2
    results['seed_only_inequality_not_anchor_feasibility']=True
    old=tuple(['s']+list(range(9)))
    edges=tuple(('s',i+1,i,1,F(1)) for i in range(9))
    c={n:F(2) if n=='s' else F(17,8) for n in old}
    p=dict(sign=1,gradient=eg,hessian=eh,contrast=F(1,16),core_resource=F(1,2))
    rows=basins.row_intervals(old,edges,c,c)['s']
    assert min(lo for lo,_ in rows)<eh and sum(lo**2 for lo,_ in rows)<eg**2
    assert not basins.classify(old,edges,c,p)['basins']
    results['saturated_candidate_without_qualified_parent']=True

    # Exact rational mode check of the A resource-block formula, not a
    # numerical proof of the nonlinear V4 theorem (see the analytic note).
    L=((F(1),F(-1)),(F(-1),F(1)))
    mode=(F(1),F(-1));lam=F(2);h=F(1,16);eta=kappa=F(1);w=F(3,4)
    lap=lambda v:tuple(sum(x*y for x,y in zip(row,v)) for row in L)
    output=tuple(x+h*eta*kappa*w*w*y for x,y in zip(mode,lap(lap(mode))))
    multiplier=1+h*eta*kappa*w*w*lam*lam
    assert sum(mode)==0 and output==tuple(multiplier*x for x in mode) and multiplier>1
    results['A_uniform_fixed_charge_mode_expands']=str(multiplier)
    return results


def checks(root, basins, contraction, geometric):
    inv=root/'implementation/investigations/grc9v4-constitutive-design'
    submitted=json.loads((inv/'evidence/spark-completion/review/SC1ScientificPressureSubmitted.json').read_bytes())
    assert contraction==submitted['isolated_supplied_contraction_checks']
    result=dict(
        scope='independent exact pressure plus repository declaration checks; zero native trajectories',
        descent=enumerate_descent(),
        reconstructed_abstract_example=reconstructed_toy(),
        capacity_pointwise_counterexample=capacity_counterexample(),
        exact_vs_represented_seed=seed_rounding(),
        relative_charge_slice_control=constraint_rounding(),
        earlier_native_declaration_checks=native_bindings(root/'implementation/phase-9-grcv4/tranche-10'),
        correction_checks=correction_checks(basins))
    for name in ('descent','capacity_pointwise_counterexample','exact_vs_represented_seed','relative_charge_slice_control'):
        assert result[name]==submitted[name],name
    assert sum(r['role_reads'] for r in result['earlier_native_declaration_checks'].values())==112
    for family,row in result['earlier_native_declaration_checks'].items():
        historical=submitted['earlier_native_declaration_checks'][family]
        serialized=json.loads(json.dumps(row))
        assert all(serialized[key]==historical[key] for key in historical),family
    retained=geometric['abstract_positive'];toy=result['reconstructed_abstract_example']
    assert toy['trace']==retained['trace']
    for key in ('radius','contraction','relative_dimension','minimum_resource','edge_order_margin',
                'image_margin','full_step_error','remaining_image_margin','basins'):
        assert toy[key]==retained['proof'][key],key
    result['submitted_arithmetic_reproduced']=True
    result['all_four_retained_evidence_files_match_review']=True
    return result
