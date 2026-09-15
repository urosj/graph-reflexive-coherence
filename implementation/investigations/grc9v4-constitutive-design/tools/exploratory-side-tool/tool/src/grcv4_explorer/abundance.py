"""Accepted availability authority, appended to the pinned P9 parent context."""

from dataclasses import replace
from pathlib import Path

from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .discovery import discover_sources
from .errors import GraphInvariantError, SourceAdmissionError
from .forensic import contract_provenance, debt_lifecycle, object_dependents, reconstruction_path
from .receipt_parents import load_parent_forensic_context
from .successor import _Overlay, _source_node_id

SOURCE = "implementation/investigations/grc9v4-constitutive-design/decisions/P9AbundanceInterfaceAuthority.json"
ADMISSION = "P9491aAbundanceAdmission.json"
POLICY_ID = "grcv4-family-abundance-diagnostic-v1"
RECORD_ID = "GRCV4-P9-4.9.1a-ABUNDANCE-v1"
CLAIM_ID = "P9-4.9.1a-CL-N-001"
ACCEPTED_SOURCE_DIGEST = "d9488700be9624da8500c1e533aa65d33b4f36a3307748ad12fd66449d8fe053"
ACCEPTED_ADMISSION_DIGEST = "f50b4623cf0400532cda0c6c4ea600d1d55552d7927fbfcef62931524380188e"
CONTRACT_IDS = (
    "P9-EC-ABUNDANCE-INTERFACE",
    "P9-EC-ABUNDANCE-OBSERVATION",
    "P9-EC-ABUNDANCE-FAILURE-AND-CEILING",
)


def build_abundance_context(repo_root: Path, side_tool_root: Path, *, historical_only=False):
    """Build the bounded overlay; loading additionally requires the admission pin."""
    old = load_parent_forensic_context(repo_root, side_tool_root)
    data = load_json_object(repo_root / SOURCE)
    if (
        data.get("schema_version") != "grcv4_p9_abundance_interface_authority_v1"
        or data.get("record_id") != RECORD_ID
        or data.get("status") != "accepted_by_user_for_implementation"
        or data.get("policy_id") != POLICY_ID
        or data.get("record_digest") != record_digest(data, "record_digest")
        or data.get("record_digest") != ACCEPTED_SOURCE_DIGEST
        or data.get("G2_accepted") is not False
        or data.get("accepted_generic_runtime_support") != []
        or data.get("admitted_specialization_support_sets") != []
    ):
        raise SourceAdmissionError("abundance authority is not accepted or exact")
    admission_row = {
        "source_id": RECORD_ID, "path": SOURCE,
        "file_sha256": file_sha256(repo_root / SOURCE),
    }
    rows = [d.admission for d in old.documents] + [admission_row]
    observation = discover_sources(repo_root, rows)
    if historical_only and observation["state"] == "new_unprocessed_source_available":
        # Reconstruct this pinned historical observation only. Current loading
        # independently requires the entire successor inventory to be exact.
        observation = dict(observation)
        observation.update(
            state="current_bundle_exact", observed_record_count=len(rows),
            added_unprocessed=[], current_repository_state_complete=True,
            historical_snapshot_only=False, live_rebuild_allowed=True,
            refresh_requirement={"required": False, "steps": []},
        )
        observation["observation_digest"] = record_digest(observation, "observation_digest")
    if observation["state"] != "current_bundle_exact":
        raise SourceAdmissionError("current abundance source set is not exact: " + observation["state"])
    document = SourceDocument(
        filename=Path(SOURCE).name, path=repo_root / SOURCE, data=data,
        admission=admission_row, adapter_kind="p9491a_abundance_authority_v1",
        record_identifier=RECORD_ID, schema_identifier=data["schema_version"],
        digest_field="record_digest", semantic_index={},
    )
    overlay = _Overlay(old.graph)
    source = _source_node_id(document)
    overlay.nodes[source] = {
        "node_id": source, "kind": "source_record", "identifier": source.split(":", 1)[1],
        "source_record_id": RECORD_ID, "source_json_pointer": "/",
        "attributes": {**admission_row, "source_digests": [document.declared_digest], "admission_layer": "P9-4.9.1a"},
    }

    def node(kind, identifier, pointer, attributes):
        result = overlay.add_node(kind, identifier, document, pointer, attributes)
        overlay.add_edge(result, source, "source_identity", document, pointer)
        return result

    claim = node("current_claim", CLAIM_ID, "/claim", data["claim"])
    debt = node("debt_transformation", data["debt"]["debt_id"], "/debt", data["debt"])
    obj = node("normative_object", data["object"]["object_id"], "/object", data["object"])
    overlay.add_edge(debt, claim, "resolved_bounded_by", document,
                     "/debt/successor_claim_ids/0", support_semantic="required")
    overlay.add_edge(obj, claim, "accepted_claim", document,
                     "/object/accepted_claim_ids/0", support_semantic="required")
    if tuple(c["equation_contract_id"] for c in data["contracts"]) != CONTRACT_IDS:
        raise SourceAdmissionError("abundance contract roster changed")
    for i, contract in enumerate(data["contracts"]):
        pointer = f"/contracts/{i}"
        target = node("equation_contract", contract["equation_contract_id"], pointer, contract)
        overlay.add_edge(target, claim, "accepted_claim", document,
                         pointer + "/accepted_claim_ids/0", support_semantic="required")
        overlay.add_edge(target, obj, "parent_object", document,
                         pointer + "/parent_object_ids/0", support_semantic="required")
    for i, predecessor in enumerate(data["source_contract_ids"]):
        overlay.add_edge("equation_contract:" + predecessor, debt, "exposed_authority_gap",
                         document, f"/source_contract_ids/{i}",
                         support_semantic="indeterminate_requires_review")
    if any(edge[key] not in overlay.nodes for edge in overlay.propagation_edges.values()
           for key in ("source", "target")):
        raise GraphInvariantError("abundance overlay contains an unresolved endpoint")
    bundle = digest({"historical_source_bundle_digest": old.source_bundle_digest,
                     "source": document.manifest_row(), "observation": observation})
    graph = {
        "schema": "grcv4_p9491a_abundance_graph_v1", "historical_graph_digest": old.graph_digest,
        "source_bundle_digest": bundle,
        "nodes": sorted(overlay.nodes.values(), key=lambda r: r["node_id"]),
        "propagation_edges": sorted(overlay.propagation_edges.values(), key=lambda r: r["edge_id"]),
        "annotation_edges": old.graph["annotation_edges"],
    }
    graph["graph_digest"] = digest(graph)
    binding = {
        "schema": "grcv4_p9491a_abundance_admission_v1", "status": "accepted_source_admission",
        "source": admission_row, "source_record_digest": document.declared_digest,
        "historical_authority_extension_digest": old.authority_extension_digest,
        "historical_graph_digest": old.graph_digest, "source_bundle_digest": bundle,
        "graph_digest": graph["graph_digest"], "policy_id": POLICY_ID, "G2_accepted": False,
    }
    binding["record_digest"] = digest(binding)
    return replace(
        old, graph=graph, graph_digest=graph["graph_digest"], source_bundle_digest=bundle,
        documents=(*old.documents, document),
        documents_by_record={**old.documents_by_record, RECORD_ID: document},
        nodes=overlay.nodes, propagation_edges=tuple(graph["propagation_edges"]),
        authority_extension_digest=binding["record_digest"],
    ), binding


