#!/usr/bin/env python3
"""Focused ET-C2 graph-kernel and invariant fixture matrix."""

from __future__ import annotations

import copy
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.adapters import adapt_source  # noqa: E402
from grcv4_explorer.bundle import build_source_bundle  # noqa: E402
from grcv4_explorer.canonical import canonical_bytes, digest  # noqa: E402
from grcv4_explorer.errors import GraphInvariantError  # noqa: E402
from grcv4_explorer.kernel import (  # noqa: E402
    backward_evidence_reachable,
    build_validated_graph,
    propagation_reachable,
    validate_graph_snapshot,
)
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


def expect_graph_error(label: str, operation: Callable[[], object]) -> None:
    try:
        operation()
    except GraphInvariantError:
        return
    raise RuntimeError(f"ET-C2 fixture did not fail closed: {label}")


def _resign_edges(rows: list[dict[str, Any]], prefix: str) -> None:
    for row in rows:
        payload = {key: value for key, value in row.items() if key != "edge_id"}
        row["edge_id"] = f"{prefix}:{digest(payload)}"
    rows.sort(key=lambda row: cast(str, row["edge_id"]))


def resign_graph(graph: dict[str, Any], *, sort_nodes: bool = True) -> None:
    nodes = cast(list[dict[str, Any]], graph["nodes"])
    propagation = cast(list[dict[str, Any]], graph["propagation_edges"])
    annotations = cast(list[dict[str, Any]], graph["annotation_edges"])
    if sort_nodes:
        nodes.sort(key=lambda row: cast(str, row["node_id"]))
    _resign_edges(propagation, "propagation")
    _resign_edges(annotations, "annotation")
    graph["node_count"] = len(nodes)
    graph["node_counts"] = dict(sorted(Counter(row["kind"] for row in nodes).items()))
    graph["propagation_edge_count"] = len(propagation)
    graph["propagation_relation_counts"] = dict(
        sorted(Counter(row["relation"] for row in propagation).items())
    )
    graph["support_semantic_counts"] = dict(
        sorted(Counter(row["support_semantic"] for row in propagation).items())
    )
    graph["annotation_edge_count"] = len(annotations)
    graph["graph_digest"] = digest(
        {key: value for key, value in graph.items() if key != "graph_digest"}
    )


def renamed_node_fixture(graph: dict[str, Any]) -> None:
    changed = copy.deepcopy(graph)
    nodes = cast(list[dict[str, Any]], changed["nodes"])
    historical = next(row for row in nodes if row["kind"] == "historical_claim")
    current = next(row for row in nodes if row["kind"] == "current_claim")
    old_id = cast(str, historical["node_id"])
    historical["identifier"] = current["identifier"]
    new_id = f"historical_claim:{current['identifier']}"
    historical["node_id"] = new_id
    for table in (changed["propagation_edges"], changed["annotation_edges"]):
        for edge in cast(list[dict[str, Any]], table):
            if edge["source"] == old_id:
                edge["source"] = new_id
            if edge["target"] == old_id:
                edge["target"] = new_id
    resign_graph(changed)
    expect_graph_error(
        "current/historical collision", lambda: validate_graph_snapshot(changed)
    )


