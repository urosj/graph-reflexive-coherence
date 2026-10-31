"""Exact SC-2 source/parent/D11/charge preflight; no constitutive trajectory.

Use the existing allocation kernel, independently check its literal four-node
target, and apply the reviewed equilibrium inequalities on that target graph.
The research namespace is not a computed/admitted native event identity.
"""
from fractions import Fraction as F

from pygrc.models.grc_9_v4_expansion import _allocate, canonical_module_node_count
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortEdge as Edge, GRC9V4PortEndpoint as Endpoint,
    GRC9V4PortGraph as Graph,
)
import spark_completion_basins as basins
from spark_completion_mechanism import incidence, matmul, transpose

POLICY = dict(sign=-1, gradient=F(4), hessian=F(1,4),
              contrast=F(1,2), core_resource=F(1,2))
NAMESPACE = 'sc2-preflight-module'  # local roles, never a lifecycle event ID
HIGH_PORTS = (1,5,9)
SHARES = (F(1,2), F(3,8), F(1,8))  # explicit dyadic request, fixed before trajectories


def tuples(graph):
    return [(e.tail.node_id,e.tail.port,e.head.node_id,e.head.port,F(1))
            for e in graph.edges]


def serialized(resources):
    return {key: str(value) for key,value in sorted(resources.items())}


