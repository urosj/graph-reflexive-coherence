#!/usr/bin/env python3
"""Independently audit ET-C2 from raw accepted source records."""

from __future__ import annotations

import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    digest,
    file_sha256,
    load_json_object,
    record_digest,
)
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


NODE_KINDS = {
    "current_claim",
    "historical_claim",
    "debt_transformation",
    "verification_obligation",
    "gate_record",
    "candidate",
    "realization",
    "profile",
    "normative_object",
    "equation_contract",
    "source_record",
    "annotation",
}


def rows(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise RuntimeError(f"ET-C2 audit found malformed rows: {label}")
    return cast(list[dict[str, Any]], value)


def strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise RuntimeError(f"ET-C2 audit found malformed strings: {label}")
    return cast(list[str], value)


def string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"ET-C2 audit found malformed string: {label}")
    return value


def node_id(kind: str, identifier: str) -> str:
    return f"{kind}:{identifier}"


def support_semantic(relation: str) -> str:
    if relation == "conditioned_by":
        return "conditional"
    if relation in {
        "negative_successor_of",
        "resolved_negative",
        "resolved_negative_by",
    }:
        return "negative_boundary"
    if relation == "requires_verification_from":
        return "required"
    if relation in {"supported_by", "blocked_by", "parent_object", "accepted_claim"}:
        return "indeterminate_requires_review"
    return "not_applicable"


class ExpectedGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.propagation: dict[str, dict[str, Any]] = {}
        self.annotations: dict[str, dict[str, Any]] = {}

    def add_node(
        self,
        kind: str,
        identifier: str,
        source_record_id: str,
        pointer: str,
        attributes: dict[str, Any],
    ) -> str:
        identifier_value = node_id(kind, identifier)
        value = {
            "node_id": identifier_value,
            "kind": kind,
            "identifier": identifier,
            "source_record_id": source_record_id,
            "source_json_pointer": pointer,
            "attributes": attributes,
        }
        if kind not in NODE_KINDS or identifier_value in self.nodes:
            raise RuntimeError(
                f"ET-C2 audit expected duplicate node: {identifier_value}"
            )
        self.nodes[identifier_value] = value
        return identifier_value

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        source_record_id: str,
        pointer: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "source": source,
            "target": target,
            "relation": relation,
            "support_semantic": support_semantic(relation),
            "source_record_id": source_record_id,
            "source_json_pointer": pointer,
            "attributes": attributes or {},
        }
        edge_id = f"propagation:{digest(payload)}"
        if edge_id in self.propagation:
            raise RuntimeError(f"ET-C2 audit expected duplicate edge: {edge_id}")
        self.propagation[edge_id] = {"edge_id": edge_id, **payload}

    def add_annotation(
        self,
        source: str,
        target: str,
        relation: str,
        source_record_id: str,
        pointer: str,
    ) -> None:
        payload = {
            "source": source,
            "target": target,
            "relation": relation,
            "authority": "display_only",
            "source_record_id": source_record_id,
            "source_json_pointer": pointer,
        }
        edge_id = f"annotation:{digest(payload)}"
        if edge_id in self.annotations:
            raise RuntimeError(f"ET-C2 audit expected duplicate annotation: {edge_id}")
        self.annotations[edge_id] = {"edge_id": edge_id, **payload}


def record_identifier(data: dict[str, Any], label: str) -> str:
    return string(data.get("record_id") or data.get("artifact_id"), label)


def record_declared_digest(data: dict[str, Any], label: str) -> str:
    value = data.get("decision_record_digest") or data.get("artifact_digest")
    return string(value, label)


