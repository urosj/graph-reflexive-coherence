"""Deterministic notebook and browser projections of accepted D11 authority."""

from __future__ import annotations

from collections import Counter
from typing import Any, Callable, cast

from .canonical import digest, record_digest
from .errors import GraphInvariantError, SourceAdmissionError
from .forensic import (
    ForensicContext,
    candidate_career,
    contract_provenance,
    debt_lifecycle,
    object_dependents,
    reconstruction_path,
)


D11_UX_BUNDLE = "ETC11D11SuccessorUXBundle.json"
D11_UX_CANDIDATE = "ETC11D11SuccessorUXCandidate.json"
D11_UX_WEB_MANIFEST = "ETC11D11UXWebBuildManifest.json"
D11_UX_BUNDLE_SCHEMA = "grcv4_explorer_ET_C11_D11_successor_UX_bundle_v1"
D11_UX_CANDIDATE_SCHEMA = "grcv4_explorer_ET_C11_D11_successor_UX_candidate_v1"
D11_UX_WEB_MANIFEST_SCHEMA = "grcv4_explorer_ET_C11_D11_UX_web_build_manifest_v1"

QUERY_OPERATIONS: dict[str, Callable[[ForensicContext, str], dict[str, Any]]] = {
    "candidate": candidate_career,
    "current_claim": reconstruction_path,
    "debt_transformation": debt_lifecycle,
    "equation_contract": contract_provenance,
    "normative_object": object_dependents,
}

PROJECTED_KINDS = {
    *QUERY_OPERATIONS,
    "profile",
    "verification_obligation",
}


def _scope(identifier: str, source_record_id: str) -> str:
    if identifier.startswith("D11-C-") or identifier.startswith("C-"):
        return "D11-C"
    if identifier.startswith("D11-G9-") or identifier.startswith("GRC9-"):
        return "D11-G9"
    if "D11-C" in source_record_id:
        return "D11-C"
    if "D11-G9" in source_record_id:
        return "D11-G9"
    raise GraphInvariantError(f"cannot classify D11 UX scope: {identifier}")


def _label(node: dict[str, Any]) -> str:
    attributes = cast(dict[str, Any], node["attributes"])
    for field in (
        "statement",
        "normative_equation_or_contract",
        "object_role",
        "reason",
        "obligation",
    ):
        value = attributes.get(field)
        if isinstance(value, str) and value:
            return value.replace("_", " ")
    return cast(str, node["identifier"]).replace("_", " ")


def _source_ref(context: ForensicContext, node: dict[str, Any]) -> dict[str, Any]:
    record_id = cast(str, node["source_record_id"])
    document = context.documents_by_record.get(record_id)
    if document is None:
        raise SourceAdmissionError(f"D11 UX node source is not admitted: {record_id}")
    return {
        "record_id": record_id,
        "record_digest": document.declared_digest,
        "source_json_pointer": node["source_json_pointer"],
        "path": document.admission["path"],
    }