def checks():
    nodes = ('p','v',*(f'n{i}' for i in range(1,10)))
    edges = [Edge(f'old-{i}','boundary',Endpoint('v',i),Endpoint(f'n{i}',1))
             for i in range(1,10)]
    edges += [Edge(f'parent-{b}','boundary',Endpoint('p',1+3*(b-1)),Endpoint(f'n{i}',4))
              for b,i in enumerate(HIGH_PORTS,1)]
    source = Graph(nodes,tuple(edges))
    base = {'p':F(3),'v':F(1),**{f'n{i}': F(3,2) if i in HIGH_PORTS else F(3,4)
                               for i in range(1,10)}}
    assert sum(base.values()) == 13
    # Fix the unchanged global wells c0=2,a=1 and a target with 3 upper nodes.
    target_n, upper_count, radius = 14, 3, F(1,8)
    target_charge = target_n + 2*upper_count
    offset = F(target_charge-sum(base.values()),len(nodes))
    assert offset == F(7,11)
    assert all(abs(13-(target_n+2*k)) > target_n*radius for k in range(2,target_n+1))
    current = {v:c+offset for v,c in base.items()}
    reset = dict(current)
    reset['n1'] += F(1,64)
    reset['n2'] -= F(1,128)
    reset['n3'] -= F(1,128)
    assert reset != current and sum(reset.values()) == sum(current.values()) == 20
    source_roles = {}
    for role,values in (('current',current),('reset',reset)):
        rows = basins.row_intervals(nodes,tuples(source),values,values)
        assert rows['v'] == [(F(0),F(0))]*3
        # Algebraic current_hybrid_signed_hessian eligibility for any positive
        # spark threshold, here fixed to 1/8; not a fresh native postbeat capture.
        assert F(0)<F(1,8) and F(0)<POLICY['gradient']**2
        classified = basins.classify(nodes,tuples(source),values,POLICY)
        assert classified['basins'] == {'p':set(nodes)}
        source_roles[role] = dict(resources=serialized(values),charge='20',
                                  expanded_rows=['0','0','0'],parent='p',parent_members=list(nodes))
    missing_parent = dict(base);missing_parent['p']=F(3,2)
    assert not basins.classify(nodes,tuples(source),missing_parent,POLICY)['basins']
    assert canonical_module_node_count(9) == 4
    results = {}
    for chirality in (-1,1):
        target,module,internal = _allocate(source,'v',NAMESPACE,chirality,(0,0,0))
        core,*satellites = module
        # Independent literal D11 boundary and primary-spine equations.
        expected = set()
        for e in source.edges:
            tail = e.tail
            if tail.node_id == 'v':
                tail = Endpoint(satellites[(tail.port-1)%3],tail.port)
            expected.add((e.edge_id,tail.node_id,tail.port,e.head.node_id,e.head.port))
        spine_ports = (2,6,7) if chirality==1 else (3,4,8)
        expected.update((NAMESPACE+f'/internal/{b}',core,port,satellite,port)
                        for b,(satellite,port) in enumerate(zip(satellites,spine_ports),1))
        actual = {(e.edge_id,e.tail.node_id,e.tail.port,e.head.node_id,e.head.port)
                  for e in target.edges}
        assert actual == expected and len(target.live_node_ids)==14 and len(actual)==15
        assert len(internal)==3 and len(module)==4 and 'v' not in target.live_node_ids
        target_roles = {}
        for role,values in (('current',current),('reset',reset)):
            transferred = {v:c for v,c in values.items() if v!='v'}
            transferred[core]=F(0)
            transferred.update({sat:share*values['v'] for sat,share in zip(satellites,SHARES)})
            assert sum(transferred.values())==20 and min(transferred.values())==0
            result = basins.classify(target.live_node_ids,tuples(target),transferred,POLICY)
            assert set(result['basins']) == {'p'}  # mechanical allocation earns no gain
            target_roles[role]=dict(resources=serialized(transferred),charge='20',
                                    immediate_qualified_basins=['p'],immediate_completion=False)

        order = target.live_node_ids
        adjacency = basins.neighbors(order,tuples(target))
        distances=[]
        for start in order:
            d={start:0};todo=[start]
            for v in todo:
                for w in sorted(adjacency[v]-d.keys()):d[w]=d[v]+1;todo.append(w)
            assert len(d)==len(order)
            distances.extend(d.values())
        diameter=max(distances)
        edge_pairs=[(e.tail.node_id,e.head.node_id) for e in target.edges]
        b=incidence(order,edge_pairs);lap=matmul(b,transpose(b))
        high={'p',satellites[0],satellites[1]}
        center={v:F(3) if v in high else F(1) for v in order}
        ell=max(sum(map(abs,row)) for row in lap)
        forcing=max(abs(sum(a*center[v] for a,v in zip(row,order))) for row in lap)
        assert (diameter,ell,forcing)==(4,8,8) and sum(center.values())==20
        # Reviewed general bounds, recomputed for n=14, degree 4 (not n=10).
        pnorm=2*(1-F(1,len(order)));kappa=F(1,64)
        image=kappa*(forcing+ell*radius)/2+pnorm*(3*radius**2+radius**3)/2
        q=kappa*ell/2+pnorm*(6*radius+3*radius**2)/2
        dmin=3*(1-radius)**2-1-kappa*ell;dmax=3*(1+radius)**2-1
        amin=F(2,(len(order)-1)*diameter);amax=ell/(1-F(1,4));h=F(1,32)
        assert image==F(829,7168)<radius and q==F(719,896)<1
        assert dmin==F(75,64)>0 and h*amax*dmax==F(179,192)<1
        derivative=1-h*amin*dmin
        assert derivative==F(53173,53248)<1 and F(1,64)<amin
        low={v:c-radius for v,c in center.items()};upper={v:c+radius for v,c in center.items()}
        rows=basins.row_intervals(order,tuples(target),low,upper)
        guaranteed={}
        for index,satellite in enumerate(satellites[:2],1):
            assert basins.seed_status(rows[satellite],POLICY)
            assert all(low[satellite]-upper[v]>POLICY['contrast'] for v in adjacency[satellite])
            private={f'n{i}' for i in range(index,10,3) if i not in HIGH_PORTS}
            assert len(private)==2 and all(adjacency[v]=={satellite} for v in private)
            guaranteed[satellite]=sorted({satellite,*private})
        assert core not in high and all(target_roles[r]['resources'][core]=='0' for r in target_roles)
        assert low[core]==F(7,8)  # neither transferred role starts in this branch box
        results[str(chirality)]=dict(
            target_graph=target.to_payload(),module=list(module),roles=target_roles,
            candidate_branch=dict(center=serialized(center),upper_nodes=sorted(high),
                                  charge='20',radius=str(radius),image_bound=str(image),
                                  image_slack=str(radius-image),solver_lipschitz=str(q),
                                  diameter=diameter,laplacian_infinity_bound=str(ell),
                                  curvature_lower=str(dmin),curvature_upper=str(dmax),
                                  mobility_lower=str(amin),mobility_upper=str(amax),
                                  full_OS_derivative_bound=str(derivative),
                                  guaranteed_new_basin_subsets=guaranteed,
                                  whole_basin_memberships_certified=False,
                                  uniform_descent_DAG_certified=False),
            organized_branch_reached=False,initial_state_inside_branch_box=False)
    return dict(
        scope='exact diagnostic/mechanical/charge compatibility and conditional target equilibrium; no admitted event or evolution',
        source_graph=source.to_payload(),source_roles=source_roles,
        derivation=dict(unshifted_charge='13',target_charge='20',uniform_source_offset='7/11',
                        offset_preserves_row_differences_not_constitutive_dynamics=True,
                        source_offset_chosen_by_charge_before_trajectories=True),
        resource_distribution=[str(x) for x in SHARES],target_effective_degree=9,
        allocation_namespace_is_not_native_event_identity=True,targets=results,
        controls=dict(unshifted_charge_excludes_all_k_at_least_two_boxes=True,
                      missing_parent_rejected=True,independent_current_reset=True,
                      both_chiral_spines_match_literal_D11=True,
                      zero_core_prevents_immediate_trap_entry=True,
                      mechanical_expansion_alone_has_no_gain=True),
        constitutive_source_target_admission=False,postbeat_capture_proved=False,
        source_formation_proved=False,uniform_physical_trapping_domain_proved=False,
        represented_error_certificate=False,proposed_site_binding_admitted=False,
        native_steps=0,native_events=0,completed_spark=False,SC2_closed=False)