def source_nodes(
    expected: ExpectedGraph,
    admissions: list[dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    provenance: dict[str, Any],
    provenance_id: str,
) -> dict[str, str]:
    identities: dict[tuple[str, str], dict[str, Any]] = {}

    def add(
        source_id: str,
        path: str,
        sha: str,
        source_digest: str | None,
        status: str | None,
        admitted: bool,
    ) -> None:
        value = identities.setdefault(
            (path, sha),
            {
                "source_ids": [],
                "path": path,
                "file_sha256": sha,
                "source_digests": [],
                "statuses": [],
                "admitted_bundle_record": False,
            },
        )
        if source_id not in value["source_ids"]:
            value["source_ids"].append(source_id)
        if source_digest is not None and source_digest not in value["source_digests"]:
            value["source_digests"].append(source_digest)
        if status is not None and status not in value["statuses"]:
            value["statuses"].append(status)
        value["admitted_bundle_record"] = value["admitted_bundle_record"] or admitted

    for admission in admissions:
        path = string(admission.get("path"), "admission path")
        data = sources[Path(path).name]
        add(
            record_identifier(data, path),
            path,
            string(admission.get("file_sha256"), "admission SHA"),
            record_declared_digest(data, path),
            string(data.get("status"), "source status"),
            True,
        )
    for index, value in enumerate(rows(provenance.get("source_identities"), "sources")):
        source_digest_value = value.get("source_digest")
        if source_digest_value is not None and not isinstance(source_digest_value, str):
            raise RuntimeError(f"ET-C2 audit malformed source digest at {index}")
        add(
            string(value.get("source_id"), "source ID"),
            string(value.get("path"), "source path"),
            string(value.get("file_sha256"), "source SHA"),
            source_digest_value,
            None,
            False,
        )

    aliases: dict[str, str] = {}
    paths_seen: dict[str, str] = {}
    for (path, sha), attributes in sorted(identities.items()):
        attributes["source_ids"] = sorted(attributes["source_ids"])
        attributes["source_digests"] = sorted(attributes["source_digests"])
        attributes["statuses"] = sorted(attributes["statuses"])
        physical_id = digest({"path": path, "file_sha256": sha})
        graph_id = expected.add_node(
            "source_record",
            physical_id,
            provenance_id,
            "/source_identities",
            attributes,
        )
        if path in paths_seen and paths_seen[path] != graph_id:
            raise RuntimeError(f"ET-C2 audit found multiple identities for {path}")
        paths_seen[path] = graph_id
        for alias in attributes["source_ids"]:
            if alias in aliases and aliases[alias] != graph_id:
                raise RuntimeError(f"ET-C2 audit found ambiguous source alias: {alias}")
            aliases[alias] = graph_id
    return aliases


def add_source_edge(
    expected: ExpectedGraph,
    source: str,
    alias: str,
    source_record_id: str,
    pointer: str,
    source_aliases: dict[str, str],
) -> None:
    expected.add_edge(
        source,
        source_aliases[alias],
        "source_identity",
        source_record_id,
        pointer,
    )


def build_expected_graph(
    admissions: list[dict[str, Any]], sources: dict[str, dict[str, Any]]
) -> ExpectedGraph:
    expected = ExpectedGraph()
    topology = sources["D10NormativeClaimTopology.json"]
    debt = sources["D10DebtClaimTransformationLedger.json"]
    provenance = sources["D10_2FullSubstrateProvenanceAndPromotionAudit.json"]
    profile_registry = sources["D9ProfileStateLifecycleRegistry.json"]
    d9_debt = sources["D9ResidualDebtLedger.json"]
    d1 = sources["D1RetainedRepresentationOntologyAndCandidateAdmission.json"]
    d10 = sources["D10DesignSynthesisAndSpecWritingDecision.json"]
    comparative = sources["GeometryTemporalRealizationComparativeSynthesis.json"]
    topology_id = record_identifier(topology, "topology ID")
    debt_id = record_identifier(debt, "debt ID")
    provenance_id = record_identifier(provenance, "provenance ID")
    profile_registry_id = record_identifier(profile_registry, "profile registry ID")
    d9_debt_id = record_identifier(d9_debt, "D9 debt ID")
    d1_id = record_identifier(d1, "D1 ID")
    comparative_id = record_identifier(comparative, "comparative ID")
    source_aliases = source_nodes(
        expected, admissions, sources, provenance, provenance_id
    )

    gate_nodes: dict[str, str] = {}
    digest_to_gate: dict[str, str] = {}
    for admission in admissions:
        filename = Path(string(admission["path"], "admission path")).name
        data = sources[filename]
        identifier = record_identifier(data, filename)
        declared = record_declared_digest(data, filename)
        graph_id = expected.add_node(
            "gate_record",
            identifier,
            identifier,
            "/",
            {
                "gate_id": data.get("gate_id"),
                "status": data["status"],
                "record_digest": declared,
                "path": admission["path"],
            },
        )
        gate_nodes[identifier] = graph_id
        digest_to_gate[declared] = graph_id
        add_source_edge(expected, graph_id, identifier, identifier, "/", source_aliases)

    for admission in admissions:
        filename = Path(cast(str, admission["path"])).name
        data = sources[filename]
        identifier = record_identifier(data, filename)
        current = gate_nodes[identifier]
        predecessor_digest = data.get("predecessor_decision_digest")
        if isinstance(predecessor_digest, str) and predecessor_digest in digest_to_gate:
            expected.add_edge(
                digest_to_gate[predecessor_digest],
                current,
                "predecessor_record",
                identifier,
                "/predecessor_decision_digest",
                {"predecessor_digest": predecessor_digest},
            )
        supersedes = data.get("supersedes")
        superseded: str | None = None
        if isinstance(supersedes, str):
            superseded = supersedes
        elif isinstance(supersedes, dict) and isinstance(
            supersedes.get("record_id"), str
        ):
            superseded = cast(str, supersedes["record_id"])
        if superseded is not None:
            expected.add_edge(
                gate_nodes[superseded],
                current,
                "superseded_by",
                identifier,
                "/supersedes",
            )

    claim_nodes: dict[str, str] = {}
    for kind, claim_rows, base in (
        ("current_claim", rows(topology.get("claims"), "current claims"), "/claims"),
        (
            "historical_claim",
            rows(topology.get("historical_claim_nodes"), "historical claims"),
            "/historical_claim_nodes",
        ),
    ):
        for index, row in enumerate(claim_rows):
            claim_id = string(row.get("claim_id"), "claim ID")
            pointer = f"{base}/{index}"
            graph_id = expected.add_node(kind, claim_id, topology_id, pointer, row)
            claim_nodes[claim_id] = graph_id
            add_source_edge(
                expected, graph_id, topology_id, topology_id, pointer, source_aliases
            )
            expected.add_edge(
                graph_id, gate_nodes[topology_id], "accepted_at", topology_id, pointer
            )
            for evidence_index, evidence_id in enumerate(
                strings(row.get("evidence_refs"), "claim evidence")
            ):
                expected.add_edge(
                    graph_id,
                    gate_nodes[evidence_id],
                    "supported_by",
                    topology_id,
                    f"{pointer}/evidence_refs/{evidence_index}",
                )

    debt_nodes: dict[str, str] = {}
    debt_rows = rows(debt.get("debt_transformations"), "debt transformations")
    for index, row in enumerate(debt_rows):
        identifier = string(row.get("debt_id"), "debt ID")
        pointer = f"/debt_transformations/{index}"
        graph_id = expected.add_node(
            "debt_transformation", identifier, debt_id, pointer, row
        )
        debt_nodes[identifier] = graph_id
        add_source_edge(expected, graph_id, debt_id, debt_id, pointer, source_aliases)
        expected.add_edge(
            graph_id, gate_nodes[debt_id], "accepted_at", debt_id, pointer
        )

    for edge_index, edge in enumerate(
        rows(topology.get("claim_debt_edges"), "claim/debt edges")
    ):
        claim_id = string(edge.get("claim_id"), "claim/debt claim ID")
        transformation_id = string(edge.get("debt_id"), "claim/debt debt ID")
        for type_index, relation in enumerate(
            strings(edge.get("edge_types"), "claim/debt edge types")
        ):
            expected.add_edge(
                claim_nodes[claim_id],
                debt_nodes[transformation_id],
                relation,
                topology_id,
                f"/claim_debt_edges/{edge_index}/edge_types/{type_index}",
            )

    for index, row in enumerate(debt_rows):
        identifier = string(row["debt_id"], "debt ID")
        pointer = f"/debt_transformations/{index}"
        for claim_index, claim_id in enumerate(
            strings(row.get("predecessor_claim_ids"), "predecessor claims")
        ):
            expected.add_edge(
                claim_nodes[claim_id],
                debt_nodes[identifier],
                "transformed_from",
                debt_id,
                f"{pointer}/predecessor_claim_ids/{claim_index}",
            )
        transformation = string(row.get("transformation"), "transformation")
        for claim_index, claim_id in enumerate(
            strings(row.get("successor_claim_ids"), "successor claims")
        ):
            expected.add_edge(
                debt_nodes[identifier],
                claim_nodes[claim_id],
                transformation,
                debt_id,
                f"{pointer}/successor_claim_ids/{claim_index}",
                {"transformation_verb": transformation},
            )
        for evidence_index, evidence_id in enumerate(
            strings(row.get("evidence_refs"), "debt evidence")
        ):
            expected.add_edge(
                debt_nodes[identifier],
                gate_nodes[evidence_id],
                "supported_by",
                debt_id,
                f"{pointer}/evidence_refs/{evidence_index}",
            )

    obligation_nodes: dict[str, str] = {}
    for index, row in enumerate(
        rows(debt.get("verification_obligations"), "verification obligations")
    ):
        obligation_id = string(row.get("obligation_id"), "obligation ID")
        pointer = f"/verification_obligations/{index}"
        graph_id = expected.add_node(
            "verification_obligation", obligation_id, debt_id, pointer, row
        )
        obligation_nodes[obligation_id] = graph_id
        add_source_edge(expected, graph_id, debt_id, debt_id, pointer, source_aliases)
        for claim_index, claim_id in enumerate(
            strings(row.get("claim_ids_blocked"), "blocked claims")
        ):
            expected.add_edge(
                claim_nodes[claim_id],
                graph_id,
                "requires_verification_from",
                debt_id,
                f"{pointer}/claim_ids_blocked/{claim_index}",
                {
                    "originating_gate_id": debt.get("gate_id"),
                    "originating_record_id": debt_id,
                    "originating_record_digest": record_declared_digest(debt, debt_id),
                    "source_json_pointer": pointer,
                },
            )
    for index, row in enumerate(debt_rows):
        referenced_obligation_id = row.get("verification_obligation")
        if isinstance(referenced_obligation_id, str):
            pointer = f"/debt_transformations/{index}/verification_obligation"
            expected.add_edge(
                debt_nodes[string(row["debt_id"], "debt ID")],
                obligation_nodes[referenced_obligation_id],
                "requires_verification_from",
                debt_id,
                pointer,
                {
                    "originating_gate_id": debt.get("gate_id"),
                    "originating_record_id": debt_id,
                    "originating_record_digest": record_declared_digest(debt, debt_id),
                    "source_json_pointer": pointer,
                },
            )
    for index, row in enumerate(
        rows(d9_debt.get("post_spec_verification_obligations"), "D9 obligations")
    ):
        obligation_id = string(row.get("obligation_id"), "D9 obligation ID")
        pointer = f"/post_spec_verification_obligations/{index}"
        expected.add_edge(
            gate_nodes[d9_debt_id],
            obligation_nodes[obligation_id],
            "requires_verification_from",
            d9_debt_id,
            pointer,
            {
                "originating_gate_id": d9_debt.get("gate_id"),
                "originating_record_id": d9_debt_id,
                "originating_record_digest": record_declared_digest(
                    d9_debt, d9_debt_id
                ),
                "source_json_pointer": pointer,
            },
        )

    candidate_nodes: dict[str, str] = {}
    d1_decision = cast(dict[str, Any], d1["decision"])
    candidate_keys = (
        "candidate_status",
        "causal_type",
        "state_authority",
        "resource_accounting",
        "rejection_reason",
        "reopening_rule",
    )
    for index, row in enumerate(
        rows(d1_decision.get("candidate_matrix"), "candidates")
    ):
        candidate_id = string(row.get("candidate_id"), "candidate ID")
        pointer = f"/decision/candidate_matrix/{index}"
        graph_id = expected.add_node(
            "candidate",
            candidate_id,
            d1_id,
            pointer,
            {key: row[key] for key in candidate_keys if key in row},
        )
        candidate_nodes[candidate_id] = graph_id
        add_source_edge(expected, graph_id, d1_id, d1_id, pointer, source_aliases)
        annotation_id = expected.add_node(
            "annotation",
            f"candidate-disposition:{candidate_id}",
            d1_id,
            pointer,
            {
                "candidate_status": row.get("candidate_status"),
                "display_summary": row.get("rejection_reason")
                or row.get("causal_type"),
                "authority": "display_only",
            },
        )
        expected.add_annotation(
            graph_id,
            annotation_id,
            "candidate_disposition_annotation",
            d1_id,
            pointer,
        )

    profile_nodes: dict[str, str] = {}
    d10_decision = cast(dict[str, Any], d10["decision"])
    grammar = cast(
        dict[str, Any], d10_decision["executable_profile_conformance_grammar"]
    )
    admitted_profile_ids = set(
        strings(grammar.get("admitted_complete_profile_ids"), "D10 admitted profiles")
    )
    source_profile_ids = {
        string(row.get("profile_id"), "profile ID")
        for row in rows(profile_registry.get("profiles"), "profiles")
    }
    if source_profile_ids != admitted_profile_ids:
        raise RuntimeError("ET-C2 audit found D9/D10 profile population mismatch")
    candidate_aliases = {
        "A": "V4-A-temporalized-W",
        "C": "V4-C-constitutive-C-sector",
    }
    for index, row in enumerate(rows(profile_registry.get("profiles"), "profiles")):
        profile_id = string(row.get("profile_id"), "profile ID")
        pointer = f"/profiles/{index}"
        profile_node = expected.add_node(
            "profile", profile_id, profile_registry_id, pointer, row
        )
        profile_nodes[profile_id] = profile_node
        realization_node = expected.add_node(
            "realization",
            f"profile:{profile_id}",
            profile_registry_id,
            pointer,
            {
                "row_role": "complete_profile_realization",
                "profile_id": profile_id,
                "candidate": row.get("candidate"),
                "timing": row.get("timing"),
                "history": row.get("history"),
            },
        )
        add_source_edge(
            expected,
            profile_node,
            profile_registry_id,
            profile_registry_id,
            pointer,
            source_aliases,
        )
        add_source_edge(
            expected,
            realization_node,
            profile_registry_id,
            profile_registry_id,
            pointer,
            source_aliases,
        )
        candidate = candidate_aliases[string(row.get("candidate"), "profile candidate")]
        expected.add_edge(
            profile_node,
            candidate_nodes[candidate],
            "candidate_scope",
            profile_registry_id,
            f"{pointer}/candidate",
        )
        expected.add_edge(
            realization_node,
            profile_node,
            "active_in_profile",
            profile_registry_id,
            f"{pointer}/profile_id",
        )

    comparative_decision = cast(dict[str, Any], comparative["decision"])
    for index, row in enumerate(
        rows(comparative_decision.get("architecture_population"), "comparisons")
    ):
        row_id = string(row.get("row_id"), "comparison row ID")
        pointer = f"/decision/architecture_population/{index}"
        graph_id = expected.add_node(
            "realization",
            f"comparison:{row_id}",
            comparative_id,
            pointer,
            {"row_role": "comparative_pressure_row", **row},
        )
        add_source_edge(
            expected, graph_id, comparative_id, comparative_id, pointer, source_aliases
        )
        expected.add_edge(
            graph_id,
            candidate_nodes[string(row.get("candidate"), "comparison candidate")],
            "candidate_scope",
            comparative_id,
            f"{pointer}/candidate",
        )

    object_nodes: dict[str, str] = {}
    for index, row in enumerate(
        rows(provenance.get("normatively_load_bearing_objects"), "objects")
    ):
        object_id = string(row.get("object_id"), "object ID")
        pointer = f"/normatively_load_bearing_objects/{index}"
        graph_id = expected.add_node(
            "normative_object", object_id, provenance_id, pointer, row
        )
        object_nodes[object_id] = graph_id
        add_source_edge(
            expected, graph_id, provenance_id, provenance_id, pointer, source_aliases
        )
        for lineage_index, source_id in enumerate(
            strings(row.get("source_lineage"), "object lineage")
        ):
            expected.add_edge(
                graph_id,
                source_aliases[source_id],
                "source_identity",
                provenance_id,
                f"{pointer}/source_lineage/{lineage_index}",
            )

    for index, row in enumerate(
        rows(provenance.get("normative_equation_contract_registry"), "contracts")
    ):
        contract_id = string(row.get("equation_contract_id"), "contract ID")
        pointer = f"/normative_equation_contract_registry/{index}"
        graph_id = expected.add_node(
            "equation_contract", contract_id, provenance_id, pointer, row
        )
        add_source_edge(
            expected, graph_id, provenance_id, provenance_id, pointer, source_aliases
        )
        for parent_index, object_id in enumerate(
            strings(row.get("parent_object_ids"), "contract parents")
        ):
            expected.add_edge(
                graph_id,
                object_nodes[object_id],
                "parent_object",
                provenance_id,
                f"{pointer}/parent_object_ids/{parent_index}",
            )
        for claim_index, claim_id in enumerate(
            strings(row.get("accepted_claim_ids"), "contract claims")
        ):
            expected.add_edge(
                graph_id,
                claim_nodes[claim_id],
                "accepted_claim",
                provenance_id,
                f"{pointer}/accepted_claim_ids/{claim_index}",
            )
        for profile_index, profile_id in enumerate(
            strings(row.get("profile_ids"), "contract profiles")
        ):
            expected.add_edge(
                graph_id,
                profile_nodes[profile_id],
                "active_in_profile",
                provenance_id,
                f"{pointer}/profile_ids/{profile_index}",
            )
        for lineage_index, source_id in enumerate(
            strings(row.get("source_lineage"), "contract lineage")
        ):
            expected.add_edge(
                graph_id,
                source_aliases[source_id],
                "source_identity",
                provenance_id,
                f"{pointer}/source_lineage/{lineage_index}",
            )
    return expected


def gate_dag_is_acyclic(graph: dict[str, Any]) -> bool:
    gates = {
        row["node_id"]
        for row in rows(graph.get("nodes"), "graph nodes")
        if row["kind"] == "gate_record"
    }
    adjacency: dict[str, set[str]] = {identifier: set() for identifier in gates}
    indegree = {identifier: 0 for identifier in gates}
    for edge in rows(graph.get("propagation_edges"), "graph edges"):
        if edge["relation"] not in {"predecessor_record", "superseded_by"}:
            continue
        source = cast(str, edge["source"])
        target = cast(str, edge["target"])
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1
    queue = deque(
        sorted(identifier for identifier, degree in indegree.items() if degree == 0)
    )
    seen = 0
    while queue:
        source = queue.popleft()
        seen += 1
        for target in sorted(adjacency[source]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return seen == len(gates)


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    checks = 0

    def verify(condition: bool, label: str) -> None:
        nonlocal checks
        if not condition:
            raise RuntimeError(f"ET-C2 independent audit failed: {label}")
        checks += 1

    records_dir = SIDE_TOOL_ROOT / "records"
    contract = load_et_c0_contract(records_dir / "ETC0SourceAndLayoutContract.json")
    admissions = admitted_rows(contract)
    sources: dict[str, dict[str, Any]] = {}
    for admission in admissions:
        relative = string(admission.get("path"), "admission path")
        path = repo_root / relative
        verify(path.is_file(), f"source exists: {relative}")
        verify(
            file_sha256(path) == admission.get("file_sha256"),
            f"source SHA: {relative}",
        )
        data = load_json_object(path)
        digest_field = string(
            admission.get("canonical_digest_field"), "canonical digest field"
        )
        verify(
            data.get(digest_field) == record_digest(data, digest_field),
            f"source digest: {relative}",
        )
        sources[path.name] = data
    verify(len(sources) == 33, "33 unique admitted source files")

    graph_path = records_dir / "ETC2GraphSnapshot.json"
    graph = load_json_object(graph_path)
    verify(
        graph_path.read_bytes() == canonical_bytes(graph) + b"\n",
        "canonical graph bytes",
    )
    verify(
        graph.get("graph_digest")
        == digest(
            {key: value for key, value in graph.items() if key != "graph_digest"}
        ),
        "graph digest",
    )
    expected = build_expected_graph(admissions, sources)
    expected_nodes = sorted(
        expected.nodes.values(), key=lambda row: cast(str, row["node_id"])
    )
    expected_propagation = sorted(
        expected.propagation.values(), key=lambda row: cast(str, row["edge_id"])
    )
    expected_annotations = sorted(
        expected.annotations.values(), key=lambda row: cast(str, row["edge_id"])
    )
    verify(graph.get("nodes") == expected_nodes, "exact raw-source node witness")
    verify(
        graph.get("propagation_edges") == expected_propagation,
        "exact raw-source propagation witness",
    )
    verify(
        graph.get("annotation_edges") == expected_annotations,
        "exact raw-source annotation witness",
    )
    verify(gate_dag_is_acyclic(graph), "gate lineage DAG")

    node_counts = dict(sorted(Counter(row["kind"] for row in expected_nodes).items()))
    verify(
        all(
            node_counts[kind] == count
            for kind, count in {
                "current_claim": 39,
                "historical_claim": 29,
                "debt_transformation": 29,
                "verification_obligation": 11,
                "normative_object": 67,
                "equation_contract": 152,
            }.items()
        ),
        "source-owned populations",
    )
    verify(graph.get("node_counts") == node_counts, "node-count projection")
    verify(
        graph.get("propagation_edge_count") == len(expected_propagation),
        "propagation count",
    )
    verify(
        graph.get("annotation_edge_count") == len(expected_annotations),
        "annotation count",
    )
    verify(
        graph.get("invariants", {}).get("all_passed") is True
        and graph.get("invariants", {}).get("passed_count") == 14,
        "14 kernel invariants",
    )
    obligation_ids = {
        row["node_id"]
        for row in expected_nodes
        if row["kind"] == "verification_obligation"
    }
    verify(
        not any(
            row["source"] in obligation_ids
            and row["relation"]
            in {"supported_by", "accepted_claim", "transformed_from", "successor_of"}
            for row in expected_propagation
        ),
        "verification obligations are forward-only",
    )
    annotation_node_ids = {
        row["node_id"] for row in expected_nodes if row["kind"] == "annotation"
    }
    verify(
        not any(
            row["source"] in annotation_node_ids or row["target"] in annotation_node_ids
            for row in expected_propagation
        ),
        "annotation isolation",
    )

    candidate = load_json_object(records_dir / "ETC2ValidatedGraphKernel.json")
    verify(candidate.get("status") == "accepted", "accepted gate status")
    verify(
        candidate.get("record_digest") == record_digest(candidate, "record_digest"),
        "candidate digest",
    )
    verify(
        candidate["graph_snapshot"]["graph_digest"] == graph["graph_digest"],
        "candidate graph binding",
    )
    verify(
        candidate["authority"]["iteration_3_authorized"] is True,
        "Iteration 3 authorization",
    )
    print(
        "ET_C2_AUDIT_PASS "
        f"checks={checks} nodes={len(expected_nodes)} "
        f"relationships={len(expected_propagation) + len(expected_annotations)} "
        f"graph={graph['graph_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