def _incident_edge_refs(context: ForensicContext, node_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for edge in context.propagation_edges:
        if edge["source"] != node_id and edge["target"] != node_id:
            continue
        document = context.documents_by_record.get(cast(str, edge["source_record_id"]))
        if document is None:
            raise SourceAdmissionError(
                f"D11 UX edge source is not admitted: {edge['source_record_id']}"
            )
        rows.append(
            {
                "edge_id": edge["edge_id"],
                "source": edge["source"],
                "target": edge["target"],
                "relation": edge["relation"],
                "support_semantic": edge["support_semantic"],
                "source_record_id": edge["source_record_id"],
                "source_record_digest": document.declared_digest,
                "source_json_pointer": edge["source_json_pointer"],
            }
        )
    return sorted(rows, key=lambda row: cast(str, row["edge_id"]))


def _node_projection(context: ForensicContext, node: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "grcv4_explorer_source_bound_node_projection_v1",
        "output_class": "source_bound_graph_projection",
        "operation": "node_projection",
        "query": {"identifier": node["identifier"], "kind": node["kind"]},
        "source_bundle_digest": context.source_bundle_digest,
        "graph_digest": context.graph_digest,
        "ET_C2_record_digest": context.et_c2_record_digest,
        "authority_extension_digest": context.authority_extension_digest,
        "node": node,
        "source_ref": _source_ref(context, node),
        "edge_refs": _incident_edge_refs(context, cast(str, node["node_id"])),
        "projection_digest": None,
    }
    payload["projection_digest"] = record_digest(payload, "projection_digest")
    return payload


def build_d11_ux_bundle(
    context: ForensicContext, et_c10_admission: dict[str, Any]
) -> dict[str, Any]:
    """Compile source-exact D11 views for notebook/browser presentation."""

    if context.authority_extension_digest != et_c10_admission.get("record_digest"):
        raise SourceAdmissionError("D11 UX context is not bound to ET-C10 admission")

    d11_record_ids = (
        {
            cast(str, row["record_id"])
            for row in cast(list[dict[str, Any]], et_c10_admission["source_records"])
        }
        if "source_records" in et_c10_admission
        else {
            document.record_identifier
            for document in context.documents
            if "D11" in document.record_identifier
        }
    )
    nodes = [
        row
        for row in cast(list[dict[str, Any]], context.graph["nodes"])
        if row["kind"] in PROJECTED_KINDS and row["source_record_id"] in d11_record_ids
    ]
    nodes.sort(key=lambda row: (row["kind"], row["identifier"]))
    if len(nodes) != 69:
        raise GraphInvariantError(f"D11 UX node population drift: {len(nodes)}")

    catalog: list[dict[str, Any]] = []
    views: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_id = cast(str, node["node_id"])
        identifier = cast(str, node["identifier"])
        kind = cast(str, node["kind"])
        scope = _scope(identifier, cast(str, node["source_record_id"]))
        operation = QUERY_OPERATIONS.get(kind)
        output = (
            operation(context, identifier)
            if operation is not None
            else _node_projection(context, node)
        )
        output_digest = output.get("trace_digest") or output.get("projection_digest")
        if not isinstance(output_digest, str):
            raise GraphInvariantError(f"D11 UX output has no digest: {node_id}")
        catalog.append(
            {
                "node_id": node_id,
                "identifier": identifier,
                "kind": kind,
                "scope": scope,
                "label": _label(node),
                "source_record_id": node["source_record_id"],
                "source_json_pointer": node["source_json_pointer"],
                "operation": output["operation"],
                "output_class": output["output_class"],
                "output_digest": output_digest,
            }
        )
        views[node_id] = {
            "node": node,
            "scope": scope,
            "output": output,
        }

    counts = Counter(row["kind"] for row in catalog)
    bundle: dict[str, Any] = {
        "schema": D11_UX_BUNDLE_SCHEMA,
        "status": "candidate",
        "gate_id": "ET-C11-D11-UX",
        "authority_extension_digest": et_c10_admission["record_digest"],
        "source_identities": {
            "ET_C10_record_digest": et_c10_admission["record_digest"],
            "source_contract_digest": et_c10_admission["source_contract_digest"],
            "source_bundle_digest": context.source_bundle_digest,
            "graph_digest": context.graph_digest,
            "historical_ET_C2_graph_digest": et_c10_admission[
                "historical_ET_C2_graph_digest"
            ],
        },
        "authority": {
            "accepted_D11_authority_presented": True,
            "presentation_only": True,
            "browser_scientific_inference": False,
            "browser_propagation": False,
            "browser_rerun_prediction": False,
            "browser_claim_promotion": False,
            "notebook_duplicates_forensic_logic": False,
            "paper_propagation_verified": False,
            "specification_or_runtime_conformance_verified": False,
            "GRC9_or_GRC9V3_change_authorized": False,
        },
        "population_counts": {
            "catalog": len(catalog),
            **{kind: counts[kind] for kind in sorted(PROJECTED_KINDS)},
            "forensic_API_outputs": sum(
                row["output_class"] == "forensic_evidence_trace" for row in catalog
            ),
            "source_bound_node_projections": sum(
                row["output_class"] == "source_bound_graph_projection"
                for row in catalog
            ),
        },
        "scope_order": ["D11-C", "D11-G9"],
        "kind_order": [
            "current_claim",
            "debt_transformation",
            "profile",
            "candidate",
            "normative_object",
            "equation_contract",
            "verification_obligation",
        ],
        "catalog": catalog,
        "views": views,
        "bundle_digest": None,
    }
    bundle["bundle_digest"] = digest(
        {key: value for key, value in bundle.items() if key != "bundle_digest"}
    )
    return bundle


def validate_d11_ux_bundle(
    bundle: dict[str, Any], et_c10_admission: dict[str, Any]
) -> None:
    """Fail closed on stale, inferred, or incomplete D11 UX projections."""

    if (
        bundle.get("schema") != D11_UX_BUNDLE_SCHEMA
        or bundle.get("status") != "candidate"
    ):
        raise GraphInvariantError("D11 UX bundle schema or lifecycle drift")
    if bundle.get("bundle_digest") != digest(
        {key: value for key, value in bundle.items() if key != "bundle_digest"}
    ):
        raise GraphInvariantError("D11 UX bundle digest mismatch")
    if bundle.get("source_identities", {}).get(
        "ET_C10_record_digest"
    ) != et_c10_admission.get("record_digest"):
        raise GraphInvariantError("D11 UX bundle ET-C10 identity mismatch")
    expected = {
        "candidate": 12,
        "current_claim": 2,
        "debt_transformation": 2,
        "equation_contract": 31,
        "normative_object": 13,
        "profile": 2,
        "verification_obligation": 7,
    }
    counts = bundle.get("population_counts", {})
    if counts.get("catalog") != 69 or any(
        counts.get(kind) != count for kind, count in expected.items()
    ):
        raise GraphInvariantError("D11 UX population mismatch")
    catalog = bundle.get("catalog")
    views = bundle.get("views")
    if not isinstance(catalog, list) or not isinstance(views, dict):
        raise GraphInvariantError("D11 UX catalog/views malformed")
    node_ids = [row.get("node_id") for row in catalog]
    if len(node_ids) != len(set(node_ids)) or set(node_ids) != set(views):
        raise GraphInvariantError("D11 UX catalog/view identity mismatch")
    catalog_by_id = {row["node_id"]: row for row in catalog}
    for node_id, view in views.items():
        if view.get("node", {}).get("node_id") != node_id:
            raise GraphInvariantError(f"D11 UX view node mismatch: {node_id}")
        output = view.get("output")
        if not isinstance(output, dict):
            raise GraphInvariantError(f"D11 UX output malformed: {node_id}")
        if output.get("output_class") == "forensic_evidence_trace":
            digest_field = "trace_digest"
        elif output.get("output_class") == "source_bound_graph_projection":
            digest_field = "projection_digest"
        else:
            raise GraphInvariantError(f"D11 UX output class unknown: {node_id}")
        if output.get(digest_field) != record_digest(output, digest_field):
            raise GraphInvariantError(f"D11 UX output digest mismatch: {node_id}")
        if catalog_by_id[node_id].get("output_digest") != output[digest_field]:
            raise GraphInvariantError(f"D11 UX catalog output mismatch: {node_id}")
        if output.get("authority_extension_digest") != et_c10_admission.get(
            "record_digest"
        ):
            raise GraphInvariantError(f"D11 UX output authority mismatch: {node_id}")
    authority = bundle.get("authority", {})
    if any(
        authority.get(key) is not False
        for key in (
            "browser_scientific_inference",
            "browser_propagation",
            "browser_rerun_prediction",
            "browser_claim_promotion",
            "notebook_duplicates_forensic_logic",
            "paper_propagation_verified",
            "specification_or_runtime_conformance_verified",
            "GRC9_or_GRC9V3_change_authorized",
        )
    ):
        raise GraphInvariantError("D11 UX authority boundary widened")