def mutation_matrix(graph: dict[str, Any]) -> int:
    fixture_count = 0

    def mutate_and_expect(
        label: str,
        mutate: Callable[[dict[str, Any]], None],
        *,
        resign: bool = True,
    ) -> None:
        nonlocal fixture_count
        changed = copy.deepcopy(graph)
        mutate(changed)
        if resign:
            resign_graph(changed)
        expect_graph_error(label, lambda: validate_graph_snapshot(changed))
        fixture_count += 1

    renamed_node_fixture(graph)
    fixture_count += 1

    def dangling_endpoint(value: dict[str, Any]) -> None:
        edge = next(
            row
            for row in value["propagation_edges"]
            if row["relation"] == "candidate_scope"
        )
        edge["target"] = "candidate:missing"

    mutate_and_expect("dangling endpoint", dangling_endpoint)

    def obligation_outgoing(value: dict[str, Any]) -> None:
        obligation = next(
            row["node_id"]
            for row in value["nodes"]
            if row["kind"] == "verification_obligation"
        )
        gate = next(
            row["node_id"] for row in value["nodes"] if row["kind"] == "gate_record"
        )
        value["propagation_edges"].append(
            {
                "edge_id": "pending",
                "source": obligation,
                "target": gate,
                "relation": "supported_by",
                "support_semantic": "indeterminate_requires_review",
                "source_record_id": "fixture",
                "source_json_pointer": "/fixture",
                "attributes": {},
            }
        )

    mutate_and_expect("obligation backward support", obligation_outgoing)

    def incomplete_obligation_metadata(value: dict[str, Any]) -> None:
        edge = next(
            row
            for row in value["propagation_edges"]
            if row["relation"] == "requires_verification_from"
        )
        del edge["attributes"]["originating_record_digest"]

    mutate_and_expect("obligation provenance missing", incomplete_obligation_metadata)

    def annotation_leak(value: dict[str, Any]) -> None:
        annotation = value["annotation_edges"][0]
        value["propagation_edges"].append(
            {
                "edge_id": "pending",
                "source": annotation["source"],
                "target": annotation["target"],
                "relation": "candidate_disposition_annotation",
                "support_semantic": "not_applicable",
                "source_record_id": annotation["source_record_id"],
                "source_json_pointer": annotation["source_json_pointer"],
                "attributes": {},
            }
        )

    mutate_and_expect("annotation enters propagation", annotation_leak)

    def annotation_authority(value: dict[str, Any]) -> None:
        value["annotation_edges"][0]["authority"] = "propagation"

    mutate_and_expect("annotation authority conversion", annotation_authority)

    def gate_cycle(value: dict[str, Any]) -> None:
        gate = next(row for row in value["nodes"] if row["kind"] == "gate_record")
        value["propagation_edges"].append(
            {
                "edge_id": "pending",
                "source": gate["node_id"],
                "target": gate["node_id"],
                "relation": "predecessor_record",
                "support_semantic": "not_applicable",
                "source_record_id": gate["identifier"],
                "source_json_pointer": "/fixture",
                "attributes": {
                    "predecessor_digest": gate["attributes"]["record_digest"]
                },
            }
        )

    mutate_and_expect("gate lineage cycle", gate_cycle)

    mutate_and_expect(
        "duplicate node",
        lambda value: value["nodes"].append(copy.deepcopy(value["nodes"][0])),
    )

    def remove_contract_claim(value: dict[str, Any]) -> None:
        index = next(
            index
            for index, row in enumerate(value["propagation_edges"])
            if row["relation"] == "accepted_claim"
        )
        value["propagation_edges"].pop(index)

    mutate_and_expect("contract claim edge omitted", remove_contract_claim)

    def remove_claim_debt(value: dict[str, Any]) -> None:
        index = next(
            index
            for index, row in enumerate(value["propagation_edges"])
            if row["source"].startswith("current_claim:")
            and row["target"].startswith("debt_transformation:")
            and row["relation"] != "transformed_from"
        )
        value["propagation_edges"].pop(index)

    mutate_and_expect("claim/debt edge omitted", remove_claim_debt)

    def substitute_claim_debt(value: dict[str, Any]) -> None:
        rows = [
            row
            for row in value["propagation_edges"]
            if row["source"].startswith(("current_claim:", "historical_claim:"))
            and row["target"].startswith("debt_transformation:")
            and row["relation"] != "transformed_from"
        ]
        first = next(row for row in rows if row["relation"] == "supported_by")
        second = next(row for row in rows if row["relation"] == "blocked_by")
        first["relation"], second["relation"] = second["relation"], first["relation"]
        first["support_semantic"], second["support_semantic"] = (
            second["support_semantic"],
            first["support_semantic"],
        )

    mutate_and_expect("count-preserving relation substitution", substitute_claim_debt)

    def unknown_support(value: dict[str, Any]) -> None:
        value["propagation_edges"][0]["support_semantic"] = "invented_support"

    mutate_and_expect("unknown support semantic", unknown_support)
    mutate_and_expect(
        "graph digest mismatch",
        lambda value: value.__setitem__("graph_digest", "0" * 64),
        resign=False,
    )

    def noncanonical_order(value: dict[str, Any]) -> None:
        value["nodes"].reverse()
        value["graph_digest"] = digest(
            {key: child for key, child in value.items() if key != "graph_digest"}
        )

    mutate_and_expect("noncanonical node ordering", noncanonical_order, resign=False)
    return fixture_count


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    et_c0_path = SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json"
    et_c0 = load_et_c0_contract(et_c0_path)
    rows = admitted_rows(et_c0)
    manifest, _ = build_source_bundle(repo_root, et_c0_path)
    documents = [adapt_source(repo_root, row) for row in rows]
    first = build_validated_graph(
        documents,
        source_bundle_digest=cast(str, manifest["source_bundle_digest"]),
    )
    second = build_validated_graph(
        list(reversed(documents)),
        source_bundle_digest=cast(str, manifest["source_bundle_digest"]),
    )
    assert canonical_bytes(first) == canonical_bytes(second)
    validate_graph_snapshot(first)

    annotation = cast(list[dict[str, Any]], first["annotation_edges"])[0]
    assert annotation["target"] not in propagation_reachable(
        first, [cast(str, annotation["source"])]
    )
    obligation = next(
        row["node_id"]
        for row in cast(list[dict[str, Any]], first["nodes"])
        if row["kind"] == "verification_obligation"
    )
    assert backward_evidence_reachable(first, cast(str, obligation)) == {obligation}
    assert any(
        row["kind"] == "source_record" and row["attributes"]["source_digests"] == []
        for row in cast(list[dict[str, Any]], first["nodes"])
    )

    fixture_count = mutation_matrix(first)
    print(f"ET_C2_TEST_PASS fixtures={fixture_count} graph={first['graph_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
