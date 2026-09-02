"""Canonical scenarios and precomputed profile-local ripple rows for ET-C5."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, cast

from .canonical import canonical_bytes, digest, load_json_object, record_digest
from .counterfactual import (
    CONFORMANCE_FIXTURE_ID,
    RESULT_CLASS,
    RESULT_SCHEMA,
    evaluate_mutation,
    load_counterfactual_context,
)
from .errors import RippleCompilationError, ScenarioValidationError, SourceAdmissionError
from .forensic import ForensicContext


SCENARIO_SCHEMA = "grcv4_exploratory_scenario_v1"
RIPPLE_SCHEMA = "grcv4_explorer_ET_C5_profile_ripple_v1"
SHARD_SCHEMA = "grcv4_explorer_ET_C5_ripple_shard_v1"
INDEX_SCHEMA = "grcv4_explorer_ET_C5_ripple_index_v1"
AGGREGATE_SCHEMA = "grcv4_explorer_ET_C5_all_profiles_aggregate_v1"
SCENARIO_BUNDLE_SCHEMA = "grcv4_explorer_ET_C5_scenario_bundle_v1"
PROFILE_INDEPENDENT = "__profile_independent__"
ET_C4_GATE_SCHEMA = "grcv4_explorer_ET_C4_bounded_counterfactual_admission_v1"
ET_C4_REPORT_SCHEMA = "grcv4_explorer_ET_C4_counterfactual_scenarios_v1"

A_CANDIDATE = "V4-A-temporalized-W"
C_CANDIDATE = "V4-C-constitutive-C-sector"
PROFILE_CANDIDATES = {"A": A_CANDIDATE, "C": C_CANDIDATE}

SCENARIO_FIELDS = {
    "schema_version",
    "kernel_schema_version",
    "scenario_id",
    "source_scenario_id",
    "source_bundle_digest",
    "graph_digest",
    "baseline_record_id",
    "baseline_record_digest",
    "profile_id",
    "candidate_ids",
    "realization_ids",
    "mutations",
    "source_result_digest",
    "result_class",
    "scenario_digest",
}


@dataclass(frozen=True)
class RippleContext:
    """Accepted ET-C4 scenarios over a revalidated ET-C2 graph."""

    forensic: ForensicContext
    et_c4_gate: dict[str, Any]
    et_c4_report: dict[str, Any]
    source_scenarios: dict[str, dict[str, Any]]
    edges_by_id: dict[str, dict[str, Any]]


def _edge_ref(context: RippleContext, edge: dict[str, Any]) -> dict[str, Any]:
    record_id = cast(str, edge["source_record_id"])
    source = context.forensic.documents_by_record[record_id]
    return {
        "edge_id": edge["edge_id"],
        "source": edge["source"],
        "target": edge["target"],
        "relation": edge["relation"],
        "support_semantic": edge["support_semantic"],
        "source_record_id": record_id,
        "source_record_digest": source.declared_digest,
        "source_json_pointer": edge["source_json_pointer"],
    }


def _require_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(row, str) for row in value):
        raise ScenarioValidationError(f"{field}_must_be_a_string_list")
    if value != sorted(set(value)):
        raise ScenarioValidationError(f"{field}_must_be_sorted_and_unique")
    return cast(list[str], value)


def load_ripple_context(repo_root: Path, side_tool_root: Path) -> RippleContext:
    """Load ET-C4 and revalidate every accepted mutation/result pair."""

    records = side_tool_root / "records"
    gate = load_json_object(records / "ETC4BoundedCounterfactualKernel.json")
    if gate.get("schema") != ET_C4_GATE_SCHEMA or gate.get("status") != "accepted":
        raise SourceAdmissionError("ET-C4 is not accepted")
    if gate.get("record_digest") != record_digest(gate, "record_digest"):
        raise SourceAdmissionError("ET-C4 gate digest mismatch")
    if gate.get("authority", {}).get("iteration_5_authorized") is not True:
        raise SourceAdmissionError("ET-C4 does not authorize Iteration 5")

    report = load_json_object(records / "ETC4CounterfactualScenarioReport.json")
    if report.get("schema") != ET_C4_REPORT_SCHEMA or report.get("status") != "accepted":
        raise SourceAdmissionError("ET-C4 scenario report is not accepted")
    if report.get("report_digest") != record_digest(report, "report_digest"):
        raise SourceAdmissionError("ET-C4 scenario report digest mismatch")
    if (
        gate.get("counterfactual_surface", {}).get("scenario_report_digest")
        != report["report_digest"]
    ):
        raise SourceAdmissionError("ET-C4 gate/report binding mismatch")

    forensic = load_counterfactual_context(repo_root, side_tool_root)
    if (
        report.get("source_bundle_digest") != forensic.source_bundle_digest
        or report.get("graph_digest") != forensic.graph_digest
    ):
        raise SourceAdmissionError("ET-C4 no longer matches ET-C2 authority")
    source_scenarios = {
        cast(str, row["scenario_id"]): row for row in report.get("scenarios", [])
    }
    if len(source_scenarios) != report.get("scenario_count"):
        raise SourceAdmissionError("ET-C4 scenario IDs are not unique")
    for scenario_id, row in source_scenarios.items():
        result = row.get("result")
        if not isinstance(result, dict):
            raise SourceAdmissionError(f"ET-C4 result missing: {scenario_id}")
        if result.get("schema") != RESULT_SCHEMA:
            raise SourceAdmissionError(f"ET-C4 result schema mismatch: {scenario_id}")
        if result.get("result_digest") != record_digest(result, "result_digest"):
            raise SourceAdmissionError(f"ET-C4 result digest mismatch: {scenario_id}")
        fixture = result.get("mutation", {}).get("target_id") == CONFORMANCE_FIXTURE_ID
        rebuilt = evaluate_mutation(
            forensic, cast(dict[str, Any], result["mutation"]), conformance_fixture=fixture
        )
        if canonical_bytes(rebuilt) != canonical_bytes(result):
            raise SourceAdmissionError(f"ET-C4 result no longer rebuilds: {scenario_id}")
    return RippleContext(
        forensic=forensic,
        et_c4_gate=gate,
        et_c4_report=report,
        source_scenarios=source_scenarios,
        edges_by_id={
            cast(str, row["edge_id"]): row for row in forensic.propagation_edges
        },
    )


def _known_profiles(context: RippleContext) -> dict[str, dict[str, Any]]:
    return {
        cast(str, row["identifier"]): cast(dict[str, Any], row["attributes"])
        for row in context.forensic.nodes.values()
        if row["kind"] == "profile"
    }


def _target_node(context: RippleContext, mutation: dict[str, Any]) -> dict[str, Any] | None:
    return context.forensic.nodes.get(
        f"{mutation['target_kind']}:{mutation['target_id']}"
    )


def _is_common_contract(attributes: dict[str, Any]) -> bool:
    return (
        not attributes.get("profile_ids")
        and (
            "common" in str(attributes.get("specification_destination", ""))
            or str(attributes.get("contract_scope", "")).startswith("parent_")
            or "specification_meta" in str(attributes.get("substrate_disposition", ""))
        )
    )


def resolve_profiles(
    context: RippleContext, mutation: dict[str, Any], result: dict[str, Any]
) -> list[str]:
    """Resolve profile scope from accepted profile rows, never family counts."""

    known = _known_profiles(context)
    declared = _require_string_list(mutation.get("profile_scope"), "profile_scope")
    node = _target_node(context, mutation)
    if node is None:
        if mutation.get("target_id") == CONFORMANCE_FIXTURE_ID and (
            "no_propagation_bearing_effect" in result.get("result_statuses", [])
        ):
            return [PROFILE_INDEPENDENT]
        raise RippleCompilationError("target_is_not_in_the_accepted_graph")
    attributes = cast(dict[str, Any], node["attributes"])
    source_profiles = set(cast(list[str], attributes.get("profile_ids", [])))
    source_profiles.update(
        cast(str, edge["target"]).split(":", 1)[1]
        for edge in context.forensic.propagation_edges
        if edge["source"] == node["node_id"]
        and edge["relation"] == "active_in_profile"
    )
    if source_profiles:
        if not declared or not set(declared) <= source_profiles:
            raise RippleCompilationError("declared_profile_scope_exceeds_source_scope")
        resolved = declared
    elif declared:
        if not _is_common_contract(attributes) or not set(declared) <= set(known):
            raise RippleCompilationError("empty_source_scope_is_not_explicit_common")
        resolved = declared
    elif mutation.get("target_kind") in {"gate_record", "candidate"} and result.get(
        "structural_result", {}
    ).get("earliest_gates_to_reopen"):
        resolved = [PROFILE_INDEPENDENT]
    else:
        raise RippleCompilationError("empty_profile_scope_is_unresolved")
    for profile_id in resolved:
        if profile_id == PROFILE_INDEPENDENT:
            continue
        row = known.get(profile_id)
        if row is None or not row.get("V3_reduction") or not row.get("candidate"):
            raise RippleCompilationError("profile_lacks_disabled_reduction_identity")
    return sorted(resolved)


def _local_candidates(
    context: RippleContext, mutation: dict[str, Any], profile_id: str
) -> list[str]:
    declared = set(_require_string_list(mutation.get("candidate_scope"), "candidate_scope"))
    if profile_id == PROFILE_INDEPENDENT:
        return sorted(declared)
    profile = _known_profiles(context)[profile_id]
    candidate = PROFILE_CANDIDATES.get(str(profile.get("candidate")))
    if candidate is None or candidate not in declared:
        raise RippleCompilationError("profile_candidate_is_outside_mutation_scope")
    return [candidate]


def _local_realizations(mutation: dict[str, Any], profile_id: str) -> list[str]:
    declared = _require_string_list(mutation.get("realization_scope"), "realization_scope")
    if not declared or profile_id == PROFILE_INDEPENDENT:
        return declared
    matched = [row for row in declared if profile_id.replace("_", "-") in row]
    if not matched and len(declared) == 1:
        matched = declared
    if not matched:
        raise RippleCompilationError("realization_scope_cannot_be_localized")
    return matched


def make_scenario(
    context: RippleContext, source_scenario_id: str, profile_id: str
) -> dict[str, Any]:
    """Create one canonical profile-local scenario from an accepted ET-C4 row."""

    source = context.source_scenarios.get(source_scenario_id)
    if source is None:
        raise ScenarioValidationError("source_scenario_is_not_accepted")
    result = cast(dict[str, Any], source["result"])
    mutation = cast(dict[str, Any], result["mutation"])
    profiles = resolve_profiles(context, mutation, result)
    if profile_id not in profiles:
        raise ScenarioValidationError("profile_is_outside_resolved_scope")
    scenario: dict[str, Any] = {
        "schema_version": SCENARIO_SCHEMA,
        "kernel_schema_version": RESULT_SCHEMA,
        "scenario_id": f"ET-C5-{source_scenario_id}-{profile_id}",
        "source_scenario_id": source_scenario_id,
        "source_bundle_digest": context.forensic.source_bundle_digest,
        "graph_digest": context.forensic.graph_digest,
        "baseline_record_id": mutation["baseline_record_id"],
        "baseline_record_digest": mutation["baseline_record_digest"],
        "profile_id": profile_id,
        "candidate_ids": _local_candidates(context, mutation, profile_id),
        "realization_ids": _local_realizations(mutation, profile_id),
        "mutations": [mutation],
        "source_result_digest": result["result_digest"],
        "result_class": RESULT_CLASS,
        "scenario_digest": None,
    }
    scenario["scenario_digest"] = digest(
        {key: value for key, value in scenario.items() if key != "scenario_digest"}
    )
    validate_scenario(context, scenario)
    return scenario


def validate_scenario(context: RippleContext, scenario: dict[str, Any]) -> None:
    """Require exact canonical identity with one accepted precomputed mutation."""

    if set(scenario) != SCENARIO_FIELDS:
        raise ScenarioValidationError("scenario_fields_mismatch")
    if scenario.get("schema_version") != SCENARIO_SCHEMA:
        raise ScenarioValidationError("scenario_schema_not_admitted")
    if scenario.get("kernel_schema_version") != RESULT_SCHEMA:
        raise ScenarioValidationError("kernel_schema_not_admitted")
    if scenario.get("result_class") != RESULT_CLASS:
        raise ScenarioValidationError("result_class_not_admitted")
    if scenario.get("source_bundle_digest") != context.forensic.source_bundle_digest:
        raise ScenarioValidationError("source_bundle_is_stale")
    if scenario.get("graph_digest") != context.forensic.graph_digest:
        raise ScenarioValidationError("graph_identity_is_stale")
    if scenario.get("scenario_digest") != record_digest(scenario, "scenario_digest"):
        raise ScenarioValidationError("scenario_digest_mismatch")
    source_id = scenario.get("source_scenario_id")
    source = context.source_scenarios.get(source_id)
    if source is None:
        raise ScenarioValidationError("source_scenario_is_not_accepted")
    result = cast(dict[str, Any], source["result"])
    mutations = scenario.get("mutations")
    if not isinstance(mutations, list) or len(mutations) != 1:
        raise ScenarioValidationError("exactly_one_precomputed_mutation_is_required")
    mutation = cast(dict[str, Any], result["mutation"])
    if canonical_bytes(mutations[0]) != canonical_bytes(mutation):
        raise ScenarioValidationError("browser_authored_or_altered_mutation")
    if scenario.get("source_result_digest") != result.get("result_digest"):
        raise ScenarioValidationError("source_result_identity_is_stale")
    if (
        scenario.get("baseline_record_id") != mutation.get("baseline_record_id")
        or scenario.get("baseline_record_digest")
        != mutation.get("baseline_record_digest")
    ):
        raise ScenarioValidationError("baseline_identity_mismatch")
    profile_id = scenario.get("profile_id")
    profiles = resolve_profiles(context, mutation, result)
    if profile_id not in profiles:
        raise ScenarioValidationError("profile_is_outside_resolved_scope")
    if scenario.get("candidate_ids") != _local_candidates(context, mutation, profile_id):
        raise ScenarioValidationError("candidate_scope_mismatch")
    if scenario.get("realization_ids") != _local_realizations(mutation, profile_id):
        raise ScenarioValidationError("realization_scope_mismatch")
    if scenario.get("scenario_id") != f"ET-C5-{source_id}-{profile_id}":
        raise ScenarioValidationError("scenario_id_mismatch")


def load_scenario_bytes(context: RippleContext, payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ScenarioValidationError("scenario_is_not_valid_JSON") from error
    if not isinstance(value, dict):
        raise ScenarioValidationError("scenario_root_is_not_an_object")
    scenario = cast(dict[str, Any], value)
    validate_scenario(context, scenario)
    if payload != canonical_bytes(scenario) + b"\n":
        raise ScenarioValidationError("scenario_bytes_are_not_canonical")
    return scenario


def scenario_bytes(scenario: dict[str, Any]) -> bytes:
    return canonical_bytes(scenario) + b"\n"


def _node_for_identifier(context: RippleContext, identifier: str) -> str | None:
    for kind in (
        "current_claim",
        "historical_claim",
        "debt_transformation",
        "gate_record",
        "verification_obligation",
        "candidate",
        "profile",
        "realization",
        "equation_contract",
        "normative_object",
    ):
        node_id = f"{kind}:{identifier}"
        if node_id in context.forensic.nodes:
            return node_id
    return None


def _witness_edges(
    context: RippleContext,
    identifier: str,
    *,
    preferred_edge_ids: Iterable[str] = (),
    fallback_node_id: str | None = None,
) -> list[dict[str, Any]]:
    preferred = [
        context.edges_by_id[edge_id]
        for edge_id in sorted(set(preferred_edge_ids))
        if edge_id in context.edges_by_id
    ]
    if preferred:
        return [_edge_ref(context, preferred[0])]
    node_id = _node_for_identifier(context, identifier) or fallback_node_id
    rows = [
        row
        for row in context.forensic.propagation_edges
        if node_id is not None and (row["source"] == node_id or row["target"] == node_id)
    ]
    if not rows:
        raise RippleCompilationError(f"consequence_has_no_source_edge:{identifier}")
    rows.sort(
        key=lambda row: (
            row["relation"] != "source_identity",
            cast(str, row["edge_id"]),
        )
    )
    return [_edge_ref(context, rows[0])]


def _claim_edge_ids(result: dict[str, Any], claim_id: str) -> list[str]:
    for witness in result.get("structural_result", {}).get(
        "claim_predicate_witnesses", []
    ):
        if witness.get("claim_id") == claim_id:
            return cast(list[str], witness.get("contract_support_edge_ids", []))
    return []


def _consequence(
    *,
    category: str,
    identifier: Any,
    source_edge_refs: list[dict[str, Any]],
    authority: str,
) -> dict[str, Any]:
    if not source_edge_refs:
        raise RippleCompilationError("every_consequence_requires_a_source_edge")
    row: dict[str, Any] = {
        "category": category,
        "identifier": identifier,
        "authority": authority,
        "source_edge_refs": source_edge_refs,
        "consequence_digest": None,
    }
    row["consequence_digest"] = digest(
        {key: value for key, value in row.items() if key != "consequence_digest"}
    )
    return row


def _scope_basis(
    context: RippleContext,
    scenario: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    profile_id = cast(str, scenario["profile_id"])
    if profile_id == PROFILE_INDEPENDENT:
        reduction = "profile_independent_source_recorded_reopening_boundary"
    else:
        reduction = _known_profiles(context)[profile_id]["V3_reduction"]
    activation_conditions = sorted(
        [
            {
                "claim_id": witness["claim_id"],
                "activation_condition": witness.get("activation_condition"),
                "predicate_disposition": witness.get("predicate_disposition"),
            }
            for witness in result.get("structural_result", {}).get(
                "claim_predicate_witnesses", []
            )
        ],
        key=lambda row: row["claim_id"],
    )
    return {
        "profile_id": profile_id,
        "disabled_reduction_or_independent_boundary": reduction,
        "candidate_ids": scenario["candidate_ids"],
        "realization_ids": scenario["realization_ids"],
        "claim_activation_conditions_consulted": activation_conditions,
        "D10_2_family_counts_used": False,
    }


def compile_ripple_row(
    context: RippleContext, scenario: dict[str, Any]
) -> dict[str, Any] | None:
    """Compile one immutable scenario into one profile-local playback row."""

    validate_scenario(context, scenario)
    source = context.source_scenarios[cast(str, scenario["source_scenario_id"])]
    result = cast(dict[str, Any], source["result"])
    if "no_propagation_bearing_effect" in result["result_statuses"]:
        return None
    structural = cast(dict[str, Any], result["structural_result"])
    target_node = _target_node(context, cast(dict[str, Any], result["mutation"]))
    fallback = cast(str, target_node["node_id"]) if target_node is not None else None

    direct = [
        _consequence(
            category="direct_source_relation",
            identifier={
                "relation": edge["relation"],
                "source": edge["source"],
                "target": edge["target"],
            },
            source_edge_refs=[edge],
            authority="accepted_source_edge",
        )
        for edge in structural.get("source_edge_refs", [])
    ]
    transitive: list[dict[str, Any]] = []
    categories = (
        "claims_invalidated",
        "claims_requiring_reexecution",
        "debts_reactivated",
        "negative_claims_activated",
        "routes_changed",
        "earliest_gates_to_reopen",
        "known_through_evidence_frontier",
        "unknown_beyond_evidence_frontier",
    )
    for category in categories:
        for identifier in structural.get(category, []):
            preferred = (
                _claim_edge_ids(result, identifier)
                if category.startswith("claims_")
                or category in {
                    "negative_claims_activated",
                    "known_through_evidence_frontier",
                }
                else []
            )
            transitive.append(
                _consequence(
                    category=category,
                    identifier=identifier,
                    source_edge_refs=_witness_edges(
                        context,
                        cast(str, identifier),
                        preferred_edge_ids=preferred,
                        fallback_node_id=fallback,
                    ),
                    authority="accepted_structural_projection",
                )
            )
    for missing in structural.get("source_recorded_missing_work", []):
        transitive.append(
            _consequence(
                category="source_recorded_missing_work",
                identifier=missing,
                source_edge_refs=_witness_edges(
                    context, "missing_work", fallback_node_id=fallback
                ),
                authority="accepted_source_route",
            )
        )
    blocked = [
        _consequence(
            category="blocked_overread_at_risk",
            identifier=value,
            source_edge_refs=_witness_edges(
                context, cast(str, value), fallback_node_id=fallback
            ),
            authority="risk_only_not_activated_claim",
        )
        for value in structural.get("blocked_overreads_at_risk", [])
    ]
    obligations = [
        _consequence(
            category="verification_obligation_at_risk",
            identifier=value,
            source_edge_refs=_witness_edges(context, cast(str, value)),
            authority="forward_work_only_not_evidence_or_debt",
        )
        for value in structural.get("verification_obligations_at_risk", [])
    ]
    key = {
        "target_id": result["mutation"]["target_id"],
        "target_kind": result["mutation"]["target_kind"],
        "mutation_id": result["mutation"]["mutation_id"],
        "profile_id": scenario["profile_id"],
        "candidate_ids": scenario["candidate_ids"],
        "realization_ids": scenario["realization_ids"],
        "baseline_record_id": scenario["baseline_record_id"],
        "baseline_record_digest": scenario["baseline_record_digest"],
    }
    row: dict[str, Any] = {
        "schema": RIPPLE_SCHEMA,
        "ripple_key": key,
        "scenario": scenario,
        "scenario_digest": scenario["scenario_digest"],
        "source_result_digest": result["result_digest"],
        "source_bundle_digest": context.forensic.source_bundle_digest,
        "graph_digest": context.forensic.graph_digest,
        "result_class": RESULT_CLASS,
        "result_statuses": result["result_statuses"],
        "scope_basis": _scope_basis(context, scenario, result),
        "direct_consequences": sorted(direct, key=lambda item: item["consequence_digest"]),
        "transitive_consequences": sorted(
            transitive, key=lambda item: (item["category"], str(item["identifier"]))
        ),
        "blocked_overreads_at_risk": sorted(
            blocked, key=lambda item: item["consequence_digest"]
        ),
        "verification_obligations_at_risk": sorted(
            obligations, key=lambda item: item["consequence_digest"]
        ),
        "browser_may_recompute": False,
        "ripple_digest": None,
    }
    row["ripple_digest"] = record_digest(row, "ripple_digest")
    return row


def serialize_selected_row(context: RippleContext, row: dict[str, Any]) -> bytes:
    """Read back the immutable scenario embedded in one verified ripple row."""

    if row.get("schema") != RIPPLE_SCHEMA:
        raise ScenarioValidationError("ripple_schema_not_admitted")
    if row.get("ripple_digest") != record_digest(row, "ripple_digest"):
        raise ScenarioValidationError("ripple_digest_mismatch")
    if row.get("browser_may_recompute") is not False:
        raise ScenarioValidationError("browser_recomputation_authority_forbidden")
    scenario = cast(dict[str, Any], row.get("scenario"))
    validate_scenario(context, scenario)
    return scenario_bytes(scenario)


def row_sort_key(row: dict[str, Any]) -> tuple[str, str, str]:
    key = cast(dict[str, Any], row["ripple_key"])
    return (
        cast(str, key["target_id"]),
        cast(str, key["profile_id"]),
        cast(str, row["scenario_digest"]),
    )


def aggregate_rows(context: RippleContext, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Project the complete local-row population; never infer additional rows."""

    ordered = sorted(rows, key=row_sort_key)
    profile_counts: dict[str, int] = {}
    for row in ordered:
        profile = cast(str, row["ripple_key"]["profile_id"])
        profile_counts[profile] = profile_counts.get(profile, 0) + 1
    aggregate: dict[str, Any] = {
        "schema": AGGREGATE_SCHEMA,
        "source_bundle_digest": context.forensic.source_bundle_digest,
        "graph_digest": context.forensic.graph_digest,
        "projection_only": True,
        "row_count": len(ordered),
        "scenario_count": len({row["scenario_digest"] for row in ordered}),
        "profile_row_counts": dict(sorted(profile_counts.items())),
        "ripple_digests": [row["ripple_digest"] for row in ordered],
        "direct_consequence_count": sum(len(row["direct_consequences"]) for row in ordered),
        "transitive_consequence_count": sum(
            len(row["transitive_consequences"]) for row in ordered
        ),
        "blocked_overread_risk_count": sum(
            len(row["blocked_overreads_at_risk"]) for row in ordered
        ),
        "verification_obligation_risk_count": sum(
            len(row["verification_obligations_at_risk"]) for row in ordered
        ),
        "aggregate_digest": None,
    }
    aggregate["aggregate_digest"] = record_digest(aggregate, "aggregate_digest")
    return aggregate
