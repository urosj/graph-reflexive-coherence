"""Accepted P9-10.1a diagnostic authority, separate from native conformance.

The explicit nested successor collection preserves the pre-basin/ATC loaders
and their historical pins. It is inventoried here, never auto-admitted.
"""

from dataclasses import replace
from pathlib import Path

from .a_initializer import load_current_forensic_context as load_predecessor
from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .errors import GraphInvariantError, SourceAdmissionError
from .forensic import (
    contract_provenance,
    debt_lifecycle,
    object_dependents,
    reconstruction_path,
)
from .successor import _Overlay, _source_node_id

INV = "implementation/investigations/grc9v4-constitutive-design/"
SOURCE = INV + "decisions/p9-basin-interface/Authority.json"
ADMISSION = "P9101aBasinAdmission.json"
RECORD_ID = "GRCV4-P9-10.1a-BASIN-v1"
POLICY_ID = "grc9v4-terminal-flow-regions-v1"
CLAIM_ID = "P9-10.1a-CL-N-BASIN-001"
DEBT_ID = "P9-10.1a-DEBT-BASIN-IDENTITY"
OBJECT_ID = "P9-O-GRC9-BASIN-DIAGNOSTIC"
OBLIGATION_ID = "P9-10.1a-VO-BASIN-NATIVE"
CONTRACT_IDS = tuple(
    "P9-EC-GRC9-BASIN-" + n
    for n in ("INPUTS", "MEMBERSHIP", "SEEDS", "IDENTITY", "LIFECYCLE", "CEILING")
)
ACCEPTED_SOURCE_DIGEST = (
    "409e503e1ba880e2ab17a61f93f950e1a3e3116619561f19e70df9f0fc5eef28"
)
ACCEPTED_ADMISSION_DIGEST = (
    "b166c00b8ff646c072cb6ddc1187bc975931488f9a0f84f81a7a4ad84ada975c"
)


def _require(condition, message):
    if not condition:
        raise SourceAdmissionError(message)


def _bound_file(root, path, sha256):
    target = root / path
    _require(
        not Path(path).is_absolute()
        and ".." not in Path(path).parts
        and target.resolve().is_relative_to(root.resolve()),
        "basin source path escapes repository",
    )
    _require(file_sha256(target) == sha256, "basin bound source changed: " + path)
    return target


