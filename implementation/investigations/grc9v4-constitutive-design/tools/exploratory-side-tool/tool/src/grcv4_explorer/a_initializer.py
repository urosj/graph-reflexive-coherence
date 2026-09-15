"""Accepted target-reference-pass design; no producer or migration implementation."""

from dataclasses import replace
from pathlib import Path

from .abundance import load_abundance_forensic_context
from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .discovery import discover_sources
from .errors import GraphInvariantError, SourceAdmissionError
from .forensic import contract_provenance, debt_lifecycle, object_dependents, reconstruction_path
from .successor import _Overlay, _source_node_id

SOURCE = "implementation/investigations/grc9v4-constitutive-design/decisions/P9CandidateAInitializerReferencePassAuthority.json"
ADMISSION = "P972aInitializerAdmission.json"
RECORD_ID = "GRCV4-P9-7.2a-A-INITIALIZER-v1"
POLICY_ID = "grcv4-a-target-reference-pass-v1"
NUMERICAL_ID = "grcv4-a-reference-pass-binary64-v1"
CLAIM_ID = "P9-7.2a-CL-O-INIT-001"
DEBT_ID = "P9-7.2a-DEBT-A-INITIALIZER-SOURCE"
OBJECT_ID = "P9-O-A-INITIALIZER-REFERENCE-PASS"
CONTRACT_ID = "P9-EC-A-INITIALIZER-REFERENCE-PASS"
OBLIGATION_ID = "P9-7.2a-VO-A-INITIALIZER-INTEGRATION"
ACCEPTED_SOURCE_DIGEST = "32f938ccb19e94d94023bb3c83c8597495fb6e5a2b1e0c84ef1feded4456a8f3"
ACCEPTED_ADMISSION_DIGEST = "d9ba802c9fd29169bcea4adac3adc83cad1f1ef6a79e2dba99b6dff3f1a10188"


