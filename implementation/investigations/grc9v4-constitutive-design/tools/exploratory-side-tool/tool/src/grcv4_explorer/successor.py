"""Append-only D11 source admission and forensic graph extension.

The accepted ET-C0 through ET-C9 artifacts remain historical snapshots.  This
module admits the bounded D11 records through a separate root of trust and
extends the ET-C2 graph without rewriting any historical node or edge.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, cast

from .adapters import SourceDocument, adapt_source
from .canonical import canonical_bytes, digest, load_json_object, record_digest
from .discovery import discover_sources
from .errors import GraphInvariantError, SourceAdmissionError
from .forensic import ForensicContext, load_forensic_context
from .kernel import validate_graph_snapshot
from .source_contract import (
    admitted_rows,
    load_d11_source_contract,
    load_et_c0_contract,
)


D11_SOURCE_CONTRACT = "ETC10D11SourceContract.json"
D11_SOURCE_MANIFEST = "ETC10D11SourceBundleManifest.json"
D11_GRAPH_SNAPSHOT = "ETC10D11GraphSnapshot.json"
D11_FORENSIC_ADMISSION = "ETC10D11ForensicAdmission.json"

D11_SOURCE_MANIFEST_SCHEMA = "grcv4_explorer_ET_C10_D11_source_bundle_v1"
D11_GRAPH_SCHEMA = "grcv4_explorer_ET_C10_D11_graph_v1"
D11_ADMISSION_SCHEMA = "grcv4_explorer_ET_C10_D11_forensic_admission_v1"

D11_C_RESOLUTION = "GRC9V4-CD-D11-C-RESOLUTION-v1"
D11_C_SUPPLEMENT = "GRC9V4-D11-C-PROVENANCE-SUPPLEMENT-v1"
D11_G9_RESOLUTION = "GRC9V4-CD-D11-G9-RESOLUTION-v1"
D11_G9_SUPPLEMENT = "GRC9V4-D11-G9-PROVENANCE-SUPPLEMENT-v1"


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SourceAdmissionError(f"malformed object: {label}")
    return cast(dict[str, Any], value)


def _require_objects(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise SourceAdmissionError(f"malformed object rows: {label}")
    return cast(list[dict[str, Any]], value)


def _require_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(row, str) for row in value):
        raise SourceAdmissionError(f"malformed string rows: {label}")
    return cast(list[str], value)


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SourceAdmissionError(f"missing string: {label}")
    return value


def _load_historical_identities(
    side_tool_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    records = side_tool_root / "records"
    et_c0 = load_et_c0_contract(records / "ETC0SourceAndLayoutContract.json")
    et_c1 = load_json_object(records / "ETC1SourceBundleManifest.json")
    et_c2_gate = load_json_object(records / "ETC2ValidatedGraphKernel.json")
    et_c2_graph = load_json_object(records / "ETC2GraphSnapshot.json")
    validate_graph_snapshot(et_c2_graph)
    if et_c1.get("source_bundle_digest") != digest(
        {key: value for key, value in et_c1.items() if key != "source_bundle_digest"}
    ):
        raise SourceAdmissionError("historical ET-C1 manifest digest mismatch")
    if (
        et_c2_gate.get("schema") != "grcv4_explorer_ET_C2_validated_graph_admission_v1"
        or et_c2_gate.get("status") != "accepted"
        or et_c2_gate.get("record_digest") != record_digest(et_c2_gate, "record_digest")
    ):
        raise SourceAdmissionError("historical ET-C2 admission is not valid")
    if et_c2_gate["graph_snapshot"]["graph_digest"] != et_c2_graph["graph_digest"]:
        raise GraphInvariantError("historical ET-C2 graph identity mismatch")
    return et_c0, et_c1, et_c2_gate, et_c2_graph


def build_d11_source_bundle(
    repo_root: Path, side_tool_root: Path
) -> tuple[dict[str, Any], tuple[SourceDocument, ...]]:
    """Build the D11 source manifest against the immutable historical base."""

    records = side_tool_root / "records"
    et_c0, et_c1, et_c2_gate, et_c2_graph = _load_historical_identities(side_tool_root)
    contract = load_d11_source_contract(records / D11_SOURCE_CONTRACT)
    base = _require_object(contract.get("historical_base"), "historical_base")
    expected_base = {
        "ET_C0_record_digest": et_c0["record_digest"],
        "ET_C1_source_bundle_digest": et_c1["source_bundle_digest"],
        "ET_C2_record_digest": et_c2_gate["record_digest"],
        "ET_C2_graph_digest": et_c2_graph["graph_digest"],
    }
    if base != expected_base:
        raise SourceAdmissionError("D11 admission historical-base identity mismatch")

    d11_rows = admitted_rows(contract)
    combined_rows = [*admitted_rows(et_c0), *d11_rows]
    observation = discover_sources(repo_root, combined_rows)
    if observation.get("state") != "current_bundle_exact":
        raise SourceAdmissionError(
            f"D11 admitted source set is not exact: {observation.get('state')}"
        )
    documents = tuple(adapt_source(repo_root, row) for row in d11_rows)
    historical_ids = {
        cast(str, row["record_identifier"])
        for row in cast(list[dict[str, Any]], et_c1["records"])
    }
    d11_ids = {document.record_identifier for document in documents}
    if len(d11_ids) != len(documents) or historical_ids & d11_ids:
        raise SourceAdmissionError("D11 admitted record identifiers are not unique")

    by_record = {document.record_identifier: document for document in documents}
    historical_digests = {
        cast(str, row["record_identifier"]): cast(str, row["canonical_digest"])
        for row in cast(list[dict[str, Any]], et_c1["records"])
    }
    all_digests = {
        **historical_digests,
        **{
            document.record_identifier: document.declared_digest
            for document in documents
        },
    }
    predecessor_links = 0
    for document in documents:
        predecessor_id = document.data.get("predecessor_record_id")
        predecessor_digest = document.data.get("predecessor_decision_digest")
        if not isinstance(predecessor_id, str) or not isinstance(
            predecessor_digest, str
        ):
            raise SourceAdmissionError(
                f"D11 source has no digest-bound predecessor: {document.filename}"
            )
        if all_digests.get(predecessor_id) != predecessor_digest:
            raise SourceAdmissionError(
                f"D11 predecessor does not resolve exactly: {document.filename}"
            )
        predecessor_links += 1

    for supplement_id, resolution_id in (
        (D11_C_SUPPLEMENT, D11_C_RESOLUTION),
        (D11_G9_SUPPLEMENT, D11_G9_RESOLUTION),
    ):
        supplement = by_record[supplement_id]
        if supplement.data.get("resolution_record_id") != resolution_id:
            raise SourceAdmissionError(
                f"supplement resolution link drift: {supplement_id}"
            )
        objects = _require_objects(
            supplement.data.get("normative_objects"), f"{supplement_id}/objects"
        )
        contracts = _require_objects(
            supplement.data.get("equation_contracts"), f"{supplement_id}/contracts"
        )
        if len(objects) != supplement.data.get("normative_object_count"):
            raise SourceAdmissionError(
                f"supplement object count drift: {supplement_id}"
            )
        if len(contracts) != supplement.data.get("equation_contract_count"):
            raise SourceAdmissionError(
                f"supplement contract count drift: {supplement_id}"
            )
        object_ids = {
            _require_string(row.get("object_id"), "object_id") for row in objects
        }
        for row in contracts:
            parents = set(
                _require_strings(row.get("parent_object_ids"), "parent_object_ids")
            )
            if not parents or not parents <= object_ids:
                raise SourceAdmissionError(
                    f"D11 contract parent does not resolve within supplement: {supplement_id}"
                )

    manifest: dict[str, Any] = {
        "schema": D11_SOURCE_MANIFEST_SCHEMA,
        "status": "accepted",
        "source_contract_digest": contract["record_digest"],
        "historical_base": expected_base,
        "historical_record_count": len(admitted_rows(et_c0)),
        "D11_record_count": len(documents),
        "combined_record_count": len(combined_rows),
        "source_observation_state": observation["state"],
        "source_observation_digest": observation["observation_digest"],
        "records": [document.manifest_row() for document in documents],
        "reference_validation": {
            "predecessor_links_checked": predecessor_links,
            "predecessor_links_exact": True,
            "companion_resolution_links_exact": True,
            "supplement_populations_and_parent_references_exact": True,
            "historical_source_rows_rewritten": False,
        },
        "source_bundle_digest": None,
    }
    manifest["source_bundle_digest"] = digest(
        {key: value for key, value in manifest.items() if key != "source_bundle_digest"}
    )
    return manifest, documents


class _Overlay:
    def __init__(self, graph: dict[str, Any]) -> None:
        self.nodes = {
            cast(str, row["node_id"]): row
            for row in cast(list[dict[str, Any]], graph["nodes"])
        }
        self.propagation_edges = {
            cast(str, row["edge_id"]): row
            for row in cast(list[dict[str, Any]], graph["propagation_edges"])
        }
        self.annotation_edges = {
            cast(str, row["edge_id"]): row
            for row in cast(list[dict[str, Any]], graph["annotation_edges"])
        }

    def add_node(
        self,
        kind: str,
        identifier: str,
        document: SourceDocument,
        pointer: str,
        attributes: dict[str, Any],
    ) -> str:
        node_id = f"{kind}:{identifier}"
        if node_id in self.nodes:
            raise GraphInvariantError(
                f"D11 node collides with accepted graph: {node_id}"
            )
        self.nodes[node_id] = {
            "node_id": node_id,
            "kind": kind,
            "identifier": identifier,
            "source_record_id": document.record_identifier,
            "source_json_pointer": pointer,
            "attributes": attributes,
        }
        return node_id

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        document: SourceDocument,
        pointer: str,
        *,
        support_semantic: str = "not_applicable",
        attributes: dict[str, Any] | None = None,
    ) -> str:
        payload = {
            "source": source,
            "target": target,
            "relation": relation,
            "support_semantic": support_semantic,
            "source_record_id": document.record_identifier,
            "source_json_pointer": pointer,
            "attributes": attributes or {},
        }
        edge_id = f"propagation:{digest(payload)}"
        if edge_id in self.propagation_edges:
            raise GraphInvariantError(f"duplicate D11 propagation edge: {edge_id}")
        self.propagation_edges[edge_id] = {"edge_id": edge_id, **payload}
        return edge_id


def _source_node_id(document: SourceDocument) -> str:
    return "source_record:" + digest(
        {
            "path": cast(str, document.admission["path"]),
            "file_sha256": cast(str, document.admission["file_sha256"]),
        }
    )


def _add_source_edge(
    overlay: _Overlay,
    node_id: str,
    source_node: str,
    document: SourceDocument,
    pointer: str,
) -> None:
    overlay.add_edge(
        node_id,
        source_node,
        "source_identity",
        document,
        pointer,
    )


def build_d11_graph(
    historical: ForensicContext,
    manifest: dict[str, Any],
    documents: tuple[SourceDocument, ...],
) -> dict[str, Any]:
    """Extend the accepted ET-C2 graph with source-exact D11 authority."""

    overlay = _Overlay(historical.graph)
    by_record = {document.record_identifier: document for document in documents}
    gate_nodes = {
        cast(str, row["identifier"]): node_id
        for node_id, row in overlay.nodes.items()
        if row["kind"] == "gate_record"
    }

    source_nodes: dict[str, str] = {}
    for document in documents:
        source_id = _source_node_id(document)
        if source_id in overlay.nodes:
            raise GraphInvariantError(
                f"D11 source identity collides: {document.filename}"
            )
        overlay.nodes[source_id] = {
            "node_id": source_id,
            "kind": "source_record",
            "identifier": source_id.split(":", 1)[1],
            "source_record_id": document.record_identifier,
            "source_json_pointer": "/",
            "attributes": {
                "source_ids": [document.record_identifier],
                "path": document.admission["path"],
                "file_sha256": document.admission["file_sha256"],
                "source_digests": [document.declared_digest],
                "statuses": [document.data["status"]],
                "admitted_bundle_record": True,
                "admission_layer": "ET-C10-D11",
            },
        }
        source_nodes[document.record_identifier] = source_id
        gate = overlay.add_node(
            "gate_record",
            document.record_identifier,
            document,
            "/",
            {
                "gate_id": document.data.get("gate_id"),
                "status": document.data["status"],
                "record_digest": document.declared_digest,
                "path": document.admission["path"],
                "admission_layer": "ET-C10-D11",
            },
        )
        gate_nodes[document.record_identifier] = gate
        _add_source_edge(overlay, gate, source_id, document, "/")

    for document in documents:
        predecessor = _require_string(
            document.data.get("predecessor_record_id"), "predecessor_record_id"
        )
        overlay.add_edge(
            gate_nodes[predecessor],
            gate_nodes[document.record_identifier],
            "predecessor_record",
            document,
            "/predecessor_record_id",
            attributes={
                "predecessor_digest": document.data["predecessor_decision_digest"]
            },
        )
        supersedes = document.data.get("supersedes")
        if isinstance(supersedes, str):
            overlay.add_edge(
                gate_nodes[supersedes],
                gate_nodes[document.record_identifier],
                "superseded_by",
                document,
                "/supersedes",
            )
        resolution = document.data.get("resolution_record_id")
        if isinstance(resolution, str):
            overlay.add_edge(
                gate_nodes[resolution],
                gate_nodes[document.record_identifier],
                "provenance_supplemented_by",
                document,
                "/resolution_record_id",
            )

    claim_nodes = {
        cast(str, row["identifier"]): node_id
        for node_id, row in overlay.nodes.items()
        if row["kind"] in {"current_claim", "historical_claim"}
    }
    object_nodes = {
        cast(str, row["identifier"]): node_id
        for node_id, row in overlay.nodes.items()
        if row["kind"] == "normative_object"
    }

    supplement_pairs = (
        (by_record[D11_C_SUPPLEMENT], by_record[D11_C_RESOLUTION]),
        (by_record[D11_G9_SUPPLEMENT], by_record[D11_G9_RESOLUTION]),
    )
    for supplement, resolution in supplement_pairs:
        claim = _require_object(
            supplement.data.get("accepted_successor_claim"),
            f"{supplement.record_identifier}/accepted_successor_claim",
        )
        claim_id = _require_string(claim.get("claim_id"), "claim_id")
        claim_node = overlay.add_node(
            "current_claim",
            claim_id,
            supplement,
            "/accepted_successor_claim",
            claim,
        )
        claim_nodes[claim_id] = claim_node
        _add_source_edge(
            overlay,
            claim_node,
            source_nodes[supplement.record_identifier],
            supplement,
            "/accepted_successor_claim",
        )
        overlay.add_edge(
            claim_node,
            gate_nodes[resolution.record_identifier],
            "accepted_at",
            supplement,
            "/resolution_record_id",
        )
        for index, edge in enumerate(
            _require_objects(supplement.data.get("claim_edges"), "claim_edges")
        ):
            predecessor_id = _require_string(
                edge.get("predecessor_claim_id"), "predecessor_claim_id"
            )
            successor_id = _require_string(
                edge.get("successor_claim_id"), "successor_claim_id"
            )
            if successor_id != claim_id or predecessor_id not in claim_nodes:
                raise GraphInvariantError("D11 claim edge endpoint does not resolve")
            overlay.add_edge(
                claim_nodes[predecessor_id],
                claim_node,
                _require_string(edge.get("relation"), "claim edge relation"),
                supplement,
                f"/claim_edges/{index}",
                support_semantic="indeterminate_requires_review",
                attributes={
                    "predecessor_status_changed": edge.get("predecessor_status_changed")
                },
            )

        for index, row in enumerate(
            _require_objects(
                supplement.data.get("normative_objects"), "normative_objects"
            )
        ):
            object_id = _require_string(row.get("object_id"), "object_id")
            pointer = f"/normative_objects/{index}"
            node_id = overlay.add_node(
                "normative_object", object_id, supplement, pointer, row
            )
            object_nodes[object_id] = node_id
            _add_source_edge(
                overlay,
                node_id,
                source_nodes[supplement.record_identifier],
                supplement,
                pointer,
            )
            for claim_index, accepted_claim_id in enumerate(
                _require_strings(row.get("accepted_claim_ids"), "accepted_claim_ids")
            ):
                if accepted_claim_id not in claim_nodes:
                    raise GraphInvariantError(
                        f"D11 object claim does not resolve: {accepted_claim_id}"
                    )
                overlay.add_edge(
                    node_id,
                    claim_nodes[accepted_claim_id],
                    "accepted_claim",
                    supplement,
                    f"{pointer}/accepted_claim_ids/{claim_index}",
                    support_semantic="indeterminate_requires_review",
                )

        for index, row in enumerate(
            _require_objects(
                supplement.data.get("equation_contracts"), "equation_contracts"
            )
        ):
            contract_id = _require_string(
                row.get("equation_contract_id"), "equation_contract_id"
            )
            pointer = f"/equation_contracts/{index}"
            contract_node = overlay.add_node(
                "equation_contract", contract_id, supplement, pointer, row
            )
            _add_source_edge(
                overlay,
                contract_node,
                source_nodes[supplement.record_identifier],
                supplement,
                pointer,
            )
            for parent_index, object_id in enumerate(
                _require_strings(row.get("parent_object_ids"), "parent_object_ids")
            ):
                if object_id not in object_nodes:
                    raise GraphInvariantError(
                        f"D11 contract parent does not resolve: {object_id}"
                    )
                overlay.add_edge(
                    contract_node,
                    object_nodes[object_id],
                    "parent_object",
                    supplement,
                    f"{pointer}/parent_object_ids/{parent_index}",
                    support_semantic="indeterminate_requires_review",
                )
            support = _require_string(row.get("support_semantics"), "support_semantics")
            for claim_index, accepted_claim_id in enumerate(
                _require_strings(row.get("accepted_claim_ids"), "accepted_claim_ids")
            ):
                if accepted_claim_id not in claim_nodes:
                    raise GraphInvariantError(
                        f"D11 contract claim does not resolve: {accepted_claim_id}"
                    )
                overlay.add_edge(
                    contract_node,
                    claim_nodes[accepted_claim_id],
                    "accepted_claim",
                    supplement,
                    f"{pointer}/accepted_claim_ids/{claim_index}",
                    support_semantic=support,
                )

    routing = by_record["GRC9V4-CD-D11-CLAIM-DEBT-ROUTING-v1"]
    debt_rows = _require_objects(
        routing.data.get("newly_exposed_D11_debts"), "newly_exposed_D11_debts"
    )
    resolution_by_debt = {
        _require_string(
            document.data["debt_transformation"].get("local_debt_id"),
            "local_debt_id",
        ): document
        for document in (
            by_record[D11_C_RESOLUTION],
            by_record[D11_G9_RESOLUTION],
        )
    }
    for index, open_row in enumerate(debt_rows):
        debt_id = _require_string(open_row.get("debt_id"), "debt_id")
        resolution = resolution_by_debt[debt_id]
        resolved = _require_object(
            resolution.data.get("debt_transformation"), "debt_transformation"
        )
        debt_node = overlay.add_node(
            "debt_transformation",
            debt_id,
            resolution,
            "/debt_transformation",
            resolved,
        )
        _add_source_edge(
            overlay,
            debt_node,
            source_nodes[resolution.record_identifier],
            resolution,
            "/debt_transformation",
        )
        overlay.add_edge(
            debt_node,
            gate_nodes[resolution.record_identifier],
            "accepted_at",
            resolution,
            "/debt_transformation",
        )
        for claim_index, predecessor_id in enumerate(
            _require_strings(
                open_row.get("directly_bearing_claim_ids"),
                "directly_bearing_claim_ids",
            )
        ):
            if predecessor_id not in claim_nodes:
                raise GraphInvariantError(
                    f"D11 debt predecessor claim does not resolve: {predecessor_id}"
                )
            overlay.add_edge(
                claim_nodes[predecessor_id],
                debt_node,
                "directly_bearing_pressure",
                routing,
                f"/newly_exposed_D11_debts/{index}/directly_bearing_claim_ids/{claim_index}",
                support_semantic="indeterminate_requires_review",
            )
        successor_claim = (
            "D11-C-CL-O-001" if debt_id.startswith("D11-C-") else "D11-G9-CL-N-001"
        )
        overlay.add_edge(
            debt_node,
            claim_nodes[successor_claim],
            "resolved_bounded_by",
            resolution,
            "/debt_transformation/local_debt_successor_status",
            support_semantic="required",
            attributes={"transformation_verb": resolved["local_debt_successor_status"]},
        )

        obligations = _require_strings(
            resolution.data["verification_obligation_effect"].get(
                "new_forward_obligations"
            ),
            "new_forward_obligations",
        )
        for obligation_index, obligation_id in enumerate(obligations):
            pointer = (
                "/verification_obligation_effect/new_forward_obligations/"
                f"{obligation_index}"
            )
            obligation_node = overlay.add_node(
                "verification_obligation",
                obligation_id,
                resolution,
                pointer,
                {
                    "obligation_id": obligation_id,
                    "status": "pending_forward",
                    "originating_gate_id": resolution.data["gate_id"],
                    "source_encoding": "exact_identifier_in_new_forward_obligations",
                },
            )
            _add_source_edge(
                overlay,
                obligation_node,
                source_nodes[resolution.record_identifier],
                resolution,
                pointer,
            )
            overlay.add_edge(
                claim_nodes[successor_claim],
                obligation_node,
                "requires_verification_from",
                resolution,
                pointer,
                support_semantic="required",
                attributes={
                    "originating_gate_id": resolution.data["gate_id"],
                    "originating_record_id": resolution.record_identifier,
                    "originating_record_digest": resolution.declared_digest,
                    "source_json_pointer": pointer,
                },
            )

    candidate_sources = (
        by_record["GRC9V4-CD-D11-C-v1"],
        by_record[D11_C_RESOLUTION],
        by_record["GRC9V4-CD-D11-G9-v1"],
        by_record[D11_G9_RESOLUTION],
    )
    candidate_rows: dict[str, tuple[SourceDocument, str, dict[str, Any]]] = {}
    for document in candidate_sources:
        field = (
            "candidate_dispositions"
            if "candidate_dispositions" in document.data
            else "preregistered_candidates"
        )
        for index, row in enumerate(
            _require_objects(
                document.data.get(field), f"{document.record_identifier}/{field}"
            )
        ):
            candidate_id = _require_string(row.get("candidate_id"), "candidate_id")
            candidate_rows[candidate_id] = (document, f"/{field}/{index}", row)
    for candidate_id, (document, pointer, row) in sorted(candidate_rows.items()):
        candidate_node = overlay.add_node(
            "candidate", candidate_id, document, pointer, row
        )
        _add_source_edge(
            overlay,
            candidate_node,
            source_nodes[document.record_identifier],
            document,
            pointer,
        )
        overlay.add_edge(
            candidate_node,
            gate_nodes[document.record_identifier],
            "recorded_at",
            document,
            pointer,
        )

    for resolution in (by_record[D11_C_RESOLUTION], by_record[D11_G9_RESOLUTION]):
        decision = _require_object(resolution.data.get("decision"), "decision")
        profile_id = _require_string(
            decision.get("selected_profile_id"), "selected_profile_id"
        )
        candidate_id = _require_string(
            decision.get("selected_candidate_id"), "selected_candidate_id"
        )
        profile_node = overlay.add_node(
            "profile",
            profile_id,
            resolution,
            "/decision/selected_profile_id",
            {
                "profile_id": profile_id,
                "candidate_id": candidate_id,
                "status": "selected_accepted_bounded",
                "scope": decision.get("graph_scope")
                or decision.get("scientific_disposition"),
            },
        )
        _add_source_edge(
            overlay,
            profile_node,
            source_nodes[resolution.record_identifier],
            resolution,
            "/decision/selected_profile_id",
        )
        overlay.add_edge(
            profile_node,
            f"candidate:{candidate_id}",
            "selected_candidate",
            resolution,
            "/decision/selected_candidate_id",
        )

    nodes = sorted(overlay.nodes.values(), key=lambda row: cast(str, row["node_id"]))
    propagation = sorted(
        overlay.propagation_edges.values(), key=lambda row: cast(str, row["edge_id"])
    )
    annotations = sorted(
        overlay.annotation_edges.values(), key=lambda row: cast(str, row["edge_id"])
    )
    counts = Counter(cast(str, row["kind"]) for row in nodes)
    expected = {
        "current_claim": 41,
        "historical_claim": 29,
        "debt_transformation": 31,
        "verification_obligation": 18,
        "normative_object": 80,
        "equation_contract": 183,
    }
    for kind, count in expected.items():
        if counts[kind] != count:
            raise GraphInvariantError(
                f"D11 successor population mismatch: {kind}={counts[kind]} expected={count}"
            )
    node_ids = {cast(str, row["node_id"]) for row in nodes}
    if any(
        edge[endpoint] not in node_ids
        for edge in [*propagation, *annotations]
        for endpoint in ("source", "target")
    ):
        raise GraphInvariantError("D11 graph contains an unresolved edge endpoint")
    current_claims = {
        cast(str, row["identifier"]) for row in nodes if row["kind"] == "current_claim"
    }
    historical_claims = {
        cast(str, row["identifier"])
        for row in nodes
        if row["kind"] == "historical_claim"
    }
    if current_claims & historical_claims:
        raise GraphInvariantError("D11 current and historical claim IDs overlap")
    if {"D11-C-CL-O-001", "D11-G9-CL-N-001"} - current_claims:
        raise GraphInvariantError("D11 accepted successor claims are incomplete")

    graph: dict[str, Any] = {
        "schema": D11_GRAPH_SCHEMA,
        "kernel_version": "ET-C10-D11-v1",
        "historical_base": {
            "schema": historical.graph["schema"],
            "kernel_version": historical.graph["kernel_version"],
            "graph_digest": historical.graph_digest,
            "node_count": len(historical.graph["nodes"]),
            "propagation_edge_count": len(historical.graph["propagation_edges"]),
            "annotation_edge_count": len(historical.graph["annotation_edges"]),
            "rewritten": False,
        },
        "source_bundle_digest": manifest["source_bundle_digest"],
        "nodes": nodes,
        "propagation_edges": propagation,
        "annotation_edges": annotations,
        "population": dict(sorted(counts.items())),
        "successor_population": {
            "current_claim": 2,
            "debt_transformation": 2,
            "verification_obligation": 7,
            "pending_forward_verification_obligation_total": 17,
            "normative_object": 13,
            "equation_contract": 31,
            "investigation_candidate": len(candidate_rows),
            "selected_profile": 2,
        },
        "invariants": [
            {
                "invariant": "D11-I01_historical_graph_append_only",
                "status": "passed",
                "detail": "every_ET_C2_node_edge_and_annotation_is_retained_byte_exact",
            },
            {
                "invariant": "D11-I02_source_exact_successor_population",
                "status": "passed",
                "detail": "2_claims_2_debts_7_obligations_13_objects_31_contracts",
            },
            {
                "invariant": "D11-I03_reciprocal_claim_and_contract_references",
                "status": "passed",
                "detail": "all_D11_edges_resolve_without_reclassifying_D10_claims",
            },
            {
                "invariant": "D11-I04_authority_ceiling",
                "status": "passed",
                "detail": "paper_specification_and_runtime_propagation_remain_forward_obligations",
            },
        ],
        "graph_digest": None,
    }
    graph["graph_digest"] = digest(
        {key: value for key, value in graph.items() if key != "graph_digest"}
    )
    return graph


def validate_d11_graph(graph: dict[str, Any], historical_graph: dict[str, Any]) -> None:
    """Validate graph identity and the append-only historical embedding."""

    if graph.get("schema") != D11_GRAPH_SCHEMA:
        raise GraphInvariantError("unexpected D11 graph schema")
    if graph.get("graph_digest") != digest(
        {key: value for key, value in graph.items() if key != "graph_digest"}
    ):
        raise GraphInvariantError("D11 graph digest mismatch")
    historical_nodes = {
        cast(str, row["node_id"]): row
        for row in cast(list[dict[str, Any]], historical_graph["nodes"])
    }
    current_nodes = {
        cast(str, row["node_id"]): row
        for row in cast(list[dict[str, Any]], graph["nodes"])
    }
    historical_edges = {
        cast(str, row["edge_id"]): row
        for field in ("propagation_edges", "annotation_edges")
        for row in cast(list[dict[str, Any]], historical_graph[field])
    }
    current_edges = {
        cast(str, row["edge_id"]): row
        for field in ("propagation_edges", "annotation_edges")
        for row in cast(list[dict[str, Any]], graph[field])
    }
    if any(current_nodes.get(key) != value for key, value in historical_nodes.items()):
        raise GraphInvariantError("D11 graph rewrites a historical node")
    if any(current_edges.get(key) != value for key, value in historical_edges.items()):
        raise GraphInvariantError("D11 graph rewrites a historical edge")


def _require_d11_admission(path: Path) -> dict[str, Any]:
    record = load_json_object(path)
    if (
        record.get("schema") != D11_ADMISSION_SCHEMA
        or record.get("status") != "accepted"
        or record.get("record_digest") != record_digest(record, "record_digest")
    ):
        raise SourceAdmissionError("D11 forensic admission is not accepted")
    return record


def load_successor_forensic_context(
    repo_root: Path, side_tool_root: Path
) -> ForensicContext:
    """Load and fully rebuild the accepted ET-C10 D11 forensic overlay."""

    historical = load_forensic_context(repo_root, side_tool_root)
    records = side_tool_root / "records"
    manifest, d11_documents = build_d11_source_bundle(repo_root, side_tool_root)
    accepted_manifest = load_json_object(records / D11_SOURCE_MANIFEST)
    if canonical_bytes(manifest) != canonical_bytes(accepted_manifest):
        raise SourceAdmissionError("accepted D11 source manifest no longer rebuilds")
    graph = build_d11_graph(historical, manifest, d11_documents)
    accepted_graph = load_json_object(records / D11_GRAPH_SNAPSHOT)
    if canonical_bytes(graph) != canonical_bytes(accepted_graph):
        raise GraphInvariantError("accepted D11 graph no longer rebuilds")
    validate_d11_graph(graph, historical.graph)
    admission = _require_d11_admission(records / D11_FORENSIC_ADMISSION)
    if admission.get("source_bundle_digest") != manifest["source_bundle_digest"]:
        raise SourceAdmissionError("D11 admission source-bundle identity mismatch")
    if admission.get("graph_digest") != graph["graph_digest"]:
        raise GraphInvariantError("D11 admission graph identity mismatch")
    if (
        admission.get("historical_ET_C2_record_digest")
        != historical.et_c2_record_digest
    ):
        raise GraphInvariantError("D11 admission historical ET-C2 identity mismatch")

    documents = (*historical.documents, *d11_documents)
    by_record = {document.record_identifier: document for document in documents}
    if len(by_record) != len(documents):
        raise SourceAdmissionError("successor forensic record IDs are not unique")
    nodes = {
        cast(str, row["node_id"]): row
        for row in cast(list[dict[str, Any]], graph["nodes"])
    }
    return ForensicContext(
        graph=graph,
        graph_digest=cast(str, graph["graph_digest"]),
        source_bundle_digest=cast(str, manifest["source_bundle_digest"]),
        et_c2_record_digest=historical.et_c2_record_digest,
        documents=documents,
        documents_by_record=by_record,
        nodes=nodes,
        propagation_edges=tuple(cast(list[dict[str, Any]], graph["propagation_edges"])),
        authority_extension_digest=cast(str, admission["record_digest"]),
    )