def build_basin_context(root: Path, side: Path):
    root, side = Path(root), Path(side)
    old = load_predecessor(root, side)
    data = load_json_object(root / SOURCE)
    _require(
        data.get("record_digest")
        == record_digest(data, "record_digest")
        == ACCEPTED_SOURCE_DIGEST,
        "basin authority is not the accepted source",
    )
    _require(
        {p.name for p in (root / SOURCE).parent.glob("*.json")} == {"Authority.json"},
        "unprocessed basin successor source",
    )
    _bound_file(root, data["design_path"], data["design_sha256"])
    ref = data["acceptance"]
    decision = load_json_object(_bound_file(root, ref["path"], ref["sha256"]))
    _require(
        decision["record_digest"]
        == record_digest(decision, "record_digest")
        == ref["record_digest"]
        and decision["status"] == "accepted_bounded_design",
        "basin design acceptance mismatch",
    )
    for subject in decision["subjects"]:
        _bound_file(root, subject["path"], subject["sha256"])
    admission_row = dict(
        source_id=RECORD_ID, path=SOURCE, file_sha256=file_sha256(root / SOURCE)
    )
    document = SourceDocument(
        filename=Path(SOURCE).name,
        path=root / SOURCE,
        data=data,
        admission=admission_row,
        adapter_kind="p9101a_basin_authority_v1",
        record_identifier=RECORD_ID,
        schema_identifier=data["schema_version"],
        digest_field="record_digest",
        semantic_index={},
    )
    overlay = _Overlay(old.graph)
    source = _source_node_id(document)
    overlay.nodes[source] = dict(
        node_id=source,
        kind="source_record",
        identifier=source.split(":", 1)[1],
        source_record_id=RECORD_ID,
        source_json_pointer="/",
        attributes={
            **admission_row,
            "source_digests": [document.declared_digest],
            "admission_layer": "P9-10.1a-basin",
        },
    )

    def node(kind, identifier, pointer, attributes):
        result = overlay.add_node(kind, identifier, document, pointer, attributes)
        overlay.add_edge(result, source, "source_identity", document, pointer)
        return result

    claim = node("current_claim", CLAIM_ID, "/claim", data["claim"])
    debt = node("debt_transformation", DEBT_ID, "/debt", data["debt"])
    obj = node("normative_object", OBJECT_ID, "/object", data["object"])
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
        overlay.add_edge(
            target,
            obj,
            "parent_object",
            document,
            pointer + "/parent_object_ids/0",
            support_semantic="required",
        )
    obligation = node(
        "verification_obligation",
        OBLIGATION_ID,
        "/verification_obligations/0",
        data["verification_obligations"][0],
    )
    overlay.add_edge(
        debt,
        obligation,
        "verification_obligation",
        document,
        "/debt/verification_obligation",
        support_semantic="not_applicable",
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
        e[k] not in overlay.nodes
        for e in overlay.propagation_edges.values()
        for k in ("source", "target")
    ):
        raise GraphInvariantError("basin authority has an unresolved graph endpoint")
    bundle = digest(
        dict(
            predecessor_source_bundle_digest=old.source_bundle_digest,
            source=document.manifest_row(),
        )
    )
    graph = dict(
        schema="grcv4_p9101a_basin_graph_v1",
        historical_graph_digest=old.graph_digest,
        source_bundle_digest=bundle,
        nodes=sorted(overlay.nodes.values(), key=lambda r: r["node_id"]),
        propagation_edges=sorted(
            overlay.propagation_edges.values(), key=lambda r: r["edge_id"]
        ),
        annotation_edges=old.graph["annotation_edges"],
    )
    graph["graph_digest"] = digest(graph)
    binding = dict(
        schema="grcv4_p9101a_basin_admission_v1",
        status="accepted_source_admission",
        source=admission_row,
        source_record_digest=document.declared_digest,
        design_path=data["design_path"],
        design_sha256=data["design_sha256"],
        design_commit=data["design_commit"],
        acceptance=ref,
        historical_authority_extension_digest=old.authority_extension_digest,
        historical_graph_digest=old.graph_digest,
        source_bundle_digest=bundle,
        graph_digest=graph["graph_digest"],
        policy_id=POLICY_ID,
        runtime_conformance_inferred=False,
        P9_10_1a_closed=False,
    )
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


def load_basin_forensic_context(root: Path, side: Path):
    context, binding = build_basin_context(root, side)
    _require(
        load_json_object(Path(side) / "records" / ADMISSION) == binding
        and binding["record_digest"] == ACCEPTED_ADMISSION_DIGEST,
        "basin admission no longer rebuilds exactly",
    )
    return context


def basin_authority(root: Path, side: Path):
    context = load_basin_forensic_context(root, side)
    data = context.documents_by_record[RECORD_ID].data
    decision = load_json_object(Path(root) / data["acceptance"]["path"])
    paths = [
        SOURCE,
        data["acceptance"]["path"],
        *[s["path"] for s in decision["subjects"]],
    ]
    output = dict(
        schema="grcv4_p9101a_basin_surface_v1",
        policy_id=POLICY_ID,
        authority_record_digest=ACCEPTED_SOURCE_DIGEST,
        authority_extension_digest=context.authority_extension_digest,
        design_accepted=True,
        native_conformance=False,
        P9_10_1a_closed=False,
        full_GRC9V4_conformance=False,
        selected_native_scope=data["selected_native_scope"],
        claim=reconstruction_path(context, CLAIM_ID),
        debt=debt_lifecycle(context, DEBT_ID),
        object=object_dependents(context, OBJECT_ID),
        contracts=[contract_provenance(context, cid) for cid in CONTRACT_IDS],
        source_refs=[dict(path=p, sha256=file_sha256(Path(root) / p)) for p in paths],
    )
    output["projection_digest"] = digest(output)
    return output


def basin_source(root: Path, side: Path, path: str):
    view = basin_authority(root, side)
    row = next((r for r in view["source_refs"] if r["path"] == path), None)
    if row is None:
        raise KeyError("not an indexed basin source")
    target = _bound_file(Path(root), path, row["sha256"])
    return target.read_bytes(), row
