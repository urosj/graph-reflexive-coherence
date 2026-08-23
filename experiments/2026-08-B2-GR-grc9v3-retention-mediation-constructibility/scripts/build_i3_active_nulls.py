"""Build B2-GR Iteration 3 active nulls and threshold calibration."""

from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from typing import Any

from b2_adjudicator import (
    ADJUDICATOR_SCHEMA_VERSION,
    DISPOSITION_PRECEDENCE,
    evaluate_control_status,
    evaluate_lineage,
    evaluate_numerical_structure,
    evaluate_partial_overlap,
    evaluate_report_semantics,
    evaluate_rule_case,
    evaluate_threshold_boundary,
)
from b2_artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    assert_envelope_digest,
    envelope,
    finalize_receipt,
    find_absolute_paths,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_file,
    write_json,
)


SCRIPT_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "scripts/build_i3_active_nulls.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
CONFIG_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "configs/b2_i3_active_null_contract.json"
)
I2_ARTIFACT_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/b2_i2_constructibility_schema.json"
)
I2_RECEIPT_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/gates/b2_i2_result_receipt.json"
)
I2_ANCHOR_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/gates/b2_i2_acceptance_anchor.json"
)
CALIBRATION_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/b2_i3_threshold_calibration.json"
)
ADJUDICATOR_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "scripts/b2_adjudicator.py"
)

BLOCKED_RELABELS = (
    "core_ReadBack",
    "write_back",
    "closed_loop",
    "memory",
    "learning",
    "identity",
    "agency",
    "extension_necessity",
    "global_impossibility",
)


def load_and_validate_i2(input_revision: str) -> dict[str, Any]:
    anchor = read_json(REPO_ROOT / I2_ANCHOR_RELATIVE)
    artifact = read_json(REPO_ROOT / I2_ARTIFACT_RELATIVE)
    receipt = read_json(REPO_ROOT / I2_RECEIPT_RELATIVE)
    assert_envelope_digest(artifact)
    expected = {
        "acceptance_status": "accepted",
        "assigned_closeout_rung": "B2-C1",
        "ready_for_iteration_3": True,
        "B2_positive_evidence_opened": False,
        "GRR_rung_assigned": False,
    }
    for key, value in expected.items():
        if anchor.get(key) != value:
            raise ValueError(f"I2 acceptance anchor {key} mismatch")
    bindings = {
        I2_ARTIFACT_RELATIVE: anchor["result_artifact_sha256"],
        I2_RECEIPT_RELATIVE: anchor["result_receipt_sha256"],
    }
    for relative, digest in bindings.items():
        if sha256_file(REPO_ROOT / relative) != digest:
            raise ValueError(f"I2 acceptance binding mismatch: {relative}")
    if artifact["payload_sha256"] != anchor["result_artifact_payload_sha256"]:
        raise ValueError("I2 artifact payload binding mismatch")
    if receipt["receipt_payload_sha256"] != anchor["result_receipt_payload_sha256"]:
        raise ValueError("I2 receipt payload binding mismatch")
    git("cat-file", "-e", f"{anchor['result_revision']}^{{commit}}")
    git("merge-base", "--is-ancestor", anchor["result_revision"], input_revision)
    return {"anchor": anchor, "artifact": artifact, "receipt": receipt}


