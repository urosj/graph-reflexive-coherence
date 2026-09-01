"""Python-owned static navigation projections for the browser client."""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable, cast

from .canonical import canonical_bytes, load_json_object, record_digest
from .forensic import ForensicContext, load_forensic_context


BUNDLE_SCHEMA = "grcv4_explorer_ET_C6_static_navigation_bundle_v1"
FOCUS_NODE_LIMIT = 32
FOCUS_EDGE_LIMIT = 72
REACH_SEMANTICS = (
    "required",
    "one_of",
    "conditional",
    "negative_boundary",
    "indeterminate_requires_review",
    "not_applicable",
)

LENS_NEIGHBOR_KINDS: dict[str, tuple[tuple[str, str, frozenset[str]], ...]] = {
    "current_claim": (
        ("support", "Support", frozenset({"normative_object", "equation_contract", "gate_record"})),
        ("bearing_debt", "Bearing debt", frozenset({"debt_transformation"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "historical_claim": (
        ("transformations", "Transformations", frozenset({"debt_transformation", "current_claim"})),
        ("accepted_at", "Accepted at", frozenset({"gate_record"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "debt_transformation": (
        ("claim_topology", "Claim topology", frozenset({"historical_claim", "current_claim"})),
        ("gate_route", "Gate and route", frozenset({"gate_record"})),
        ("forward_work", "Forward work", frozenset({"verification_obligation"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "gate_record": (
        ("claims", "Claims", frozenset({"current_claim", "historical_claim"})),
        ("debts", "Debt transformations", frozenset({"debt_transformation"})),
        ("lineage", "Lineage", frozenset({"gate_record"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "profile": (
        ("candidate", "Candidate", frozenset({"candidate"})),
        ("realization", "Realization", frozenset({"realization"})),
        ("contracts", "Objects and contracts", frozenset({"normative_object", "equation_contract"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "normative_object": (
        ("claims", "Accepted claims", frozenset({"current_claim", "historical_claim"})),
        ("contracts", "Contracts", frozenset({"equation_contract", "normative_object"})),
        ("scope", "Candidate, profile, realization", frozenset({"candidate", "profile", "realization"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "equation_contract": (
        ("claims", "Accepted claims", frozenset({"current_claim", "historical_claim"})),
        ("objects", "Parent objects", frozenset({"normative_object"})),
        ("scope", "Candidate, profile, realization", frozenset({"candidate", "profile", "realization"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "source_record": (
        ("accepted_content", "Accepted content", frozenset({"gate_record", "current_claim", "debt_transformation"})),
        ("objects_contracts", "Objects and contracts", frozenset({"normative_object", "equation_contract"})),
        ("profiles", "Profiles and realizations", frozenset({"profile", "realization", "candidate"})),
    ),
    "candidate": (
        ("profiles", "Profiles", frozenset({"profile"})),
        ("claims", "Claims", frozenset({"current_claim", "historical_claim"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "realization": (
        ("profiles", "Profiles", frozenset({"profile"})),
        ("contracts", "Objects and contracts", frozenset({"normative_object", "equation_contract"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "verification_obligation": (
        ("blocked_claims", "Blocked claims", frozenset({"current_claim"})),
        ("bearing_debt", "Bearing debt", frozenset({"debt_transformation"})),
        ("source", "Source", frozenset({"source_record"})),
    ),
    "annotation": (
        ("annotated_content", "Annotated content", frozenset({"candidate", "gate_record", "current_claim"})),
    ),
}


def _accepted_payload(path: Path, schema: str, digest_field: str) -> dict[str, Any]:
    value = load_json_object(path)
    if value.get("schema") != schema or value.get("status") != "accepted":
        raise RuntimeError(f"accepted payload unavailable: {path.name}")
    if value.get(digest_field) != record_digest(value, digest_field):
        raise RuntimeError(f"accepted payload digest mismatch: {path.name}")
    return value


def _node_label(node: dict[str, Any]) -> str:
    attributes = cast(dict[str, Any], node["attributes"])
    for key in (
        "statement",
        "normative_object",
        "issue",
        "display_summary",
        "profile_id",
        "record_id",
        "artifact_id",
        "claim_id",
        "debt_id",
        "object_id",
    ):
        value = attributes.get(key)
        if isinstance(value, str) and value:
            return value
    return cast(str, node["identifier"])


def _catalog_node(node: dict[str, Any]) -> dict[str, Any]:
    attributes = cast(dict[str, Any], node["attributes"])
    scope = {
        key: value
        for key, value in attributes.items()
        if any(token in key.lower() for token in ("family", "candidate", "profile", "realization"))
    }
    return {
        "node_id": node["node_id"],
        "kind": node["kind"],
        "identifier": node["identifier"],
        "label": _node_label(node),
        "source_record_id": node["source_record_id"],
        "source_json_pointer": node["source_json_pointer"],
        "scope": scope,
    }


def _edge_sort_key(edge: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        cast(str, edge.get("support_semantic", "")),
        cast(str, edge.get("relation", "")),
        cast(str, edge.get("source", "")),
        cast(str, edge["edge_id"]),
    )


def _incident_edges(edges: Iterable[dict[str, Any]], node_id: str) -> list[dict[str, Any]]:
    return sorted(
        (row for row in edges if row["source"] == node_id or row["target"] == node_id),
        key=_edge_sort_key,
    )


def _other(edge: dict[str, Any], node_id: str) -> str:
    return cast(str, edge["target"] if edge["source"] == node_id else edge["source"])


def _focus_projection(
    node_id: str,
    nodes: dict[str, dict[str, Any]],
    propagation_edges: list[dict[str, Any]],
    annotation_edges: list[dict[str, Any]],
) -> dict[str, Any]:
    incident = _incident_edges(propagation_edges, node_id)
    annotation_incident = _incident_edges(annotation_edges, node_id)
    neighbor_ids: list[str] = []
    for edge in (*incident, *annotation_incident):
        neighbor = _other(edge, node_id)
        if neighbor not in neighbor_ids:
            neighbor_ids.append(neighbor)
        if len(neighbor_ids) >= FOCUS_NODE_LIMIT - 1:
            break
    selected_ids = {node_id, *neighbor_ids}
    selected_edges: list[dict[str, Any]] = []
    covered_neighbors: set[str] = set()
    for edge in (*incident, *annotation_incident):
        neighbor = _other(edge, node_id)
        if neighbor in selected_ids and neighbor not in covered_neighbors:
            selected_edges.append(edge)
            covered_neighbors.add(neighbor)
    for edge in (*incident, *annotation_incident):
        if edge in selected_edges:
            continue
        if edge["source"] in selected_ids and edge["target"] in selected_ids:
            selected_edges.append(edge)
        if len(selected_edges) >= FOCUS_EDGE_LIMIT:
            break
    selected_edges.sort(key=_edge_sort_key)
    return {
        "root_node_id": node_id,
        "node_limit": FOCUS_NODE_LIMIT,
        "edge_limit": FOCUS_EDGE_LIMIT,
        "node_ids": sorted(selected_ids),
        "edge_ids": [edge["edge_id"] for edge in selected_edges],
        "omitted_direct_neighbor_count": max(
            0,
            len({_other(edge, node_id) for edge in (*incident, *annotation_incident)})
            - len(neighbor_ids),
        ),
        "omitted_incident_edge_count": max(
            0, len(incident) + len(annotation_incident) - len(selected_edges)
        ),
    }


def _triangulation(
    node_id: str,
    nodes: dict[str, dict[str, Any]],
    propagation_edges: list[dict[str, Any]],
    annotation_edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    node_kind = cast(str, nodes[node_id]["kind"])
    incident = _incident_edges((*propagation_edges, *annotation_edges), node_id)
    rows: list[dict[str, Any]] = []
    for lens_id, label, neighbor_kinds in LENS_NEIGHBOR_KINDS.get(node_kind, ()):
        lens_edges = [
            edge
            for edge in incident
            if nodes[_other(edge, node_id)]["kind"] in neighbor_kinds
        ]
        if not lens_edges:
            continue
        rows.append(
            {
                "lens_id": lens_id,
                "label": label,
                "edge_count": len(lens_edges),
                "rows": [
                    {
                        "neighbor_node_id": _other(edge, node_id),
                        "direction": "outgoing" if edge["source"] == node_id else "incoming",
                        "edge_id": edge["edge_id"],
                    }
                    for edge in lens_edges
                ],
            }
        )
    return rows


def _transitive_targets(
    node_id: str,
    adjacency: dict[str, list[dict[str, Any]]],
    semantic: str,
) -> tuple[list[str], list[str]]:
    direct = sorted(
        {cast(str, edge["target"]) for edge in adjacency[node_id] if edge["support_semantic"] == semantic}
    )
    seen = {node_id, *direct}
    queue = deque(direct)
    transitive: set[str] = set()
    while queue:
        current = queue.popleft()
        for edge in adjacency[current]:
            if edge["support_semantic"] != semantic:
                continue
            target = cast(str, edge["target"])
            if target in seen:
                continue
            seen.add(target)
            transitive.add(target)
            queue.append(target)
    return direct, sorted(transitive)


def _reach_projection(
    node_id: str,
    annotation_edges: list[dict[str, Any]],
    adjacency: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    semantics: dict[str, Any] = {}
    for semantic in REACH_SEMANTICS:
        direct, transitive = _transitive_targets(node_id, adjacency, semantic)
        semantics[semantic] = {
            "direct_count": len(direct),
            "transitive_count": len(transitive),
            "direct_node_ids": direct,
            "transitive_node_ids": transitive,
        }
    annotations = sorted(
        {
            _other(edge, node_id)
            for edge in annotation_edges
            if edge["source"] == node_id or edge["target"] == node_id
        }
    )
    return {
        "classification": "dependency_reach_not_importance_priority_or_severity",
        "by_support_semantic": semantics,
        "annotation_display_only": {
            "direct_count": len(annotations),
            "direct_node_ids": annotations,
            "transitive_count": 0,
            "transitive_node_ids": [],
        },
    }


def _ripple_for_node(node_id: str, ripple_rows: list[dict[str, Any]]) -> str | None:
    node_kind, _, identifier = node_id.partition(":")
    for row in ripple_rows:
        key = row["ripple_key"]
        if node_kind == "profile" and key["profile_id"] == identifier:
            return cast(str, row["ripple_digest"])
        if key["target_kind"] == node_kind and key["target_id"] == identifier:
            return cast(str, row["ripple_digest"])
    return None


def build_static_navigation_bundle(
    repo_root: Path,
    side_tool_root: Path,
    source_observation: dict[str, Any],
) -> dict[str, Any]:
    """Compile the complete I6 lookup surface without browser-side traversal."""

    records = side_tool_root / "records"
    context: ForensicContext = load_forensic_context(repo_root, side_tool_root)
    et_c5_gate = _accepted_payload(
        records / "ETC5RippleAndScenarioContract.json",
        "grcv4_explorer_ET_C5_ripple_scenario_admission_v1",
        "record_digest",
    )
    source_manifest = load_json_object(records / "ETC1SourceBundleManifest.json")
    graph = context.graph
    scenario_bundle = _accepted_payload(
        records / "ETC5ScenarioBundle.json",
        "grcv4_explorer_ET_C5_scenario_bundle_v1",
        "scenario_bundle_digest",
    )
    aggregate = load_json_object(records / "ETC5AllProfilesAggregate.json")
    index = _accepted_payload(
        records / "ETC5RippleShardIndex.json",
        "grcv4_explorer_ET_C5_ripple_index_v1",
        "index_digest",
    )
    shards = [
        load_json_object(side_tool_root / descriptor["path"])
        for descriptor in index["shards"]
    ]
    ripple_rows = [row for shard in shards for row in shard["rows"]]

    nodes = {cast(str, row["node_id"]): row for row in graph["nodes"]}
    propagation_edges = cast(list[dict[str, Any]], graph["propagation_edges"])
    annotation_edges = cast(list[dict[str, Any]], graph["annotation_edges"])
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in propagation_edges:
        adjacency[cast(str, edge["source"])].append(edge)
    for rows in adjacency.values():
        rows.sort(key=_edge_sort_key)

    d10_2 = context.documents_by_record["GRC9V4-CD-D10.2-v1"].data
    required_families = cast(dict[str, int], d10_2["coverage_contract"]["required_families"])
    family_objects: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in d10_2["normatively_load_bearing_objects"]:
        family_objects[cast(str, row["family"])].append(row)
    families = []
    for family, count in required_families.items():
        objects = sorted(family_objects[family], key=lambda row: cast(str, row["object_id"]))
        if len(objects) != count:
            raise RuntimeError(f"D10.2 family count mismatch: {family}")
        families.append(
            {
                "family_id": family,
                "object_count": count,
                "classification": "coverage_not_profile_scope_or_ranking",
                "object_ids": [row["object_id"] for row in objects],
                "node_ids": [f"normative_object:{row['object_id']}" for row in objects],
            }
        )

    projections: dict[str, Any] = {}
    for node_id in sorted(nodes):
        projections[node_id] = {
            "schema": "grcv4_explorer_ET_C6_selection_projection_v1",
            "selection_node_id": node_id,
            "focus": _focus_projection(node_id, nodes, propagation_edges, annotation_edges),
            "triangulation": _triangulation(node_id, nodes, propagation_edges, annotation_edges),
            "dependency_reach": _reach_projection(node_id, annotation_edges, adjacency),
            "selected_ripple_digest": _ripple_for_node(node_id, ripple_rows),
        }

    embedded = {
        "source_manifest": source_manifest,
        "graph_projection": graph,
        "scenario_bundle": scenario_bundle,
        "ripple_aggregate": aggregate,
        "ripple_index": index,
        "ripple_shards": shards,
    }
    receipts = {
        "source_manifest": {"digest_field": "source_bundle_digest", "digest": source_manifest["source_bundle_digest"]},
        "graph_projection": {"digest_field": "graph_digest", "digest": graph["graph_digest"]},
        "scenario_bundle": {"digest_field": "scenario_bundle_digest", "digest": scenario_bundle["scenario_bundle_digest"]},
        "ripple_aggregate": {"digest_field": "aggregate_digest", "digest": aggregate["aggregate_digest"]},
        "ripple_index": {"digest_field": "index_digest", "digest": index["index_digest"]},
        "ripple_shards": [
            {"digest_field": "payload_digest", "digest": row["payload_digest"]}
            for row in shards
        ],
    }
    bundle: dict[str, Any] = {
        "schema": BUNDLE_SCHEMA,
        "status": "accepted",
        "snapshot_semantics": "build_time_snapshot_live_rescan_unavailable_in_static_browser",
        "source_observation": {
            "state": source_observation["state"],
            "observation_digest": source_observation["observation_digest"],
            "new_unprocessed_paths": source_observation.get("new_unprocessed_paths", []),
            "changed_admitted_paths": source_observation.get("changed_admitted_paths", []),
            "missing_admitted_paths": source_observation.get("missing_admitted_paths", []),
        },
        "authority": {
            "python_compiled_navigation": True,
            "browser_propagation_rule": False,
            "browser_ripple_compilation": False,
            "browser_mutation_authoring": False,
            "scientific_claim_added": False,
        },
        "accepted_identities": {
            "ET_C5_record_digest": et_c5_gate["record_digest"],
            "source_bundle_digest": context.source_bundle_digest,
            "graph_digest": context.graph_digest,
            "scenario_bundle_digest": scenario_bundle["scenario_bundle_digest"],
            "ripple_index_digest": index["index_digest"],
        },
        "embedded_payload_receipts": receipts,
        "embedded_payloads": embedded,
        "family_coverage": families,
        "catalog": [_catalog_node(nodes[node_id]) for node_id in sorted(nodes)],
        "selection_projection_count": len(projections),
        "selection_projections": projections,
        "bundle_digest": None,
    }
    bundle["bundle_digest"] = record_digest(bundle, "bundle_digest")
    return bundle


def hydrate_selection_projection(bundle: dict[str, Any], node_id: str) -> dict[str, Any]:
    """Dereference one compiled projection without deriving any graph relation."""

    projections = cast(dict[str, dict[str, Any]], bundle["selection_projections"])
    if node_id not in projections:
        raise KeyError(node_id)
    compiled = projections[node_id]
    graph = bundle["embedded_payloads"]["graph_projection"]
    nodes = {row["node_id"]: row for row in graph["nodes"]}
    catalog = {row["node_id"]: row for row in bundle["catalog"]}
    edges = {
        row["edge_id"]: row
        for row in (*graph["propagation_edges"], *graph["annotation_edges"])
    }
    ripple_rows = {
        row["ripple_digest"]: row
        for shard in bundle["embedded_payloads"]["ripple_shards"]
        for row in shard["rows"]
    }

    def node_payload(value: str) -> dict[str, Any]:
        return {**catalog[value], "attributes": nodes[value]["attributes"]}

    focus = compiled["focus"]
    return {
        "schema": compiled["schema"],
        "selection": node_payload(compiled["selection_node_id"]),
        "focus": {
            **{key: value for key, value in focus.items() if key not in {"node_ids", "edge_ids"}},
            "nodes": [node_payload(value) for value in focus["node_ids"]],
            "edges": [edges[value] for value in focus["edge_ids"]],
        },
        "triangulation": [
            {
                **{key: value for key, value in lens.items() if key != "rows"},
                "rows": [
                    {
                        "neighbor": node_payload(row["neighbor_node_id"]),
                        "direction": row["direction"],
                        "edge": edges[row["edge_id"]],
                    }
                    for row in lens["rows"]
                ],
            }
            for lens in compiled["triangulation"]
        ],
        "dependency_reach": compiled["dependency_reach"],
        "selected_ripple_row": ripple_rows.get(compiled["selected_ripple_digest"]),
    }


def selection_payload(bundle: dict[str, Any], node_id: str) -> bytes:
    """Return the exact browser selection payload for cross-surface tests."""

    return canonical_bytes(hydrate_selection_projection(bundle, node_id))