def load_abundance_forensic_context(repo_root: Path, side_tool_root: Path):
    """Pinned P9-4.9.1a context, excluding subsequent authority."""
    context, binding = build_abundance_context(repo_root, side_tool_root, historical_only=True)
    if (load_json_object(side_tool_root / "records" / ADMISSION) != binding
            or binding["record_digest"] != ACCEPTED_ADMISSION_DIGEST):
        raise SourceAdmissionError("abundance admission no longer rebuilds exactly")
    return context


def load_current_forensic_context(repo_root: Path, side_tool_root: Path):
    """Compatibility import for current authority; never historical fallback."""
    from .a_initializer import load_current_forensic_context as load
    return load(repo_root, side_tool_root)


def abundance_authority(repo_root: Path, side_tool_root: Path):
    """Identical typed traces for API, notebook and the read-only browser panel."""
    context = load_current_forensic_context(repo_root, side_tool_root)
    output = {
        "schema": "grcv4_p9491a_abundance_surface_v1", "policy_id": POLICY_ID,
        "authority_extension_digest": context.authority_extension_digest,
        "G2_accepted": False, "runtime_conformance_inferred": False,
        "numeric_definition_admitted": False,
        "claim": reconstruction_path(context, CLAIM_ID),
        "debt": debt_lifecycle(context, "P9-4.9.1a-DEBT-ABUNDANCE"),
        "object": object_dependents(context, "P9-O-ABUNDANCE-INTERFACE"),
        "contracts": [contract_provenance(context, name) for name in CONTRACT_IDS],
    }
    output["projection_digest"] = digest(output)
    return output
