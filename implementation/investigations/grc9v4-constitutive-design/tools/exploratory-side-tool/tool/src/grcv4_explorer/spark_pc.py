"""Accepted C_PC applicability over immutable C_OS/C_CI authority.

This explicit successor adds conditional claims and forward obligations while
preserving predecessor graphs, execution bytes and the original research view.
"""
from dataclasses import replace
from pathlib import Path
import hashlib
import subprocess

from . import spark_applicability as predecessor
from .adapters import SourceDocument
from .basin import _bound_file
from .canonical import digest, file_sha256, load_json_object, record_digest
from .forensic import contract_provenance, debt_lifecycle, object_dependents, reconstruction_path
from .successor import _Overlay, _source_node_id

INV = predecessor.INV
SOURCE = INV + "decisions/spark-completion-pc/Authority.json"
MANIFEST = "specs/grc-9-v4-spark-completion-pc-source-manifest.json"
ADMISSION = "SC3SparkPCAdmission.json"
RECORD_ID = "GRC9V4-SC3-SPARK-PC-v1"
SOURCE_DIGEST = "72e5e0d7d745e5100581e38ee1f35698ab813a3d69d76073b7d5d0c9511d9339"
MANIFEST_DIGEST = "e57ec5fa3ce054fb550484709d9b092d5545a0048e4f7f8c5c566ed74fb18989"
ADMISSION_DIGEST = "bac69d2aa6b6716711d461e6a94b20b81b3b44c4b7d0ee190cca55fd18f9045a"
need = predecessor.need
METADATA = INV + 'evidence/spark-completion/applicability/CPCSC3Sources.json'
METADATA_DIGEST = '1ef39e724a041491fdc9f1632089ebe558b0255b0013ecb383e6c4ee1cc6ce80'
REVIEWED_COMMIT = '5d5d9960d1683f1fc2adad4951fd7a3c39571d8c'


def checked_metadata_successor(root):
    """Authenticate the finite metadata transition without rewriting old evidence."""
    root = Path(root)
    value = load_json_object(root / METADATA)
    need(value.get('record_digest') == record_digest(value, 'record_digest') == METADATA_DIGEST,
         'unbound C_PC acceptance metadata transition')
    need(value['reviewed_commit'] == REVIEWED_COMMIT and not value['native_runtime_changed']
         and not value['execution_relabelled'], 'C_PC acceptance changed execution scope')
    rows = {r['path']: r for r in value['sources']}
    need(len(rows) == len(value['sources']), 'duplicate acceptance metadata path')
    for path, row in rows.items():
        before = subprocess.check_output(['git', 'show', REVIEWED_COMMIT+':'+path], cwd=root)
        need(hashlib.sha256(before).hexdigest() == row['before_sha256'], 'reviewed metadata differs')
        _bound_file(root, path, row['after_sha256'])
    validation = load_json_object(root / (INV+'evidence/spark-completion/applicability/CPCValidation.json'))
    need(validation['record_digest'] == record_digest(validation, 'record_digest'), 'original validation digest')
    for ref in validation['sources']:
        actual = file_sha256(root / ref['path'])
        if actual != ref['sha256']:
            row = rows.get(ref['path'])
            need(row is not None and row['before_sha256'] == ref['sha256']
                 and row['after_sha256'] == actual, 'unbound validation metadata successor')
    return value


def checked_manifest(root):
    root = Path(root)
    checked_metadata_successor(root)
    value = load_json_object(root / MANIFEST)
    need(value.get("record_digest") == record_digest(value, "record_digest") == MANIFEST_DIGEST,
         "unbound spark applicability propagation")
    need(value["authority_record_digest"] == SOURCE_DIGEST, "wrong applicability authority")
    for row in [value["predecessor_manifest"], *value["chain"]]:
        _bound_file(root, row["path"], row["sha256"])
    predecessor.checked_manifest(root)
    return value


def build_spark_pc_context(root, side):
    root, side = Path(root), Path(side)
    old = predecessor.load_spark_applicability_forensic_context(root, side)
    value = load_json_object(root / SOURCE)
    need(value.get("record_digest") == record_digest(value, "record_digest") == SOURCE_DIGEST,
         "unaccepted spark applicability authority or changed scope")
    need({p.name for p in (root / SOURCE).parent.glob("*.json")} == {"Authority.json"},
         "unprocessed spark applicability source")
    prior = value["predecessor"]
    _bound_file(root, prior["path"], prior["sha256"])
    need(prior["record_digest"] == predecessor.SOURCE_DIGEST, "wrong SC-3 predecessor")
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
        admission=admission, adapter_kind="spark_pc_authority_v1", record_identifier=RECORD_ID,
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
    graph = dict(schema="grc9v4_spark_pc_graph_v1", historical_graph_digest=old.graph_digest,
        source_bundle_digest=bundle, nodes=sorted(overlay.nodes.values(), key=lambda r: r["node_id"]),
        propagation_edges=sorted(overlay.propagation_edges.values(), key=lambda r: r["edge_id"]),
        annotation_edges=old.graph["annotation_edges"])
    graph["graph_digest"] = digest(graph)
    binding = dict(schema="grc9v4_spark_pc_admission_v1", source=admission,
        source_record_digest=value["record_digest"], acceptance=ref,
        predecessor_authority_extension_digest=old.authority_extension_digest,
        historical_graph_digest=old.graph_digest, source_bundle_digest=bundle,
        graph_digest=graph["graph_digest"], scope=value["scope"])
    binding["record_digest"] = digest(binding)
    return replace(old, graph=graph, graph_digest=graph["graph_digest"], source_bundle_digest=bundle,
        documents=(*old.documents, document), documents_by_record={**old.documents_by_record, RECORD_ID: document},
        nodes=overlay.nodes, propagation_edges=tuple(graph["propagation_edges"]),
        authority_extension_digest=binding["record_digest"]), binding


def load_spark_pc_forensic_context(root, side):
    context, binding = build_spark_pc_context(root, side)
    need(load_json_object(Path(side) / "records" / ADMISSION) == binding
         and binding["record_digest"] == ADMISSION_DIGEST, "spark applicability admission changed")
    return context


def spark_pc_authority(root, side):
    root = Path(root)
    context = load_spark_pc_forensic_context(root, side)
    data = context.documents_by_record[RECORD_ID].data
    acceptance = load_json_object(root / data["acceptance"]["path"])
    manifest = checked_manifest(root)
    paths = sorted({SOURCE, MANIFEST, data["acceptance"]["path"], data["predecessor"]["path"],
        manifest["predecessor_manifest"]["path"], *[r["path"] for r in acceptance["subjects"]],
        *[r["path"] for r in manifest["chain"]]})
    value = dict(schema="grc9v4_spark_pc_surface_v1", authority_record_digest=SOURCE_DIGEST,
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


def spark_pc_source(root, side, path):
    view = spark_pc_authority(root, side)
    row = next((r for r in view["source_refs"] if r["path"] == path), None)
    if row is None:
        raise KeyError("not an indexed spark applicability source")
    return _bound_file(Path(root), path, row["sha256"]).read_bytes(), row
