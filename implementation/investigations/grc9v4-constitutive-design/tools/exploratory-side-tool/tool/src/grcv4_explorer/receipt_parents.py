"""Source-exact P9-4.9.2 overlay; D11 remains an immutable historical context."""

from dataclasses import replace
from pathlib import Path

from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .discovery import discover_sources
from .errors import GraphInvariantError, SourceAdmissionError
from .forensic import (
    contract_provenance,
    debt_lifecycle,
    object_dependents,
    reconstruction_path,
)
from .successor import _Overlay, _source_node_id, load_successor_forensic_context

SOURCE = "implementation/investigations/grc9v4-constitutive-design/decisions/P9ReceiptParentAuthority.json"
ADMISSION = "P9492ReceiptParentAdmission.json"
POLICY_ID = "grcv4-previous-successful-primary-v1"
RECORD_ID = "GRCV4-P9-4.9.2-PARENTS-v1"
CLAIM_ID = "P9-4.9.2-CL-N-001"
ACCEPTED_SOURCE_DIGEST = "ba7d69189c527153828b02c2bb3311899b036a634446de9ad8f36af6592c28f8"
ACCEPTED_ADMISSION_DIGEST = "3715d198eb15564ea459fcd0fdf9d7f185ddce4800cc9b66c31fed41b3f129a0"
CONTRACT_IDS = (
    "P9-EC-RECEIPT-PARENT-CHAIN",
    "P9-EC-RECEIPT-PARENT-ADMISSION",
    "P9-EC-RECEIPT-PARENT-CEILING",
)