def family_registry(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for family in contract["control_families"]:
        for null_id in family["null_ids"]:
            if null_id in registry:
                raise ValueError(f"duplicate I3 null family assignment: {null_id}")
            registry[null_id] = family
    return registry


def calibrate_thresholds(
    contract: dict[str, Any], i2_payload: dict[str, Any], input_revision: str
) -> dict[str, Any]:
    recipes = {
        row["threshold_id"]: row
        for row in i2_payload["threshold_schema"]["calibration_recipes"]
    }
    fixture_rows = {
        row["threshold_id"]: row for row in contract["threshold_null_fixtures"]
    }
    if set(recipes) != set(fixture_rows):
        raise ValueError("I3 threshold fixtures do not exactly cover I2 recipes")

    records: list[dict[str, Any]] = []
    quantum = Decimal(1).scaleb(-contract["rounding_decimal_places"])
    for threshold_id in recipes:
        recipe = recipes[threshold_id]
        fixture = fixture_rows[threshold_id]
        maximum_null = max(
            Decimal(str(abs(value))) for value in fixture["fixture_values"]
        )
        uncertainty = Decimal(str(fixture["fixture_uncertainty"]))
        raw_value = (
            maximum_null + Decimal(str(recipe["safety_multiplier"])) * uncertainty
        )
        floored_value = max(Decimal(str(recipe["minimum_absolute_floor"])), raw_value)
        rounded_value = floored_value.quantize(quantum, rounding=ROUND_CEILING)
        maximum_allowed = Decimal(str(recipe["maximum_permitted_threshold"]))
        status = "usable" if rounded_value <= maximum_allowed else "unusable_blocks_I4"
        records.append(
            {
                "threshold_id": threshold_id,
                "metric": recipe["metric"],
                "null_population": recipe["null_population"],
                "fixture_role": fixture["fixture_role"],
                "fixture_values": deepcopy(fixture["fixture_values"]),
                "fixture_uncertainty": fixture["fixture_uncertainty"],
                "fixture_uncertainty_basis": fixture["fixture_uncertainty_basis"],
                "null_population_digest": semantic_digest(fixture),
                "recipe_digest": semantic_digest(recipe),
                "calculation": "max(minimum_absolute_floor, maximum_absolute_fixture_value_plus_safety_multiplier_times_fixture_uncertainty)",
                "unrounded_value": float(floored_value),
                "instantiated_value": float(rounded_value),
                "instantiated_value_decimal": format(rounded_value, "f"),
                "maximum_permitted_threshold": recipe["maximum_permitted_threshold"],
                "rounding_rule": recipe["rounding_rule"],
                "calibration_status": status,
                "declared_before_positive_search": True,
            }
        )

    payload = {
        "gate_id": "B2-I3-threshold-calibration",
        "input_execution_revision": input_revision,
        "source_I2_payload_sha256": semantic_digest(i2_payload),
        "calibration_role": contract["calibration_role"],
        "runtime_measurement_performed": False,
        "source_current_evidence_opened": False,
        "positive_search_must_also_apply_row_numerical_uncertainty": contract[
            "positive_search_must_also_apply_row_numerical_uncertainty"
        ],
        "records": records,
        "all_calibrations_usable": all(
            row["calibration_status"] == "usable" for row in records
        ),
        "positive_search_opened": False,
    }
    return envelope(payload, "b2_i3_threshold_calibration_v2", COMMAND)


def build_null_rows(
    contract: dict[str, Any], i2_payload: dict[str, Any]
) -> list[dict[str, Any]]:
    required = [row["null_id"] for row in i2_payload["active_null_schema"]]
    registry = family_registry(contract)
    rule_registry = contract["rule_dispositions"]
    if set(required) != set(registry):
        missing = sorted(set(required) - set(registry))
        extra = sorted(set(registry) - set(required))
        raise ValueError(
            f"I3 null-family coverage mismatch: missing={missing}, extra={extra}"
        )
    if set(required) != set(rule_registry):
        raise ValueError("I3 rule registry does not exactly cover accepted I2 nulls")
    fixture = contract["fixture_semantics"]
    rows = []
    for index, null_id in enumerate(required, 1):
        family = registry[null_id]
        control_id = f"{null_id}_control"
        gate_results = {rule_id: True for rule_id in required}
        gate_results[null_id] = False
        rule = rule_registry[null_id]
        case = {
            "case_id": f"b2_i3_atomic_{index:02d}_{null_id}",
            "case_kind": "atomic_null",
            "gate_results": gate_results,
            "target_rule_ids": [null_id],
            "expected_primary_disposition": rule["failure_disposition"],
            "allowed_secondary_dispositions": [],
            "expected_alternative_classification": rule.get(
                "alternative_classification", "none"
            ),
        }
        observed = evaluate_rule_case(case, rule_registry)
        failed_open = observed["result"] != "passed"
        rows.append(
            {
                "case_id": case["case_id"],
                "case_kind": case["case_kind"],
                "null_row_id": f"b2_i3_null_{index:02d}_{null_id}",
                "null_id": null_id,
                "control_id": control_id,
                "control_family": family["family_id"],
                "false_positive_path": null_id.replace("_", " "),
                "i2_rule_ids_exercised": [null_id],
                "mutation_from_reference": {
                    "changed_rule_id": null_id,
                    "reference_gate_value": True,
                    "mutated_gate_value": False,
                    "all_other_gate_values": True,
                },
                "expected_preconditions_pass": True,
                "expected_primary_disposition": case["expected_primary_disposition"],
                "allowed_secondary_dispositions": [],
                "observed_disposition": observed["observed_disposition"],
                "observed_secondary_dispositions": observed[
                    "observed_secondary_dispositions"
                ],
                "target_rule_reached": observed["target_rule_reached"],
                "unexpected_blockers": observed["unexpected_blockers"],
                "expected_alternative_classification": case[
                    "expected_alternative_classification"
                ],
                "preserved_alternative_classifications": observed[
                    "preserved_alternative_classifications"
                ],
                "blocked_gate_family": family["blocked_gate_family"],
                "blocked_rungs": deepcopy(family["blocked_rungs"]),
                "expected_result": "failed_closed",
                "actual_result": "failed_open" if failed_open else "failed_closed",
                "control_status": "failed_open" if failed_open else "failed_closed",
                "control_status_meaning": fixture["failed_closed_meaning"],
                "failed_open": failed_open,
                "control_results": [
                    {
                        "control_id": control_id,
                        "control_status": (
                            "failed_open" if failed_open else "failed_closed"
                        ),
                        "blocked_condition": null_id,
                        "expected_result": "claim_rejected",
                        "actual_result": (
                            "claim_not_rejected_for_expected_reason"
                            if failed_open
                            else "claim_rejected"
                        ),
                        "claim_allowed_when_control_triggers": False,
                        "rung_effect": "all_listed_dependent_rungs_blocked",
                    }
                ],
                "observation_source": "pre_positive_active_null_fixture",
                "observed_result_semantics": fixture["observed_result_semantics"],
                "schema_instantiation_only": fixture["schema_instantiation_only"],
                "derived_report_only": fixture["derived_report_only"],
                "positive_evidence_admissible": fixture["positive_evidence_admissible"],
                "source_current_inputs": deepcopy(fixture["source_current_inputs"]),
                "artifact_manifest": deepcopy(fixture["artifact_manifest"]),
                "artifact_sha256_status": "not_applicable_active_null_fixture",
                "all_artifact_sha256_match_file_contents": "not_applicable_active_null_fixture",
                "artifact_paths_equal_manifest_paths": "not_applicable_active_null_fixture",
                "maximum_GRR_rung": fixture["maximum_GRR_rung"],
                "GRR_rung_assigned": False,
                "row_decision": "rejected_failed_closed_active_null",
                "claim_ceiling": "active_null_admission_control_only",
                "threshold_calibration_role": "held_out_audit_null_not_calibration",
                "validator_result": observed["result"],
            }
        )
    return rows


def build_pass_through_sentinels(
    contract: dict[str, Any], i2_payload: dict[str, Any]
) -> list[dict[str, Any]]:
    required = [row["null_id"] for row in i2_payload["active_null_schema"]]
    rules = contract["rule_dispositions"]
    baseline = {rule_id: True for rule_id in required}
    rows = []
    for index, rule_id in enumerate(required, 1):
        case = {
            "case_id": f"b2_i3_sentinel_{index:02d}_{rule_id}",
            "case_kind": "pass_through_sentinel",
            "gate_results": deepcopy(baseline),
            "target_rule_ids": [],
            "expected_primary_disposition": "pass_through_fixture",
            "allowed_secondary_dispositions": [],
            "expected_alternative_classification": "none",
        }
        observed = evaluate_rule_case(case, rules)
        rows.append(
            {
                "case_id": case["case_id"],
                "case_kind": case["case_kind"],
                "i2_rule_ids_exercised": [rule_id],
                "mutation_from_reference": "none_nearby_fixture_remains_inside_target_gate",
                "positive_evidence_eligible": False,
                "expected_primary_disposition": "pass_through_fixture",
                "observed_disposition": observed["observed_disposition"],
                "target_rule_reached": observed["target_rule_reached"],
                "unexpected_blockers": observed["unexpected_blockers"],
                "result": observed["result"],
            }
        )
    return rows


def build_compound_cases(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rules = contract["rule_dispositions"]
    baseline = {rule_id: True for rule_id in rules}
    specs = [
        {
            "case_id": "b2_i3_compound_outside_assumption_control",
            "violations": [
                "eventful_preparation_as_clean_primary_lane",
                "projector_recomputed_to_follow_candidate_across_horizons",
                "reset_does_not_remove_effect",
            ],
            "expected": "outside_envelope",
            "secondary": ["required_assumption_failed", "required_control_failed"],
        },
        {
            "case_id": "b2_i3_compound_source_then_assumption",
            "violations": [
                "synthetic_only_preparation_as_runtime_reached",
                "no_matched_sham_as_native_formation",
            ],
            "expected": "source_or_provenance_failure",
            "secondary": ["required_assumption_failed"],
        },
        {
            "case_id": "b2_i3_compound_unresolved_search_debts",
            "violations": [
                "failed_search_as_impossibility",
                "budget_consumed_as_resolved_coverage",
            ],
            "expected": "search_unresolved",
            "secondary": ["search_unresolved"],
        },
        {
            "case_id": "b2_i3_compound_duplicate_representation_and_history",
            "violations": [
                "overlapping_carrier_representations_as_independent_witnesses",
                "distinct_histories_same_state_as_independent_retention_witnesses",
            ],
            "expected": "duplicate_candidate",
            "secondary": ["duplicate_candidate"],
        },
    ]
    rows = []
    for spec in specs:
        gates = deepcopy(baseline)
        for rule_id in spec["violations"]:
            gates[rule_id] = False
        case = {
            "case_id": spec["case_id"],
            "case_kind": "compound_null",
            "gate_results": gates,
            "target_rule_ids": spec["violations"],
            "expected_primary_disposition": spec["expected"],
            "allowed_secondary_dispositions": spec["secondary"],
            "expected_alternative_classification": "none",
        }
        observed = evaluate_rule_case(case, rules)
        rows.append(
            {
                "case_id": case["case_id"],
                "case_kind": case["case_kind"],
                "i2_rule_ids_exercised": deepcopy(spec["violations"]),
                "mutation_from_reference": {
                    "violated_rules": deepcopy(spec["violations"])
                },
                "positive_evidence_eligible": False,
                "expected_primary_disposition": spec["expected"],
                "allowed_secondary_dispositions": deepcopy(spec["secondary"]),
                "observed_disposition": observed["observed_disposition"],
                "observed_secondary_dispositions": observed[
                    "observed_secondary_dispositions"
                ],
                "target_rule_reached": observed["target_rule_reached"],
                "unexpected_blockers": observed["unexpected_blockers"],
                "result": observed["result"],
            }
        )
    return rows


def build_threshold_audits(
    calibration_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for record in calibration_records:
        threshold = float(record["instantiated_value"])
        delta = max(abs(threshold) * 0.1, 1e-12)
        direction = (
            "strictly_below"
            if record["threshold_id"] == "control_target_residual_ceiling_v1"
            else "strictly_above"
        )
        pass_value = (
            threshold - delta if direction == "strictly_below" else threshold + delta
        )
        fail_value = (
            threshold + delta if direction == "strictly_below" else threshold - delta
        )
        variants = [
            ("exact_equality", threshold, "bounded_negative"),
            ("just_inside", pass_value, "pass_through_fixture"),
            ("just_outside", fail_value, "bounded_negative"),
        ]
        for variant, value, expected in variants:
            case = {
                "case_id": f"b2_i3_threshold_{record['threshold_id']}_{variant}",
                "case_kind": "threshold_boundary_audit",
                "value": value,
                "threshold": threshold,
                "admission_direction": direction,
                "expected_primary_disposition": expected,
            }
            observed = evaluate_threshold_boundary(case)
            rows.append(
                {
                    "case_id": case["case_id"],
                    "case_kind": case["case_kind"],
                    "threshold_id": record["threshold_id"],
                    "threshold_calibration_role": "held_out_boundary_audit_not_calibration",
                    "boundary_variant": variant,
                    "positive_evidence_eligible": False,
                    "expected_primary_disposition": expected,
                    "observed_disposition": observed["observed_disposition"],
                    "threshold_equality_is_positive": observed[
                        "threshold_equality_is_positive"
                    ],
                    "result": observed["result"],
                }
            )
    return rows


def build_control_truth_cases() -> list[dict[str, Any]]:
    specs = [
        ("required_passed", "required", "applicable", "passed", "pass_through_fixture"),
        (
            "required_failed",
            "required",
            "applicable",
            "failed",
            "required_control_failed",
        ),
        (
            "required_not_identifiable",
            "required",
            "applicable",
            "not_identifiable",
            "required_control_not_identifiable",
        ),
        (
            "required_not_run",
            "required",
            "applicable",
            "not_run",
            "required_assumption_failed",
        ),
        (
            "required_inapplicable_but_marked_NA",
            "required",
            "not_applicable",
            "not_applicable_with_reason",
            "pass_through_fixture",
        ),
        (
            "required_applicable_but_marked_NA",
            "required",
            "applicable",
            "not_applicable_with_reason",
            "required_assumption_failed",
        ),
        ("optional_passed", "optional", "applicable", "passed", "pass_through_fixture"),
        ("optional_failed", "optional", "applicable", "failed", "bounded_negative"),
        (
            "optional_not_identifiable",
            "optional",
            "applicable",
            "not_identifiable",
            "pass_through_fixture",
        ),
        ("optional_not_run", "optional", "applicable", "not_run", "bounded_negative"),
        (
            "optional_inapplicable_but_marked_NA",
            "optional",
            "not_applicable",
            "not_applicable_with_reason",
            "pass_through_fixture",
        ),
        (
            "optional_failed_open",
            "optional",
            "applicable",
            "failed_open",
            "invalid_candidate",
        ),
        (
            "required_failed_open",
            "required",
            "applicable",
            "failed_open",
            "invalid_candidate",
        ),
        ("missing_status", "required", "applicable", "missing", "invalid_test_fixture"),
    ]
    rows = []
    for case_id, requirement, applicability, status, expected in specs:
        case = {
            "case_id": f"b2_i3_control_truth_{case_id}",
            "case_kind": "control_truth_table_audit",
            "control_requirement": requirement,
            "applicability": applicability,
            "control_status": status,
            "expected_primary_disposition": expected,
        }
        observed = evaluate_control_status(case)
        rows.append(
            {
                "case_id": case["case_id"],
                "case_kind": case["case_kind"],
                "control_requirement": requirement,
                "applicability": applicability,
                "control_status": status,
                "positive_evidence_eligible": False,
                "expected_primary_disposition": expected,
                "observed_disposition": observed["observed_disposition"],
                "mechanism_falsified": observed["mechanism_falsified"],
                "rung_blocked": observed["rung_blocked"],
                "result": observed["result"],
            }
        )
    return rows


def build_partial_overlap_cases() -> list[dict[str, Any]]:
    specs = [
        (
            "ninety_percent_authored_residual_passes",
            1.0,
            0.9,
            0.05,
            "pass_through_fixture",
        ),
        ("runtime_residual_equals_floor", 1.0, 0.95, 0.05, "bounded_negative"),
        ("fully_authored_carrier", 1.0, 1.0, 0.05, "bounded_negative"),
    ]
    rows = []
    for case_id, apparent, authored, threshold, expected in specs:
        case = {
            "case_id": f"b2_i3_overlap_{case_id}",
            "case_kind": "partial_driver_carrier_overlap_audit",
            "apparent_carrier_norm": apparent,
            "authored_component_norm": authored,
            "formation_threshold": threshold,
            "expected_primary_disposition": expected,
        }
        observed = evaluate_partial_overlap(case)
        rows.append({**case, **observed, "positive_evidence_eligible": False})
    return rows


def build_lineage_cases() -> list[dict[str, Any]]:
    common = {
        "formation_lineage_id": "lineage-A",
        "probe_lineage_id": "lineage-A",
        "formation_digest": "digest-A",
        "probe_digest": "digest-A",
        "formation_carrier_definition_id": "C_ZERO_SUM_V1",
        "probe_carrier_definition_id": "C_ZERO_SUM_V1",
        "transport_map_declared": False,
        "transport_map_valid": False,
    }
    specs = [
        ("exact_same_lineage", {}, "pass_through_fixture"),
        (
            "reused_id_incompatible_digest",
            {"probe_digest": "digest-B"},
            "required_assumption_failed",
        ),
        (
            "silent_representation_broadening",
            {
                "probe_digest": "digest-B",
                "probe_carrier_definition_id": "JOINT_C_W_BLOCK_V1",
            },
            "required_assumption_failed",
        ),
        (
            "valid_transport_changes_coordinates",
            {
                "probe_digest": "digest-B",
                "probe_carrier_definition_id": "JOINT_C_W_BLOCK_V1",
                "transport_map_declared": True,
                "transport_map_valid": True,
            },
            "pass_through_fixture",
        ),
        (
            "invalid_transport_high_overlap",
            {
                "probe_digest": "digest-B",
                "transport_map_declared": True,
                "transport_map_valid": False,
            },
            "required_assumption_failed",
        ),
    ]
    rows = []
    for case_id, updates, expected in specs:
        case = deepcopy(common)
        case.update(updates)
        case.update(
            {
                "case_id": f"b2_i3_lineage_{case_id}",
                "case_kind": "carrier_lineage_transport_audit",
                "expected_primary_disposition": expected,
            }
        )
        observed = evaluate_lineage(case)
        rows.append(
            {
                "case_id": case["case_id"],
                "case_kind": case["case_kind"],
                "mutation_from_reference": updates,
                "positive_evidence_eligible": False,
                "expected_primary_disposition": expected,
                **observed,
            }
        )
    return rows


def build_numerical_cases() -> list[dict[str, Any]]:
    identity = [[1.0, 0.0], [0.0, 1.0]]
    zero = [[0.0, 0.0], [0.0, 0.0]]
    common = {
        "carrier_vector": [1.0, -1.0],
        "projector": identity,
        "complement": zero,
        "structural_tolerance": 1e-9,
        "expected_projector_rank": 2,
        "carrier_separation_margin": 1.0,
        "slow_cluster_isolation_margin": 1.0,
        "uncertainty_bound": 0.1,
        "orientation_basis_matches": True,
    }
    specs = [
        ("valid_structure", {}, "pass_through_fixture"),
        ("nan_carrier", {"carrier_vector": [float("nan"), -1.0]}, "numerical_failure"),
        ("inf_carrier", {"carrier_vector": [float("inf"), -1.0]}, "numerical_failure"),
        ("dimension_mismatch", {"projector": [[1.0]]}, "numerical_failure"),
        (
            "non_idempotent_projector",
            {"projector": [[0.5, 0.0], [0.0, 0.5]]},
            "numerical_failure",
        ),
        ("P_plus_Q_inconsistent", {"complement": identity}, "numerical_failure"),
        (
            "wrong_projector_rank",
            {"projector": zero, "complement": identity},
            "numerical_failure",
        ),
        (
            "zero_carrier_margin",
            {"carrier_separation_margin": 0.1},
            "numerical_failure",
        ),
        (
            "uncertainty_straddles_admission",
            {"carrier_separation_margin": 0.05},
            "numerical_failure",
        ),
        (
            "zero_isolation_margin",
            {"slow_cluster_isolation_margin": 0.1},
            "numerical_failure",
        ),
        (
            "orientation_basis_reversed",
            {"orientation_basis_matches": False},
            "numerical_failure",
        ),
    ]
    rows = []
    for case_id, updates, expected in specs:
        case = deepcopy(common)
        case.update(updates)
        case.update(
            {
                "case_id": f"b2_i3_numerical_{case_id}",
                "case_kind": "numerical_structural_boundary_audit",
                "expected_primary_disposition": expected,
            }
        )
        observed = evaluate_numerical_structure(case)
        rows.append(
            {
                "case_id": case["case_id"],
                "case_kind": case["case_kind"],
                "mutation_from_reference": sorted(updates),
                "positive_evidence_eligible": False,
                "expected_primary_disposition": expected,
                **observed,
            }
        )
    return rows


def build_report_semantic_cases() -> list[dict[str, Any]]:
    specs = [
        ("numerical_failure_not_scientific_negative", "numerical_failure"),
        ("budget_consumed_without_resolved_coverage", "search_unresolved"),
        ("symmetry_duplicate_not_independent", "duplicate_candidate"),
        ("state_duplicate_not_independent", "duplicate_candidate"),
        ("history_distinct_same_state_not_independent", "duplicate_candidate"),
        ("global_GRR_max_cross_row_or_lineage", "required_assumption_failed"),
        ("empty_or_negative_search_no_automatic_extension", "search_unresolved"),
        ("preparation_event_disappears_by_k0", "outside_envelope"),
        ("preparation_clipping_disappears_by_k0", "outside_envelope"),
    ]
    rows = []
    for scenario, expected in specs:
        case = {
            "case_id": f"b2_i3_report_{scenario}",
            "case_kind": "search_and_closeout_semantics_audit",
            "scenario": scenario,
            "expected_primary_disposition": expected,
            "expected_extension_selected": False,
        }
        observed = evaluate_report_semantics(case)
        rows.append({**case, **observed, "positive_evidence_eligible": False})
    return rows


def build_rule_coverage_matrix(
    atomic_rows: list[dict[str, Any]],
    sentinels: list[dict[str, Any]],
    compounds: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sentinel_by_rule = {
        row["i2_rule_ids_exercised"][0]: row["case_id"] for row in sentinels
    }
    result = []
    for row in atomic_rows:
        rule_id = row["null_id"]
        result.append(
            {
                "I2_rule_id": rule_id,
                "atomic_null_case_ids": [row["case_id"]],
                "pass_through_sentinel_case_ids": [sentinel_by_rule[rule_id]],
                "compound_precedence_case_ids": [
                    case["case_id"]
                    for case in compounds
                    if rule_id in case["i2_rule_ids_exercised"]
                ],
            }
        )
    return result


def build_checks(payload: dict[str, Any]) -> dict[str, bool]:
    rows = payload["active_null_rows"]
    required = payload["source_schema_contract"]["required_null_ids"]
    calibrations = payload["threshold_calibration"]["records"]
    sentinels = payload["pass_through_sentinel_rows"]
    compounds = payload["compound_precedence_rows"]
    threshold_audits = payload["threshold_boundary_audit_rows"]
    control_cases = payload["control_truth_table_rows"]
    overlap_cases = payload["partial_driver_carrier_overlap_rows"]
    lineage_cases = payload["carrier_lineage_transport_rows"]
    numerical_cases = payload["numerical_structural_boundary_rows"]
    report_cases = payload["search_and_closeout_semantic_rows"]
    auxiliary_cases = (
        sentinels
        + compounds
        + threshold_audits
        + control_cases
        + overlap_cases
        + lineage_cases
        + numerical_cases
        + report_cases
    )
    coverage = payload["rule_coverage_matrix"]
    return {
        "i2_acceptance_anchor_consumed": payload["source_schema_contract"][
            "I2_acceptance_status"
        ]
        == "accepted",
        "i2_B2_C1_consumed": payload["source_schema_contract"][
            "I2_assigned_closeout_rung"
        ]
        == "B2-C1",
        "i2_artifact_and_receipt_bound": all(
            len(payload["source_schema_contract"][key]) == 64
            for key in ["I2_artifact_payload_sha256", "I2_receipt_payload_sha256"]
        ),
        "all_52_frozen_nulls_instantiated": len(rows) == len(required) == 52,
        "null_order_matches_accepted_I2": [row["null_id"] for row in rows] == required,
        "null_family_assignment_is_exact": sum(
            payload["control_family_counts"].values()
        )
        == 52,
        "all_nulls_failed_closed": all(
            row["control_status"] == "failed_closed" for row in rows
        ),
        "all_atomic_nulls_reach_intended_gate": all(
            row["target_rule_reached"]
            and row["unexpected_blockers"] == []
            and row["observed_disposition"] == row["expected_primary_disposition"]
            and row["validator_result"] == "passed"
            for row in rows
        ),
        "all_atomic_alternative_classifications_preserved": all(
            row["expected_alternative_classification"] == "none"
            or row["expected_alternative_classification"]
            in row["preserved_alternative_classifications"]
            for row in rows
        ),
        "failed_open_row_count_zero": not any(row["failed_open"] for row in rows),
        "one_pass_through_sentinel_per_I2_rule": len(sentinels) == len(required) == 52
        and [row["i2_rule_ids_exercised"][0] for row in sentinels] == required,
        "all_pass_through_sentinels_pass": all(
            row["observed_disposition"] == "pass_through_fixture"
            and row["result"] == "passed"
            and row["unexpected_blockers"] == []
            for row in sentinels
        ),
        "compound_precedence_is_deterministic": len(compounds) == 4
        and all(
            row["observed_disposition"] == row["expected_primary_disposition"]
            and row["target_rule_reached"]
            and row["unexpected_blockers"] == []
            and row["result"] == "passed"
            for row in compounds
        ),
        "every_I2_rule_has_atomic_and_sentinel_coverage": len(coverage) == 52
        and [row["I2_rule_id"] for row in coverage] == required
        and all(
            len(row["atomic_null_case_ids"]) == 1
            and len(row["pass_through_sentinel_case_ids"]) == 1
            for row in coverage
        ),
        "held_out_threshold_boundaries_cover_equality_inside_outside": len(
            threshold_audits
        )
        == 12
        and all(row["result"] == "passed" for row in threshold_audits)
        and {row["boundary_variant"] for row in threshold_audits}
        == {"exact_equality", "just_inside", "just_outside"},
        "threshold_equality_never_admitted": all(
            row["observed_disposition"] == "bounded_negative"
            and row["threshold_equality_is_positive"] is False
            for row in threshold_audits
            if row["boundary_variant"] == "exact_equality"
        ),
        "control_status_truth_table_passes": len(control_cases) == 14
        and all(row["result"] == "passed" for row in control_cases),
        "partial_authorship_excluded_before_formation_test": len(overlap_cases) == 3
        and all(
            row["authored_component_excluded"]
            and row["full_apparent_carrier_used_for_formation"] is False
            and row["result"] == "passed"
            for row in overlap_cases
        ),
        "lineage_transport_and_representation_rules_pass": len(lineage_cases) == 5
        and all(row["result"] == "passed" for row in lineage_cases),
        "numerical_and_structural_pathologies_fail_typed": len(numerical_cases) == 11
        and all(row["result"] == "passed" for row in numerical_cases)
        and sum(
            row["observed_disposition"] == "numerical_failure"
            for row in numerical_cases
        )
        == 10,
        "search_and_closeout_semantics_pass": len(report_cases) == 9
        and all(
            row["result"] == "passed" and row["extension_selected"] is False
            for row in report_cases
        ),
        "all_validator_cases_are_non_evidence": all(
            row["positive_evidence_eligible"] is False for row in auxiliary_cases
        )
        and all(row["positive_evidence_admissible"] is False for row in rows),
        "all_validator_cases_pass": all(
            row["validator_result"] == "passed" for row in rows
        )
        and all(row["result"] == "passed" for row in auxiliary_cases),
        "validator_case_count_is_complete": payload["validator_case_count"]
        == len(rows) + len(auxiliary_cases)
        == 162,
        "shared_adjudicator_schema_and_digest_bound": payload["adjudicator_binding"][
            "schema_version"
        ]
        == payload["adjudicator_contract"]["required_schema_version"]
        == ADJUDICATOR_SCHEMA_VERSION
        and len(payload["adjudicator_binding"]["sha256"]) == 64,
        "downstream_adjudicator_change_requires_rerun": payload["adjudicator_contract"][
            "later_iterations_must_use_same_adjudicator_digest"
        ]
        and payload["adjudicator_contract"]["adjudicator_change_requires_I3_rerun"]
        and payload["adjudicator_contract"][
            "scientific_rule_change_requires_I2_revision_and_reacceptance"
        ],
        "superseded_unaccepted_I3_result_recorded": payload["supersession"][
            "prior_acceptance_state"
        ]
        == "awaiting_scientific_review"
        and payload["supersession"]["prior_acceptance_anchor_created"] is False,
        "all_claims_rejected_when_blocker_triggers": all(
            row["control_results"][0]["claim_allowed_when_control_triggers"] is False
            for row in rows
        ),
        "all_nulls_fixture_or_report_only": all(
            row["schema_instantiation_only"] and row["derived_report_only"]
            for row in rows
        ),
        "no_source_current_inputs_opened": all(
            row["source_current_inputs"] == [] for row in rows
        ),
        "null_artifact_manifests_empty": all(
            row["artifact_manifest"] == [] for row in rows
        ),
        "artifact_sentinels_limited_to_nonpositive_fixtures": all(
            row["all_artifact_sha256_match_file_contents"]
            == "not_applicable_active_null_fixture"
            and row["positive_evidence_admissible"] is False
            for row in rows
        ),
        "no_GRR_rung_assigned_to_nulls": all(
            row["maximum_GRR_rung"] == "not_assigned"
            and row["GRR_rung_assigned"] is False
            for row in rows
        ),
        "control_result_schema_complete": all(
            set(row["control_results"][0])
            == {
                "control_id",
                "control_status",
                "blocked_condition",
                "expected_result",
                "actual_result",
                "claim_allowed_when_control_triggers",
                "rung_effect",
            }
            for row in rows
        ),
        "all_four_I2_calibration_recipes_instantiated": len(calibrations) == 4,
        "all_calibration_recipe_digests_bound": all(
            len(row["recipe_digest"]) == 64 for row in calibrations
        ),
        "all_calibrations_declared_pre_positive": all(
            row["declared_before_positive_search"] for row in calibrations
        ),
        "all_calibrations_within_frozen_maxima": all(
            row["instantiated_value"] <= row["maximum_permitted_threshold"]
            for row in calibrations
        ),
        "all_calibrations_usable": payload["threshold_calibration"][
            "all_calibrations_usable"
        ],
        "calibration_is_not_runtime_evidence": payload["threshold_calibration"][
            "runtime_measurement_performed"
        ]
        is False,
        "row_numerical_uncertainty_still_required": payload["threshold_calibration"][
            "positive_search_must_also_apply_row_numerical_uncertainty"
        ],
        "positive_evidence_remains_closed": payload["claim_boundary"][
            "B2_positive_evidence_opened"
        ]
        is False,
        "GRR_ladder_remains_unassigned": payload["claim_boundary"]["GRR_rung_assigned"]
        is False,
        "B2_C2_only_ready": payload["claim_boundary"]["B2_closeout_ceiling"]
        == "B2-C2-ready"
        and payload["claim_boundary"]["B2_closeout_rung_assigned"] is False,
        "I4_ready_only_after_I3_acceptance": payload["claim_boundary"][
            "ready_for_iteration_4_after_acceptance"
        ],
        "extension_selection_remains_closed": payload["claim_boundary"][
            "extension_target_selected"
        ]
        is False,
        "unsafe_claims_blocked": all(
            not value for value in payload["unsafe_claim_flags"].values()
        ),
        "no_absolute_paths": find_absolute_paths(payload) == [],
    }


def build_payload(
    input_revision: str, threshold_artifact_sha256: str = "0" * 64
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = read_json(REPO_ROOT / CONFIG_RELATIVE)
    source = load_and_validate_i2(input_revision)
    i2_payload = source["artifact"]["payload"]
    calibration_artifact = calibrate_thresholds(contract, i2_payload, input_revision)
    rows = build_null_rows(contract, i2_payload)
    sentinels = build_pass_through_sentinels(contract, i2_payload)
    compounds = build_compound_cases(contract)
    threshold_audits = build_threshold_audits(
        calibration_artifact["payload"]["records"]
    )
    control_cases = build_control_truth_cases()
    overlap_cases = build_partial_overlap_cases()
    lineage_cases = build_lineage_cases()
    numerical_cases = build_numerical_cases()
    report_cases = build_report_semantic_cases()
    coverage = build_rule_coverage_matrix(rows, sentinels, compounds)
    auxiliary_cases = (
        sentinels
        + compounds
        + threshold_audits
        + control_cases
        + overlap_cases
        + lineage_cases
        + numerical_cases
        + report_cases
    )
    family_counts: dict[str, int] = {}
    for row in rows:
        family_counts[row["control_family"]] = (
            family_counts.get(row["control_family"], 0) + 1
        )

    payload: dict[str, Any] = {
        "gate_id": "B2-I3",
        "status": "passed",
        "acceptance_state": "awaiting_scientific_review",
        "schema_instantiation_only": True,
        "supersession": deepcopy(contract["supersession"]),
        "adjudicator_contract": deepcopy(contract["adjudicator_contract"]),
        "adjudicator_binding": {
            "path": ADJUDICATOR_RELATIVE,
            "schema_version": ADJUDICATOR_SCHEMA_VERSION,
            "sha256": sha256_file(REPO_ROOT / ADJUDICATOR_RELATIVE),
            "disposition_precedence": list(DISPOSITION_PRECEDENCE),
        },
        "source_schema_contract": {
            "I2_acceptance_anchor_path": I2_ANCHOR_RELATIVE,
            "I2_acceptance_anchor_sha256": sha256_file(REPO_ROOT / I2_ANCHOR_RELATIVE),
            "I2_acceptance_status": source["anchor"]["acceptance_status"],
            "I2_assigned_closeout_rung": source["anchor"]["assigned_closeout_rung"],
            "I2_result_revision": source["anchor"]["result_revision"],
            "I2_artifact_payload_sha256": source["artifact"]["payload_sha256"],
            "I2_receipt_payload_sha256": source["receipt"]["receipt_payload_sha256"],
            "required_null_ids": [
                row["null_id"] for row in i2_payload["active_null_schema"]
            ],
            "calibration_recipe_section_sha256": semantic_digest(
                i2_payload["threshold_schema"]["calibration_recipes"]
            ),
        },
        "active_null_rows": rows,
        "active_null_row_count": len(rows),
        "pass_through_sentinel_rows": sentinels,
        "compound_precedence_rows": compounds,
        "threshold_boundary_audit_rows": threshold_audits,
        "control_truth_table_rows": control_cases,
        "partial_driver_carrier_overlap_rows": overlap_cases,
        "carrier_lineage_transport_rows": lineage_cases,
        "numerical_structural_boundary_rows": numerical_cases,
        "search_and_closeout_semantic_rows": report_cases,
        "rule_coverage_matrix": coverage,
        "validator_case_count": len(rows) + len(auxiliary_cases),
        "validator_case_counts": {
            "atomic_null": len(rows),
            "pass_through_sentinel": len(sentinels),
            "compound_null": len(compounds),
            "threshold_boundary_audit": len(threshold_audits),
            "control_truth_table_audit": len(control_cases),
            "partial_driver_carrier_overlap_audit": len(overlap_cases),
            "carrier_lineage_transport_audit": len(lineage_cases),
            "numerical_structural_boundary_audit": len(numerical_cases),
            "search_and_closeout_semantics_audit": len(report_cases),
        },
        "control_family_counts": family_counts,
        "failed_closed_row_count": sum(
            row["control_status"] == "failed_closed" for row in rows
        ),
        "failed_open_row_count": sum(row["failed_open"] for row in rows),
        "threshold_calibration_artifact": {
            "path": CALIBRATION_RELATIVE,
            "sha256": threshold_artifact_sha256,
            "payload_sha256": calibration_artifact["payload_sha256"],
        },
        "threshold_calibration": deepcopy(calibration_artifact["payload"]),
        "claim_boundary": {
            "B2_positive_evidence_opened": False,
            "candidate_rows_classified": False,
            "scientific_transition_executed": False,
            "GRR_rung_assigned": False,
            "B2_closeout_rung_assigned": False,
            "B2_closeout_ceiling": "B2-C2-ready",
            "ready_for_iteration_4_after_acceptance": True,
            "extension_target_selected": False,
        },
        "unsafe_claim_flags": {name: False for name in BLOCKED_RELABELS},
    }
    checks = build_checks(payload)
    payload["checks"] = checks
    payload["check_count"] = len(checks)
    payload["passed_check_count"] = sum(checks.values())
    payload["failed_checks"] = [name for name, passed in checks.items() if not passed]
    payload["status"] = "passed" if not payload["failed_checks"] else "blocked"
    return payload, calibration_artifact


def render_report(artifact: dict[str, Any]) -> str:
    payload = artifact["payload"]
    lines = [
        "# B2-GR Iteration 3 - Active Nulls And Failure Baselines",
        "",
        "## Result",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"checks = {payload['passed_check_count']}/{payload['check_count']} passed",
        f"failed_checks = {payload['failed_checks']}",
        f"active_null_rows = {payload['active_null_row_count']}",
        f"failed_closed_rows = {payload['failed_closed_row_count']}",
        f"failed_open_rows = {payload['failed_open_row_count']}",
        f"validator_cases = {payload['validator_case_count']}",
        f"pass_through_sentinels = {len(payload['pass_through_sentinel_rows'])}",
        f"compound_precedence_cases = {len(payload['compound_precedence_rows'])}",
        "B2_positive_evidence_opened = false",
        "GRR_rung_assigned = false",
        "B2_closeout_ceiling = B2-C2-ready",
        "```",
        "",
        "## Admission Boundary",
        "",
        "All 52 frozen I2 false-positive paths are instantiated exactly once as atomic rule-vector mutations. Every mutation reaches its intended gate with all other frozen rule gates passing. `failed_closed` means the blocker triggered and the dependent claim was rejected; it does not mean that a positive scientific control failed. These rows are deterministic admission fixtures, not runtime measurements, source-current candidate evidence, or replay evidence.",
        "",
        "The null surface covers temporal/spectral relabels, branch relation and search coverage, formation provenance and full-path cleanliness, probe provenance and matched mediation, reset/swap/bypass semantics, carrier lineage/equivalence, and selection/threshold/claim governance.",
        "",
        "## Adjudicator Specificity And Permissiveness",
        "",
        "The 52 atomic nulls are paired with 52 pass-through sentinels under the same adjudicator. The sentinels assign no evidence; they prove that a nearby fixture with all frozen gates satisfied is not rejected. Four compound cases verify deterministic primary/secondary demotion precedence. Alternative classifications such as eventful-history persistence, regenerated carrier, ordinary slow relaxation, and branch relocation remain visible while the prohibited stronger relabel is rejected.",
        "",
        "The same experiment-local adjudicator is bound by path, schema version, and SHA-256. I4-I8 must consume that exact digest. An adjudicator implementation change requires rerunning I3; a scientific rule or applicability change requires revision and human reacceptance of I2.",
        "",
        "## Focused Boundary Audits",
        "",
        "Held-out exact/inside/outside threshold twins, the complete required/optional control-state truth table, partial authored-carrier subtraction, lineage transport and representation changes, malformed numerical/projector cases, and search/closeout semantics all pass their preregistered expectations. Numerical failures remain numerical failures, duplicate witnesses remain duplicates, unresolved searches remain unresolved, and no fixture can select an extension.",
        "",
        "## Threshold Calibration",
        "",
        "The four I2 calibration recipes were instantiated from preregistered deterministic null fixtures. Their uncertainty bases are inherited replay tolerances, except for the dimensionless occupancy floor, which uses the frozen minimum floor divided by the safety multiplier. They are pre-positive admission floors, not empirical noise estimates. Every later candidate still must apply its row-local numerical uncertainty and the stronger frozen I2 margin rule. No runtime measurement or positive evidence was opened by calibration.",
        "",
    ]
    for row in payload["threshold_calibration"]["records"]:
        lines.append(
            f"- `{row['threshold_id']}` = `{row['instantiated_value_decimal']}` ({row['calibration_status']})"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "I3 is mechanically ready for scientific review. Human acceptance may assign `B2-C2` and open I4 native preparation/reachability search. It cannot assign a GRR rung or support constructibility by itself.",
            "",
            f"Artifact payload SHA-256: `{artifact['payload_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def execute(output_root: Path, report_root: Path) -> dict[str, Any]:
    if git("status", "--porcelain"):
        raise RuntimeError("B2 I3 requires a clean committed execution package")
    input_revision = git("rev-parse", "HEAD")
    _, calibration_artifact = build_payload(input_revision)
    calibration_path = output_root / "b2_i3_threshold_calibration.json"
    write_json(calibration_path, calibration_artifact)

    payload, calibration_artifact_check = build_payload(
        input_revision, sha256_file(calibration_path)
    )
    if calibration_artifact_check != calibration_artifact:
        raise ValueError("I3 calibration artifact changed between deterministic builds")
    payload["input_execution_revision"] = input_revision
    payload["generating_script_path"] = SCRIPT_RELATIVE
    payload["generating_script_sha256"] = sha256_file(Path(__file__))
    payload["config_path"] = CONFIG_RELATIVE
    payload["config_sha256"] = sha256_file(REPO_ROOT / CONFIG_RELATIVE)
    artifact = envelope(payload, "b2_i3_active_nulls_v2", COMMAND)

    artifact_path = output_root / "b2_i3_active_nulls.json"
    report_path = report_root / "b2_i3_active_nulls.md"
    write_json(artifact_path, artifact)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(artifact), encoding="utf-8")

    receipt = finalize_receipt(
        {
            "gate_id": "B2-I3",
            "input_execution_revision": input_revision,
            "generating_script_path": SCRIPT_RELATIVE,
            "generating_script_sha256": sha256_file(Path(__file__)),
            "config_path": CONFIG_RELATIVE,
            "config_sha256": sha256_file(REPO_ROOT / CONFIG_RELATIVE),
            "adjudicator_path": ADJUDICATOR_RELATIVE,
            "adjudicator_schema_version": ADJUDICATOR_SCHEMA_VERSION,
            "adjudicator_sha256": sha256_file(REPO_ROOT / ADJUDICATOR_RELATIVE),
            "supersedes_result_revision": payload["supersession"][
                "supersedes_result_revision"
            ],
            "supersedes_artifact_payload_sha256": payload["supersession"][
                "supersedes_artifact_payload_sha256"
            ],
            "prerequisite_result_receipt_digests": [
                {
                    "path": I2_RECEIPT_RELATIVE,
                    "sha256": sha256_file(REPO_ROOT / I2_RECEIPT_RELATIVE),
                    "receipt_payload_sha256": read_json(
                        REPO_ROOT / I2_RECEIPT_RELATIVE
                    )["receipt_payload_sha256"],
                }
            ],
            "prerequisite_acceptance_anchors": [
                {
                    "path": I2_ANCHOR_RELATIVE,
                    "sha256": sha256_file(REPO_ROOT / I2_ANCHOR_RELATIVE),
                    "acceptance_status": "accepted",
                    "assigned_closeout_rung": "B2-C1",
                    "result_revision": read_json(REPO_ROOT / I2_ANCHOR_RELATIVE)[
                        "result_revision"
                    ],
                }
            ],
            "output_artifact_digests": {
                repo_relative(artifact_path): sha256_file(artifact_path),
                repo_relative(calibration_path): sha256_file(calibration_path),
                repo_relative(report_path): sha256_file(report_path),
            },
            "output_payload_sha256": artifact["payload_sha256"],
            "threshold_calibration_payload_sha256": calibration_artifact[
                "payload_sha256"
            ],
            "status": "awaiting_scientific_review"
            if payload["status"] == "passed"
            else "blocked",
            "blocked_gates": ["B2-I4", "B2-I5", "B2-I6", "B2-I7", "B2-I8"],
            "claim_ceiling": "B2-C2-ready_active_nulls_only_no_positive_constructibility_evidence",
        }
    )
    receipt_path = output_root / "gates/b2_i3_result_receipt.json"
    write_json(receipt_path, receipt)
    return {
        "artifact": artifact,
        "threshold_calibration": calibration_artifact,
        "receipt": receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=EXPERIMENT_ROOT / "outputs")
    parser.add_argument("--report-root", type=Path, default=EXPERIMENT_ROOT / "reports")
    args = parser.parse_args()
    execute(args.output_root, args.report_root)


if __name__ == "__main__":
    main()
