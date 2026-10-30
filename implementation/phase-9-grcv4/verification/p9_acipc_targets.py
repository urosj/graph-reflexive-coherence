"""Independent affine A_CI_PC transfer for arbitrary saved graph identities."""
from copy import deepcopy
from dataclasses import replace
import p984b_acipc_runtime as r
from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference, GRC9V4PortGraph

b=r.b
SELF=b.HERE+'p9_acipc_targets.py'


def target(seed,case):
    source=seed.inputs;p=deepcopy(source.geometry.reference.to_payload())
    graph=case['oracle']['target_graph'];m=len(graph['edges'])
    p['graph']=graph;p['K4_base']=[[0.0]*m for _ in range(m)]
    p['reference_hodge']['edge_weights']={e['edge_id']:1 for e in graph['edges']}
    params=p['profile']['params_resolved'];ident=p['profile']['identity_payload']
    port_graph=GRC9V4PortGraph.from_payload(graph)
    params['candidate']['descriptor_backend_id']=GRC9V4CandidateADifferentialReference(port_graph).identity
    params['geometry']['reference_hodge_digest']=b.payload_identity('reference_hodge_identity_payload',p['reference_hodge'])
    params['geometry']['K4_base_digest']=b.payload_identity('k4_identity_payload',dict(schema_version='grcv4-k4-identity-v1',K4_base=p['K4_base']))
    ident['params_hash']=b.payload_identity('resolved_params',params)
    p['profile']=b.resolve_profile(params,ident).to_payload()
    ref=b.GRCV4ReferenceGeometry.from_payload(p);roles={}
    for role in r.ROLES:
        old=getattr(source,role)
        C=dict(zip(source.geometry.reference.graph.live_node_ids,old.C,strict=True))
        W=dict(zip(source.geometry.reference.graph.live_edge_ids,old.W_A,strict=True))
        shares={case['oracle']['event_id']+f'/satellite/{i}':r.Q(s) for i,s in enumerate(case['request']['resource_distribution'],1)}
        roles[role]=b.GRCV4AuthoritativeState(tuple(C[n] if n in C else float(r.Q(C[case['request']['source_node_id']])*shares.get(n,0)) for n in ref.graph.live_node_ids),
            tuple(W.get(e,seed.specialization.resolved['expansion']['bond_seed']) for e in ref.graph.live_edge_ids),(0.0,)*(m*m))
        b.require(sum(map(r.Q,roles[role].C))==sum(map(r.Q,old.C)),'exact represented transfer charge')
    return replace(seed,inputs=replace(source,geometry=ref.geometry(),**roles,dt=0,operation_id=case['request']['operation_id']))
