"""SC-1 geometric attraction domains and an exact abstract return example.

This is investigation-local conditional mathematics. The affine return map is
not a GRCV4 constitutive law; the small chart replacement is not a D11-G9 event.
No native feasibility or completed-spark implementation follows from this file.
"""
from fractions import Fraction as F


class Uncertified(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Uncertified(message)


def neighbors(nodes, edges):
    adjacent = {n: set() for n in nodes}
    occupied = set()
    for a, pa, b, pb, weight in edges:
        need(a in adjacent and b in adjacent and weight > 0, "invalid_edge")
        for node, port in ((a, pa), (b, pb)):
            need(type(port) is int and 1 <= port <= 9 and (node, port) not in occupied,
                 "port_collision")
            occupied.add((node, port))
        if a != b:
            adjacent[a].add(b)
            adjacent[b].add(a)
    return adjacent


def row_intervals(nodes, edges, low, high):
    """Exact fixed-row means, enclosing every C in the supplied box."""
    terms = {n: [[], [], []] for n in nodes}
    for a, pa, b, pb, w in edges:
        for here, port, there in ((a, pa, b), (b, pb, a)):
            lo, hi = (F(0), F(0)) if here == there else (
                low[there] - high[here], high[there] - low[here])
            terms[here][(port - 1)//3].append((w, lo, hi))
    result = {}
    for n, rows in terms.items():
        result[n] = []
        for row in rows:
            total = sum(w for w, _, _ in row)
            result[n].append((sum(w*l for w,l,_ in row)/total,
                              sum(w*h for w,_,h in row)/total) if total else (F(0),F(0)))
    return result


def seed_status(rows, policy):
    signed = [(lo,hi) if policy['sign'] == 1 else (-hi,-lo) for lo,hi in rows]
    norm_upper = sum(max(abs(lo),abs(hi))**2 for lo,hi in rows)
    norm_lower = sum((F(0) if lo <= 0 <= hi else min(abs(lo),abs(hi)))**2 for lo,hi in rows)
    if norm_upper < policy['gradient']**2 and min(lo for lo,_ in signed) > policy['hessian']:
        return True
    if norm_lower >= policy['gradient']**2 or min(hi for _,hi in signed) <= policy['hessian']:
        return False
    raise Uncertified('unresolved_seed_predicate')


def certified_seed_agreement(exact_rows, represented_rows, errors, policy):
    """Exact scientific rows with certified agreement of the represented flag.

    This research helper validates explicit evaluation bounds; it does not
    produce them. The accepted represented-only diagnostic is unchanged.
    """
    need(len(exact_rows) == len(represented_rows) == len(errors) == 3,
         'invalid_row_bound')
    exact_rows, represented_rows, errors = (
        tuple(map(F, values)) for values in (exact_rows, represented_rows, errors))
    need(all(e >= 0 and abs(x-y) <= e for x,y,e in
             zip(exact_rows, represented_rows, errors)), 'invalid_row_bound')
    certified = seed_status([(x-e,x+e) for x,e in zip(represented_rows,errors)], policy)
    need(certified == seed_status([(x,x) for x in exact_rows], policy)
         == seed_status([(x,x) for x in represented_rows], policy), 'row_flag_disagreement')
    return certified


def require_exact_charge_slice(values, charge):
    """A tolerated residual is not membership in an exact-charge proof domain."""
    need(sum(map(F, values), F(0)) == F(charge), 'outside_exact_charge_slice')


def classify(nodes, edges, C, policy):
    """All strict descents of psi=s_H*C; ties never select an outgoing edge."""
    need(policy['sign'] in (-1, 1) and policy['gradient'] > 0
         and policy['hessian'] > 0 and policy['contrast'] > 0
         and policy['core_resource'] > 0, 'invalid_policy')
    need(set(C) == set(nodes) and min(C.values()) >= 0, 'invalid_resources')
    adjacent = neighbors(nodes, edges)
    psi = {n: policy['sign']*C[n] for n in nodes}
    down = {n: {v for v in adjacent[n] if psi[v] < psi[n]} for n in nodes}
    # Strict descent is a DAG. Ordering equal levels is irrelevant because they
    # have no descent edge between them; no label-dependent successor is chosen.
    destinations = {}
    depth = {}
    for n in sorted(nodes, key=lambda n: psi[n]):
        destinations[n] = set().union(*(destinations[v] for v in down[n])) if down[n] else {n}
        depth[n] = 1+max(depth[v] for v in down[n]) if down[n] else 0
    rows = row_intervals(nodes, edges, C, C)
    seeds = {n for n in nodes if seed_status(rows[n], policy)}
    anchors = {n for n in seeds if adjacent[n] and C[n] > policy['core_resource']
               and all(psi[v]-psi[n] > policy['contrast'] for v in adjacent[n])}
    basins = {s: {n for n in nodes if destinations[n] == {s}} for s in anchors}
    # This proposed bounded class requires a genuine nontrivial attraction
    # domain, not an isolated labelled point. Other classes remain unclaimed.
    basins = {s: b for s,b in basins.items() if len(b) > 1}
    return dict(basins=basins, seeds=seeds, destinations=destinations, depth=depth,
                down=down, psi=psi)


def correspondence(source_nodes, source_edges, source_C, target_nodes, target_edges,
                   target_C, expanded, module, policy):
    module = set(module)
    need(expanded in source_nodes and module and not module & set(source_nodes)
         and set(target_nodes) == (set(source_nodes)-{expanded}) | module, 'invalid_lineage')
    before = classify(source_nodes, source_edges, source_C, policy)
    parents = [(a,b) for a,b in before['basins'].items() if expanded in b]
    need(len(parents) == 1, 'missing_qualified_geometric_parent')
    parent_anchor, parent = parents[0]
    collapse = {n: expanded if n in module else n for n in target_nodes}
    footprint = {n for n in target_nodes if collapse[n] in parent}
    after = classify(target_nodes, target_edges, target_C, policy)
    descendants = {a:b for a,b in after['basins'].items()
                   if b <= footprint and (a in module or a == parent_anchor)}
    need(len(descendants) >= 2 and set(descendants) & module, 'no_additional_basin')
    return dict(parent_anchor=parent_anchor, parent=parent, descendants=descendants,
                new_anchors=set(descendants) & module, gain=len(descendants)-1)


def prove_affine_box(nodes, edges, center, radius, factor, policy, error=F(0)):
    """Certificate for T(C)=center+factor*(C-center), only this named toy map.

    K is the closed box intersected with sum(C)=sum(center). radius>0 and the
    positive center give relative interior in the full charge hyperplane.
    """
    need(radius > 0 and 0 <= factor < 1, 'no_full_neighborhood_or_contraction')
    need(error >= 0 and error < (1-factor)*radius, 'unproved_represented_invariance')
    low = {n:c-radius for n,c in center.items()}
    high = {n:c+radius for n,c in center.items()}
    need(min(low.values()) > 0, 'nonpositive_box')
    adjacent = neighbors(nodes, edges)
    sign = policy['sign']
    lo = low if sign == 1 else {n:-x for n,x in high.items()}
    hi = high if sign == 1 else {n:-x for n,x in low.items()}
    edge_gaps = []
    for a,_,b,_,_ in edges:
        if a == b:
            continue
        gap = max(lo[a]-hi[b], lo[b]-hi[a])
        need(gap > 0, 'unresolved_landscape_order')
        edge_gaps.append(gap)
    rows = row_intervals(nodes, edges, low, high)
    seeds = {n for n in nodes if seed_status(rows[n], policy)}
    for n in seeds:
        need(adjacent[n] and low[n] > policy['core_resource'], 'unproved_viable_seed')
        need(all(lo[v]-hi[n] > policy['contrast'] for v in adjacent[n]), 'unproved_seed_barrier')
    point = classify(nodes, edges, center, policy)
    need(seeds == point['seeds'], 'seed_roster_mismatch')
    return dict(charge=str(sum(center.values())), radius=str(radius), contraction=str(factor),
        relative_dimension=len(nodes)-1, minimum_resource=str(min(low.values())),
        edge_order_margin=str(min(edge_gaps)),
        image_margin=str((1-factor)*radius), full_step_error=str(error),
        remaining_image_margin=str((1-factor)*radius-error),
        basins={s:sorted(b) for s,b in sorted(point['basins'].items())},
        spatial_descent_steps=max(point['depth'][v] for b in point['basins'].values() for v in b),
        full_state_fixed_points_in_box=1, actual_V4_operator_certificate=False)


def example():
    source = ('p','v','a','b','d','e','f','g')
    target = ('p','x','m','y','a','b','d','e','f','g')
    old_edges = (('p',1,'v',1,F(1)),('p',4,'a',1,F(1)),('p',7,'b',1,F(1)),
                 ('v',4,'d',1,F(1)),('v',5,'e',1,F(1)),('v',7,'f',1,F(1)),('v',8,'g',1,F(1)))
    new_edges = (('p',1,'m',1,F(1)),('p',4,'a',1,F(1)),('p',7,'b',1,F(1)),
                 ('m',4,'x',1,F(1)),('m',7,'y',1,F(1)),('x',4,'d',1,F(1)),
                 ('x',7,'f',1,F(1)),('y',4,'e',1,F(1)),('y',7,'g',1,F(1)))
    old_C = {n:F(3) if n == 'p' else F(2) if n == 'v' else F(1) for n in source}
    event_C = {n:old_C[n] if n in old_C else F(1,2) if n == 'm' else F(3,4) for n in target}
    center = {n:F(2) if n in ('p','x','y') else F(5,7) for n in target}
    policy = dict(sign=-1, gradient=F(4), hessian=F(1,4), contrast=F(1,2), core_resource=F(1,2))
    return source, old_edges, old_C, target, new_edges, event_C, center, policy


def checks():
    old, oe, oc, new, ne, ec, center, p = example()
    radius, factor = F(1,14), F(1,2)
    proof = prove_affine_box(new, ne, center, radius, factor, p, F(1,112))
    need(sum(oc.values()) == sum(ec.values()) == sum(center.values()) == 11, 'charge')
    need(ec['x']+ec['m']+ec['y'] == oc['v'] and all(ec[n] == oc[n] for n in old if n != 'v'),
         'event_resource_accounting')
    source_observation = classify(old, oe, oc, p)
    need(source_observation['basins']['p'] == set(old) and 'v' not in source_observation['seeds'],
         'parent_is_a_basin_not_necessarily_the_expanded_seed')
    need(set(classify(new, ne, ec, p)['basins']) == {'p'}, 'mechanical_stage_gained_children')
    trace = []
    c = dict(ec)
    for k in range(1,8):
        c = {n:center[n]+factor*(c[n]-center[n]) for n in new}
        need(sum(c.values()) == 11 and min(c.values()) > 0, 'toy_return_domain')
        distance = max(abs(c[n]-center[n]) for n in new)
        trace.append(dict(step=k, distance=str(distance), in_box=distance <= radius,
                          basins=sorted(classify(new,ne,c,p)['basins'])))
    need(next(r['step'] for r in trace if r['in_box']) == 5, 'wrong_first_entry')
    gain = correspondence(old,oe,oc,new,ne,c,'v',{'x','m','y'},p)
    need(gain['gain'] == 2 and gain['new_anchors'] == {'x','y'}, 'wrong_gain')
    need(proof['basins'] == {'p':['a','b','p'], 'x':['d','f','x'], 'y':['e','g','y']}, 'wrong_domains')
    results = dict(abstract_positive=dict(proof=proof, source_parent='p', initial_basins=['p'],
        descendants=sorted(gain['descendants']), new_children=sorted(gain['new_anchors']),
        additional_basins=gain['gain'], first_entry=5, positive_observations_after_entry=2,
        trace=trace, native_steps=0, D11_event=False, V4_constitutive_map=False,
        meaning='One full-state attracting pattern contains three distinct geometric routing basins.'))

    def reject(name, call, reason):
        try:
            call()
        except Uncertified as e:
            need(str(e) == reason, name+': '+str(e))
        else:
            raise AssertionError(name+': unexpectedly certified')
        results[name] = reason

    reject('mechanical_refinement_only',lambda:correspondence(old,oe,oc,new,ne,ec,'v',{'x','m','y'},p), 'no_additional_basin')
    reject('missing_parent_not_zero_count',lambda:correspondence(old,oe,{n:F(1) for n in old},new,ne,c,'v',{'x','m','y'},p), 'missing_qualified_geometric_parent')
    reject('zero_radius_not_a_neighborhood',lambda:prove_affine_box(new,ne,center,F(0),factor,p), 'no_full_neighborhood_or_contraction')
    reject('no_temporal_contraction',lambda:prove_affine_box(new,ne,center,radius,F(1),p), 'no_full_neighborhood_or_contraction')
    reject('contraction_without_organization',lambda:prove_affine_box(new,ne,{n:F(11,10) for n in new},radius,factor,p), 'unresolved_landscape_order')
    reject('barrier_equality',lambda:prove_affine_box(new,ne,center,radius,factor,dict(p,contrast=F(8,7))), 'unproved_seed_barrier')
    boundary = classify(old,oe,oc,dict(p,hessian=F(1)))
    need('p' not in boundary['seeds'] and 'p' not in boundary['basins'], 'seed_equality_accepted')
    results['seed_hessian_equality'] = 'strict_seed_rejected'
    reject('numerical_error_at_image_margin',lambda:prove_affine_box(new,ne,center,radius,factor,p,F(1,28)), 'unproved_represented_invariance')
    reject('wrong_parent_lineage',lambda:correspondence(old,oe,oc,new,ne,c,'p',{'x','m','y'},p), 'invalid_lineage')

    # Equal adjacent values form no arbitrary directed choice. Their terminals
    # remain visible, even when they are not qualified seeds.
    flat = classify(new,ne,{n:F(11,10) for n in new},p)
    need(not flat['basins'] and all(flat['destinations'][n] == {n} for n in new), 'plateau_created_basins')
    results['flat_plateau_not_children'] = True
    need(classify(new,ne,center,p)['destinations']['m'] == {'p','x','y'}, 'ambiguous_saddle_assigned')
    results['all_routes_no_chooser'] = True
    # Reflect scalar sign without changing the declaration: this is not gauge
    # covariance, and the old peaks must not continue to pass by renaming.
    opposite = classify(new,ne,center,dict(p,sign=1))
    need(not {'p','x','y'} & set(opposite['basins']), 'sign_change_silently_accepted')
    results['global_sign_is_part_of_policy'] = True
    rename = {n:'renamed-'+str(len(new)-i) for i,n in enumerate(new)}
    renamed_edges = tuple((rename[a],pa,rename[b],pb,w) for a,pa,b,pb,w in reversed(ne))
    mapped = classify(tuple(rename[n] for n in reversed(new)),renamed_edges,{rename[n]:v for n,v in center.items()},p)
    expected = {rename[s]:{rename[n] for n in b} for s,b in classify(new,ne,center,p)['basins'].items()}
    need(mapped['basins'] == expected, 'label_or_order_selects_a_basin')
    flipped = tuple((b,pb,a,pa,w) for a,pa,b,pb,w in ne)
    need(classify(new,flipped,center,p)['basins'] == classify(new,ne,center,p)['basins'], 'edge_orientation_changes_geometry')
    results['label_order_orientation_covariance'] = True
    # A second abstract map T(c,w)=(c/2,2w) contracts the observed coordinate
    # while the omitted history direction expands. Compare actual perturbations.
    x, y = (F(0),F(0)), (F(1),F(1))
    step = lambda z: (factor*z[0],F(2)*z[1])
    before_distance = max(abs(a-b) for a,b in zip(x,y))
    after_distance = max(abs(a-b) for a,b in zip(step(x),step(y)))
    current_ratio = abs(step(x)[0]-step(y)[0])/abs(x[0]-y[0])
    need(current_ratio == F(1,2) and after_distance == 2*before_distance,
         'hidden_history_instability')
    results['omitted_history_contraction_rejected'] = dict(C_ratio=str(current_ratio),
        full_state_distance_ratio=str(after_distance/before_distance), full_contraction=False)
    return results
