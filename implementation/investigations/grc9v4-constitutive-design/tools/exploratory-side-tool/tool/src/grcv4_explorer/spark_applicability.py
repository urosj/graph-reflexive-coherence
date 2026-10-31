"""Explicit family applicability successor over immutable SC-3 authority.

The admitted data supplies family rows and claim/debt/contract collections.
Adding a reviewed family extends that data and its pinned propagation; it
does not require a family-specific dispatcher or change historical loaders.
"""
from dataclasses import replace
from pathlib import Path

from . import spark_completion as predecessor
from .adapters import SourceDocument
from .basin import _bound_file
from .canonical import digest, file_sha256, load_json_object, record_digest
from .forensic import contract_provenance, debt_lifecycle, object_dependents, reconstruction_path
from .successor import _Overlay, _source_node_id

INV = predecessor.INV
SOURCE = INV + "decisions/spark-completion-applicability/Authority.json"
MANIFEST = "specs/grc-9-v4-spark-completion-applicability-source-manifest.json"
ADMISSION = "SC3SparkApplicabilityAdmission.json"
RECORD_ID = "GRC9V4-SC3-SPARK-APPLICABILITY-v1"
SOURCE_DIGEST = "6a3ce4ff9190a528779b419645c52d6e4f0d14aaca9dd64f555370d27e726bb7"
MANIFEST_DIGEST = "4904ec03d9366a860f1628b438234f844b08f5bae79eeca4ada06c64057ab0ae"
ADMISSION_DIGEST = "25578a8fc86c3de969807091333f82aed555587cebd06bb8016da14d4688493f"
need = predecessor.need


def checked_manifest(root):
    root = Path(root)
    value = load_json_object(root / MANIFEST)
    need(value.get("record_digest") == record_digest(value, "record_digest") == MANIFEST_DIGEST,
         "unbound spark applicability propagation")
    need(value["authority_record_digest"] == SOURCE_DIGEST, "wrong applicability authority")
    for row in [value["predecessor_manifest"], *value["chain"]]:
        _bound_file(root, row["path"], row["sha256"])
    predecessor.checked_manifest(root)
    return value


