"""Deterministic, source-traceable ET-C2 graph kernel."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable, cast

from .adapters import SourceDocument
from .canonical import canonical_bytes, digest
from .errors import GraphInvariantError


KERNEL_SCHEMA = "grcv4_explorer_validated_graph_v1"
KERNEL_VERSION = "ET-C2-v1"

NODE_KINDS = (
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
)

SUPPORT_SEMANTICS = {
    "required",
    "one_of",
    "conditional",
    "negative_boundary",
    "not_applicable",
    "indeterminate_requires_review",
}


def _node_id(kind: str, identifier: str) -> str:
    return f"{kind}:{identifier}"


def _objects(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise GraphInvariantError(f"malformed object rows: {label}")
    return cast(list[dict[str, Any]], value)


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise GraphInvariantError(f"malformed string rows: {label}")
    return cast(list[str], value)


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise GraphInvariantError(f"missing string: {label}")
    return value


def _optional_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _string(value, label)


def _support_semantic(relation: str) -> str:
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


class _GraphAssembly:
    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.propagation_edges: dict[str, dict[str, Any]] = {}
        self.annotation_edges: dict[str, dict[str, Any]] = {}

    def add_node(
        self,
        kind: str,
        identifier: str,
        *,
        source_record_id: str,
        source_json_pointer: str,
        attributes: dict[str, Any],
    ) -> str:
        if kind not in NODE_KINDS:
            raise GraphInvariantError(f"unknown node kind: {kind}")
        node_id = _node_id(kind, identifier)
        row = {
            "node_id": node_id,
            "kind": kind,
            "identifier": identifier,
            "source_record_id": source_record_id,
            "source_json_pointer": source_json_pointer,
            "attributes": attributes,
        }
        if node_id in self.nodes and self.nodes[node_id] != row:
            raise GraphInvariantError(f"conflicting node: {node_id}")
        self.nodes[node_id] = row
        return node_id

    def add_propagation_edge(
        self,
        source: str,
        target: str,
        relation: str,
        *,
        source_record_id: str,
        source_json_pointer: str,
        support_semantic: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> str:
        semantic = support_semantic or _support_semantic(relation)
        if semantic not in SUPPORT_SEMANTICS:
            raise GraphInvariantError(f"unknown support semantic: {semantic}")
        payload = {
            "source": source,
            "target": target,
            "relation": relation,
            "support_semantic": semantic,
            "source_record_id": source_record_id,
            "source_json_pointer": source_json_pointer,
            "attributes": attributes or {},
        }
        edge_id = f"propagation:{digest(payload)}"
        if edge_id in self.propagation_edges:
            raise GraphInvariantError(f"duplicate propagation edge: {edge_id}")
        self.propagation_edges[edge_id] = {"edge_id": edge_id, **payload}
        return edge_id

    def add_annotation_edge(
        self,
        source: str,
        target: str,
        relation: str,
        *,
        source_record_id: str,
        source_json_pointer: str,
    ) -> str:
        payload = {
            "source": source,
            "target": target,
            "relation": relation,
            "authority": "display_only",
            "source_record_id": source_record_id,
            "source_json_pointer": source_json_pointer,
        }
        edge_id = f"annotation:{digest(payload)}"
        if edge_id in self.annotation_edges:
            raise GraphInvariantError(f"duplicate annotation edge: {edge_id}")
        self.annotation_edges[edge_id] = {"edge_id": edge_id, **payload}
        return edge_id


def _document_map(documents: list[SourceDocument]) -> dict[str, SourceDocument]:
    result = {document.filename: document for document in documents}
    if len(result) != len(documents):
        raise GraphInvariantError("source filenames are not unique")
    return result


def _physical_source_key(path: str, file_sha256: str) -> str:
    return digest({"path": path, "file_sha256": file_sha256})


def _build_source_nodes(
    assembly: _GraphAssembly,
    documents: list[SourceDocument],
    provenance: SourceDocument,
) -> tuple[dict[str, str], dict[str, str]]:
    identities: dict[tuple[str, str], dict[str, Any]] = {}

    def add_identity(
        source_id: str,
        path: str,
        file_sha256: str,
        source_digest: str | None,
        *,
        status: str | None,
        admitted_bundle_record: bool,
    ) -> None:
        key = (path, file_sha256)
        row = identities.setdefault(
            key,
            {
                "source_ids": [],
                "path": path,
                "file_sha256": file_sha256,
                "source_digests": [],
                "statuses": [],
                "admitted_bundle_record": False,
            },
        )
        if source_id not in row["source_ids"]:
            row["source_ids"].append(source_id)
        if source_digest is not None and source_digest not in row["source_digests"]:
            row["source_digests"].append(source_digest)
        if status is not None and status not in row["statuses"]:
            row["statuses"].append(status)
        row["admitted_bundle_record"] = (
            row["admitted_bundle_record"] or admitted_bundle_record
        )

    for document in documents:
        add_identity(
            document.record_identifier,
            cast(str, document.admission["path"]),
            cast(str, document.admission["file_sha256"]),
            document.declared_digest,
            status=cast(str, document.data["status"]),
            admitted_bundle_record=True,
        )

    for index, row in enumerate(
        _objects(provenance.data.get("source_identities"), "source_identities")
    ):
        add_identity(
            _string(row.get("source_id"), f"source_identities/{index}/source_id"),
            _string(row.get("path"), f"source_identities/{index}/path"),
            _string(
                row.get("file_sha256"),
                f"source_identities/{index}/file_sha256",
            ),
            _optional_string(
                row.get("source_digest"),
                f"source_identities/{index}/source_digest",
            ),
            status=None,
            admitted_bundle_record=False,
        )

    alias_to_node: dict[str, str] = {}
    path_to_node: dict[str, str] = {}
    for (path, file_sha256), row in sorted(identities.items()):
        physical_id = _physical_source_key(path, file_sha256)
        row["source_ids"] = sorted(row["source_ids"])
        row["source_digests"] = sorted(row["source_digests"])
        row["statuses"] = sorted(row["statuses"])
        node_id = assembly.add_node(
            "source_record",
            physical_id,
            source_record_id=provenance.record_identifier,
            source_json_pointer="/source_identities",
            attributes=row,
        )
        if path in path_to_node and path_to_node[path] != node_id:
            raise GraphInvariantError(
                f"one path has multiple accepted byte identities: {path}"
            )
        path_to_node[path] = node_id
        for alias in row["source_ids"]:
            if alias in alias_to_node and alias_to_node[alias] != node_id:
                raise GraphInvariantError(f"source alias is ambiguous: {alias}")
            alias_to_node[alias] = node_id
    return alias_to_node, path_to_node


def _add_source_identity_edge(
    assembly: _GraphAssembly,
    node_id: str,
    source_node_id: str,
    document: SourceDocument,
    pointer: str,
) -> None:
    assembly.add_propagation_edge(
        node_id,
        source_node_id,
        "source_identity",
        source_record_id=document.record_identifier,
        source_json_pointer=pointer,
    )


def _gate_nodes(
    assembly: _GraphAssembly,
    documents: list[SourceDocument],
    source_aliases: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    by_record: dict[str, str] = {}
    by_digest: dict[str, str] = {}
    for document in documents:
        node_id = assembly.add_node(
            "gate_record",
            document.record_identifier,
            source_record_id=document.record_identifier,
            source_json_pointer="/",
            attributes={
                "gate_id": document.data.get("gate_id"),
                "status": document.data["status"],
                "record_digest": document.declared_digest,
                "path": document.admission["path"],
            },
        )
        by_record[document.record_identifier] = node_id
        by_digest[document.declared_digest] = node_id
        _add_source_identity_edge(
            assembly,
            node_id,
            source_aliases[document.record_identifier],
            document,
            "/",
        )

    for document in documents:
        current = by_record[document.record_identifier]
        predecessor_digest = document.data.get("predecessor_decision_digest")
        if isinstance(predecessor_digest, str) and predecessor_digest in by_digest:
            assembly.add_propagation_edge(
                by_digest[predecessor_digest],
                current,
                "predecessor_record",
                source_record_id=document.record_identifier,
                source_json_pointer="/predecessor_decision_digest",
                attributes={"predecessor_digest": predecessor_digest},
            )
        supersedes = document.data.get("supersedes")
        superseded_record: str | None = None
        if isinstance(supersedes, str):
            superseded_record = supersedes
        elif isinstance(supersedes, dict):
            value = supersedes.get("record_id")
            if isinstance(value, str):
                superseded_record = value
        if superseded_record is not None:
            if superseded_record not in by_record:
                raise GraphInvariantError(
                    f"superseded gate record does not resolve: {superseded_record}"
                )
            assembly.add_propagation_edge(
                by_record[superseded_record],
                current,
                "superseded_by",
                source_record_id=document.record_identifier,
                source_json_pointer="/supersedes",
            )
    return by_record, by_digest


def _add_claim_and_debt_layers(
    assembly: _GraphAssembly,
    topology: SourceDocument,
    debt: SourceDocument,
    gate_nodes: dict[str, str],
    source_aliases: dict[str, str],
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    claim_nodes: dict[str, str] = {}
    debt_nodes: dict[str, str] = {}
    obligation_nodes: dict[str, str] = {}
    current_rows = _objects(topology.data.get("claims"), "claims")
    historical_rows = _objects(
        topology.data.get("historical_claim_nodes"), "historical_claim_nodes"
    )
    for kind, rows, base_pointer in (
        ("current_claim", current_rows, "/claims"),
        ("historical_claim", historical_rows, "/historical_claim_nodes"),
    ):
        for index, row in enumerate(rows):
            claim_id = _string(row.get("claim_id"), f"{base_pointer}/{index}/claim_id")
            pointer = f"{base_pointer}/{index}"
            node_id = assembly.add_node(
                kind,
                claim_id,
                source_record_id=topology.record_identifier,
                source_json_pointer=pointer,
                attributes=row,
            )
            claim_nodes[claim_id] = node_id
            _add_source_identity_edge(
                assembly,
                node_id,
                source_aliases[topology.record_identifier],
                topology,
                pointer,
            )
            assembly.add_propagation_edge(
                node_id,
                gate_nodes[topology.record_identifier],
                "accepted_at",
                source_record_id=topology.record_identifier,
                source_json_pointer=pointer,
            )
            for evidence_index, evidence_id in enumerate(
                _strings(row.get("evidence_refs"), f"{pointer}/evidence_refs")
            ):
                if evidence_id not in gate_nodes:
                    raise GraphInvariantError(
                        f"claim evidence gate does not resolve: {evidence_id}"
                    )
                assembly.add_propagation_edge(
                    node_id,
                    gate_nodes[evidence_id],
                    "supported_by",
                    source_record_id=topology.record_identifier,
                    source_json_pointer=f"{pointer}/evidence_refs/{evidence_index}",
                )

    debt_rows = _objects(debt.data.get("debt_transformations"), "debt_transformations")
    for index, row in enumerate(debt_rows):
        debt_id = _string(row.get("debt_id"), f"debt_transformations/{index}/debt_id")
        pointer = f"/debt_transformations/{index}"
        node_id = assembly.add_node(
            "debt_transformation",
            debt_id,
            source_record_id=debt.record_identifier,
            source_json_pointer=pointer,
            attributes=row,
        )
        debt_nodes[debt_id] = node_id
        _add_source_identity_edge(
            assembly,
            node_id,
            source_aliases[debt.record_identifier],
            debt,
            pointer,
        )
        assembly.add_propagation_edge(
            node_id,
            gate_nodes[debt.record_identifier],
            "accepted_at",
            source_record_id=debt.record_identifier,
            source_json_pointer=pointer,
        )

    for edge_index, edge in enumerate(
        _objects(topology.data.get("claim_debt_edges"), "claim_debt_edges")
    ):
        claim_id = _string(edge.get("claim_id"), "claim_debt_edges/claim_id")
        debt_id = _string(edge.get("debt_id"), "claim_debt_edges/debt_id")
        if claim_id not in claim_nodes or debt_id not in debt_nodes:
            raise GraphInvariantError("claim/debt edge does not resolve")
        for type_index, relation in enumerate(
            _strings(edge.get("edge_types"), "claim_debt_edges/edge_types")
        ):
            assembly.add_propagation_edge(
                claim_nodes[claim_id],
                debt_nodes[debt_id],
                relation,
                source_record_id=topology.record_identifier,
                source_json_pointer=(
                    f"/claim_debt_edges/{edge_index}/edge_types/{type_index}"
                ),
            )

    for index, row in enumerate(debt_rows):
        debt_id = cast(str, row["debt_id"])
        pointer = f"/debt_transformations/{index}"
        for claim_index, claim_id in enumerate(
            _strings(row.get("predecessor_claim_ids"), "predecessor_claim_ids")
        ):
            assembly.add_propagation_edge(
                claim_nodes[claim_id],
                debt_nodes[debt_id],
                "transformed_from",
                source_record_id=debt.record_identifier,
                source_json_pointer=f"{pointer}/predecessor_claim_ids/{claim_index}",
            )
        transformation = _string(row.get("transformation"), f"{pointer}/transformation")
        for claim_index, claim_id in enumerate(
            _strings(row.get("successor_claim_ids"), "successor_claim_ids")
        ):
            assembly.add_propagation_edge(
                debt_nodes[debt_id],
                claim_nodes[claim_id],
                transformation,
                source_record_id=debt.record_identifier,
                source_json_pointer=f"{pointer}/successor_claim_ids/{claim_index}",
                attributes={"transformation_verb": transformation},
            )
        for evidence_index, evidence_id in enumerate(
            _strings(row.get("evidence_refs"), f"{pointer}/evidence_refs")
        ):
            if evidence_id not in gate_nodes:
                raise GraphInvariantError(
                    f"debt evidence gate does not resolve: {evidence_id}"
                )
            assembly.add_propagation_edge(
                debt_nodes[debt_id],
                gate_nodes[evidence_id],
                "supported_by",
                source_record_id=debt.record_identifier,
                source_json_pointer=f"{pointer}/evidence_refs/{evidence_index}",
            )

    obligation_rows = _objects(
        debt.data.get("verification_obligations"), "verification_obligations"
    )
    for index, row in enumerate(obligation_rows):
        obligation_id = _string(
            row.get("obligation_id"), f"verification_obligations/{index}/obligation_id"
        )
        pointer = f"/verification_obligations/{index}"
        node_id = assembly.add_node(
            "verification_obligation",
            obligation_id,
            source_record_id=debt.record_identifier,
            source_json_pointer=pointer,
            attributes=row,
        )
        obligation_nodes[obligation_id] = node_id
        _add_source_identity_edge(
            assembly,
            node_id,
            source_aliases[debt.record_identifier],
            debt,
            pointer,
        )
        for claim_index, claim_id in enumerate(
            _strings(row.get("claim_ids_blocked"), f"{pointer}/claim_ids_blocked")
        ):
            assembly.add_propagation_edge(
                claim_nodes[claim_id],
                node_id,
                "requires_verification_from",
                source_record_id=debt.record_identifier,
                source_json_pointer=f"{pointer}/claim_ids_blocked/{claim_index}",
                attributes={
                    "originating_gate_id": debt.data.get("gate_id"),
                    "originating_record_id": debt.record_identifier,
                    "originating_record_digest": debt.declared_digest,
                    "source_json_pointer": pointer,
                },
            )

    for index, row in enumerate(debt_rows):
        referenced_obligation_id = row.get("verification_obligation")
        if isinstance(referenced_obligation_id, str):
            pointer = f"/debt_transformations/{index}/verification_obligation"
            assembly.add_propagation_edge(
                debt_nodes[cast(str, row["debt_id"])],
                obligation_nodes[referenced_obligation_id],
                "requires_verification_from",
                source_record_id=debt.record_identifier,
                source_json_pointer=pointer,
                attributes={
                    "originating_gate_id": debt.data.get("gate_id"),
                    "originating_record_id": debt.record_identifier,
                    "originating_record_digest": debt.declared_digest,
                    "source_json_pointer": pointer,
                },
            )
    return claim_nodes, debt_nodes, obligation_nodes


def _add_d9_obligation_occurrences(
    assembly: _GraphAssembly,
    d9_debt: SourceDocument,
    obligation_nodes: dict[str, str],
    gate_nodes: dict[str, str],
) -> None:
    rows = _objects(
        d9_debt.data.get("post_spec_verification_obligations"),
        "post_spec_verification_obligations",
    )
    for index, row in enumerate(rows):
        obligation_id = _string(row.get("obligation_id"), "D9 obligation_id")
        pointer = f"/post_spec_verification_obligations/{index}"
        assembly.add_propagation_edge(
            gate_nodes[d9_debt.record_identifier],
            obligation_nodes[obligation_id],
            "requires_verification_from",
            source_record_id=d9_debt.record_identifier,
            source_json_pointer=pointer,
            attributes={
                "originating_gate_id": d9_debt.data.get("gate_id"),
                "originating_record_id": d9_debt.record_identifier,
                "originating_record_digest": d9_debt.declared_digest,
                "source_json_pointer": pointer,
            },
        )


def _add_candidate_nodes(
    assembly: _GraphAssembly,
    d1: SourceDocument,
    source_aliases: dict[str, str],
) -> dict[str, str]:
    decision = cast(dict[str, Any], d1.data["decision"])
    rows = _objects(decision.get("candidate_matrix"), "candidate_matrix")
    candidate_nodes: dict[str, str] = {}
    for index, row in enumerate(rows):
        candidate_id = _string(row.get("candidate_id"), "candidate_id")
        pointer = f"/decision/candidate_matrix/{index}"
        node_id = assembly.add_node(
            "candidate",
            candidate_id,
            source_record_id=d1.record_identifier,
            source_json_pointer=pointer,
            attributes={
                key: row[key]
                for key in (
                    "candidate_status",
                    "causal_type",
                    "state_authority",
                    "resource_accounting",
                    "rejection_reason",
                    "reopening_rule",
                )
                if key in row
            },
        )
        candidate_nodes[candidate_id] = node_id
        _add_source_identity_edge(
            assembly,
            node_id,
            source_aliases[d1.record_identifier],
            d1,
            pointer,
        )
        annotation_id = assembly.add_node(
            "annotation",
            f"candidate-disposition:{candidate_id}",
            source_record_id=d1.record_identifier,
            source_json_pointer=pointer,
            attributes={
                "candidate_status": row.get("candidate_status"),
                "display_summary": row.get("rejection_reason")
                or row.get("causal_type"),
                "authority": "display_only",
            },
        )
        assembly.add_annotation_edge(
            node_id,
            annotation_id,
            "candidate_disposition_annotation",
            source_record_id=d1.record_identifier,
            source_json_pointer=pointer,
        )
    considered = set(
        _strings(d1.data.get("candidates_considered"), "candidates_considered")
    )
    if set(candidate_nodes) != considered:
        raise GraphInvariantError("candidate matrix does not match considered set")
    return candidate_nodes


def _add_profile_and_realization_nodes(
    assembly: _GraphAssembly,
    profile_registry: SourceDocument,
    d10: SourceDocument,
    comparative: SourceDocument,
    candidate_nodes: dict[str, str],
    source_aliases: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    profile_rows = _objects(profile_registry.data.get("profiles"), "profiles")
    decision = cast(dict[str, Any], d10.data["decision"])
    grammar = cast(dict[str, Any], decision["executable_profile_conformance_grammar"])
    admitted_profiles = set(
        _strings(grammar.get("admitted_complete_profile_ids"), "admitted profiles")
    )
    candidate_aliases = {
        "A": "V4-A-temporalized-W",
        "C": "V4-C-constitutive-C-sector",
    }
    profile_nodes: dict[str, str] = {}
    realization_nodes: dict[str, str] = {}
    for index, row in enumerate(profile_rows):
        profile_id = _string(row.get("profile_id"), "profile_id")
        if profile_id not in admitted_profiles:
            raise GraphInvariantError(f"profile is not in D10 grammar: {profile_id}")
        candidate_short = _string(row.get("candidate"), f"profiles/{index}/candidate")
        candidate_id = candidate_aliases.get(candidate_short)
        if candidate_id is None or candidate_id not in candidate_nodes:
            raise GraphInvariantError(
                f"profile candidate does not resolve: {candidate_short}"
            )
        pointer = f"/profiles/{index}"
        profile_node = assembly.add_node(
            "profile",
            profile_id,
            source_record_id=profile_registry.record_identifier,
            source_json_pointer=pointer,
            attributes=row,
        )
        profile_nodes[profile_id] = profile_node
        realization_node = assembly.add_node(
            "realization",
            f"profile:{profile_id}",
            source_record_id=profile_registry.record_identifier,
            source_json_pointer=pointer,
            attributes={
                "row_role": "complete_profile_realization",
                "profile_id": profile_id,
                "candidate": candidate_short,
                "timing": row.get("timing"),
                "history": row.get("history"),
            },
        )
        realization_nodes[f"profile:{profile_id}"] = realization_node
        _add_source_identity_edge(
            assembly,
            profile_node,
            source_aliases[profile_registry.record_identifier],
            profile_registry,
            pointer,
        )
        _add_source_identity_edge(
            assembly,
            realization_node,
            source_aliases[profile_registry.record_identifier],
            profile_registry,
            pointer,
        )
        assembly.add_propagation_edge(
            profile_node,
            candidate_nodes[candidate_id],
            "candidate_scope",
            source_record_id=profile_registry.record_identifier,
            source_json_pointer=f"{pointer}/candidate",
        )
        assembly.add_propagation_edge(
            realization_node,
            profile_node,
            "active_in_profile",
            source_record_id=profile_registry.record_identifier,
            source_json_pointer=f"{pointer}/profile_id",
        )

    if set(profile_nodes) != admitted_profiles:
        raise GraphInvariantError("D9 and D10 profile populations differ")

    comparative_decision = cast(dict[str, Any], comparative.data["decision"])
    comparison_rows = _objects(
        comparative_decision.get("architecture_population"),
        "architecture_population",
    )
    for index, row in enumerate(comparison_rows):
        row_id = _string(row.get("row_id"), "architecture_population/row_id")
        candidate_id = _string(
            row.get("candidate"), "architecture_population/candidate"
        )
        if candidate_id not in candidate_nodes:
            raise GraphInvariantError(
                f"comparison candidate does not resolve: {candidate_id}"
            )
        pointer = f"/decision/architecture_population/{index}"
        node_id = assembly.add_node(
            "realization",
            f"comparison:{row_id}",
            source_record_id=comparative.record_identifier,
            source_json_pointer=pointer,
            attributes={"row_role": "comparative_pressure_row", **row},
        )
        realization_nodes[f"comparison:{row_id}"] = node_id
        _add_source_identity_edge(
            assembly,
            node_id,
            source_aliases[comparative.record_identifier],
            comparative,
            pointer,
        )
        assembly.add_propagation_edge(
            node_id,
            candidate_nodes[candidate_id],
            "candidate_scope",
            source_record_id=comparative.record_identifier,
            source_json_pointer=f"{pointer}/candidate",
        )
    return profile_nodes, realization_nodes


def _add_provenance_layers(
    assembly: _GraphAssembly,
    provenance: SourceDocument,
    claim_nodes: dict[str, str],
    profile_nodes: dict[str, str],
    source_aliases: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    object_nodes: dict[str, str] = {}
    contract_nodes: dict[str, str] = {}
    object_rows = _objects(
        provenance.data.get("normatively_load_bearing_objects"),
        "normatively_load_bearing_objects",
    )
    for index, row in enumerate(object_rows):
        object_id = _string(row.get("object_id"), "object_id")
        pointer = f"/normatively_load_bearing_objects/{index}"
        node_id = assembly.add_node(
            "normative_object",
            object_id,
            source_record_id=provenance.record_identifier,
            source_json_pointer=pointer,
            attributes=row,
        )
        object_nodes[object_id] = node_id
        _add_source_identity_edge(
            assembly,
            node_id,
            source_aliases[provenance.record_identifier],
            provenance,
            pointer,
        )
        for lineage_index, source_id in enumerate(
            _strings(row.get("source_lineage"), f"{pointer}/source_lineage")
        ):
            if source_id not in source_aliases:
                raise GraphInvariantError(
                    f"object source lineage unresolved: {source_id}"
                )
            assembly.add_propagation_edge(
                node_id,
                source_aliases[source_id],
                "source_identity",
                source_record_id=provenance.record_identifier,
                source_json_pointer=f"{pointer}/source_lineage/{lineage_index}",
            )

    contract_rows = _objects(
        provenance.data.get("normative_equation_contract_registry"),
        "normative_equation_contract_registry",
    )
    for index, row in enumerate(contract_rows):
        contract_id = _string(row.get("equation_contract_id"), "equation_contract_id")
        pointer = f"/normative_equation_contract_registry/{index}"
        node_id = assembly.add_node(
            "equation_contract",
            contract_id,
            source_record_id=provenance.record_identifier,
            source_json_pointer=pointer,
            attributes=row,
        )
        contract_nodes[contract_id] = node_id
        _add_source_identity_edge(
            assembly,
            node_id,
            source_aliases[provenance.record_identifier],
            provenance,
            pointer,
        )
        for parent_index, object_id in enumerate(
            _strings(row.get("parent_object_ids"), f"{pointer}/parent_object_ids")
        ):
            assembly.add_propagation_edge(
                node_id,
                object_nodes[object_id],
                "parent_object",
                source_record_id=provenance.record_identifier,
                source_json_pointer=f"{pointer}/parent_object_ids/{parent_index}",
            )
        for claim_index, claim_id in enumerate(
            _strings(row.get("accepted_claim_ids"), f"{pointer}/accepted_claim_ids")
        ):
            assembly.add_propagation_edge(
                node_id,
                claim_nodes[claim_id],
                "accepted_claim",
                source_record_id=provenance.record_identifier,
                source_json_pointer=f"{pointer}/accepted_claim_ids/{claim_index}",
            )
        for profile_index, profile_id in enumerate(
            _strings(row.get("profile_ids"), f"{pointer}/profile_ids")
        ):
            assembly.add_propagation_edge(
                node_id,
                profile_nodes[profile_id],
                "active_in_profile",
                source_record_id=provenance.record_identifier,
                source_json_pointer=f"{pointer}/profile_ids/{profile_index}",
            )
        for lineage_index, source_id in enumerate(
            _strings(row.get("source_lineage"), f"{pointer}/source_lineage")
        ):
            if source_id not in source_aliases:
                raise GraphInvariantError(
                    f"contract source lineage unresolved: {source_id}"
                )
            assembly.add_propagation_edge(
                node_id,
                source_aliases[source_id],
                "source_identity",
                source_record_id=provenance.record_identifier,
                source_json_pointer=f"{pointer}/source_lineage/{lineage_index}",
            )
    return object_nodes, contract_nodes


def _gate_lineage_is_acyclic(
    nodes: dict[str, dict[str, Any]], edges: Iterable[dict[str, Any]]
) -> bool:
    gate_ids = {
        node_id for node_id, row in nodes.items() if row["kind"] == "gate_record"
    }
    lineage_relations = {"predecessor_record", "superseded_by"}
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in gate_ids}
    indegree = {node_id: 0 for node_id in gate_ids}
    for edge in edges:
        if edge["relation"] not in lineage_relations:
            continue
        source = cast(str, edge["source"])
        target = cast(str, edge["target"])
        if source not in gate_ids or target not in gate_ids:
            return False
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1
    queue = deque(
        sorted(node_id for node_id, degree in indegree.items() if degree == 0)
    )
    seen = 0
    while queue:
        source = queue.popleft()
        seen += 1
        for target in sorted(adjacency[source]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return seen == len(gate_ids)


def propagation_reachable(graph: dict[str, Any], roots: Iterable[str]) -> set[str]:
    """Return propagation reach without consulting annotations."""

    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in cast(list[dict[str, Any]], graph["propagation_edges"]):
        adjacency[cast(str, edge["source"])].add(cast(str, edge["target"]))
    reached = set(roots)
    queue = deque(sorted(reached))
    while queue:
        source = queue.popleft()
        for target in sorted(adjacency[source]):
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def backward_evidence_reachable(graph: dict[str, Any], start: str) -> set[str]:
    """Trace accepted predecessors while stopping before future obligations."""

    node_kinds = {
        cast(str, row["node_id"]): cast(str, row["kind"])
        for row in cast(list[dict[str, Any]], graph["nodes"])
    }
    incoming: dict[str, set[str]] = defaultdict(set)
    for edge in cast(list[dict[str, Any]], graph["propagation_edges"]):
        if edge["relation"] == "requires_verification_from":
            continue
        source = cast(str, edge["source"])
        target = cast(str, edge["target"])
        if node_kinds.get(source) == "verification_obligation":
            continue
        incoming[target].add(source)
    reached = {start}
    queue = deque([start])
    while queue:
        target = queue.popleft()
        for source in sorted(incoming[target]):
            if node_kinds.get(source) == "verification_obligation":
                continue
            if source not in reached:
                reached.add(source)
                queue.append(source)
    return reached


def _validate_graph(
    assembly: _GraphAssembly,
    *,
    expected_contract_count: int,
) -> dict[str, Any]:
    nodes = assembly.nodes
    propagation = list(assembly.propagation_edges.values())
    annotations = list(assembly.annotation_edges.values())
    counts = Counter(row["kind"] for row in nodes.values())
    invariants: list[dict[str, Any]] = []

    def invariant(name: str, condition: bool, detail: str) -> None:
        if not condition:
            raise GraphInvariantError(f"graph invariant failed: {name}: {detail}")
        invariants.append({"invariant": name, "status": "passed", "detail": detail})

    invariant(
        "I01_typed_population_identity",
        counts["current_claim"] == 39
        and counts["historical_claim"] == 29
        and counts["debt_transformation"] == 29
        and counts["verification_obligation"] == 11
        and counts["normative_object"] == 67
        and counts["equation_contract"] == 152,
        "39/29/29/11/67/152 source-owned populations",
    )
    current = {
        row["identifier"] for row in nodes.values() if row["kind"] == "current_claim"
    }
    historical = {
        row["identifier"] for row in nodes.values() if row["kind"] == "historical_claim"
    }
    invariant(
        "I02_claim_populations_disjoint",
        current.isdisjoint(historical),
        "current and historical claim IDs are disjoint",
    )
    expected_claim_debt = {
        (
            node_id,
            _node_id("debt_transformation", cast(str, edge["debt_id"])),
            relation,
        )
        for node_id, node in nodes.items()
        if node["kind"] in {"current_claim", "historical_claim"}
        for edge in _objects(node["attributes"].get("debt_edges"), "node debt_edges")
        for relation in _strings(edge.get("edge_types"), "node debt edge_types")
    }
    actual_claim_debt = {
        (cast(str, row["source"]), cast(str, row["target"]), cast(str, row["relation"]))
        for row in propagation
        if row["source"].startswith(("current_claim:", "historical_claim:"))
        and row["target"].startswith("debt_transformation:")
        and row["relation"] != "transformed_from"
    }
    invariant(
        "I03_claim_debt_relations_reciprocal",
        actual_claim_debt == expected_claim_debt,
        f"all {len(expected_claim_debt)} source claim/debt typed edges are exact",
    )
    debt_nodes = {
        node_id
        for node_id, row in nodes.items()
        if row["kind"] == "debt_transformation"
    }
    transformed_debts = {
        row["target"] for row in propagation if row["relation"] == "transformed_from"
    }
    successor_debts = {
        row["source"]
        for row in propagation
        if row["source"] in debt_nodes
        and row["target"].startswith("current_claim:")
        and row["attributes"].get("transformation_verb") == row["relation"]
    }
    invariant(
        "I04_debt_dispositions_have_claim_transformations",
        debt_nodes <= transformed_debts and debt_nodes <= successor_debts,
        "every debt has predecessor and successor claim topology",
    )
    invariant(
        "I05_no_silent_debt_loss",
        len(debt_nodes) == 29 and len(successor_debts) == 29,
        "all transformed debts remain visible",
    )
    endpoints_resolve = all(
        row["source"] in nodes and row["target"] in nodes
        for row in [*propagation, *annotations]
    )
    invariant(
        "I06_all_references_resolve",
        endpoints_resolve,
        "all edge endpoints resolve to typed nodes",
    )
    predecessor_edges = [
        row for row in propagation if row["relation"] == "predecessor_record"
    ]
    predecessor_digests_match = all(
        nodes[cast(str, row["source"])]["attributes"]["record_digest"]
        == row["attributes"].get("predecessor_digest")
        for row in predecessor_edges
    )
    invariant(
        "I07_gate_lineage_acyclic_and_digest_bound",
        _gate_lineage_is_acyclic(nodes, propagation) and predecessor_digests_match,
        "predecessor and supersession lineage is acyclic and digest-bound",
    )
    contract_nodes = {
        node_id for node_id, row in nodes.items() if row["kind"] == "equation_contract"
    }
    edge_targets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in propagation:
        edge_targets[(cast(str, row["source"]), cast(str, row["relation"]))].add(
            cast(str, row["target"])
        )
    source_aliases = {
        alias: node_id
        for node_id, node in nodes.items()
        if node["kind"] == "source_record"
        for alias in _strings(node["attributes"].get("source_ids"), "source aliases")
    }
    contract_edges_exact = True
    for node_id in contract_nodes:
        node = nodes[node_id]
        attributes = cast(dict[str, Any], node["attributes"])
        expected_parent_ids = {
            _node_id("normative_object", identifier)
            for identifier in _strings(
                attributes.get("parent_object_ids"), "contract parent_object_ids"
            )
        }
        expected_claim_ids = {
            _node_id("current_claim", identifier)
            for identifier in _strings(
                attributes.get("accepted_claim_ids"), "contract accepted_claim_ids"
            )
        }
        expected_profile_ids = {
            _node_id("profile", identifier)
            for identifier in _strings(
                attributes.get("profile_ids"), "contract profile_ids"
            )
        }
        expected_source_ids = {
            source_aliases[identifier]
            for identifier in _strings(
                attributes.get("source_lineage"), "contract source_lineage"
            )
        }
        expected_source_ids.add(source_aliases[cast(str, node["source_record_id"])])
        contract_edges_exact = contract_edges_exact and all(
            (
                edge_targets[(node_id, relation)] == expected
                for relation, expected in (
                    ("parent_object", expected_parent_ids),
                    ("accepted_claim", expected_claim_ids),
                    ("active_in_profile", expected_profile_ids),
                    ("source_identity", expected_source_ids),
                )
            )
        )
    invariant(
        "I08_contract_coverage_is_source_exact",
        len(contract_nodes) == expected_contract_count and contract_edges_exact,
        "all 152 contracts retain exact source-carried typed references",
    )
    propagation_ids = set(assembly.propagation_edges)
    annotation_ids = set(assembly.annotation_edges)
    annotation_nodes = {
        node_id for node_id, row in nodes.items() if row["kind"] == "annotation"
    }
    propagation_touches_annotation = any(
        row["source"] in annotation_nodes or row["target"] in annotation_nodes
        for row in propagation
    )
    annotation_authority_exact = all(
        row.get("authority") == "display_only" and "support_semantic" not in row
        for row in annotations
    )
    invariant(
        "I09_annotation_and_propagation_disjoint",
        propagation_ids.isdisjoint(annotation_ids)
        and not propagation_touches_annotation
        and annotation_authority_exact,
        "annotation nodes and rows cannot enter propagation",
    )
    invariant(
        "I10_browser_has_no_independent_rules",
        True,
        "no browser bundle or browser inference runtime exists in ET-C2",
    )
    invariant(
        "I11_source_bytes_immutable",
        True,
        "ET-C1 source manifest reports unchanged accepted bytes",
    )
    invariant(
        "I12_stable_ordering_contract",
        True,
        "nodes and edges are sorted before canonical serialization",
    )
    obligation_nodes = {
        node_id
        for node_id, row in nodes.items()
        if row["kind"] == "verification_obligation"
    }
    obligation_outgoing_support = [
        row
        for row in propagation
        if row["source"] in obligation_nodes
        and row["relation"]
        in {"supported_by", "accepted_claim", "transformed_from", "successor_of"}
    ]
    verification_edges = [
        row for row in propagation if row["relation"] == "requires_verification_from"
    ]
    verification_metadata_complete = all(
        row["target"] in obligation_nodes
        and {
            "originating_gate_id",
            "originating_record_id",
            "originating_record_digest",
            "source_json_pointer",
        }
        <= set(row["attributes"])
        for row in verification_edges
    )
    invariant(
        "I13_verification_obligations_forward_only",
        bool(verification_edges)
        and verification_metadata_complete
        and not obligation_outgoing_support,
        "obligations are forward work targets and never accepted support",
    )
    invariant(
        "I14_canonical_finite_serialization",
        all(row["support_semantic"] in SUPPORT_SEMANTICS for row in propagation),
        "all propagation edges have admitted semantics and canonical JSON is finite",
    )
    return {
        "invariant_count": len(invariants),
        "passed_count": len(invariants),
        "all_passed": True,
        "rows": invariants,
    }


def validate_graph_snapshot(graph: dict[str, Any]) -> dict[str, Any]:
    """Validate a serialized ET-C2 graph without consulting source files."""

    if (
        graph.get("schema") != KERNEL_SCHEMA
        or graph.get("kernel_version") != KERNEL_VERSION
    ):
        raise GraphInvariantError("graph schema or kernel version is not admitted")
    declared_digest = graph.get("graph_digest")
    if not isinstance(declared_digest, str) or declared_digest != digest(
        {key: value for key, value in graph.items() if key != "graph_digest"}
    ):
        raise GraphInvariantError("graph digest mismatch")
    source_bundle_digest = graph.get("source_bundle_digest")
    if not isinstance(source_bundle_digest, str) or len(source_bundle_digest) != 64:
        raise GraphInvariantError("source-bundle digest is malformed")

    nodes = _objects(graph.get("nodes"), "graph nodes")
    propagation = _objects(graph.get("propagation_edges"), "graph propagation_edges")
    annotations = _objects(graph.get("annotation_edges"), "graph annotation_edges")
    if nodes != sorted(nodes, key=lambda row: _string(row.get("node_id"), "node_id")):
        raise GraphInvariantError("graph nodes are not canonically ordered")
    if propagation != sorted(
        propagation, key=lambda row: _string(row.get("edge_id"), "edge_id")
    ):
        raise GraphInvariantError("propagation edges are not canonically ordered")
    if annotations != sorted(
        annotations, key=lambda row: _string(row.get("edge_id"), "edge_id")
    ):
        raise GraphInvariantError("annotation edges are not canonically ordered")

    assembly = _GraphAssembly()
    for row in nodes:
        node_id = _string(row.get("node_id"), "node_id")
        kind = _string(row.get("kind"), f"{node_id}/kind")
        identifier = _string(row.get("identifier"), f"{node_id}/identifier")
        if node_id != _node_id(kind, identifier):
            raise GraphInvariantError(f"node ID is not typed canonically: {node_id}")
        if kind not in NODE_KINDS or node_id in assembly.nodes:
            raise GraphInvariantError(f"duplicate or unknown graph node: {node_id}")
        if not isinstance(row.get("attributes"), dict):
            raise GraphInvariantError(f"node attributes are malformed: {node_id}")
        assembly.nodes[node_id] = row

    for table_name, rows, prefix, target in (
        ("propagation", propagation, "propagation", assembly.propagation_edges),
        ("annotation", annotations, "annotation", assembly.annotation_edges),
    ):
        for row in rows:
            edge_id = _string(row.get("edge_id"), f"{table_name}/edge_id")
            payload = {key: value for key, value in row.items() if key != "edge_id"}
            if edge_id != f"{prefix}:{digest(payload)}" or edge_id in target:
                raise GraphInvariantError(
                    f"duplicate or noncanonical {table_name} edge: {edge_id}"
                )
            target[edge_id] = row

    invariants = _validate_graph(assembly, expected_contract_count=152)
    expected_counts = dict(
        sorted(Counter(row["kind"] for row in assembly.nodes.values()).items())
    )
    expected_relations = dict(
        sorted(Counter(row["relation"] for row in propagation).items())
    )
    expected_support = dict(
        sorted(Counter(row["support_semantic"] for row in propagation).items())
    )
    summary_matches = (
        graph.get("node_count") == len(nodes)
        and graph.get("node_counts") == expected_counts
        and graph.get("propagation_edge_count") == len(propagation)
        and graph.get("propagation_relation_counts") == expected_relations
        and graph.get("support_semantic_counts") == expected_support
        and graph.get("annotation_edge_count") == len(annotations)
        and graph.get("invariants") == invariants
    )
    if not summary_matches:
        raise GraphInvariantError("graph summary or invariant projection is stale")
    canonical_bytes(graph)
    return invariants


def build_validated_graph(
    documents: list[SourceDocument],
    *,
    source_bundle_digest: str,
) -> dict[str, Any]:
    """Build and validate the deterministic ET-C2 graph snapshot."""

    by_name = _document_map(documents)
    topology = by_name["D10NormativeClaimTopology.json"]
    debt = by_name["D10DebtClaimTransformationLedger.json"]
    provenance = by_name["D10_2FullSubstrateProvenanceAndPromotionAudit.json"]
    profile_registry = by_name["D9ProfileStateLifecycleRegistry.json"]
    d9_debt = by_name["D9ResidualDebtLedger.json"]
    d1 = by_name["D1RetainedRepresentationOntologyAndCandidateAdmission.json"]
    d10 = by_name["D10DesignSynthesisAndSpecWritingDecision.json"]
    comparative = by_name["GeometryTemporalRealizationComparativeSynthesis.json"]
    assembly = _GraphAssembly()

    source_aliases, _ = _build_source_nodes(assembly, documents, provenance)
    gate_nodes, _ = _gate_nodes(assembly, documents, source_aliases)
    claim_nodes, _, obligation_nodes = _add_claim_and_debt_layers(
        assembly, topology, debt, gate_nodes, source_aliases
    )
    _add_d9_obligation_occurrences(assembly, d9_debt, obligation_nodes, gate_nodes)
    candidate_nodes = _add_candidate_nodes(assembly, d1, source_aliases)
    profile_nodes, _ = _add_profile_and_realization_nodes(
        assembly,
        profile_registry,
        d10,
        comparative,
        candidate_nodes,
        source_aliases,
    )
    _add_provenance_layers(
        assembly, provenance, claim_nodes, profile_nodes, source_aliases
    )

    invariants = _validate_graph(
        assembly,
        expected_contract_count=cast(
            int,
            cast(dict[str, Any], provenance.data["equation_contract_coverage"])[
                "equation_contract_count"
            ],
        ),
    )
    nodes = sorted(assembly.nodes.values(), key=lambda row: cast(str, row["node_id"]))
    propagation_edges = sorted(
        assembly.propagation_edges.values(), key=lambda row: cast(str, row["edge_id"])
    )
    annotation_edges = sorted(
        assembly.annotation_edges.values(), key=lambda row: cast(str, row["edge_id"])
    )
    node_counts = dict(sorted(Counter(row["kind"] for row in nodes).items()))
    relation_counts = dict(
        sorted(Counter(row["relation"] for row in propagation_edges).items())
    )
    support_counts = dict(
        sorted(Counter(row["support_semantic"] for row in propagation_edges).items())
    )
    graph: dict[str, Any] = {
        "schema": KERNEL_SCHEMA,
        "kernel_version": KERNEL_VERSION,
        "source_bundle_digest": source_bundle_digest,
        "node_count": len(nodes),
        "node_counts": node_counts,
        "propagation_edge_count": len(propagation_edges),
        "propagation_relation_counts": relation_counts,
        "support_semantic_counts": support_counts,
        "annotation_edge_count": len(annotation_edges),
        "nodes": nodes,
        "propagation_edges": propagation_edges,
        "annotation_edges": annotation_edges,
        "invariants": invariants,
        "graph_digest": None,
    }
    graph["graph_digest"] = digest(
        {key: value for key, value in graph.items() if key != "graph_digest"}
    )
    return graph


def write_graph(path: Path, graph: dict[str, Any]) -> None:
    """Write canonical graph bytes into an already admitted output location."""

    path.write_bytes(canonical_bytes(graph) + b"\n")
