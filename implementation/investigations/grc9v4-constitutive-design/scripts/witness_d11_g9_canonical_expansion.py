#!/usr/bin/env python3
"""Finite combinatorial witness for accepted D11-G9 candidate P4a."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, deque
from dataclasses import asdict, dataclass
from math import ceil
from random import Random
from typing import Literal


PORTS = tuple(range(1, 10))
EVENT_ID = "grc-event-sha256:" + "a" * 64


def add3(value: int, offset: int) -> int:
    return 1 + ((value - 1 + offset) % 3)


def port_row(port: int) -> int:
    return 1 + (port - 1) // 3


def port_column(port: int) -> int:
    return 1 + (port - 1) % 3


def port_of(row: int, column: int) -> int:
    return column + 3 * (row - 1)


@dataclass(frozen=True)
class PlannedEdge:
    edge_id: str
    kind: Literal["boundary", "spine", "tree"]
    branch: int
    node_u: str
    port_u: int
    node_v: str
    port_v: int
    source_port: int | None = None


def canonical_phase(extra_count: int, growth_phase: int | None) -> int | None:
    remainder = extra_count % 3
    if remainder == 0:
        if growth_phase is not None:
            raise ValueError("growth_phase must be none when no remainder exists")
        return None
    if growth_phase not in (1, 2, 3):
        raise ValueError("growth_phase must be 1, 2, or 3 when a remainder exists")
    return growth_phase


def branch_extra_counts(
    extra_count: int,
    chirality: Literal[-1, 1],
    growth_phase: int | None,
) -> dict[int, int]:
    phase = canonical_phase(extra_count, growth_phase)
    base, remainder = divmod(extra_count, 3)
    counts = {1: base, 2: base, 3: base}
    if phase is not None:
        for index in range(remainder):
            counts[add3(phase, chirality * index)] += 1
    return counts


def role_node_id(branch: int, local_ordinal: int, width: int) -> str:
    return f"{EVENT_ID}/extra/{branch}/{local_ordinal:0{width}d}"


def role_edge_id(branch: int, local_ordinal: int, width: int) -> str:
    return f"{EVENT_ID}/internal/extra/{branch}/{local_ordinal:0{width}d}"


def build_plan(
    target_effective_degree: int,
    *,
    chirality: Literal[-1, 1],
    growth_phase: int | None,
    old_edge_iteration_order: tuple[int, ...] = PORTS,
) -> dict[str, object]:
    if (
        isinstance(target_effective_degree, bool)
        or not isinstance(target_effective_degree, int)
        or target_effective_degree < 9
    ):
        raise ValueError("target_effective_degree must be an integer >= 9")
    if chirality not in (-1, 1):
        raise ValueError("chirality must be -1 or +1")
    if (
        len(old_edge_iteration_order) != 9
        or tuple(sorted(old_edge_iteration_order)) != PORTS
    ):
        raise ValueError("the saturated source must contain ports 1..9 once")

    n_cap = ceil((target_effective_degree - 2) / 7)
    node_count = max(4, n_cap)
    extra_count = node_count - 4
    phase = canonical_phase(extra_count, growth_phase)
    branch_counts = branch_extra_counts(extra_count, chirality, phase)
    width = max(1, len(str(extra_count)))

    nodes = {
        f"{EVENT_ID}/core",
        *(f"{EVENT_ID}/satellite/{branch}" for branch in (1, 2, 3)),
    }
    occupancy: dict[tuple[str, int], str] = {}
    edges: list[PlannedEdge] = []
    edge_ids: set[str] = set()

    # Reserve exact inherited boundaries before internal planning.
    for source_port in old_edge_iteration_order:
        branch = port_column(source_port)
        satellite = f"{EVENT_ID}/satellite/{branch}"
        endpoint = (satellite, source_port)
        if endpoint in occupancy:
            raise AssertionError(f"duplicate boundary endpoint {endpoint}")
        edge_id = f"old-{source_port}"
        if edge_id in edge_ids:
            raise AssertionError("old-edge identity collision")
        edge_ids.add(edge_id)
        occupancy[endpoint] = edge_id
        edges.append(
            PlannedEdge(
                edge_id=edge_id,
                kind="boundary",
                branch=branch,
                node_u=satellite,
                port_u=source_port,
                node_v=f"outside-{source_port}",
                port_v=source_port,
                source_port=source_port,
            )
        )

    # Primary same-port cyclic transversal.
    incoming_column: dict[str, int] = {}
    for branch in (1, 2, 3):
        satellite = f"{EVENT_ID}/satellite/{branch}"
        column = add3(branch, chirality)
        port = port_of(branch, column)
        core = f"{EVENT_ID}/core"
        for endpoint in ((core, port), (satellite, port)):
            if endpoint in occupancy:
                raise AssertionError(f"primary-spine collision at {endpoint}")
        edge_id = f"{EVENT_ID}/internal/{branch}"
        if edge_id in edge_ids:
            raise AssertionError("primary-edge identity collision")
        edge_ids.add(edge_id)
        occupancy[(core, port)] = edge_id
        occupancy[(satellite, port)] = edge_id
        edges.append(
            PlannedEdge(
                edge_id=edge_id,
                kind="spine",
                branch=branch,
                node_u=core,
                port_u=port,
                node_v=satellite,
                port_v=port,
            )
        )
        incoming_column[satellite] = column

    # Build each branch independently in creation-order breadth-first form.
    for branch in (1, 2, 3):
        satellite = f"{EVENT_ID}/satellite/{branch}"
        candidates = deque(
            column
            for column in (
                add3(incoming_column[satellite], chirality),
                add3(incoming_column[satellite], -chirality),
            )
            if (satellite, port_of(branch, column)) not in occupancy
        )
        if len(candidates) != 1:
            raise AssertionError("primary branch must expose one growth port")
        frontier: deque[tuple[str, deque[int]]] = deque([(satellite, candidates)])

        for local_ordinal in range(1, branch_counts[branch] + 1):
            while frontier and not frontier[0][1]:
                frontier.popleft()
            if not frontier:
                raise AssertionError("recursive allocator stalled")
            parent, parent_candidates = frontier[0]
            column = parent_candidates.popleft()
            port = port_of(branch, column)
            child = role_node_id(branch, local_ordinal, width)
            edge_id = role_edge_id(branch, local_ordinal, width)
            if child in nodes or edge_id in edge_ids:
                raise AssertionError("stable identity collision")
            for endpoint in ((parent, port), (child, port)):
                if endpoint in occupancy:
                    raise AssertionError(f"tree collision at {endpoint}")
            occupancy[(parent, port)] = edge_id
            occupancy[(child, port)] = edge_id
            edge_ids.add(edge_id)
            edges.append(
                PlannedEdge(
                    edge_id=edge_id,
                    kind="tree",
                    branch=branch,
                    node_u=parent,
                    port_u=port,
                    node_v=child,
                    port_v=port,
                )
            )
            nodes.add(child)
            incoming_column[child] = column
            frontier.append(
                (
                    child,
                    deque(
                        [
                            add3(column, chirality),
                            add3(column, -chirality),
                        ]
                    ),
                )
            )

    return {
        "D_eff": target_effective_degree,
        "chirality": chirality,
        "growth_phase": phase,
        "n_cap": n_cap,
        "node_count": node_count,
        "extra_count": extra_count,
        "branch_counts": branch_counts,
        "nodes": nodes,
        "edges": edges,
        "occupancy": occupancy,
    }


def normalized_edges(plan: dict[str, object]) -> list[tuple[object, ...]]:
    return sorted(tuple(asdict(edge).values()) for edge in plan["edges"])


def check_plan(plan: dict[str, object]) -> None:
    node_count = int(plan["node_count"])
    nodes = set(plan["nodes"])
    edges = list(plan["edges"])
    occupancy = dict(plan["occupancy"])
    chirality = int(plan["chirality"])
    boundary = [edge for edge in edges if edge.kind == "boundary"]
    internal = [edge for edge in edges if edge.kind != "boundary"]

    assert len(nodes) == node_count
    assert len(boundary) == 9
    assert len(internal) == node_count - 1
    assert len(occupancy) == 9 + 2 * (node_count - 1)
    assert {edge.source_port for edge in boundary} == set(PORTS)
    for edge in boundary:
        assert edge.source_port is not None
        assert edge.branch == port_column(edge.source_port)
        assert edge.node_u == f"{EVENT_ID}/satellite/{edge.branch}"
        assert edge.port_u == edge.source_port

    for edge in internal:
        assert edge.port_u == edge.port_v
        assert port_row(edge.port_u) == edge.branch

    spine = {edge.branch: edge for edge in internal if edge.kind == "spine"}
    assert len(spine) == 3
    for branch in (1, 2, 3):
        expected = port_of(branch, add3(branch, chirality))
        assert spine[branch].port_u == expected
        assert spine[branch].port_v == expected

    adjacency = {node: set() for node in nodes}
    for edge in internal:
        adjacency[edge.node_u].add(edge.node_v)
        adjacency[edge.node_v].add(edge.node_u)
    visited: set[str] = set()
    stack = [f"{EVENT_ID}/core"]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        stack.extend(adjacency[node] - visited)
    assert visited == nodes

    row_counts = Counter(port_row(edge.port_u) for edge in internal)
    column_counts = Counter(port_column(edge.port_u) for edge in internal)
    rows = [row_counts[index] for index in (1, 2, 3)]
    columns = [column_counts[index] for index in (1, 2, 3)]
    assert max(rows) - min(rows) <= 1
    assert max(columns) - min(columns) <= 1

    external_capacity = 9 * node_count - 2 * (node_count - 1)
    assert external_capacity == 7 * node_count + 2
    assert external_capacity >= int(plan["D_eff"])
    if node_count > 4:
        assert 7 * (node_count - 1) + 2 < int(plan["D_eff"])


def rotate_port(port: int, offset: int) -> int:
    return port_of(add3(port_row(port), offset), add3(port_column(port), offset))


def reflect_port(port: int) -> int:
    return port_of(4 - port_row(port), 4 - port_column(port))


def rotate_node(node: str, offset: int) -> str:
    if node == f"{EVENT_ID}/core":
        return node
    prefix = f"{EVENT_ID}/satellite/"
    if node.startswith(prefix):
        return f"{prefix}{add3(int(node.removeprefix(prefix)), offset)}"
    prefix = f"{EVENT_ID}/extra/"
    if node.startswith(prefix):
        branch, ordinal = node.removeprefix(prefix).split("/")
        return f"{prefix}{add3(int(branch), offset)}/{ordinal}"
    if node.startswith("outside-"):
        return f"outside-{rotate_port(int(node.removeprefix('outside-')), offset)}"
    raise ValueError(node)


def reflect_node(node: str) -> str:
    if node == f"{EVENT_ID}/core":
        return node
    prefix = f"{EVENT_ID}/satellite/"
    if node.startswith(prefix):
        return f"{prefix}{4 - int(node.removeprefix(prefix))}"
    prefix = f"{EVENT_ID}/extra/"
    if node.startswith(prefix):
        branch, ordinal = node.removeprefix(prefix).split("/")
        return f"{prefix}{4 - int(branch)}/{ordinal}"
    if node.startswith("outside-"):
        return f"outside-{reflect_port(int(node.removeprefix('outside-')))}"
    raise ValueError(node)


def transform_edge(
    edge: PlannedEdge,
    *,
    offset: int | None = None,
    reflect: bool = False,
) -> PlannedEdge:
    if reflect:
        branch = 4 - edge.branch
        node_u = reflect_node(edge.node_u)
        node_v = reflect_node(edge.node_v)
        port_u = reflect_port(edge.port_u)
        port_v = reflect_port(edge.port_v)
        source_port = (
            None if edge.source_port is None else reflect_port(edge.source_port)
        )
    else:
        assert offset is not None
        branch = add3(edge.branch, offset)
        node_u = rotate_node(edge.node_u, offset)
        node_v = rotate_node(edge.node_v, offset)
        port_u = rotate_port(edge.port_u, offset)
        port_v = rotate_port(edge.port_v, offset)
        source_port = (
            None if edge.source_port is None else rotate_port(edge.source_port, offset)
        )

    if edge.kind == "boundary":
        edge_id = f"old-{source_port}"
    elif edge.kind == "spine":
        edge_id = f"{EVENT_ID}/internal/{branch}"
    else:
        ordinal = edge.edge_id.rsplit("/", 1)[1]
        edge_id = f"{EVENT_ID}/internal/extra/{branch}/{ordinal}"
    return PlannedEdge(
        edge_id=edge_id,
        kind=edge.kind,
        branch=branch,
        node_u=node_u,
        port_u=port_u,
        node_v=node_v,
        port_v=port_v,
        source_port=source_port,
    )


def digest_plan(plan: dict[str, object]) -> str:
    payload = {
        "nodes": sorted(plan["nodes"]),
        "edges": normalized_edges(plan),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def admitted_phases(target_effective_degree: int) -> tuple[int | None, ...]:
    node_count = max(4, ceil((target_effective_degree - 2) / 7))
    return (None,) if (node_count - 4) % 3 == 0 else (1, 2, 3)


def main() -> int:
    plan_count = 0
    for target_effective_degree in range(9, 5001):
        for chirality in (-1, 1):
            for growth_phase in admitted_phases(target_effective_degree):
                check_plan(
                    build_plan(
                        target_effective_degree,
                        chirality=chirality,
                        growth_phase=growth_phase,
                    )
                )
                plan_count += 1

    rng = Random(0)
    reference = normalized_edges(build_plan(137, chirality=1, growth_phase=2))
    for _ in range(1000):
        shuffled = list(PORTS)
        rng.shuffle(shuffled)
        candidate = normalized_edges(
            build_plan(
                137,
                chirality=1,
                growth_phase=2,
                old_edge_iteration_order=tuple(shuffled),
            )
        )
        assert candidate == reference

    covariance_case_count = 0
    for target_effective_degree in (9, 30, 31, 45, 137, 5000):
        for chirality in (-1, 1):
            for growth_phase in admitted_phases(target_effective_degree):
                plan = build_plan(
                    target_effective_degree,
                    chirality=chirality,
                    growth_phase=growth_phase,
                )
                for offset in (0, 1, 2):
                    rotated = sorted(
                        tuple(asdict(transform_edge(edge, offset=offset)).values())
                        for edge in plan["edges"]
                    )
                    target_phase = (
                        None if growth_phase is None else add3(growth_phase, offset)
                    )
                    target = normalized_edges(
                        build_plan(
                            target_effective_degree,
                            chirality=chirality,
                            growth_phase=target_phase,
                        )
                    )
                    assert rotated == target
                reflected = sorted(
                    tuple(asdict(transform_edge(edge, reflect=True)).values())
                    for edge in plan["edges"]
                )
                target_phase = None if growth_phase is None else 4 - growth_phase
                target = normalized_edges(
                    build_plan(
                        target_effective_degree,
                        chirality=-chirality,
                        growth_phase=target_phase,
                    )
                )
                assert reflected == target
                covariance_case_count += 1

    positive = build_plan(30, chirality=1, growth_phase=None)
    negative = build_plan(30, chirality=-1, growth_phase=None)
    positive_spine = tuple(
        edge.port_u for edge in positive["edges"] if edge.kind == "spine"
    )
    negative_spine = tuple(
        edge.port_u for edge in negative["edges"] if edge.kind == "spine"
    )
    assert positive_spine == (2, 6, 7)
    assert negative_spine == (3, 4, 8)

    five_node = build_plan(31, chirality=1, growth_phase=2)
    assert int(five_node["node_count"]) == 5
    large = build_plan(5000, chirality=1, growth_phase=1)
    assert int(large["node_count"]) == 714
    assert sorted(large["branch_counts"].values()) == [236, 237, 237]

    for invalid_phase in (1, 2, 3):
        try:
            build_plan(30, chirality=1, growth_phase=invalid_phase)
        except ValueError:
            pass
        else:
            raise AssertionError("inactive growth phase was not rejected")
    try:
        build_plan(31, chirality=1, growth_phase=None)
    except ValueError:
        pass
    else:
        raise AssertionError("missing active growth phase was not rejected")

    result = {
        "candidate_id": "D11-G9-P4a",
        "policy_id": "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
        "positive_primary_spine": positive_spine,
        "negative_primary_spine": negative_spine,
        "target_effective_degree_range": [9, 5000],
        "target_effective_degree_case_count": 4992,
        "admitted_plan_case_count": plan_count,
        "checked_chiralities": [-1, 1],
        "checked_active_growth_phases": [1, 2, 3],
        "input_order_shuffle_count": 1000,
        "covariance_case_count": covariance_case_count,
        "unique_local_endpoint_occupancy": True,
        "exact_old_boundary_ports": True,
        "same_port_internal_edges": True,
        "connected_acyclic_tree": True,
        "row_and_column_imbalance_at_most_one": True,
        "capacity_identity": "7*n+2",
        "inactive_phase_rejected": True,
        "missing_active_phase_rejected": True,
        "large_plan_digest": digest_plan(large),
        "claim_ceiling": "finite_combinatorial_identity_and_covariance_witness_not_runtime_atomicity_history_target_readmission_stability_or_endpoint_evidence",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
