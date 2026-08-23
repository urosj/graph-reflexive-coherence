"""Shared experiment-local B2 constructibility adjudicator."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import math
from typing import Any


ADJUDICATOR_SCHEMA_VERSION = "b2_constructibility_adjudicator_v2"

DISPOSITION_PRECEDENCE = (
    "invalid_candidate",
    "outside_envelope",
    "source_or_provenance_failure",
    "required_assumption_failed",
    "numerical_failure",
    "required_control_failed",
    "required_control_not_identifiable",
    "duplicate_candidate",
    "search_unresolved",
    "bounded_negative",
    "pass_through_fixture",
)


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    disposition: str
    alternative_classification: str
    candidate_effects: dict[str, Any]


def evaluate_rule_case(
    case: dict[str, Any], rule_registry: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Evaluate atomic, compound, and pass-through rule-vector fixtures."""
    gate_results = case["gate_results"]
    unknown = sorted(set(gate_results) - set(rule_registry))
    if unknown:
        return {
            "observed_disposition": "invalid_test_fixture",
            "target_rule_reached": False,
            "unexpected_blockers": [f"unknown_rule:{rule}" for rule in unknown],
            "result": "invalid_test_fixture",
        }

    violations = [
        RuleResult(
            rule_id=rule_id,
            disposition=rule_registry[rule_id]["failure_disposition"],
            alternative_classification=rule_registry[rule_id].get(
                "alternative_classification", "none"
            ),
            candidate_effects=rule_registry[rule_id]["candidate_effects"],
        )
        for rule_id, passed in gate_results.items()
        if passed is False
    ]
    targets = set(case.get("target_rule_ids", []))
    violated_ids = {row.rule_id for row in violations}
    unexpected = sorted(violated_ids - targets)
    missing_target = sorted(targets - violated_ids)

    if not violations:
        primary = "pass_through_fixture"
        secondary: list[str] = []
        alternatives: list[str] = []
        candidate_effects = {
            "effect_scope": "none",
            "candidate_disposition": "pass_through_fixture",
            "underlying_witness_preserved": True,
            "rung_effect": "no_rung_effect",
            "blocked_rungs": [],
            "lane_blocked_rungs": [],
            "claim_effect": "no_claim_effect",
            "robustness_effect": "no_robustness_effect",
            "route_effect": "no_route_effect",
            "duplicate_effect": "no_duplicate_effect",
        }
    else:
        order = {name: index for index, name in enumerate(DISPOSITION_PRECEDENCE)}
        violations.sort(key=lambda row: (order[row.disposition], row.rule_id))
        primary = violations[0].disposition
        secondary = [row.disposition for row in violations[1:]]
        alternatives = sorted(
            {
                row.alternative_classification
                for row in violations
                if row.alternative_classification != "none"
            }
        )
        candidate_effects = violations[0].candidate_effects

    expected_primary = case["expected_primary_disposition"]
    allowed_secondary = set(case.get("allowed_secondary_dispositions", []))
    secondary_allowed = set(secondary).issubset(allowed_secondary)
    target_reached = not missing_target and not unexpected
    expected_alternative = case.get("expected_alternative_classification", "none")
    alternative_preserved = (
        expected_alternative == "none" or expected_alternative in alternatives
    )
    passed = (
        primary == expected_primary
        and secondary_allowed
        and target_reached
        and alternative_preserved
    )
    return {
        "observed_disposition": primary,
        "observed_secondary_dispositions": secondary,
        "observed_rule_violations": [row.rule_id for row in violations],
        "target_rule_reached": target_reached,
        "unexpected_blockers": unexpected,
        "missing_target_violations": missing_target,
        "preserved_alternative_classifications": alternatives,
        "alternative_classification_preserved": alternative_preserved,
        "candidate_effects": candidate_effects,
        "secondary_candidate_effects": [
            {"rule_id": row.rule_id, **row.candidate_effects} for row in violations[1:]
        ],
        "result": "passed" if passed else "failed_open",
    }


def evaluate_threshold_boundary(case: dict[str, Any]) -> dict[str, Any]:
    """Evaluate strict threshold admission without equality ambiguity."""
    value = float(case["value"])
    threshold = float(case["threshold"])
    direction = case["admission_direction"]
    if not math.isfinite(value) or not math.isfinite(threshold):
        observed = "numerical_failure"
    elif direction == "strictly_above":
        observed = "pass_through_fixture" if value > threshold else "bounded_negative"
    elif direction == "strictly_below":
        observed = "pass_through_fixture" if value < threshold else "bounded_negative"
    else:
        observed = "invalid_test_fixture"
    return {
        "observed_disposition": observed,
        "threshold_equality_is_positive": False,
        "result": "passed"
        if observed == case["expected_primary_disposition"]
        else "failed_open",
    }


