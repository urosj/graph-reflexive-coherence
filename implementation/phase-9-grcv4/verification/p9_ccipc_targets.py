"""Independent unit-reference C_CI_PC affine transfer, including relabelled sources."""
from copy import deepcopy
from dataclasses import replace
import p984b_ccipc_runtime as r
import p984e_cos as ordering
b = r.b


def target(manifest, case):
    """Same independent affine construction, generalized to a relabelled source."""
    source = b.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
    p = deepcopy(source.to_payload())
    graph = case["oracle"]["target_graph"]
    ref = p["reference"]
    ref["graph"] = graph
    weights = {e["edge_id"]:1 for e in graph["edges"]}
    m = len(weights)
    ref["K4_base"] = [[0.0]*m for _ in range(m)]
    ref["reference_hodge"]["edge_weights"] = weights.copy()
    ref["profile"]["params_resolved"]["candidate"]["W_C_tr"] = weights.copy()
    ordering.reidentify(ref)
    reference = b.GRCV4ReferenceGeometry.from_payload(ref)
    roles = {}
    for role in r.ROLES:
        old = dict(zip(source.geometry.reference.graph.live_node_ids, getattr(source,role).C, strict=True))
        image = {n:old.get(n,0.0) for n in graph["live_node_ids"]}
        for j,share in enumerate(case["request"]["resource_distribution"],1):
            image[case["oracle"]["event_id"]+f"/satellite/{j}"] = float(r.Q(old[case["request"]["source_node_id"]])*r.Q(share))
        roles[role] = b.GRCV4AuthoritativeState(tuple(image[n] for n in graph["live_node_ids"]),None,(0.0,)*(m*m))
    return replace(source, geometry=reference.geometry(), **roles, dt=0, operation_id=case["request"]["operation_id"])
