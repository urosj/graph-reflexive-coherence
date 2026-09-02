"""Source-exact ET-C7 claim-ceiling and alternative projections."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, cast

from .canonical import load_json_object, record_digest
from .forensic import (
    ForensicContext,
    candidate_career,
    load_forensic_context,
    negative_claims,
    pruned_choices_at,
)


LAYER_SCHEMA = "grcv4_explorer_ET_C7_claim_ceiling_alternative_layer_v1"
LOCK_CLASSES = frozenset(
    {
        "accepted_negative_claim",
        "normative_object_blocked_overread",
        "provenance_blocked_relabel",
        "targeted_provenance_hardening",
    }
)
ALTERNATIVE_CLASSES = frozenset(
    {
        "routed_candidate",
        "conditional_claim",
        "blocked_relabel",
        "historical_claim",
        "rejected_candidate",
        "rejected_alternative",
    }
)
VISIBILITY_THRESHOLDS = {
    "routed_candidate": 20,
    "conditional_claim": 40,
    "blocked_relabel": 60,
    "historical_claim": 80,
    "rejected_candidate": 100,
    "rejected_alternative": 100,
}
REASON_TOKENS = {
    "derivation": ("derive", "derivation"),
    "contradiction": ("contradiction",),
    "routing": ("route", "routed", "routing"),
    "out_of_scope": ("out_of_scope",),
}


def _escape_pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _source_ref(
    context: ForensicContext, record_id: str, pointer: str
) -> dict[str, str]:
    document = context.documents_by_record[record_id]
    return {
        "record_id": record_id,
        "record_digest": document.declared_digest,
        "source_json_pointer": pointer,
        "path": cast(str, document.admission["path"]),
    }


def _annotation(value: str) -> dict[str, str]:
    return {
        "authority": "non_authoritative_readability_annotation",
        "text": value.replace("_", " "),
    }


def _reason_kinds(value: Any, pointer: str) -> list[dict[str, str]]:
    """Classify only reason words that are literally present in source payloads."""

    rows: list[dict[str, str]] = []
    if isinstance(value, dict) and value.get("evidence_refs"):
        rows.append(
            {
                "kind": "evidence",
                "source_json_pointer": f"{pointer}/evidence_refs",
                "source_value": "evidence_refs",
            }
        )
    text = str(value).lower()
    for kind, tokens in REASON_TOKENS.items():
        token = next((candidate for candidate in tokens if candidate in text), None)
        if token is not None:
            rows.append(
                {
                    "kind": kind,
                    "source_json_pointer": pointer,
                    "source_value": token,
                }
            )
    return rows


def _debt_boundaries(
    debt_ids: Iterable[str], transformations: dict[str, dict[str, Any]]
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for debt_id in debt_ids:
        transformation = transformations.get(debt_id)
        if transformation is None:
            continue
        if transformation.get("activation_condition"):
            rows.append(
                {
                    "boundary_kind": "activation_condition",
                    "boundary_id": cast(str, transformation["activation_condition"]),
                    "source_debt_id": debt_id,
                    "source_record_id": "GRC9V4-D10-DEBT-CLAIM-TRANSFORMATION-LEDGER-v2",
                    "source_json_pointer": f"{transformation['_source_json_pointer']}/activation_condition",
                }
            )
        if transformation.get("verification_obligation"):
            rows.append(
                {
                    "boundary_kind": "verification_obligation",
                    "boundary_id": cast(str, transformation["verification_obligation"]),
                    "source_debt_id": debt_id,
                    "source_record_id": "GRC9V4-D10-DEBT-CLAIM-TRANSFORMATION-LEDGER-v2",
                    "source_json_pointer": f"{transformation['_source_json_pointer']}/verification_obligation",
                }
            )
    return sorted(rows, key=lambda row: tuple(row.values()))


def _lock(
    *,
    lock_id: str,
    lock_class: str,
    blocked_claims: list[str],
    source_reason: str,
    source: dict[str, str],
    source_reason_ref: dict[str, str] | None = None,
    target_node_ids: list[str],
    bearing_debt_ids: list[str] | None = None,
    reopening_boundaries: list[dict[str, str]] | None = None,
    hardening: dict[str, str] | None = None,
) -> dict[str, Any]:
    if lock_class not in LOCK_CLASSES:
        raise RuntimeError(f"unknown lock class: {lock_class}")
    reason_ref = source_reason_ref or source
    return {
        "lock_id": lock_id,
        "lock_class": lock_class,
        "authority_status": "accepted_source_lock",
        "promotion_allowed": False,
        "stronger_blocked_claims": blocked_claims,
        "bearing_debt_ids": bearing_debt_ids or [],
        "source_reason": source_reason,
        "source_reason_kinds": _reason_kinds(
            {
                "source_reason": source_reason,
                "evidence_refs": source_reason
                if lock_class == "accepted_negative_claim"
                else [],
            },
            reason_ref["source_json_pointer"],
        ),
        "reopening_boundary_set": reopening_boundaries or [],
        "reopening_boundary_status": (
            "source_named" if reopening_boundaries else "not_source_named"
        ),
        "target_node_ids": target_node_ids,
        "hardening": hardening,
        "readable_annotation": _annotation(source_reason),
        "source": source,
        "source_reason_ref": reason_ref,
    }


def _alternative(
    *,
    alternative_id: str,
    alternative_class: str,
    immutable_status: str,
    label: str,
    source: dict[str, str],
    target_node_id: str | None,
    payload: Any,
) -> dict[str, Any]:
    if alternative_class not in ALTERNATIVE_CLASSES:
        raise RuntimeError(f"unknown alternative class: {alternative_class}")
    return {
        "alternative_id": alternative_id,
        "alternative_class": alternative_class,
        "immutable_status": immutable_status,
        "label": label,
        "target_node_id": target_node_id,
        "payload": payload,
        "visibility_threshold": VISIBILITY_THRESHOLDS[alternative_class],
        "presentation_order_semantic": "staged_disclosure_not_rank_priority_or_evidence_strength",
        "ghost_style_required": True,
        "promotion_allowed": False,
        "source": source,
    }


def build_claim_ceiling_layer(
    repo_root: Path, side_tool_root: Path
) -> dict[str, Any]:
    """Compile I7 locks and ghosts without changing accepted graph authority."""

    context = load_forensic_context(repo_root, side_tool_root)
    records = side_tool_root / "records"
    et_c6 = load_json_object(records / "ETC6StaticNavigationSurface.json")
    if et_c6.get("status") != "accepted" or et_c6.get("record_digest") != record_digest(
        et_c6, "record_digest"
    ):
        raise RuntimeError("accepted ET-C6 predecessor is unavailable")

    topology_doc = context.documents_by_record["GRC9V4-D10-CLAIM-TOPOLOGY-v2"]
    topology = topology_doc.data
    ledger_doc = context.documents_by_record[
        "GRC9V4-D10-DEBT-CLAIM-TRANSFORMATION-LEDGER-v2"
    ]
    ledger = ledger_doc.data
    provenance_doc = context.documents_by_record["GRC9V4-CD-D10.2-v1"]
    provenance = provenance_doc.data
    transformations = {
        row["debt_id"]: {**row, "_source_json_pointer": f"/debt_transformations/{index}"}
        for index, row in enumerate(ledger["debt_transformations"])
    }

    locks: list[dict[str, Any]] = []
    for index, claim in enumerate(topology["claims"]):
        if claim.get("claim_class") != "negative":
            continue
        claim_id = cast(str, claim["claim_id"])
        source = _source_ref(
            context, topology_doc.record_identifier, f"/claims/{index}"
        )
        locks.append(
            _lock(
                lock_id=f"negative:{claim_id}",
                lock_class="accepted_negative_claim",
                blocked_claims=list(claim["blocked_relabels"]),
                bearing_debt_ids=list(claim["bearing_debt_ids"]),
                source_reason=cast(str, claim["statement"]),
                reopening_boundaries=_debt_boundaries(
                    claim["bearing_debt_ids"], transformations
                ),
                target_node_ids=[f"current_claim:{claim_id}"],
                source=source,
            )
        )

    for index, value in enumerate(provenance["normatively_load_bearing_objects"]):
        object_id = cast(str, value["object_id"])
        overread = cast(str, value["blocked_overread"])
        locks.append(
            _lock(
                lock_id=f"object_overread:{object_id}",
                lock_class="normative_object_blocked_overread",
                blocked_claims=[overread],
                source_reason=overread,
                target_node_ids=[f"normative_object:{object_id}"],
                source=_source_ref(
                    context,
                    provenance_doc.record_identifier,
                    f"/normatively_load_bearing_objects/{index}/blocked_overread",
                ),
            )
        )

    common_reopening = [
        {
            "boundary_kind": "future_profile_rule",
            "boundary_id": cast(str, provenance["promotion_result"]["future_profile_rule"]),
            "source_debt_id": "not_applicable",
            "source_record_id": provenance_doc.record_identifier,
            "source_json_pointer": "/promotion_result/future_profile_rule",
        }
    ]
    for index, relabel in enumerate(provenance["blocked_relabels"]):
        locks.append(
            _lock(
                lock_id=f"provenance_relabel:{index}",
                lock_class="provenance_blocked_relabel",
                blocked_claims=[cast(str, relabel)],
                source_reason=cast(str, provenance["claim_ceiling"]),
                reopening_boundaries=common_reopening,
                target_node_ids=["gate_record:GRC9V4-CD-D10.2-v1"],
                source=_source_ref(
                    context,
                    provenance_doc.record_identifier,
                    f"/blocked_relabels/{index}",
                ),
                source_reason_ref=_source_ref(
                    context,
                    provenance_doc.record_identifier,
                    "/claim_ceiling",
                ),
            )
        )

    for key in sorted(provenance["targeted_type_and_provenance_hardening"]):
        value = cast(str, provenance["targeted_type_and_provenance_hardening"][key])
        targets = ["gate_record:GRC9V4-CD-D10.2-v1"]
        if key.startswith("Candidate_A_"):
            targets.append("candidate:V4-A-temporalized-W")
        boundary = common_reopening if "reopening" in value else []
        locks.append(
            _lock(
                lock_id=f"hardening:{key}",
                lock_class="targeted_provenance_hardening",
                blocked_claims=[value],
                source_reason=value,
                reopening_boundaries=boundary,
                target_node_ids=targets,
                hardening={"key": key, "machine_value": value},
                source=_source_ref(
                    context,
                    provenance_doc.record_identifier,
                    f"/targeted_type_and_provenance_hardening/{_escape_pointer(key)}",
                ),
            )
        )

    alternatives: list[dict[str, Any]] = []
    b_career = candidate_career(context, "V4-B-independent-derived-carrier")
    b_source = next(
        row["source_ref"]
        for row in b_career["rows"]
        if row["row_id"].startswith("GRC9V4-CD-D7V2-v1:")
    )
    alternatives.append(
        _alternative(
            alternative_id="routed:V4-B-independent-derived-carrier",
            alternative_class="routed_candidate",
            immutable_status="routed_not_rejected_no_lifecycle_profile",
            label="Candidate B / routed, not rejected",
            source=b_source,
            target_node_id="candidate:V4-B-independent-derived-carrier",
            payload={"candidate_id": "V4-B-independent-derived-carrier"},
        )
    )

    for index, claim in enumerate(topology["claims"]):
        if claim.get("claim_class") != "conditional":
            continue
        claim_id = cast(str, claim["claim_id"])
        alternatives.append(
            _alternative(
                alternative_id=f"conditional:{claim_id}",
                alternative_class="conditional_claim",
                immutable_status="accepted_conditional_claim",
                label=cast(str, claim["statement"]),
                source=_source_ref(
                    context, topology_doc.record_identifier, f"/claims/{index}"
                ),
                target_node_id=f"current_claim:{claim_id}",
                payload=claim,
            )
        )

    for index, claim in enumerate(topology["historical_claim_nodes"]):
        claim_id = cast(str, claim["claim_id"])
        alternatives.append(
            _alternative(
                alternative_id=f"historical:{claim_id}",
                alternative_class="historical_claim",
                immutable_status="historical_not_current_authority",
                label=cast(str, claim["statement"]),
                source=_source_ref(
                    context,
                    topology_doc.record_identifier,
                    f"/historical_claim_nodes/{index}",
                ),
                target_node_id=f"historical_claim:{claim_id}",
                payload=claim,
            )
        )

    d1_trace = pruned_choices_at(context, "GRC9V4-CD-D1-v1")
    for row in d1_trace["rows"]:
        if row["classification"] == "resolved_negative_uninstantiated_slot":
            alternatives.append(
                _alternative(
                    alternative_id="rejected:V4-D-source-admitted-structural",
                    alternative_class="rejected_candidate",
                    immutable_status="resolved_negative_uninstantiated_slot",
                    label="V4-D / closed uninstantiated admission slot",
                    source=row["source_ref"],
                    target_node_id="candidate:V4-D-source-admitted-structural",
                    payload=row["payload"],
                )
            )
        elif row["classification"] == "pruned_alternative":
            payload = cast(dict[str, Any], row["payload"])
            alternatives.append(
                _alternative(
                    alternative_id=f"rejected_alternative:{row['row_id']}",
                    alternative_class="rejected_alternative",
                    immutable_status="source_pruned_alternative",
                    label=cast(str, payload["alternative"]),
                    source=row["source_ref"],
                    target_node_id="gate_record:GRC9V4-CD-D1-v1",
                    payload=payload,
                )
            )

    blocked_seen: set[tuple[str, str]] = set()
    for lock in locks:
        for index, relabel in enumerate(lock["stronger_blocked_claims"]):
            key = (cast(str, relabel), cast(str, lock["source"]["record_id"]))
            if key in blocked_seen:
                continue
            blocked_seen.add(key)
            alternatives.append(
                _alternative(
                    alternative_id=f"blocked:{lock['lock_id']}:{index}",
                    alternative_class="blocked_relabel",
                    immutable_status="accepted_blocked_relabel",
                    label=cast(str, relabel),
                    source=lock["source"],
                    target_node_id=lock["target_node_ids"][0],
                    payload={"lock_id": lock["lock_id"], "blocked_relabel": relabel},
                )
            )

    et_c4 = load_json_object(records / "ETC4CounterfactualScenarioReport.json")
    c1 = next(row for row in et_c4["scenarios"] if row["scenario_id"] == "C1")
    b_result = c1["result"]["structural_result"]
    candidate_careers = {
        "V4-A-temporalized-W": candidate_career(
            context, "V4-A-temporalized-W"
        ),
        "V4-B-independent-derived-carrier": b_career,
        "V4-C-constitutive-C-sector": candidate_career(
            context, "V4-C-constitutive-C-sector"
        ),
    }
    layer: dict[str, Any] = {
        "schema": LAYER_SCHEMA,
        "status": "accepted",
        "authority": {
            "source_classification_immutable": True,
            "browser_scientific_inference": False,
            "browser_propagation": False,
            "browser_scenario_serialization": False,
            "ghost_promotion": False,
            "slider_changes_presentation_only": True,
            "hidden_score_or_ranking": False,
        },
        "predecessor": {
            "gate_id": et_c6["gate_id"],
            "record_digest": et_c6["record_digest"],
            "static_bundle_digest": et_c6["compiled_surface"]["static_bundle_digest"],
        },
        "source_identities": {
            "source_bundle_digest": context.source_bundle_digest,
            "graph_digest": context.graph_digest,
            "D10_claim_topology_digest": topology_doc.declared_digest,
            "D10_debt_ledger_digest": ledger_doc.declared_digest,
            "D10_2_provenance_digest": provenance_doc.declared_digest,
            "ET_C4_report_digest": et_c4["report_digest"],
        },
        "lock_classes": sorted(LOCK_CLASSES),
        "alternative_classes": sorted(ALTERNATIVE_CLASSES),
        "visibility_contract": {
            "range": [0, 100],
            "thresholds": VISIBILITY_THRESHOLDS,
            "semantic": "staged_disclosure_not_rank_priority_evidence_strength_or_acceptance",
            "ghost_style": "dashed_outline_plus_pattern_marker_at_every_nonzero_opacity",
        },
        "locks": sorted(locks, key=lambda row: row["lock_id"]),
        "alternatives": sorted(
            alternatives, key=lambda row: row["alternative_id"]
        ),
        "candidate_careers": candidate_careers,
        "candidate_B_readmission": {
            "current_status": "routed_not_rejected",
            "earliest_counterfactual_reexecution_gate_ids": b_result[
                "earliest_gates_to_reopen"
            ],
            "source_recorded_missing_work": b_result["source_recorded_missing_work"],
            "accepted_route_boundary": "derive_and_admit_U_B_then_reopen_D2_through_D9_for_B",
            "outcome_status": "open_work_not_promised_success",
            "source_scenario_id": "C1",
            "source_result_digest": c1["result"]["result_digest"],
        },
        "authority_populations": {
            "current_debt_transformations": len(ledger["debt_transformations"]),
            "verification_obligations": len(ledger["verification_obligations"]),
            "historical_claims": len(topology["historical_claim_nodes"]),
            "classification": "separate_populations_not_priority_or_current_blocker_score",
        },
        "population_counts": {
            "locks": len(locks),
            "alternatives": len(alternatives),
            "negative_claims": sum(
                row["lock_class"] == "accepted_negative_claim" for row in locks
            ),
            "object_blocked_overreads": sum(
                row["lock_class"] == "normative_object_blocked_overread"
                for row in locks
            ),
            "provenance_blocked_relabels": sum(
                row["lock_class"] == "provenance_blocked_relabel" for row in locks
            ),
            "targeted_hardenings": sum(
                row["lock_class"] == "targeted_provenance_hardening" for row in locks
            ),
        },
        "layer_digest": None,
    }
    layer["layer_digest"] = record_digest(layer, "layer_digest")
    return layer