def evaluate_control_status(case: dict[str, Any]) -> dict[str, Any]:
    """Apply the frozen required/optional control-state truth table."""
    status = case["control_status"]
    required = case["control_requirement"] == "required"
    applicable = case["applicability"] == "applicable"
    if status in {None, False, "missing"}:
        observed = "invalid_test_fixture"
        control_effect = "missing_control_status_invalid_fixture"
        candidate_disposition = "invalid_test_fixture"
        robustness_effect = "not_assessable"
    elif status == "passed":
        observed = "pass_through_fixture"
        control_effect = "control_passed"
        candidate_disposition = "dependent_rung_may_proceed"
        robustness_effect = "may_strengthen" if not required else "unchanged"
    elif status in {"failed", "failed_closed"}:
        observed = "required_control_failed" if required else "pass_through_fixture"
        control_effect = (
            "dependent_mechanism_or_rung_failed"
            if required
            else "optional_robustness_or_scope_narrowed"
        )
        candidate_disposition = (
            "dependent_rung_blocked" if required else "underlying_witness_preserved"
        )
        robustness_effect = "narrowed"
    elif status == "failed_open":
        observed = "invalid_candidate"
        control_effect = "false_positive_remained_admitted"
        candidate_disposition = "candidate_invalid"
        robustness_effect = "not_assessable"
    elif status == "not_identifiable":
        observed = (
            "required_control_not_identifiable" if required else "pass_through_fixture"
        )
        control_effect = (
            "dependent_rung_blocked_without_mechanism_falsification"
            if required
            else "optional_robustness_scope_narrowed"
        )
        candidate_disposition = (
            "dependent_rung_blocked" if required else "underlying_witness_preserved"
        )
        robustness_effect = "narrowed"
    elif status == "not_run":
        observed = "required_assumption_failed" if required else "pass_through_fixture"
        control_effect = (
            "gate_incomplete_required_control_not_run"
            if required
            else "optional_hardening_unresolved"
        )
        candidate_disposition = (
            "gate_incomplete_dependent_rung_blocked"
            if required
            else "underlying_witness_preserved"
        )
        robustness_effect = "uncharacterized"
    elif status == "not_applicable_with_reason":
        observed = (
            "pass_through_fixture" if not applicable else "required_assumption_failed"
        )
        control_effect = (
            "no_effect_frozen_not_applicable"
            if not applicable
            else "applicable_control_incorrectly_marked_not_applicable"
        )
        candidate_disposition = (
            "dependent_rung_may_proceed"
            if not applicable
            else "gate_incomplete_dependent_rung_blocked"
        )
        robustness_effect = "unchanged" if not applicable else "not_assessable"
    else:
        observed = "invalid_test_fixture"
        control_effect = "unknown_control_status_invalid_fixture"
        candidate_disposition = "invalid_test_fixture"
        robustness_effect = "not_assessable"
    return {
        "observed_disposition": observed,
        "control_effect_status": control_effect,
        "candidate_disposition": candidate_disposition,
        "robustness_effect": robustness_effect,
        "mechanism_falsified": required and status in {"failed", "failed_closed"},
        "rung_blocked": observed
        in {
            "required_control_failed",
            "required_control_not_identifiable",
            "required_assumption_failed",
            "invalid_candidate",
            "invalid_test_fixture",
        },
        "result": "passed"
        if observed == case["expected_primary_disposition"]
        else "failed_open",
    }


def evaluate_partial_overlap(case: dict[str, Any]) -> dict[str, Any]:
    """Exclude authored carrier content and test only runtime-generated residual."""
    apparent = Decimal(str(case["apparent_carrier_norm"]))
    authored = Decimal(str(case["authored_component_norm"]))
    threshold = Decimal(str(case["formation_threshold"]))
    residual = apparent - authored
    if authored < 0 or apparent < 0 or authored > apparent:
        observed = "invalid_test_fixture"
    elif residual > threshold:
        observed = "pass_through_fixture"
    else:
        observed = "bounded_negative"
    return {
        "runtime_generated_residual_norm": float(residual),
        "authored_component_excluded": True,
        "full_apparent_carrier_used_for_formation": False,
        "observed_disposition": observed,
        "result": "passed"
        if observed == case["expected_primary_disposition"]
        else "failed_open",
    }


def evaluate_lineage(case: dict[str, Any]) -> dict[str, Any]:
    """Check lineage identity across digest, representation, and transport changes."""
    same_id = case["formation_lineage_id"] == case["probe_lineage_id"]
    digests_equal = case["formation_digest"] == case["probe_digest"]
    representation_equal = (
        case["formation_carrier_definition_id"] == case["probe_carrier_definition_id"]
    )
    transport_declared = bool(case["transport_map_declared"])
    transport_valid = bool(case["transport_map_valid"])
    if not same_id:
        observed = "required_assumption_failed"
    elif digests_equal and representation_equal:
        observed = "pass_through_fixture"
    elif transport_declared and transport_valid:
        observed = "pass_through_fixture"
    else:
        observed = "required_assumption_failed"
    return {
        "same_lineage_id": same_id,
        "byte_equality_required": False,
        "transport_required": not (digests_equal and representation_equal),
        "observed_disposition": observed,
        "result": "passed"
        if observed == case["expected_primary_disposition"]
        else "failed_open",
    }


