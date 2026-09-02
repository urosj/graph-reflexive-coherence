#!/usr/bin/env python3
"""Independently audit ET-C8 against raw accepted ET-C2/ET-C5 sources."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, load_json_object, record_digest  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise RuntimeError(message)


def longest_path(nodes: set[str], edges: list[dict[str, Any]]) -> list[str]:
    outgoing: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in nodes}
    for edge in edges:
        outgoing[edge["source"]].append(edge["target"])
        indegree[edge["target"]] += 1
    for values in outgoing.values():
        values.sort()
    queue = sorted(node for node, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    check(len(order) == len(nodes), "raw accepted gate DAG is cyclic")
    paths = {node: (node,) for node in order}
    for node in order:
        for target in outgoing[node]:
            candidate = paths[node] + (target,)
            if len(candidate) > len(paths[target]) or (
                len(candidate) == len(paths[target]) and candidate < paths[target]
            ):
                paths[target] = candidate
    return list(max(paths.values(), key=lambda path: (len(path), tuple(reversed(path)))))


def raw_reconstruction(
    claim_node: str,
    nodes: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[set[str], set[str]]:
    first = {
        edge["source"]
        for edge in edges
        if edge["target"] == claim_node
        and edge["relation"] != "requires_verification_from"
    } | {
        edge["target"]
        for edge in edges
        if edge["source"] == claim_node
        and edge["relation"] != "requires_verification_from"
        and not edge["target"].startswith("verification_obligation:")
    }
    reached = {claim_node, *first}
    expandable = {
        "debt_transformation",
        "equation_contract",
        "normative_object",
        "gate_record",
        "profile",
        "candidate",
        "realization",
    }
    for node_id in sorted(first):
        node = nodes.get(node_id)
        if node is None or node["kind"] not in expandable:
            continue
        for edge in edges:
            if edge["relation"] == "requires_verification_from":
                continue
            if edge["source"] == node_id:
                reached.add(edge["target"])
            if edge["target"] == node_id and edge["relation"] in {
                "transformed_from",
                "predecessor_claim",
                "accepted_claim",
            }:
                reached.add(edge["source"])
    edge_ids = {
        edge["edge_id"]
        for edge in edges
        if edge["relation"] != "requires_verification_from"
        and edge["source"] in reached
        and edge["target"] in reached
    }
    return reached, edge_ids


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    records = SIDE_TOOL_ROOT / "records"
    layer = load_json_object(records / "ETC8LineagePlaybackLayer.json")
    graph = load_json_object(records / "ETC2GraphSnapshot.json")
    check(layer["layer_digest"] == record_digest(layer, "layer_digest"), "layer digest")
    check(layer["status"] == "accepted", "accepted lifecycle")
    check(layer["source_identities"]["graph_digest"] == graph["graph_digest"], "graph identity")
    check(layer["authority"]["browser_propagation"] is False, "browser propagation")
    check(layer["authority"]["browser_rerun_prediction"] is False, "browser prediction")

    raw_nodes = {row["node_id"]: row for row in graph["nodes"]}
    raw_gates = {node_id: row for node_id, row in raw_nodes.items() if row["kind"] == "gate_record"}
    compiled_gates = {row["node_id"]: row for row in layer["lineage"]["nodes"]}
    check(set(raw_gates) == set(compiled_gates), "gate population")
    for node_id, source in raw_gates.items():
        compiled = compiled_gates[node_id]
        for field in ("record_digest", "gate_id", "status", "path"):
            target = "accepted_status" if field == "status" else field
            check(compiled[target] == source["attributes"][field], f"gate {node_id} {field}")

    raw_predecessors = sorted(
        (
            edge
            for edge in graph["propagation_edges"]
            if edge["relation"] == "predecessor_record"
            and edge["source"] in raw_gates
            and edge["target"] in raw_gates
        ),
        key=lambda edge: edge["edge_id"],
    )
    compiled_predecessors = layer["lineage"]["predecessor_edges"]
    check(len(raw_predecessors) == len(compiled_predecessors) == 27, "predecessor population")
    for source, compiled in zip(raw_predecessors, compiled_predecessors, strict=True):
        for field in ("edge_id", "source", "target", "relation", "source_record_id", "source_json_pointer"):
            check(compiled[field] == source[field], f"predecessor {source['edge_id']} {field}")
        check(compiled["predecessor_digest"] == source["attributes"]["predecessor_digest"], "predecessor digest")
    expected_spine = longest_path(set(raw_gates), raw_predecessors)
    check(layer["lineage"]["spine_node_ids"] == expected_spine, "readable spine")
    for index, position in enumerate(layer["lineage"]["scrub_positions"]):
        source = raw_gates[position["node_id"]]
        check(position["index"] == index, "scrub index")
        check(position["node_id"] == expected_spine[index], "scrub path")
        check(position["record_id"] == source["identifier"], "scrub record")
        check(position["record_digest"] == source["attributes"]["record_digest"], "scrub digest")

    raw_supersessions = {
        edge["edge_id"]: edge
        for edge in graph["propagation_edges"]
        if edge["relation"] == "superseded_by" and edge["source"] in raw_gates
    }
    compiled_supersessions = {row["edge_id"]: row for row in layer["lineage"]["supersession_markers"]}
    check(set(raw_supersessions) == set(compiled_supersessions), "supersession population")
    for edge_id, source in raw_supersessions.items():
        compiled = compiled_supersessions[edge_id]
        check((compiled["source"], compiled["target"]) == (source["source"], source["target"]), "supersession endpoints")
        check(compiled["source_json_pointer"] == source["source_json_pointer"], "supersession pointer")

    correction = load_json_object(
        repo_root
        / "implementation/investigations/grc9v4-constitutive-design/decisions/D7GPostv2GraphHodgeTypeCorrection.json"
    )
    marker = layer["lineage"]["correction_markers"][0]
    check(marker["source_record_id"] == correction["record_id"], "correction record")
    check(marker["source_record_digest"] == correction["decision_record_digest"], "correction digest")
    check(marker["correction_scope"] == correction["correction_scope"], "correction scope")
    check(marker["accepted_record_bytes_modified"] is False, "correction byte boundary")
    check(marker["accepted_decision_dispositions_reopened"] is False, "correction reopening boundary")

    raw_edges = graph["propagation_edges"]
    edge_by_id = {row["edge_id"]: row for row in raw_edges}
    raw_claims = {
        node_id: row
        for node_id, row in raw_nodes.items()
        if row["kind"] in {"current_claim", "historical_claim"}
    }
    check(len(layer["claim_reconstructions"]) == len(raw_claims) == 68, "claim reconstruction population")
    for node_id, source in raw_claims.items():
        claim_id = source["identifier"]
        compiled = layer["claim_reconstructions"][claim_id]
        expected_nodes, expected_edges = raw_reconstruction(node_id, raw_nodes, raw_edges)
        check(set(compiled["node_ids"]) == expected_nodes, f"reconstruction nodes {claim_id}")
        check({row["edge_id"] for row in compiled["edge_refs"]} == expected_edges, f"reconstruction edges {claim_id}")
        check(compiled["verification_obligations_excluded"] is True, "verification exclusion")
        for edge in compiled["edge_refs"]:
            check(edge["relation"] != "requires_verification_from", "forward obligation leakage")
            check(edge["source"] == edge_by_id[edge["edge_id"]]["source"], "reconstruction edge source")
            check(edge["target"] == edge_by_id[edge["edge_id"]]["target"], "reconstruction edge target")

    index = load_json_object(records / "ETC5RippleShardIndex.json")
    raw_ripples: dict[str, dict[str, Any]] = {}
    for reference in index["shards"]:
        shard = load_json_object(SIDE_TOOL_ROOT / reference["path"])
        check(shard["payload_digest"] == record_digest(shard, "payload_digest"), "shard digest")
        for row in shard["rows"]:
            raw_ripples[row["scenario"]["scenario_id"]] = row
    check(set(layer["playbacks"]) == set(raw_ripples), "playback population")
    check(len(raw_ripples) == 24, "playback count")
    for playback_id, source in raw_ripples.items():
        compiled = layer["playbacks"][playback_id]
        check(compiled["ripple_digest"] == source["ripple_digest"], "ripple identity")
        check(compiled["direct_consequences"] == source["direct_consequences"], "direct consequences")
        check(compiled["transitive_consequences"] == source["transitive_consequences"], "transitive consequences")
        check(compiled["browser_may_recompute"] is False, "browser recompute")
        check(compiled["browser_may_predict_rerun"] is False, "browser prediction")
        scenario_bytes = canonical_bytes(source["scenario"]) + b"\n"
        check(compiled["scenario_canonical_json"].encode("ascii") == scenario_bytes, "scenario roundtrip")
        check(compiled["playback_digest"] == record_digest(compiled, "playback_digest"), "playback digest")
        check([frame["frame_id"] for frame in compiled["frames"]] == ["baseline", "direct", "transitive", "frontier"], "frame sequence")
        for frame in compiled["frames"]:
            check(len(frame["node_states"]) == len(raw_gates), "frame gate population")
            check(len({row["node_id"] for row in frame["node_states"]}) == len(raw_gates), "frame uniqueness")
    c1 = next(row for row in layer["playbacks"].values() if row["source_scenario_id"] == "C1")
    check(c1["baseline_scrub_position"]["record_id"] == "GRC9V4-CD-D7V2-v1", "C1 baseline")
    check(c1["minimal_invalidation_root_node_ids"] == ["gate_record:GRC9V4-CD-D7V2-v1"], "C1 root")
    c2 = next(row for row in layer["playbacks"].values() if row["source_scenario_id"] == "C2")
    check(c2["profile_id"] == "A_CI", "C2 profile")
    check(json.loads(c2["scenario_canonical_json"])["candidate_ids"] == ["V4-A-temporalized-W"], "C2 candidate scope")

    provenance = load_json_object(
        repo_root
        / "implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json"
    )
    orientation = layer["orientation_path"]
    check(orientation["factorization"] == provenance["promotion_result"]["factorization"], "E1 factorization")
    check(orientation["source"]["record_digest"] == provenance["decision_record_digest"], "E1 source digest")
    check([row["substrate_id"] for row in orientation["steps"]] == ["GRCV4", "GRC9V4", "GRC9V3"], "E1 substrate order")
    print(f"ET_C8_INDEPENDENT_AUDIT_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
