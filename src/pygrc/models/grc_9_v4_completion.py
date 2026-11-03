"""Geometric SC-1 classifier, separate from represented-current flow basins.

Every strict descending route contributes a terminal. Ties never choose a
successor, and nodes reaching an excluded terminal cannot belong to a child.
"""

from dataclasses import dataclass

from .grc_9_v4_completion_codec import CompletionPolicy, node
from .grc_v4_spark_carrier import ExactCarrierState
from .grc_v4_spark_conductance import ExactConductanceState
from .grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState
from .grc_v4_spark_state import ExactResources, flint_operation


@dataclass(frozen=True, slots=True)
class GeometricBasins:
    basins: tuple
    terminals: tuple
    rows: tuple

    def to_payload(self):
        return {
            "basins": [
                {"anchor": node(a), "members": [node(x) for x in members]}
                for a, members in self.basins
            ],
            "terminals": [
                {"node": node(x), "terminals": [node(t) for t in ts]}
                for x, ts in self.terminals
            ],
            "rows": [r.to_dict() for r in self.rows],
        }


def terminal_roster(nodes, down, anchors):
    """Complete DAG reachability; order is the canonical graph order."""
    terminals, visiting = {}, set()

    def visit(x):
        if x in visiting:
            raise ValueError("descent graph is cyclic")
        if x not in terminals:
            visiting.add(x)
            terminals[x] = set().union(*(visit(y) for y in down[x])) if down[x] else {x}
            visiting.remove(x)
        return terminals[x]

    for x in nodes:
        visit(x)
    basins = tuple(
        (a, tuple(x for x in nodes if terminals[x] == {a}))
        for a in nodes
        if a in anchors
    )
    return tuple((a, b) for a, b in basins if len(b) > 1), tuple(
        (x, tuple(t for t in nodes if t in terminals[x])) for x in nodes
    )


@flint_operation
def classify(state: ExactResources, policy: CompletionPolicy):
    if type(state) not in (ExactResources, ExactCarrierState, ExactConductanceState, ExactAdaptiveCarrierState) or type(policy) is not CompletionPolicy:
        raise TypeError("exact resources and explicit completion policy required")
    nodes = state.graph.live_node_ids
    down = {x: set() for x in nodes}
    for edge, order in zip(
        state.graph.oriented_edges,
        state.edge_orders(policy.landscape_sign),
        strict=True,
    ):
        a, b = edge.tail_node_id, edge.head_node_id
        if order < 0:
            down[a].add(b)
        elif order > 0:
            down[b].add(a)
    rows = state.spatial_diagnostics(
        sign=policy.landscape_sign,
        gradient=policy.epsilon_gradient,
        hessian=policy.epsilon_Hessian,
        contrast=policy.contrast,
        core_resource=policy.minimum_resource,
    )
    basins, terminals = terminal_roster(
        nodes, down, {r["node_id"] for r in rows if r["anchor"]}
    )
    return GeometricBasins(basins, terminals, rows)


def descendants(source_capture, expanded, module, target_capture):
    """Lift the actual unique geometric parent through the event collapse map."""
    parents = [(a, b) for a, b in source_capture.basins if expanded in b]
    if len(parents) != 1:
        raise ValueError("event has no unique qualified geometric parent")
    anchor, parent = parents[0]
    module = set(module)
    footprint = (set(parent) - {expanded}) | module
    children = tuple(
        (a, b)
        for a, b in target_capture.basins
        if set(b) <= footprint and (a == anchor or a in module)
    )
    new = tuple(a for a, _ in children if a in module)
    return {
        "parent": parent,
        "parent_anchor": anchor,
        "footprint": footprint,
        "children": children,
        "new_anchors": new,
        "local_gain": max(0, len(children) - 1),
    }
