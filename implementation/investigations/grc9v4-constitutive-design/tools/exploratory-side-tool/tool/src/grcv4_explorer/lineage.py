"""Source-bound lineage and precomputed ripple playback projections for ET-C8."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, cast

from .canonical import canonical_bytes, load_json_object, record_digest
from .forensic import ForensicContext, load_forensic_context, reconstruction_path
from .ripple import load_ripple_context, serialize_selected_row


LAYER_SCHEMA = "grcv4_explorer_ET_C8_lineage_playback_layer_v1"
PREDECESSOR_RELATION = "predecessor_record"
SUPERSESSION_RELATION = "superseded_by"
PLAYBACK_STATES = frozenset(
    {
        "accepted_unaffected",
        "baseline_anchor",
        "direct_effect",
        "transitive_effect",
        "reopening_gate",
        "evidence_frontier_unresolved",
    }
)
STATE_PRIORITY = {
    "accepted_unaffected": 0,
    "baseline_anchor": 1,
    "direct_effect": 2,
    "transitive_effect": 3,
    "evidence_frontier_unresolved": 4,
    "reopening_gate": 5,
}


def _gate_nodes(context: ForensicContext) -> dict[str, dict[str, Any]]:
    return {
        node_id: node
        for node_id, node in context.nodes.items()
        if node["kind"] == "gate_record"
    }


def _gate_row(node: dict[str, Any]) -> dict[str, Any]:
    attributes = cast(dict[str, Any], node["attributes"])
    return {
        "node_id": node["node_id"],
        "record_id": node["identifier"],
        "record_digest": attributes["record_digest"],
        "gate_id": attributes["gate_id"],
        "accepted_status": attributes["status"],
        "path": attributes["path"],
        "source_json_pointer": node["source_json_pointer"],
    }


def _predecessor_edges(
    context: ForensicContext, gate_nodes: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = [
        edge
        for edge in context.propagation_edges
        if edge["relation"] == PREDECESSOR_RELATION
        and edge["source"] in gate_nodes
        and edge["target"] in gate_nodes
    ]
    return sorted(rows, key=lambda row: cast(str, row["edge_id"]))


def _longest_spine(
    gate_nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]
) -> list[str]:
    """Return the deterministic longest accepted predecessor path."""

    successors: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in gate_nodes}
    for edge in edges:
        source = cast(str, edge["source"])
        target = cast(str, edge["target"])
        successors[source].append(target)
        indegree[target] += 1
    for values in successors.values():
        values.sort()

    queue = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while queue:
        node_id = queue.pop(0)
        order.append(node_id)
        for target in successors[node_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    if len(order) != len(gate_nodes):
        raise RuntimeError("accepted predecessor gate graph is cyclic")

    paths: dict[str, tuple[str, ...]] = {node_id: (node_id,) for node_id in order}
    for node_id in order:
        for target in successors[node_id]:
            candidate = paths[node_id] + (target,)
            current = paths[target]
            if len(candidate) > len(current) or (
                len(candidate) == len(current) and candidate < current
            ):
                paths[target] = candidate
    return list(max(paths.values(), key=lambda path: (len(path), tuple(reversed(path)))))


def _record_digest_for(context: ForensicContext, record_id: str) -> str:
    return context.documents_by_record[record_id].declared_digest


def _lineage_projection(context: ForensicContext) -> dict[str, Any]:
    gates = _gate_nodes(context)
    predecessor_edges = _predecessor_edges(context, gates)
    spine_ids = _longest_spine(gates, predecessor_edges)
    spine_set = set(spine_ids)
    spine_positions = {node_id: index for index, node_id in enumerate(spine_ids)}

    incoming: dict[str, list[str]] = defaultdict(list)
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in predecessor_edges:
        incoming[cast(str, edge["target"])].append(cast(str, edge["source"]))
        outgoing[cast(str, edge["source"])].append(cast(str, edge["target"]))

    anchors: dict[str, int] = {}
    for node_id in sorted(gates):
        if node_id in spine_set:
            anchors[node_id] = spine_positions[node_id]
            continue
        adjacent = incoming[node_id] + outgoing[node_id]
        candidates = [spine_positions[value] for value in adjacent if value in spine_set]
        anchors[node_id] = max(candidates) if candidates else len(spine_ids) - 1

    correction_id = "gate_record:GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1"
    correction = gates[correction_id]
    correction_doc = context.documents_by_record[cast(str, correction["identifier"])]
    correction_sources = cast(list[dict[str, Any]], correction_doc.data["source_identities"])
    correction_anchor = next(
        row for row in correction_sources if row["source_id"] == "D7G-v2"
    )
    anchors[correction_id] = spine_positions["gate_record:GRC9V4-CD-D7G-v2"]

    branch_lanes: dict[int, int] = defaultdict(int)
    nodes: list[dict[str, Any]] = []
    for node_id in sorted(gates, key=lambda value: (anchors[value], value)):
        row = _gate_row(gates[node_id])
        if node_id in spine_set:
            x = 120 + 170 * spine_positions[node_id]
            y = 190
            role = "spine"
        else:
            anchor = anchors[node_id]
            lane = branch_lanes[anchor]
            branch_lanes[anchor] += 1
            x = 120 + 170 * anchor + 55 + 80 * lane
            y = 54 if lane % 2 == 0 else 326
            role = "correction" if node_id == correction_id else "branch"
        nodes.append({**row, "lineage_role": role, "position": {"x": x, "y": y}})

    predecessor_rows = [
        {
            "edge_id": edge["edge_id"],
            "source": edge["source"],
            "target": edge["target"],
            "relation": PREDECESSOR_RELATION,
            "predecessor_digest": edge["attributes"]["predecessor_digest"],
            "source_record_id": edge["source_record_id"],
            "source_record_digest": _record_digest_for(
                context, cast(str, edge["source_record_id"])
            ),
            "source_json_pointer": edge["source_json_pointer"],
            "lineage_role": (
                "spine"
                if edge["source"] in spine_set
                and edge["target"] in spine_set
                and spine_positions[cast(str, edge["target"])]
                == spine_positions[cast(str, edge["source"])] + 1
                else "branch"
            ),
        }
        for edge in predecessor_edges
    ]
    supersessions = [
        {
            "edge_id": edge["edge_id"],
            "source": edge["source"],
            "target": edge["target"],
            "relation": SUPERSESSION_RELATION,
            "source_record_id": edge["source_record_id"],
            "source_record_digest": _record_digest_for(
                context, cast(str, edge["source_record_id"])
            ),
            "source_json_pointer": edge["source_json_pointer"],
        }
        for edge in sorted(
            (
                edge
                for edge in context.propagation_edges
                if edge["relation"] == SUPERSESSION_RELATION
                and edge["source"] in gates
                and edge["target"] in gates
            ),
            key=lambda row: cast(str, row["edge_id"]),
        )
    ]
    correction_marker = {
        "marker_id": "correction:D7G-post-v2-HODGE-TYPE",
        "marker_class": "accepted_companion_correction_not_predecessor_step",
        "node_id": correction_id,
        "anchor_node_id": "gate_record:GRC9V4-CD-D7G-v2",
        "correction_scope": correction_doc.data["correction_scope"],
        "source_record_id": correction_doc.record_identifier,
        "source_record_digest": correction_doc.declared_digest,
        "source_json_pointer": "/correction_scope",
        "anchor_source_json_pointer": next(
            f"/source_identities/{index}"
            for index, row in enumerate(correction_sources)
            if row is correction_anchor
        ),
        "accepted_record_bytes_modified": correction_doc.data[
            "accepted_record_bytes_modified"
        ],
        "accepted_decision_dispositions_reopened": correction_doc.data[
            "accepted_decision_dispositions_reopened"
        ],
    }
    scrub_positions = [
        {
            "index": index,
            "node_id": node_id,
            "record_id": gates[node_id]["identifier"],
            "record_digest": gates[node_id]["attributes"]["record_digest"],
            "gate_id": gates[node_id]["attributes"]["gate_id"],
            "accepted_status": gates[node_id]["attributes"]["status"],
        }
        for index, node_id in enumerate(spine_ids)
    ]
    return {
        "nodes": nodes,
        "predecessor_edges": predecessor_rows,
        "supersession_markers": supersessions,
        "correction_markers": [correction_marker],
        "spine_node_ids": spine_ids,
        "branch_node_ids": sorted(set(gates) - spine_set),
        "scrub_positions": scrub_positions,
        "population_counts": {
            "accepted_gate_records": len(gates),
            "predecessor_edges": len(predecessor_rows),
            "spine_positions": len(spine_ids),
            "branch_nodes": len(gates) - len(spine_ids),
            "supersession_markers": len(supersessions),
            "correction_markers": 1,
        },
    }


def _claim_reconstructions(context: ForensicContext) -> dict[str, Any]:
    claim_nodes = sorted(
        (
            row
            for row in context.nodes.values()
            if row["kind"] in {"current_claim", "historical_claim"}
        ),
        key=lambda row: (cast(str, row["kind"]), cast(str, row["identifier"])),
    )
    result: dict[str, Any] = {}
    for node in claim_nodes:
        claim_id = cast(str, node["identifier"])
        trace = reconstruction_path(context, claim_id)
        trace_row = cast(dict[str, Any], trace["rows"][0])
        payload = cast(dict[str, Any], trace_row["payload"])
        source = context.documents_by_record[cast(str, node["source_record_id"])]
        result[claim_id] = {
            "claim_id": claim_id,
            "claim_kind": node["kind"],
            "claim_node_id": node["node_id"],
            "claim_class": node["attributes"].get("claim_class", "historical"),
            "statement": node["attributes"].get(
                "statement", node["attributes"].get("supported_claim_statement", claim_id)
            ),
            "node_ids": [row["node_id"] for row in payload["nodes"]],
            "edge_refs": [
                {
                    "edge_id": edge["edge_id"],
                    "source": edge["source"],
                    "target": edge["target"],
                    "relation": edge["relation"],
                    "support_semantic": edge["support_semantic"],
                    "source_record_id": edge["source_record_id"],
                    "source_json_pointer": edge["source_json_pointer"],
                }
                for edge in trace_row["edge_refs"]
            ],
            "verification_obligations_excluded": payload[
                "verification_obligations_excluded"
            ],
            "source": {
                "record_id": source.record_identifier,
                "record_digest": source.declared_digest,
                "source_json_pointer": node["source_json_pointer"],
                "path": source.admission["path"],
            },
            "trace_digest": trace["trace_digest"],
        }
    return result


def _load_ripple_rows(side_tool_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    records = side_tool_root / "records"
    index = load_json_object(records / "ETC5RippleShardIndex.json")
    if index.get("status") != "accepted" or index.get("index_digest") != record_digest(
        index, "index_digest"
    ):
        raise RuntimeError("accepted ET-C5 ripple index is unavailable")
    rows: list[dict[str, Any]] = []
    for shard_ref in index["shards"]:
        shard = load_json_object(side_tool_root / shard_ref["path"])
        if shard.get("payload_digest") != record_digest(shard, "payload_digest"):
            raise RuntimeError(f"ET-C5 shard digest mismatch: {shard_ref['path']}")
        if shard["payload_digest"] != shard_ref["payload_digest"]:
            raise RuntimeError(f"ET-C5 index/shard mismatch: {shard_ref['path']}")
        rows.extend(shard["rows"])
    if len(rows) != index["row_count"]:
        raise RuntimeError("ET-C5 ripple row count mismatch")
    return index, sorted(rows, key=lambda row: cast(str, row["scenario_digest"]))


def _gate_identifier(value: Any, gate_record_ids: set[str]) -> str | None:
    if isinstance(value, str) and value in gate_record_ids:
        return f"gate_record:{value}"
    return None


def _gate_ids_from_consequences(
    rows: Iterable[dict[str, Any]], gate_record_ids: set[str]
) -> set[str]:
    result: set[str] = set()
    for row in rows:
        identifier = row["identifier"]
        if isinstance(identifier, dict):
            for value in (identifier.get("source"), identifier.get("target")):
                if isinstance(value, str) and value.startswith("gate_record:"):
                    result.add(value)
        else:
            gate_id = _gate_identifier(identifier, gate_record_ids)
            if gate_id is not None:
                result.add(gate_id)
    return result


def _frame(
    *,
    frame_id: str,
    label: str,
    gate_node_ids: set[str],
    baseline_node_id: str,
    direct_node_ids: set[str],
    transitive_node_ids: set[str],
    reopening_node_ids: set[str],
    unresolved_node_ids: set[str],
) -> dict[str, Any]:
    node_states: list[dict[str, str]] = []
    for node_id in sorted(gate_node_ids):
        state = "accepted_unaffected"
        candidates = [("baseline_anchor", node_id == baseline_node_id)]
        if frame_id in {"direct", "transitive", "frontier"}:
            candidates.append(("direct_effect", node_id in direct_node_ids))
        if frame_id in {"transitive", "frontier"}:
            candidates.append(("transitive_effect", node_id in transitive_node_ids))
        if frame_id == "frontier":
            candidates.extend(
                (
                    ("evidence_frontier_unresolved", node_id in unresolved_node_ids),
                    ("reopening_gate", node_id in reopening_node_ids),
                )
            )
        for candidate, active in candidates:
            if active and STATE_PRIORITY[candidate] > STATE_PRIORITY[state]:
                state = candidate
        if state not in PLAYBACK_STATES:
            raise RuntimeError(f"unknown playback state: {state}")
        node_states.append({"node_id": node_id, "state": state})
    return {"frame_id": frame_id, "label": label, "node_states": node_states}


def _playbacks(
    repo_root: Path,
    side_tool_root: Path,
    context: ForensicContext,
    lineage: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    index, rows = _load_ripple_rows(side_tool_root)
    ripple_context = load_ripple_context(repo_root, side_tool_root)
    gate_record_ids = {
        cast(str, row["record_id"]) for row in lineage["nodes"]
    }
    gate_node_ids = {f"gate_record:{value}" for value in gate_record_ids}
    scrub_by_record = {
        row["record_id"]: row for row in lineage["scrub_positions"]
    }
    playbacks: dict[str, Any] = {}
    for row in rows:
        if row.get("browser_may_recompute") is not False:
            raise RuntimeError("ET-C5 ripple grants browser recomputation authority")
        if row.get("ripple_digest") != record_digest(row, "ripple_digest"):
            raise RuntimeError("ET-C5 ripple digest mismatch")
        baseline_id = cast(str, row["ripple_key"]["baseline_record_id"])
        baseline = scrub_by_record.get(baseline_id)
        if baseline is None or baseline["record_digest"] != row["ripple_key"][
            "baseline_record_digest"
        ]:
            raise RuntimeError("ripple baseline is not an exact accepted scrub position")
        baseline_node_id = cast(str, baseline["node_id"])
        direct_nodes = _gate_ids_from_consequences(
            cast(list[dict[str, Any]], row["direct_consequences"]), gate_record_ids
        )
        by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for consequence in row["transitive_consequences"]:
            by_category[cast(str, consequence["category"])].append(consequence)
        transitive_nodes = _gate_ids_from_consequences(
            (
                consequence
                for category, consequences in by_category.items()
                if category
                not in {"earliest_gates_to_reopen", "unknown_beyond_evidence_frontier"}
                for consequence in consequences
            ),
            gate_record_ids,
        )
        reopening_nodes = _gate_ids_from_consequences(
            by_category["earliest_gates_to_reopen"], gate_record_ids
        )
        unresolved_nodes = _gate_ids_from_consequences(
            by_category["unknown_beyond_evidence_frontier"], gate_record_ids
        )
        frames = [
            _frame(
                frame_id="baseline",
                label="Accepted baseline",
                gate_node_ids=gate_node_ids,
                baseline_node_id=baseline_node_id,
                direct_node_ids=set(),
                transitive_node_ids=set(),
                reopening_node_ids=set(),
                unresolved_node_ids=set(),
            ),
            _frame(
                frame_id="direct",
                label="Direct source effects",
                gate_node_ids=gate_node_ids,
                baseline_node_id=baseline_node_id,
                direct_node_ids=direct_nodes,
                transitive_node_ids=set(),
                reopening_node_ids=set(),
                unresolved_node_ids=set(),
            ),
            _frame(
                frame_id="transitive",
                label="Recorded transitive effects",
                gate_node_ids=gate_node_ids,
                baseline_node_id=baseline_node_id,
                direct_node_ids=direct_nodes,
                transitive_node_ids=transitive_nodes,
                reopening_node_ids=set(),
                unresolved_node_ids=set(),
            ),
            _frame(
                frame_id="frontier",
                label="Reopening gate and evidence frontier",
                gate_node_ids=gate_node_ids,
                baseline_node_id=baseline_node_id,
                direct_node_ids=direct_nodes,
                transitive_node_ids=transitive_nodes,
                reopening_node_ids=reopening_nodes,
                unresolved_node_ids=unresolved_nodes,
            ),
        ]
        scenario_bytes = serialize_selected_row(ripple_context, row)
        playback = {
            "playback_id": cast(str, row["scenario"]["scenario_id"]),
            "source_scenario_id": row["scenario"]["source_scenario_id"],
            "profile_id": row["ripple_key"]["profile_id"],
            "baseline_scrub_position": baseline,
            "scenario_digest": row["scenario_digest"],
            "scenario_canonical_json": scenario_bytes.decode("ascii"),
            "ripple_digest": row["ripple_digest"],
            "result_statuses": row["result_statuses"],
            "direct_consequences": row["direct_consequences"],
            "transitive_consequences": row["transitive_consequences"],
            "blocked_overreads_at_risk": row["blocked_overreads_at_risk"],
            "verification_obligations_at_risk": row[
                "verification_obligations_at_risk"
            ],
            "minimal_invalidation_root_node_ids": sorted(reopening_nodes),
            "evidence_frontier_node_ids": sorted(unresolved_nodes),
            "frames": frames,
            "browser_may_recompute": False,
            "browser_may_predict_rerun": False,
            "playback_digest": None,
        }
        playback["playback_digest"] = record_digest(playback, "playback_digest")
        playbacks[cast(str, playback["playback_id"])] = playback
    return index, playbacks


def _orientation_path(context: ForensicContext) -> dict[str, Any]:
    document = context.documents_by_record["GRC9V4-CD-D10.2-v1"]
    promotion = cast(dict[str, Any], document.data["promotion_result"])
    return {
        "orientation_id": "E1-GRCV4-GRC9V4-GRC9V3",
        "factorization": promotion["factorization"],
        "factorization_disposition": promotion["factorization_disposition"],
        "scope": promotion["scope"],
        "steps": [
            {
                "substrate_id": "GRCV4",
                "label": "GRCv4",
                "role": "general_constitutive_architecture",
                "object_ids": promotion["GRCV4_object_ids"],
            },
            {
                "substrate_id": "GRC9V4",
                "label": "GRC9v4",
                "role": "substantive_nine_port_specialization",
                "object_ids": promotion["GRC9V4_specialization_object_ids"],
            },
            {
                "substrate_id": "GRC9V3",
                "label": "GRC9v3",
                "role": "exact_disabled_profile_compatibility_target",
                "object_ids": [],
            },
        ],
        "edges": [
            {
                "source": "GRCV4",
                "target": "GRC9V4",
                "relation": "nine_port_specialization",
            },
            {
                "source": "GRC9V4",
                "target": "GRC9V3",
                "relation": "disabled_V4_profile",
            },
        ],
        "source": {
            "record_id": document.record_identifier,
            "record_digest": document.declared_digest,
            "source_json_pointer": "/promotion_result/factorization",
            "path": document.admission["path"],
        },
    }


def build_lineage_playback_layer(
    repo_root: Path, side_tool_root: Path
) -> dict[str, Any]:
    """Compile the accepted read-only ET-C8 lineage and playback layer."""

    context = load_forensic_context(repo_root, side_tool_root)
    et_c7 = load_json_object(side_tool_root / "records/ETC7ClaimCeilingAlternativeLayer.json")
    if et_c7.get("status") != "accepted" or et_c7.get("layer_digest") != record_digest(
        et_c7, "layer_digest"
    ):
        raise RuntimeError("accepted ET-C7 predecessor is unavailable")
    lineage = _lineage_projection(context)
    ripple_index, playbacks = _playbacks(
        repo_root, side_tool_root, context, lineage
    )
    reconstructions = _claim_reconstructions(context)
    layer: dict[str, Any] = {
        "schema": LAYER_SCHEMA,
        "status": "accepted",
        "predecessor": {
            "gate_id": "ET-C7_claim_ceiling_and_alternative_navigation",
            "layer_digest": et_c7["layer_digest"],
            "accepted_record_digest": load_json_object(
                side_tool_root / "records/ETC7ClaimCeilingAlternativeNavigation.json"
            )["record_digest"],
        },
        "source_identities": {
            "source_bundle_digest": context.source_bundle_digest,
            "graph_digest": context.graph_digest,
            "ET_C2_record_digest": context.et_c2_record_digest,
            "ET_C5_ripple_index_digest": ripple_index["index_digest"],
            "ET_C5_scenario_bundle_digest": ripple_index["scenario_bundle_digest"],
        },
        "authority": {
            "source_graph_immutable": True,
            "lineage_projection_only": True,
            "browser_propagation": False,
            "browser_rerun_prediction": False,
            "browser_scenario_editing": False,
            "browser_scenario_recomputation": False,
            "playback_rows_precomputed": True,
            "source_mode_changed_by_playback": False,
            "unresolved_frontier_promoted": False,
            "scientific_claim_added": False,
        },
        "lineage": lineage,
        "claim_reconstructions": reconstructions,
        "orientation_path": _orientation_path(context),
        "playbacks": playbacks,
        "population_counts": {
            **lineage["population_counts"],
            "claim_reconstructions": len(reconstructions),
            "playback_rows": len(playbacks),
            "canonical_scenario_bytes": len(playbacks),
        },
        "layer_digest": None,
    }
    layer["layer_digest"] = record_digest(layer, "layer_digest")
    return layer


def scenario_roundtrip_bytes(layer: dict[str, Any], playback_id: str) -> bytes:
    """Return only the compiler-owned canonical scenario bytes."""

    if layer.get("schema") != LAYER_SCHEMA:
        raise RuntimeError("ET-C8 lineage layer schema mismatch")
    if layer.get("layer_digest") != record_digest(layer, "layer_digest"):
        raise RuntimeError("ET-C8 lineage layer digest mismatch")
    playback = cast(dict[str, Any], layer["playbacks"].get(playback_id))
    if playback is None:
        raise KeyError(playback_id)
    if playback.get("playback_digest") != record_digest(playback, "playback_digest"):
        raise RuntimeError("ET-C8 playback digest mismatch")
    value = cast(str, playback["scenario_canonical_json"]).encode("ascii")
    if not value.endswith(b"\n"):
        raise RuntimeError("ET-C8 canonical scenario is not newline terminated")
    if canonical_bytes(load_json_object_from_bytes(value)) + b"\n" != value:
        raise RuntimeError("ET-C8 canonical scenario bytes are not canonical")
    return value


def load_json_object_from_bytes(value: bytes) -> dict[str, Any]:
    import json

    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise RuntimeError("scenario root must be an object")
    return cast(dict[str, Any], parsed)
