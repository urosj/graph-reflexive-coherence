"""Investigation-only realization of ATC-SUP-MW-AOS-v1's reduced equations.

Not a pygrc backend, receipt implementation or runtime registration. All
geometry-changing/OS channels vanish in this fixed all-one-W, zero-exponent
fixture. Research provenance lives outside the scientific state and read.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

INV = Path(__file__).resolve().parents[1]
BINDING_PATH = INV / 'evidence/autonomous-topology-change/ATCSupportPotentialBinding.json'
BINDING_ID = 'grcv4-research-potential-sha256:9f4a7d3c69c1e52a4551029e7085d8123f68215647e63706397b3cd8bfcbfd8d'
INITIALIZER_ID = 'research_atc_a_target_reference_pass_mw_v1'
DT, ETA, KAPPA = F(1, 64), F(1, 4), F(1, 1024)
CHARGE, CHARGE_TOLERANCE = F(5), F(1, 2**40)


class ResearchDomainError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_binding():
    record = json.loads(BINDING_PATH.read_text())
    if (set(record) != {'schema', 'status', 'runtime_installed', 'binding_digest', 'identity_payload'}
            or record['schema'] != 'grcv4_atc_research_potential_binding_record_v1'
            or record['status'] != 'proposed_not_admitted' or record['runtime_installed'] is not False
            or record['binding_digest'] != BINDING_ID
            or 'grcv4-research-potential-sha256:' + digest(record['identity_payload']) != BINDING_ID):
        raise ResearchDomainError('unbound research potential')
    return record['identity_payload']


_BINDING = load_binding()
_ROOTS = tuple(map(F, _BINDING['polynomial']['roots_in_evaluation_order']))


@dataclass(frozen=True)
class Edge:
    edge_id: str
    tail_node_id: str
    head_node_id: str


@dataclass(frozen=True)
class Graph:
    live_node_ids: tuple[str, ...]
    oriented_edges: tuple[Edge, ...]

    def __post_init__(self):
        vertices, edges = self.live_node_ids, self.oriented_edges
        if (type(vertices) is not tuple or type(edges) is not tuple
                or not 1 <= len(vertices) <= 16 or len(edges) > 32
                or any(type(v) is not str or not v for v in vertices)
                or len(set(vertices)) != len(vertices) or any(type(e) is not Edge for e in edges)):
            raise ResearchDomainError('graph shape/work bound')
        seen_ids, seen_pairs = set(), set()
        degree = {v: 0 for v in vertices}
        for e in edges:
            if any(type(x) is not str or not x for x in (e.edge_id, e.tail_node_id, e.head_node_id)):
                raise ResearchDomainError('edge IDs must be nonempty strings')
            pair = frozenset((e.tail_node_id, e.head_node_id))
            if (type(e.edge_id) is not str or not e.edge_id or e.edge_id in seen_ids
                    or e.tail_node_id not in degree or e.head_node_id not in degree
                    or len(pair) != 2 or pair in seen_pairs):
                raise ResearchDomainError('graph edge/loop/parallel domain')
            seen_ids.add(e.edge_id)
            seen_pairs.add(pair)
            degree[e.tail_node_id] += 1
            degree[e.head_node_id] += 1
        if max(degree.values()) > 2:
            raise ResearchDomainError('degree outside research domain')

    @property
    def live_edge_ids(self):
        return tuple(e.edge_id for e in self.oriented_edges)

    def star(self, vertex):
        return tuple(i for i, e in enumerate(self.oriented_edges)
                     if vertex in (e.tail_node_id, e.head_node_id))

    @property
    def components(self):
        remaining = set(self.live_node_ids)
        result = []
        for seed in self.live_node_ids:
            if seed not in remaining:
                continue
            found, todo = {seed}, [seed]
            remaining.remove(seed)
            while todo:
                v = todo.pop()
                for i in self.star(v):
                    e = self.oriented_edges[i]
                    u = e.head_node_id if e.tail_node_id == v else e.tail_node_id
                    if u in remaining:
                        remaining.remove(u)
                        found.add(u)
                        todo.append(u)
            result.append(tuple(i for i, v in enumerate(self.live_node_ids) if v in found))
        return tuple(result)

    def to_payload(self):
        return dict(vertices=self.live_node_ids,
                    edges=[(e.edge_id, e.tail_node_id, e.head_node_id) for e in self.oriented_edges])


SOURCE_GRAPH = Graph(('a', 'b', 'c'), (Edge('ab', 'a', 'b'), Edge('bc', 'b', 'c')))
TARGET_GRAPH = Graph(('a', 'c', 'v0', 'v1'),
                     (Edge('ab', 'a', 'v0'), Edge('bc', 'v1', 'c'), Edge('connector', 'v0', 'v1')))


def resources(graph, C):
    if type(graph) is not Graph or type(C) is not tuple or len(C) != len(graph.live_node_ids):
        raise ResearchDomainError('resource coverage/type')
    if any(type(c) is not float or not math.isfinite(c) or c < 0 for c in C):
        raise ResearchDomainError('finite nonnegative binary64 required')
    return tuple(map(F, C))


def rounded(value):
    try:
        result = float(value)
    except OverflowError as exc:
        raise ResearchDomainError('nonfinite rounded output') from exc
    if not math.isfinite(result):
        raise ResearchDomainError('nonfinite rounded output')
    return result


def site_exact(c):
    result = F(1)
    for root in _ROOTS:
        result *= c - root
    return result


@dataclass(frozen=True)
class Read:
    Phi: tuple[float, ...]
    J: tuple[float, ...]
    f: tuple[F, ...]

    def to_payload(self):
        return dict(Phi=self.Phi, J=self.J, f=list(map(str, self.f)),
                    baseline_J=self.J, readback_J=(0.,)*len(self.J),
                    W_hat=(1.,)*len(self.J), structural_increment='exact_zero', carrier=None)


def read(graph, C):
    """Edge-local implementation; oracle uses expanded polynomial/dense matrices."""
    c = resources(graph, C)
    index = {v: i for i, v in enumerate(graph.live_node_ids)}
    lap = [F() for _ in c]
    for e in graph.oriented_edges:
        u, v = index[e.tail_node_id], index[e.head_node_id]
        dc = c[u] - c[v]
        lap[u] += dc
        lap[v] -= dc
    p = tuple(site_exact(x) for x in c)
    phi = [KAPPA*x-y for x, y in zip(lap, p, strict=True)]
    for component in graph.components:
        mean = sum((p[i] for i in component), F()) / len(component)
        for i in component:
            phi[i] += mean
    Phi = tuple(rounded(x) for x in phi)
    J, f = [], [F() for _ in c]
    for e in graph.oriented_edges:
        u, v = index[e.tail_node_id], index[e.head_node_id]
        current = rounded(-ETA*(F(Phi[u])-F(Phi[v])))
        J.append(current)
        f[u] -= F(current)
        f[v] += F(current)
    return Read(Phi, tuple(J), tuple(f))


def initialize(graph, C, role):
    if role not in ('current', 'reset'):
        raise ResearchDomainError('initializer role')
    point = read(graph, C)
    payload = dict(schema='atc_local_reference_pass_v1', policy_id=INITIALIZER_ID,
        binding_id=BINDING_ID, role=role, graph=graph.to_payload(), target_C=C,
        W_A_init=(1.,)*len(graph.live_edge_ids),
        derived=dict(W_base=(1.,)*len(graph.live_edge_ids), Phi_base=point.Phi, J_ref=point.J))
    return dict(payload=payload, research_construction_digest=digest(payload))


def check_initialization(record, graph, C, role):
    # Public data only. This validates the local construction, not a pygrc wire schema.
    if canonical(record) != canonical(initialize(graph, C, role)):
        raise ResearchDomainError('initializer record/evidence does not recompute')


@dataclass(frozen=True)
class State:
    graph: Graph
    C: tuple[float, ...]
    reset_C: tuple[float, ...]

    def __post_init__(self):
        for value in (self.C, self.reset_C):
            c = resources(self.graph, value)
            if abs(sum(c, F())-CHARGE) > CHARGE_TOLERANCE:
                raise ResearchDomainError('charge-5 research fixture; no resource repair')

    def scientific_payload(self):
        return dict(graph=self.graph.to_payload(), binding_id=BINDING_ID,
                    current=dict(C=self.C, W_A=(1.,)*len(self.graph.live_edge_ids), Z_4=None),
                    reset=dict(C=self.reset_C, W_A=(1.,)*len(self.graph.live_edge_ids), Z_4=None),
                    reference='identity_hodge_unit_weights', context='constant_zero')


def admit(state):
    read(state.graph, state.C)
    read(state.graph, state.reset_C)
    return state


def advance(state):
    point = read(state.graph, state.C)
    C = tuple(rounded(F(c)+DT*f) for c, f in zip(state.C, point.f, strict=True))
    return admit(replace(state, C=C))


def reset(state):
    return admit(replace(state, C=state.reset_C))


def encounter(state, direction, amplitude=F(1, 4096)):
    if (len(direction) != len(state.C) or sum(direction) != 0
            or abs(amplitude) > F(1, 4096)):
        raise ResearchDomainError('encounter coverage/charge/amplitude')
    return admit(replace(state, C=tuple(rounded(F(c)+amplitude*d)
                 for c, d in zip(state.C, direction, strict=True))))


def fixed_fission(state, prescription):
    """Only the preregistered fixed-source split; not a general event dispatcher."""
    if (state.graph != SOURCE_GRAPH or state.C != (1., 3., 1.)
            or prescription['vertex'] != 'b'
            or prescription['blocks'] != [[['ab', 'head']], [['bc', 'tail']]]
            or prescription['shares'] != ['1/2', '1/2']):
        raise ResearchDomainError('outside fixed preregistered fission')
    def mapped(c):
        return (c[0], c[2], rounded(F(c[1])/2), rounded(F(c[1])/2))
    target = State(TARGET_GRAPH, mapped(state.C), mapped(state.reset_C))
    constructions = {role: initialize(target.graph, getattr(target, attr), role)
                     for role, attr in (('current', 'C'), ('reset', 'reset_C'))}
    admit(target)
    return target, constructions
