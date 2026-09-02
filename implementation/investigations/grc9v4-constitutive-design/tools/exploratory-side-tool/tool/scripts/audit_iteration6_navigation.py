#!/usr/bin/env python3
"""Independent raw-record audit of the ET-C6 static navigation surface."""

from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    file_sha256,
    load_json_object,
    record_digest,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


SEMANTICS = (
    "required",
    "one_of",
    "conditional",
    "negative_boundary",
    "indeterminate_requires_review",
    "not_applicable",
)


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    arguments = set(sys.argv[1:])
    if arguments - {"--skip-dist-identity"}:
        raise RuntimeError(f"unsupported ET-C6 audit arguments: {sorted(arguments)}")
    skip_dist_identity = "--skip-dist-identity" in arguments
    checks = 0

    def require(condition: bool, label: str) -> None:
        nonlocal checks
        if not condition:
            raise RuntimeError(f"ET-C6 audit failed: {label}")
        checks += 1

    records = SIDE_TOOL_ROOT / "records"
    bundle_path = records / "ETC6StaticNavigationBundle.json"
    bundle = load_json_object(bundle_path)
    parity = load_json_object(records / "ETC6CrossSurfaceParity.json")
    manifest = load_json_object(records / "ETC6WebBuildManifest.json")
    gate = load_json_object(records / "ETC6StaticNavigationSurface.json")
    et_c5 = load_json_object(records / "ETC5RippleAndScenarioContract.json")
    d10_2 = load_json_object(
        repo_root
        / "implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json"
    )

    for path, value in (
        (bundle_path, bundle),
        (records / "ETC6CrossSurfaceParity.json", parity),
        (records / "ETC6WebBuildManifest.json", manifest),
        (records / "ETC6StaticNavigationSurface.json", gate),
    ):
        require(path.read_bytes() == canonical_bytes(value) + b"\n", f"canonical:{path.name}")
    for value, field, label in (
        (bundle, "bundle_digest", "bundle_digest"),
        (parity, "parity_digest", "parity_digest"),
        (manifest, "manifest_digest", "manifest_digest"),
        (gate, "record_digest", "gate_digest"),
    ):
        require(value[field] == record_digest(value, field), label)
    require(et_c5["status"] == "accepted", "ET_C5_accepted")
    require(gate["predecessor"]["record_digest"] == et_c5["record_digest"], "ET_C5_binding")
    require(gate["status"] == "accepted", "accepted_status")
    require(gate["authority"]["iteration_7_authorized"] is True, "iteration_7_authorized")
    require(
        gate["acceptance_requirements"]
        == {
            "independent_static_bundle_audit": "passed_44895_checks_7_cross_surface_parity_rows",
            "python_and_node_component_tests": "passed_47_python_checks_8_node_tests",
            "deterministic_double_rebuild": "passed",
            "playwright_desktop_mobile": "passed_2_viewports_desktop_mobile",
            "ET_C5_regression": "passed_full_verification",
            "human_review": "accepted",
        },
        "accepted_requirements",
    )
    require(bundle["authority"]["browser_propagation_rule"] is False, "browser_rule_absent")
    require(bundle["authority"]["browser_ripple_compilation"] is False, "browser_compiler_absent")
    require(bundle["source_observation"]["state"] == "current_bundle_exact", "source_current")

    embedded = bundle["embedded_payloads"]
    receipts = bundle["embedded_payload_receipts"]
    for key in (
        "source_manifest",
        "graph_projection",
        "scenario_bundle",
        "ripple_aggregate",
        "ripple_index",
    ):
        value = embedded[key]
        receipt = receipts[key]
        require(value[receipt["digest_field"]] == receipt["digest"], f"declared:{key}")
        require(record_digest(value, receipt["digest_field"]) == receipt["digest"], f"payload:{key}")
    require(len(embedded["ripple_shards"]) == len(receipts["ripple_shards"]) == 3, "shard_population")
    for index, (value, receipt) in enumerate(zip(embedded["ripple_shards"], receipts["ripple_shards"], strict=True)):
        require(value[receipt["digest_field"]] == receipt["digest"], f"declared:shard:{index}")
        require(record_digest(value, receipt["digest_field"]) == receipt["digest"], f"payload:shard:{index}")

    graph = embedded["graph_projection"]
    nodes = {row["node_id"]: row for row in graph["nodes"]}
    propagation = {row["edge_id"]: row for row in graph["propagation_edges"]}
    annotations = {row["edge_id"]: row for row in graph["annotation_edges"]}
    all_edges = {**propagation, **annotations}
    require(len(nodes) == 436, "node_population")
    require(len(propagation) == 2666, "propagation_population")
    require(len(annotations) == 4, "annotation_population")
    require(bundle["selection_projection_count"] == len(bundle["selection_projections"]) == 436, "projection_population")
    require(len(bundle["catalog"]) == 436, "catalog_population")
    catalog = {row["node_id"]: row for row in bundle["catalog"]}
    require(set(catalog) == set(nodes), "catalog_node_identity")
    for node_id, row in catalog.items():
        raw = nodes[node_id]
        require(row["kind"] == raw["kind"], f"catalog_kind:{node_id}")
        require(row["identifier"] == raw["identifier"], f"catalog_identifier:{node_id}")
        require(row["source_record_id"] == raw["source_record_id"], f"catalog_source:{node_id}")
        require(bool(row["label"]), f"catalog_label:{node_id}")

    required_families = d10_2["coverage_contract"]["required_families"]
    source_family_objects: dict[str, list[str]] = defaultdict(list)
    for row in d10_2["normatively_load_bearing_objects"]:
        source_family_objects[row["family"]].append(row["object_id"])
    require(len(required_families) == len(bundle["family_coverage"]) == 9, "family_population")
    for family in bundle["family_coverage"]:
        family_id = family["family_id"]
        expected = sorted(source_family_objects[family_id])
        require(family["object_count"] == required_families[family_id], f"family_count:{family_id}")
        require(family["object_ids"] == expected, f"family_objects:{family_id}")
        require(family["node_ids"] == [f"normative_object:{value}" for value in expected], f"family_nodes:{family_id}")
        require(family["classification"] == "coverage_not_profile_scope_or_ranking", f"family_boundary:{family_id}")

    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incident: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in propagation.values():
        adjacency[edge["source"]].append(edge)
        incident[edge["source"]].append(edge)
        incident[edge["target"]].append(edge)
    for edge in annotations.values():
        incident[edge["source"]].append(edge)
        incident[edge["target"]].append(edge)

    ripple_rows = {
        row["ripple_digest"]: row
        for shard in embedded["ripple_shards"]
        for row in shard["rows"]
    }
    require(len(ripple_rows) == 24, "ripple_population")

    for node_id, projection in bundle["selection_projections"].items():
        require(node_id in nodes, f"projection_node:{node_id}")
        require(projection["selection_node_id"] == node_id, f"projection_selection:{node_id}")
        focus = projection["focus"]
        require(focus["root_node_id"] == node_id, f"focus_root:{node_id}")
        require(node_id in focus["node_ids"], f"focus_contains_root:{node_id}")
        require(len(focus["node_ids"]) <= focus["node_limit"] == 32, f"focus_nodes:{node_id}")
        require(len(focus["edge_ids"]) <= focus["edge_limit"] == 72, f"focus_edges:{node_id}")
        require(len(focus["node_ids"]) == len(set(focus["node_ids"])), f"focus_node_unique:{node_id}")
        require(len(focus["edge_ids"]) == len(set(focus["edge_ids"])), f"focus_edge_unique:{node_id}")
        require(all(value in nodes for value in focus["node_ids"]), f"focus_nodes_resolve:{node_id}")
        require(all(value in all_edges for value in focus["edge_ids"]), f"focus_edges_resolve:{node_id}")
        focus_nodes = set(focus["node_ids"])
        for edge_id in focus["edge_ids"]:
            edge = all_edges[edge_id]
            require(node_id in {edge["source"], edge["target"]}, f"focus_edge_incident:{edge_id}")
            require(edge["source"] in focus_nodes and edge["target"] in focus_nodes, f"focus_edge_endpoints:{edge_id}")
        source_neighbors = {
            edge["target"] if edge["source"] == node_id else edge["source"]
            for edge in incident[node_id]
        }
        require(
            focus["omitted_direct_neighbor_count"] == len(source_neighbors - focus_nodes),
            f"focus_omitted_neighbors:{node_id}",
        )
        require(
            focus["omitted_incident_edge_count"] == len(incident[node_id]) - len(focus["edge_ids"]),
            f"focus_omitted_edges:{node_id}",
        )

        if nodes[node_id]["kind"] == "current_claim":
            require(all(row["lens_id"] != "forward_work" for row in projection["triangulation"]), f"claim_lens_boundary:{node_id}")
        if nodes[node_id]["kind"] == "debt_transformation":
            require(all(row["lens_id"] != "support" for row in projection["triangulation"]), f"debt_lens_boundary:{node_id}")
        for lens in projection["triangulation"]:
            require(lens["edge_count"] == len(lens["rows"]) > 0, f"lens_count:{node_id}:{lens['lens_id']}")
            for row in lens["rows"]:
                edge = all_edges[row["edge_id"]]
                require(node_id in {edge["source"], edge["target"]}, f"lens_incident:{node_id}")
                other = edge["target"] if edge["source"] == node_id else edge["source"]
                require(row["neighbor_node_id"] == other, f"lens_neighbor:{node_id}")
                require(row["direction"] == ("outgoing" if edge["source"] == node_id else "incoming"), f"lens_direction:{node_id}")

        reach = projection["dependency_reach"]
        require(reach["classification"] == "dependency_reach_not_importance_priority_or_severity", f"reach_boundary:{node_id}")
        for semantic in SEMANTICS:
            direct = sorted({edge["target"] for edge in adjacency[node_id] if edge["support_semantic"] == semantic})
            seen = {node_id, *direct}
            queue = deque(direct)
            transitive: set[str] = set()
            while queue:
                current = queue.popleft()
                for edge in adjacency[current]:
                    if edge["support_semantic"] != semantic or edge["target"] in seen:
                        continue
                    seen.add(edge["target"])
                    transitive.add(edge["target"])
                    queue.append(edge["target"])
            actual = reach["by_support_semantic"][semantic]
            require(actual["direct_node_ids"] == direct, f"reach_direct:{node_id}:{semantic}")
            require(actual["transitive_node_ids"] == sorted(transitive), f"reach_transitive:{node_id}:{semantic}")
            require(actual["direct_count"] == len(direct), f"reach_direct_count:{node_id}:{semantic}")
            require(actual["transitive_count"] == len(transitive), f"reach_transitive_count:{node_id}:{semantic}")
        ripple_digest = projection["selected_ripple_digest"]
        require(ripple_digest is None or ripple_digest in ripple_rows, f"ripple_selection:{node_id}")

    require(parity["static_bundle_digest"] == bundle["bundle_digest"], "parity_bundle_binding")
    require(len(parity["selection_payloads"]) == 7, "parity_population")
    for node_id, payload in parity["selection_payloads"].items():
        require(payload["selection"]["node_id"] == node_id, f"parity_selection:{node_id}")
        require(payload["focus"]["root_node_id"] == node_id, f"parity_focus:{node_id}")

    dist = TOOL_ROOT / "web/dist"
    require(manifest["static_bundle_digest"] == bundle["bundle_digest"], "manifest_bundle_binding")
    require(manifest["cross_surface_parity_digest"] == parity["parity_digest"], "manifest_parity_binding")
    require(manifest["file_count"] == len(manifest["files"]), "manifest_file_count")
    if not skip_dist_identity:
        for row in manifest["files"]:
            path = dist / row["path"]
            require(path.is_file(), f"dist_file:{row['path']}")
            require(path.stat().st_size == row["size_bytes"], f"dist_size:{row['path']}")
            require(file_sha256(path) == row["sha256"], f"dist_digest:{row['path']}")
    package = load_json_object(TOOL_ROOT / "web/package.json")
    require(package["devDependencies"]["cytoscape"] == "3.33.1", "cytoscape_pin")
    require(package["devDependencies"]["vite"] == "7.1.3", "vite_pin")
    require(package["devDependencies"]["@playwright/test"] == "1.55.0", "playwright_pin")
    require(package["devDependencies"]["lucide"] == "0.468.0", "lucide_pin")

    client_source = "\n".join(
        (TOOL_ROOT / "web/src" / name).read_text(encoding="utf-8")
        for name in ("app.js", "bundle.js")
    )
    for forbidden in (
        "compileRipple",
        "compile_ripple",
        "evaluateMutation",
        "evaluate_mutation",
        "breadthFirstSearch",
    ):
        require(forbidden not in client_source, f"client_rule_absent:{forbidden}")

    print(
        "ET_C6_AUDIT_PASS "
        f"checks={checks} nodes={len(nodes)} projections={len(bundle['selection_projections'])} "
        f"families={len(bundle['family_coverage'])} parity={len(parity['selection_payloads'])} "
        f"dist={'historical_skipped' if skip_dist_identity else 'exact'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