def _matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [sum(a * b for a, b in zip(row, column)) for column in zip(*right)]
        for row in left
    ]


def _matrix_max_error(left: list[list[float]], right: list[list[float]]) -> float:
    return max(
        abs(a - b)
        for left_row, right_row in zip(left, right)
        for a, b in zip(left_row, right_row)
    )


def _matrix_rank(matrix: list[list[float]], tolerance: float) -> int:
    work = [[float(value) for value in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    rank = 0
    column = 0
    while rank < row_count and column < column_count:
        pivot = max(range(rank, row_count), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= tolerance:
            column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(work[row], work[rank])
            ]
        rank += 1
        column += 1
    return rank


def evaluate_numerical_structure(case: dict[str, Any]) -> dict[str, Any]:
    """Fail malformed carrier/projector numerics before scientific classification."""
    vector = case["carrier_vector"]
    projector = case["projector"]
    complement = case["complement"]
    dimension = len(vector)
    square = (
        len(projector) == dimension
        and len(complement) == dimension
        and all(len(row) == dimension for row in projector + complement)
    )
    finite = all(math.isfinite(float(value)) for value in vector) and all(
        math.isfinite(float(value)) for row in projector + complement for value in row
    )
    if not finite or not square:
        observed = "numerical_failure"
        diagnostics = {"finite": finite, "square_dimension_match": square}
    else:
        p2 = _matmul(projector, projector)
        identity = [
            [1.0 if i == j else 0.0 for j in range(dimension)] for i in range(dimension)
        ]
        p_plus_q = [
            [projector[i][j] + complement[i][j] for j in range(dimension)]
            for i in range(dimension)
        ]
        idempotence_error = _matrix_max_error(p2, projector)
        complement_error = _matrix_max_error(p_plus_q, identity)
        tolerance = float(case["structural_tolerance"])
        projector_rank = _matrix_rank(projector, tolerance)
        expected_rank = int(case["expected_projector_rank"])
        margin = float(case["carrier_separation_margin"])
        isolation = float(case["slow_cluster_isolation_margin"])
        uncertainty = float(case["uncertainty_bound"])
        orientation_match = bool(case["orientation_basis_matches"])
        valid = (
            idempotence_error <= tolerance
            and complement_error <= tolerance
            and projector_rank == expected_rank
            and margin > uncertainty
            and isolation > uncertainty
            and orientation_match
        )
        observed = "pass_through_fixture" if valid else "numerical_failure"
        diagnostics = {
            "finite": finite,
            "square_dimension_match": square,
            "projector_idempotence_error": idempotence_error,
            "P_plus_Q_identity_error": complement_error,
            "projector_rank": projector_rank,
            "expected_projector_rank": expected_rank,
            "projector_rank_matches": projector_rank == expected_rank,
            "strict_carrier_margin": margin > uncertainty,
            "strict_isolation_margin": isolation > uncertainty,
            "orientation_basis_matches": orientation_match,
        }
    return {
        "observed_disposition": observed,
        "diagnostics": diagnostics,
        "result": "passed"
        if observed == case["expected_primary_disposition"]
        else "failed_open",
    }


def evaluate_report_semantics(case: dict[str, Any]) -> dict[str, Any]:
    """Preserve frozen search, duplicate, aggregation, and extension semantics."""
    scenario = case["scenario"]
    if scenario == "numerical_failure_not_scientific_negative":
        observed = "numerical_failure"
        extension_selected = False
    elif scenario == "budget_consumed_without_resolved_coverage":
        observed = "search_unresolved"
        extension_selected = False
    elif scenario in {
        "symmetry_duplicate_not_independent",
        "state_duplicate_not_independent",
        "history_distinct_same_state_not_independent",
    }:
        observed = "duplicate_candidate"
        extension_selected = False
    elif scenario == "global_GRR_max_cross_row_or_lineage":
        observed = "required_assumption_failed"
        extension_selected = False
    elif scenario == "empty_or_negative_search_no_automatic_extension":
        observed = "search_unresolved"
        extension_selected = False
    elif scenario in {
        "preparation_event_disappears_by_k0",
        "preparation_clipping_disappears_by_k0",
    }:
        observed = "outside_envelope"
        extension_selected = False
    else:
        observed = "invalid_test_fixture"
        extension_selected = False
    passed = (
        observed == case["expected_primary_disposition"]
        and extension_selected == case["expected_extension_selected"]
    )
    return {
        "observed_disposition": observed,
        "extension_selected": extension_selected,
        "result": "passed" if passed else "failed_open",
    }
