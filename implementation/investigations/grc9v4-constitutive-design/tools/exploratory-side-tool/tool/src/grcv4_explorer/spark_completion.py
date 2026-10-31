"""Explicit SC-3 scientific successor; historical loaders and native grants stay fixed."""
from dataclasses import replace
from pathlib import Path

from .basin import load_basin_forensic_context as load_predecessor, _bound_file
from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .errors import SourceAdmissionError
from .forensic import contract_provenance, debt_lifecycle, object_dependents, reconstruction_path
from .successor import _Overlay, _source_node_id

INV = "implementation/investigations/grc9v4-constitutive-design/"
SOURCE = INV + "decisions/spark-completion/Authority.json"
MANIFEST = "specs/grc-9-v4-spark-completion-source-manifest.json"
ADMISSION = "SC3SparkCompletionAdmission.json"
RECORD_ID = "GRC9V4-SC3-SPARK-COMPLETION-v1"
ACCEPTED_SOURCE_DIGEST = "dd2583ca6b0192c9f72f15ed1c01d82b5c2a9de95da9583cbaeafe2530684383"
ACCEPTED_ADMISSION_DIGEST = '6d1edd7a57d4eedc72ebd96f14fb6c3c026d5307c890be5eda12bd0be57b0915'
ACCEPTED_MANIFEST_DIGEST = '1e3fd782f52c8d798f31827208b1a4815510be1d891fe857cb3ad4387b1bf1c0'


def need(condition, message):
    if not condition:
        raise SourceAdmissionError(message)


def build_spark_completion_context(root: Path, side: Path):
    root, side = Path(root), Path(side)
    old = load_predecessor(root, side)
    data = load_json_object(root / SOURCE)
    need(data.get("record_digest") == record_digest(data, "record_digest") == ACCEPTED_SOURCE_DIGEST,
         "unaccepted SC-3 authority or changed claim/debt scope")
    need({p.name for p in (root / SOURCE).parent.glob("*.json")} == {"Authority.json"},
         "unprocessed spark successor source")
    _bound_file(root, data["design_path"], data["design_sha256"])
    ref = data["acceptance"]
    accepted = load_json_object(_bound_file(root, ref["path"], ref["sha256"]))
    need(accepted["record_digest"] == record_digest(accepted, "record_digest") == ref["record_digest"]
         and accepted["status"] == "accepted_bounded_scientific_completion", "SC-2 acceptance changed")
    for row in [*accepted["subjects"], *data["historical_sources"]]:
        _bound_file(root, row["path"], row["sha256"])
    admission = dict(source_id=RECORD_ID, path=SOURCE, file_sha256=file_sha256(root / SOURCE))
    document = SourceDocument(filename="Authority.json", path=root / SOURCE, data=data,
        admission=admission, adapter_kind="sc3_spark_authority_v1", record_identifier=RECORD_ID,
        schema_identifier=data["schema_version"], digest_field="record_digest", semantic_index={})
    overlay = _Overlay(old.graph)
    source = _source_node_id(document)
    overlay.nodes[source] = dict(node_id=source, kind="source_record", identifier=source.split(":",1)[1],
        source_record_id=RECORD_ID, source_json_pointer="/", attributes={**admission,
        "source_digests":[document.declared_digest], "admission_layer":"SC-3-scientific"})

    def node(kind, identifier, pointer, attrs):
        result = overlay.add_node(kind, identifier, document, pointer, attrs)
        overlay.add_edge(result, source, "source_identity", document, pointer)
        return result

    classes = {c["claim_id"]:c["claim_class"] for c in data["claims"]}
    for collection, kind, key in [("claims","current_claim","claim_id"),
            ("debts","debt_transformation","debt_id"), ("objects","normative_object","object_id"),
            ("contracts","equation_contract","equation_contract_id"),
            ("verification_obligations","verification_obligation","obligation_id")]:
        for i, row in enumerate(data[collection]):
            pointer = f"/{collection}/{i}"
            current = node(kind, row[key], pointer, row)
            field = "successor_claim_ids" if collection == "debts" else "accepted_claim_ids"
            for j, claim in enumerate(row.get(field, [])):
                conditional = classes[claim] == "conditional_mathematical"
                overlay.add_edge(current, "current_claim:"+claim,
                    "resolved_bounded_by" if collection == "debts" else "accepted_claim", document,
                    f"{pointer}/{field}/{j}", support_semantic=("accepted_bounded_conditional_science"
                    if conditional else "accepted_bounded_scientific_design"))
            for j, obj in enumerate(row.get("parent_object_ids", [])):
                overlay.add_edge(current,"normative_object:"+obj,"parent_object",document,
                    f"{pointer}/parent_object_ids/{j}",support_semantic="required")
            if collection == "debts":
                overlay.add_edge(current,"verification_obligation:"+row["verification_obligation"],
                    "verification_obligation",document,pointer+"/verification_obligation",
                    support_semantic="pending_forward")
    for i, predecessor in enumerate(data["source_contract_ids"]):
        overlay.add_edge("equation_contract:"+predecessor,"debt_transformation:SC-DEBT-ORGANIZATION",
            "exposed_authority_gap",document,f"/source_contract_ids/{i}",
            support_semantic="indeterminate_requires_review")
    need(all(e[k] in overlay.nodes for e in overlay.propagation_edges.values()
             for k in ("source","target")), "unresolved SC-3 graph endpoint")
    bundle = digest(dict(predecessor_source_bundle_digest=old.source_bundle_digest,source=document.manifest_row()))
    graph = dict(schema="grc9v4_sc3_spark_graph_v1",historical_graph_digest=old.graph_digest,
        source_bundle_digest=bundle,nodes=sorted(overlay.nodes.values(),key=lambda r:r["node_id"]),
        propagation_edges=sorted(overlay.propagation_edges.values(),key=lambda r:r["edge_id"]),
        annotation_edges=old.graph["annotation_edges"])
    graph["graph_digest"] = digest(graph)
    binding = dict(schema="grc9v4_sc3_spark_admission_v1",source=admission,
        source_record_digest=data["record_digest"],acceptance=ref,
        historical_authority_extension_digest=old.authority_extension_digest,
        historical_graph_digest=old.graph_digest,source_bundle_digest=bundle,graph_digest=graph["graph_digest"],
        scope=data["scope"])
    binding["record_digest"] = digest(binding)
    return replace(old,graph=graph,graph_digest=graph["graph_digest"],source_bundle_digest=bundle,
        documents=(*old.documents,document),documents_by_record={**old.documents_by_record,RECORD_ID:document},
        nodes=overlay.nodes,propagation_edges=tuple(graph["propagation_edges"]),
        authority_extension_digest=binding["record_digest"]), binding