def build_parent_context(repo_root: Path, side_tool_root: Path):
    """Build from exact sources; callers must check the accepted admission pin."""
    old = load_successor_forensic_context(repo_root, side_tool_root)
    data = load_json_object(repo_root / SOURCE)
    if (
        data.get("schema_version") != "grcv4_p9_receipt_parent_authority_v1"
        or data.get("record_id") != RECORD_ID
        or data.get("status") != "accepted_by_user_for_implementation"
        or data.get("policy_id") != POLICY_ID
        or data.get("record_digest") != record_digest(data, "record_digest")
        or data.get("record_digest") != ACCEPTED_SOURCE_DIGEST
        or data.get("G2_accepted") is not False
        or data.get("accepted_generic_runtime_support") != []
        or data.get("admitted_specialization_support_sets") != []
    ):
        raise SourceAdmissionError("receipt-parent authority is not accepted or exact")
    admission_row = {
        "source_id": RECORD_ID,
        "path": SOURCE,
        "file_sha256": file_sha256(repo_root / SOURCE),
    }
    rows = [d.admission for d in old.documents] + [admission_row]
    observation = discover_sources(repo_root, rows)
    if observation["state"] != "current_bundle_exact":
        raise SourceAdmissionError(
            "current parent source set is not exact: " + observation["state"]
        )
    document = SourceDocument(
        filename=Path(SOURCE).name,
        path=repo_root / SOURCE,
        data=data,
        admission=admission_row,
        adapter_kind="p9492_receipt_parent_authority_v1",
        record_identifier=RECORD_ID,
        schema_identifier=data["schema_version"],
        digest_field="record_digest",
        semantic_index={},
    )
    overlay = _Overlay(old.graph)
    source = _source_node_id(document)
    overlay.nodes[source] = {
        "node_id": source,
        "kind": "source_record",
        "identifier": source.split(":", 1)[1],
        "source_record_id": RECORD_ID,
        "source_json_pointer": "/",
        "attributes": {
            **admission_row,
            "source_digests": [document.declared_digest],
            "admission_layer": "P9-4.9.2",
        },
    }

    def node(kind, identifier, pointer, attributes):
        result = overlay.add_node(kind, identifier, document, pointer, attributes)
        overlay.add_edge(result, source, "source_identity", document, pointer)
        return result

    claim = node("current_claim", CLAIM_ID, "/claim", data["claim"])
    debt = node("debt_transformation", data["debt"]["debt_id"], "/debt", data["debt"])
    obj = node(
        "normative_object", data["object"]["object_id"], "/object", data["object"]
    )
    overlay.add_edge(
        debt,
        claim,
        "resolved_bounded_by",
        document,
        "/debt/successor_claim_ids/0",
        support_semantic="required",
    )
    overlay.add_edge(
        obj,
        claim,
        "accepted_claim",
        document,
        "/object/accepted_claim_ids/0",
        support_semantic="required",
    )
    if tuple(c["equation_contract_id"] for c in data["contracts"]) != CONTRACT_IDS:
        raise SourceAdmissionError("parent contract roster changed")
    for i, contract in enumerate(data["contracts"]):
        pointer = f"/contracts/{i}"
        target = node(
            "equation_contract", contract["equation_contract_id"], pointer, contract
        )
        overlay.add_edge(
            target,
            claim,
            "accepted_claim",
            document,
            pointer + "/accepted_claim_ids/0",
            support_semantic="required",
        )
        for j, parent in enumerate(contract["parent_object_ids"]):
            overlay.add_edge(
                target,
                "normative_object:" + parent,
                "parent_object",
                document,
                f"{pointer}/parent_object_ids/{j}",
                support_semantic="required",
            )
    for i, predecessor in enumerate(data["source_contract_ids"]):
        overlay.add_edge(
            "equation_contract:" + predecessor,
            debt,
            "exposed_authority_gap",
            document,
            f"/source_contract_ids/{i}",
            support_semantic="indeterminate_requires_review",
        )
    if any(
        edge[key] not in overlay.nodes
        for edge in overlay.propagation_edges.values()
        for key in ("source", "target")
    ):
        raise GraphInvariantError("parent overlay contains an unresolved endpoint")
    bundle = digest(
        {
            "historical_source_bundle_digest": old.source_bundle_digest,
            "source": document.manifest_row(),
            "observation": observation,
        }
    )
    graph = {
        "schema": "grcv4_p9492_parent_graph_v1",
        "historical_graph_digest": old.graph_digest,
        "source_bundle_digest": bundle,
        "nodes": sorted(overlay.nodes.values(), key=lambda r: r["node_id"]),
        "propagation_edges": sorted(
            overlay.propagation_edges.values(), key=lambda r: r["edge_id"]
        ),
        "annotation_edges": old.graph["annotation_edges"],
    }
    graph["graph_digest"] = digest(graph)
    binding = {
        "schema": "grcv4_p9492_parent_admission_v1",
        "status": "accepted_source_admission",
        "source": admission_row,
        "source_record_digest": document.declared_digest,
        "historical_authority_extension_digest": old.authority_extension_digest,
        "historical_graph_digest": old.graph_digest,
        "source_bundle_digest": bundle,
        "graph_digest": graph["graph_digest"],
        "policy_id": POLICY_ID,
        "G2_accepted": False,
    }
    binding["record_digest"] = digest(binding)
    return replace(
        old,
        graph=graph,
        graph_digest=graph["graph_digest"],
        source_bundle_digest=bundle,
        documents=(*old.documents, document),
        documents_by_record={**old.documents_by_record, RECORD_ID: document},
        nodes=overlay.nodes,
        propagation_edges=tuple(graph["propagation_edges"]),
        authority_extension_digest=binding["record_digest"],
    ), binding


def load_current_forensic_context(repo_root: Path, side_tool_root: Path):
    """Current admitted authority, including P9 parents; no fallback to D11."""
    context, binding = build_parent_context(repo_root, side_tool_root)
    if (load_json_object(side_tool_root / "records" / ADMISSION) != binding
            or binding["record_digest"] != ACCEPTED_ADMISSION_DIGEST):
        raise SourceAdmissionError("parent admission no longer rebuilds exactly")
    return context


def parent_authority(repo_root: Path, side_tool_root: Path):
    """The same typed traces for API, notebook and the Phase 9 browser panel."""
    context = load_current_forensic_context(repo_root, side_tool_root)
    output = {
        "schema": "grcv4_p9492_parent_surface_v1",
        "policy_id": POLICY_ID,
        "authority_extension_digest": context.authority_extension_digest,
        "G2_accepted": False,
        "runtime_conformance_inferred": False,
        "claim": reconstruction_path(context, CLAIM_ID),
        "debt": debt_lifecycle(context, "P9-4.9.2-DEBT-PARENTS"),
        "object": object_dependents(context, "P9-L-RECEIPT-PARENTS"),
        "contracts": [contract_provenance(context, name) for name in CONTRACT_IDS],
    }
    output["projection_digest"] = digest(output)
    return output