def build_initializer_context(repo_root: Path, side_tool_root: Path):
    """Rebuild from pinned predecessors and exact accepted source/design bytes."""
    old = load_abundance_forensic_context(repo_root, side_tool_root)
    data = load_json_object(repo_root / SOURCE)
    if (
        data.get("schema_version") != "grcv4_p972a_initializer_authority_v1"
        or data.get("record_id") != RECORD_ID
        or data.get("status") != "accepted_bounded_design"
        or data.get("policy_id") != POLICY_ID
        or data.get("numerical_id") != NUMERICAL_ID
        or data.get("record_digest") != record_digest(data, "record_digest")
        or data.get("record_digest") != ACCEPTED_SOURCE_DIGEST
        or data.get("producer_choice_resolved") is not True
        or any(data.get(k) is not False for k in (
            "payload_specification_complete", "positive_migration_verified",
            "aggregate_closed", "G2_accepted", "G3_accepted"))
        or data.get("accepted_generic_runtime_support") != []
        or data.get("admitted_specialization_support_sets") != []
    ):
        raise SourceAdmissionError("initializer authority is not accepted or exact")
    design = repo_root / data["design_path"]
    if not design.resolve().is_relative_to(repo_root.resolve()) or file_sha256(design) != data["design_sha256"]:
        raise SourceAdmissionError("accepted initializer design changed or escaped repository")
    admission_row = {"source_id": RECORD_ID, "path": SOURCE,
                     "file_sha256": file_sha256(repo_root / SOURCE)}
    observation = discover_sources(repo_root, [d.admission for d in old.documents] + [admission_row])
    if observation["state"] != "current_bundle_exact":
        raise SourceAdmissionError("current initializer source set is not exact: " + observation["state"])
    document = SourceDocument(
        filename=Path(SOURCE).name, path=repo_root / SOURCE, data=data,
        admission=admission_row, adapter_kind="p972a_initializer_authority_v1",
        record_identifier=RECORD_ID, schema_identifier=data["schema_version"],
        digest_field="record_digest", semantic_index={},
    )
    overlay = _Overlay(old.graph)
    source = _source_node_id(document)
    overlay.nodes[source] = {
        "node_id": source, "kind": "source_record", "identifier": source.split(":", 1)[1],
        "source_record_id": RECORD_ID, "source_json_pointer": "/",
        "attributes": {**admission_row, "source_digests": [document.declared_digest],
                       "admission_layer": "P9-7.2a-initializer"},
    }

    def node(kind, identifier, pointer, attributes):
        result = overlay.add_node(kind, identifier, document, pointer, attributes)
        overlay.add_edge(result, source, "source_identity", document, pointer)
        return result

    claim = node("current_claim", CLAIM_ID, "/claim", data["claim"])
    debt = node("debt_transformation", DEBT_ID, "/debt", data["debt"])
    obj = node("normative_object", OBJECT_ID, "/object", data["object"])
    overlay.add_edge(debt, claim, "resolved_bounded_by", document,
                     "/debt/successor_claim_ids/0", support_semantic="required")
    overlay.add_edge(obj, claim, "accepted_claim", document,
                     "/object/accepted_claim_ids/0", support_semantic="required")
    contract = data["contracts"][0]
    target = node("equation_contract", CONTRACT_ID, "/contracts/0", contract)
    overlay.add_edge(target, claim, "accepted_claim", document,
                     "/contracts/0/accepted_claim_ids/0", support_semantic="required")
    overlay.add_edge(target, obj, "parent_object", document,
                     "/contracts/0/parent_object_ids/0", support_semantic="required")
    obligation = node("verification_obligation", OBLIGATION_ID,
                      "/verification_obligations/0", data["verification_obligations"][0])
    overlay.add_edge(debt, obligation, "verification_obligation", document,
                     "/debt/verification_obligation", support_semantic="not_applicable")
    for i, predecessor in enumerate(data["source_contract_ids"]):
        overlay.add_edge("equation_contract:" + predecessor, debt, "exposed_authority_gap",
                         document, f"/source_contract_ids/{i}",
                         support_semantic="indeterminate_requires_review")
    if any(edge[key] not in overlay.nodes for edge in overlay.propagation_edges.values()
           for key in ("source", "target")):
        raise GraphInvariantError("initializer overlay contains an unresolved endpoint")
    bundle = digest({"historical_source_bundle_digest": old.source_bundle_digest,
                     "source": document.manifest_row(), "observation": observation})
    graph = {
        "schema": "grcv4_p972a_initializer_graph_v1", "historical_graph_digest": old.graph_digest,
        "source_bundle_digest": bundle,
        "nodes": sorted(overlay.nodes.values(), key=lambda r: r["node_id"]),
        "propagation_edges": sorted(overlay.propagation_edges.values(), key=lambda r: r["edge_id"]),
        "annotation_edges": old.graph["annotation_edges"],
    }
    graph["graph_digest"] = digest(graph)
    binding = {
        "schema": "grcv4_p972a_initializer_admission_v1", "status": "accepted_source_admission",
        "source": admission_row, "source_record_digest": document.declared_digest,
        "design_path": data["design_path"], "design_sha256": data["design_sha256"],
        "design_commit": data["design_commit"],
        "historical_authority_extension_digest": old.authority_extension_digest,
        "historical_graph_digest": old.graph_digest, "source_bundle_digest": bundle,
        "graph_digest": graph["graph_digest"], "policy_id": POLICY_ID,
        "producer_choice_resolved": True, "positive_migration_verified": False,
        "G2_accepted": False, "G3_accepted": False,
    }
    binding["record_digest"] = digest(binding)
    return replace(
        old, graph=graph, graph_digest=graph["graph_digest"], source_bundle_digest=bundle,
        documents=(*old.documents, document),
        documents_by_record={**old.documents_by_record, RECORD_ID: document},
        nodes=overlay.nodes, propagation_edges=tuple(graph["propagation_edges"]),
        authority_extension_digest=binding["record_digest"],
    ), binding


def load_current_forensic_context(repo_root: Path, side_tool_root: Path):
    context, binding = build_initializer_context(repo_root, side_tool_root)
    if (load_json_object(side_tool_root / "records" / ADMISSION) != binding
            or binding["record_digest"] != ACCEPTED_ADMISSION_DIGEST):
        raise SourceAdmissionError("initializer admission no longer rebuilds exactly")
    return context


def initializer_authority(repo_root: Path, side_tool_root: Path):
    """Same source-bound typed traces for agents, notebook and browser."""
    context = load_current_forensic_context(repo_root, side_tool_root)
    output = {
        "schema": "grcv4_p972a_initializer_surface_v1", "policy_id": POLICY_ID,
        "numerical_id": NUMERICAL_ID, "authority_extension_digest": context.authority_extension_digest,
        "producer_choice_resolved": True, "payload_specification_complete": False,
        "positive_migration_verified": False, "aggregate_closed": False,
        "G2_accepted": False, "G3_accepted": False, "runtime_conformance_inferred": False,
        "claim": reconstruction_path(context, CLAIM_ID),
        "debt": debt_lifecycle(context, DEBT_ID),
        "object": object_dependents(context, OBJECT_ID),
        "contracts": [contract_provenance(context, CONTRACT_ID)],
    }
    output["projection_digest"] = digest(output)
    return output