def load_spark_completion_forensic_context(root: Path, side: Path):
    context, binding = build_spark_completion_context(root,side)
    need(load_json_object(Path(side)/"records"/ADMISSION) == binding
         and binding["record_digest"] == ACCEPTED_ADMISSION_DIGEST,
         "SC-3 admission no longer rebuilds exactly")
    return context


def checked_manifest(root):
    value = load_json_object(Path(root)/MANIFEST)
    need(value.get("record_digest") == record_digest(value,"record_digest") == ACCEPTED_MANIFEST_DIGEST,
         "unbound SC-3 propagation")
    for row in value["chain"]:
        _bound_file(Path(root),row["path"],row["sha256"])
    return value


def spark_completion_authority(root: Path, side: Path):
    context = load_spark_completion_forensic_context(root,side)
    data = context.documents_by_record[RECORD_ID].data
    manifest = checked_manifest(root)
    paths = sorted({SOURCE,MANIFEST,data["acceptance"]["path"],
        *[r["path"] for r in data["historical_sources"]], *[r["path"] for r in manifest["chain"]]})
    value = dict(schema="grc9v4_sc3_spark_surface_v1",authority_record_digest=ACCEPTED_SOURCE_DIGEST,
        authority_extension_digest=context.authority_extension_digest,scope=data["scope"],
        check_mode="retained_authority_propagation_integrity_not_numerical_rerun",
        claims=[reconstruction_path(context,r["claim_id"]) for r in data["claims"]],
        debts=[debt_lifecycle(context,r["debt_id"]) for r in data["debts"]],
        objects=[object_dependents(context,r["object_id"]) for r in data["objects"]],
        contracts=[contract_provenance(context,r["equation_contract_id"]) for r in data["contracts"]],
        source_refs=[dict(path=p,sha256=file_sha256(Path(root)/p)) for p in paths])
    value["projection_digest"] = digest(value)
    return value


def spark_completion_source(root: Path, side: Path, path: str):
    value = spark_completion_authority(root,side)
    row = next((r for r in value["source_refs"] if r["path"] == path),None)
    if row is None:
        raise KeyError("not an indexed spark-completion source")
    return _bound_file(Path(root),path,row["sha256"]).read_bytes(),row