def build_spark_applicability_context(root, side):
    root, side = Path(root), Path(side)
    old = predecessor.load_spark_completion_forensic_context(root, side)
    value = load_json_object(root / SOURCE)
    need(value.get("record_digest") == record_digest(value, "record_digest") == SOURCE_DIGEST,
         "unaccepted spark applicability authority or changed scope")
    need({p.name for p in (root / SOURCE).parent.glob("*.json")} == {"Authority.json"},
         "unprocessed spark applicability source")
    prior = value["predecessor"]
    _bound_file(root, prior["path"], prior["sha256"])
    need(prior["record_digest"] == predecessor.ACCEPTED_SOURCE_DIGEST, "wrong SC-3 predecessor")
    _bound_file(root, value["design_path"], value["design_sha256"])
    ref = value["acceptance"]
    acceptance = load_json_object(_bound_file(root, ref["path"], ref["sha256"]))
    need(acceptance["record_digest"] == record_digest(acceptance, "record_digest") == ref["record_digest"]
         and acceptance["status"] == "accepted_bounded_scientific_completion", "family acceptance changed")
    for row in acceptance["subjects"]:
        _bound_file(root, row["path"], row["sha256"])
    manifest = checked_manifest(root)
    contracts = value["contracts"]
    need(manifest["contract_ids"] == [r["equation_contract_id"] for r in contracts],
         "applicability propagation omitted a contract")
    decision = (root / value["design_path"]).read_text()
    for row in contracts:
        body = decision.split(row["design_section"] + "\n", 1)[1].split("\n## ", 1)[0].strip()
        need(body == row["normative_equation_or_contract"], "contract differs from adjudication")

    admission = dict(source_id=RECORD_ID, path=SOURCE, file_sha256=file_sha256(root / SOURCE))
    document = SourceDocument(filename="Authority.json", path=root / SOURCE, data=value,
        admission=admission, adapter_kind="spark_applicability_authority_v1", record_identifier=RECORD_ID,
        schema_identifier=value["schema_version"], digest_field="record_digest", semantic_index={})
    overlay = _Overlay(old.graph)
    source = _source_node_id(document)
    overlay.nodes[source] = dict(node_id=source, kind="source_record", identifier=source.split(":", 1)[1],
        source_record_id=RECORD_ID, source_json_pointer="/", attributes={**admission,
        "source_digests": [document.declared_digest], "admission_layer": "SC-3-family-applicability"})
    for collection, kind, key in [("claims", "current_claim", "claim_id"),
            ("debts", "debt_transformation", "debt_id"), ("objects", "normative_object", "object_id"),
            ("contracts", "equation_contract", "equation_contract_id"),
            ("verification_obligations", "verification_obligation", "obligation_id")]:
        for i, row in enumerate(value[collection]):
            pointer = f"/{collection}/{i}"
            node = overlay.add_node(kind, row[key], document, pointer, row)
            overlay.add_edge(node, source, "source_identity", document, pointer)
            field = "successor_claim_ids" if collection == "debts" else "accepted_claim_ids"
            for j, claim in enumerate(row.get(field, [])):
                overlay.add_edge(node, "current_claim:" + claim,
                    "resolved_bounded_by" if collection == "debts" else "accepted_claim", document,
                    f"{pointer}/{field}/{j}", support_semantic="accepted_bounded_conditional_science")
            for j, obj in enumerate(row.get("parent_object_ids", [])):
                overlay.add_edge(node, "normative_object:" + obj, "parent_object", document,
                    f"{pointer}/parent_object_ids/{j}", support_semantic="required")
            for j, obligation in enumerate(row.get("verification_obligation_ids", [])):
                overlay.add_edge(node, "verification_obligation:" + obligation, "verification_obligation",
                    document, f"{pointer}/verification_obligation_ids/{j}", support_semantic="pending_forward")
            for j, debt in enumerate(row.get("contributes_to_debt_ids", [])):
                overlay.add_edge(node, "debt_transformation:" + debt, "bounded_scientific_contribution",
                    document, f"{pointer}/contributes_to_debt_ids/{j}", support_semantic="no_aggregate_closure")
    for i, contract in enumerate(value["source_contract_ids"]):
        overlay.add_edge(source, "equation_contract:" + contract, "authority_reference", document,
            f"/source_contract_ids/{i}", support_semantic="provenance_reference_only")
    need(all(edge[k] in overlay.nodes for edge in overlay.propagation_edges.values()
             for k in ("source", "target")), "unresolved applicability graph endpoint")
    bundle = digest(dict(predecessor_source_bundle_digest=old.source_bundle_digest, source=document.manifest_row()))
    graph = dict(schema="grc9v4_spark_applicability_graph_v1", historical_graph_digest=old.graph_digest,
        source_bundle_digest=bundle, nodes=sorted(overlay.nodes.values(), key=lambda r: r["node_id"]),
        propagation_edges=sorted(overlay.propagation_edges.values(), key=lambda r: r["edge_id"]),
        annotation_edges=old.graph["annotation_edges"])
    graph["graph_digest"] = digest(graph)
    binding = dict(schema="grc9v4_spark_applicability_admission_v1", source=admission,
        source_record_digest=value["record_digest"], acceptance=ref,
        predecessor_authority_extension_digest=old.authority_extension_digest,
        historical_graph_digest=old.graph_digest, source_bundle_digest=bundle,
        graph_digest=graph["graph_digest"], scope=value["scope"])
    binding["record_digest"] = digest(binding)
    return replace(old, graph=graph, graph_digest=graph["graph_digest"], source_bundle_digest=bundle,
        documents=(*old.documents, document), documents_by_record={**old.documents_by_record, RECORD_ID: document},
        nodes=overlay.nodes, propagation_edges=tuple(graph["propagation_edges"]),
        authority_extension_digest=binding["record_digest"]), binding


def load_spark_applicability_forensic_context(root, side):
    context, binding = build_spark_applicability_context(root, side)
    need(load_json_object(Path(side) / "records" / ADMISSION) == binding
         and binding["record_digest"] == ADMISSION_DIGEST, "spark applicability admission changed")
    return context


def spark_applicability_authority(root, side):
    root = Path(root)
    context = load_spark_applicability_forensic_context(root, side)
    data = context.documents_by_record[RECORD_ID].data
    acceptance = load_json_object(root / data["acceptance"]["path"])
    manifest = checked_manifest(root)
    paths = sorted({SOURCE, MANIFEST, data["acceptance"]["path"], data["predecessor"]["path"],
        manifest["predecessor_manifest"]["path"], *[r["path"] for r in acceptance["subjects"]],
        *[r["path"] for r in manifest["chain"]]})
    value = dict(schema="grc9v4_spark_applicability_surface_v1", authority_record_digest=SOURCE_DIGEST,
        authority_extension_digest=context.authority_extension_digest, scope=data["scope"],
        family_dispositions=data["family_dispositions"], review_limits=acceptance["review_limits"],
        check_mode="retained_authority_propagation_integrity_not_numerical_rerun",
        claims=[reconstruction_path(context, r["claim_id"]) for r in data["claims"]],
        debts=[debt_lifecycle(context, r["debt_id"]) for r in data["debts"]],
        objects=[object_dependents(context, r["object_id"]) for r in data["objects"]],
        contracts=[contract_provenance(context, r["equation_contract_id"]) for r in data["contracts"]],
        source_refs=[dict(path=p, sha256=file_sha256(root / p)) for p in paths])
    value["projection_digest"] = digest(value)
    return value


def spark_applicability_source(root, side, path):
    view = spark_applicability_authority(root, side)
    row = next((r for r in view["source_refs"] if r["path"] == path), None)
    if row is None:
        raise KeyError("not an indexed spark applicability source")
    return _bound_file(Path(root), path, row["sha256"]).read_bytes(), row
