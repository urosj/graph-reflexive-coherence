"""Bind P9-8.4 subjects, prerequisites and comparison contracts; execute no runtime.

The inventory is reconstructed from frozen vectors and retained evidence. It
does not turn construction expectations or accepted nearby cases into new runs.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from pygrc.models.grc_v4_codec import canonical_json_bytes

SPEC = importlib.util.spec_from_file_location(
    "p984_catalog", ROOT / "examples/grcv4/catalog.py"
)
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)

BASE = "implementation/phase-9-grcv4/tranche-8/"
VERIFY = "implementation/phase-9-grcv4/verification/"
DESIGN = "implementation/investigations/grc9v4-constitutive-design/"
VECTORS = "specs/grc-v4-conformance-vectors.json"
OUTPUT = BASE + "P9-8.4a-Coverage.json"
FAMILIES = catalog.FAMILIES
ROLES = ("current", "reset")
PINNED = "G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-3"
STAGES = (
    "source_admission",
    "source_schedule",
    "fresh_trigger_request",
    "mechanical_history_transfer",
    "target_readmission",
    "receipt_publication",
    "target_continuation",
    "final_read",
)
MECHANICS = "tests/models/test_grc_9_v4_expansion.py"
LIFECYCLE = "tests/models/test_grc_9_v4_lifecycle.py"
C_VERIFIERS = {
    "C_OS": LIFECYCLE,
    "C_PC": LIFECYCLE,
    "C_CI": VERIFY + "verify_p983cci_native.py",
    "C_CI_PC": VERIFY + "verify_p983ccipc_native.py",
    "C_RG2b": VERIFY + "verify_p983crg2b_native.py",
}
PREREQUISITES = {
    "OS": [
        "complete_predictor_generated_geometry_corrector_and_split",
        "poststate_charge_and_domain",
    ],
    "CI": [
        "whole_domain_self_map_and_contraction",
        "joint_root_and_output_error",
        "poststate_charge_and_domain",
    ],
    "PC": [
        "whole_base_chart_and_carrier_envelope",
        "old_Z_read_and_same_source_single_Z_write",
        "poststate_charge_and_domain",
    ],
    "CI_PC": [
        "whole_base_chart_and_carrier_envelope",
        "composite_self_map_contraction_and_strict_slack",
        "joint_root_and_output_error",
        "old_Z_read_and_same_source_single_Z_write",
        "poststate_charge_and_domain",
    ],
    "RG2b": [
        "graph_specific_signed_completion_hypotheses",
        "every_inverse_level_residual_and_error",
        "section_contraction_tail_and_input_error",
        "native_current_L2_and_geometry_error_bridges",
        "K_readmission_vs_K_minus_ordinary_entry",
        "poststate_charge_and_domain",
    ],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(canonical_json_bytes(value))


def record_digest(record):
    return digest({k: v for k, v in record.items() if k != "record_digest"})


class Sources:
    def __init__(self, root):
        self.root = Path(root)
        self.bindings = {}

    def bind(self, path):
        require(
            not Path(path).is_absolute() and ".." not in Path(path).parts,
            "nonportable source",
        )
        raw = (self.root / path).read_bytes()
        self.bindings[path] = {"path": path, "sha256": sha(raw)}
        return self.bindings[path]

    def read(self, path):
        self.bind(path)
        return catalog.json_read((self.root / path).read_bytes())

    def symbol(self, path, name):
        self.bind(path)
        tree = ast.parse((self.root / path).read_text())
        require(
            any(
                isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name
                for n in ast.walk(tree)
            ),
            f"missing evidence symbol: {path}:{name}",
        )
        return {"path": path, "symbol": name}


def fixture_inventory(sources, bundle):
    records = []
    for i, row in enumerate(bundle["grc9_expansion_vectors"]):
        request, expected = row["request"], row["expected"]
        records.append(
            {
                "id": row["fixture_id"],
                "kind": "expansion",
                "source": {
                    "path": VECTORS,
                    "pointer": f"/grc9_expansion_vectors/{i}",
                    "jcs_sha256": digest(row),
                },
                "literal_family": expected["identity_payloads"]["target_profile"][
                    "profile_family_id"
                ],
                "capacity_request": request["target_effective_degree"],
                "module_nodes": expected["canonical_module_node_count"],
                "chirality": request["module_chirality"],
                "phase": request["growth_phase"],
                "request": request,
                "event_id": expected["event_id"],
                "target_graph_digest": expected["target_graph_digest"],
                "target_complete_profile_id": expected["target_complete_profile_id"],
                "comparison": row["numeric_comparison_policy"],
                "existing_mechanical_evidence": sources.symbol(
                    MECHANICS, "test_all_frozen_allocation_subjects_and_identity_bytes"
                ),
                "owner": "P9-8.4b",
            }
        )
    expansion = {r["id"]: r for r in records}
    for i, row in enumerate(bundle["grc9_metamorphic_vectors"]):
        base = expansion[row["base_vector_id"]]
        target = expansion.get(row.get("expected_target_vector_id"), base)
        records.append(
            {
                "id": row["vector_id"],
                "kind": row["kind"],
                "source": {
                    "path": VECTORS,
                    "pointer": f"/grc9_metamorphic_vectors/{i}",
                    "jcs_sha256": digest(row),
                },
                "literal_family": base["literal_family"],
                "base": base["id"],
                "target": row.get("expected_target_vector_id"),
                "chirality": base["chirality"],
                "phase": base["phase"],
                "target_chirality": target["chirality"],
                "target_phase": target["phase"],
                "normalization_policy_id": row.get("normalization_policy_id"),
                "existing_mechanical_evidence": sources.symbol(
                    MECHANICS, "test_frozen_metamorphic_vectors"
                ),
                "owner": "P9-8.4e"
                if row["kind"] == "source_edge_input_order_permutation"
                else "P9-8.4f",
            }
        )
    return records


def baseline_budgets(family, raw, sources):
    """Historical comparison ceilings, never default budgets for new subjects."""
    common = {
        "scope": "exact_retained_native_small_subject_only",
        "new_subject_budget": "must_be_bound_and_reviewed_before_execution",
    }
    if family.startswith("A_"):
        common.update(
            kind="independent_interval_full_formula_error",
            numerical_scope=raw["numerical_scope"],
        )
        common["norm"] = (
            "max_coordinate_error_to_full_independent_interval; native solver norms remain separate"
        )
        common["scope_note"] = (
            "numerical_scope_is_not_the_entire_checker; all_bound_oracle_domain_root_and_output_gates_remain_required"
        )
    elif family == "C_OS":
        common.update(
            kind="bounded_dense_crosscheck_not_certified_full_error",
            resource_atol=2e-13,
            resource_rtol=2e-13,
            weighted_stage_atol=3e-12,
            weighted_stage_rtol=3e-12,
        )
        common["comparator"] = sources.symbol(
            LIFECYCLE,
            "test_independent_numerics_and_ten_beat_continuation_for_both_roles",
        )
    elif family == "C_PC":
        common.update(
            kind="bounded_dense_crosscheck_not_certified_full_error",
            current_resource_atol=3e-12,
            rtol=3e-12,
            source_carrier_atol=3e-20,
            geometry="exact_represented_affine_reconstruction",
        )
        common["comparator"] = sources.symbol(LIFECYCLE, "assert_independent_step")
    else:
        limits = {
            "resource": "1/1099511627776",
            "current": "1/1099511627776",
            "geometry": "1/281474976710656",
        }
        if family == "C_CI":
            limits.update(source="1/18446744073709551616")
            owner = VERIFY + "test_p980_realization_numerical.py"
        elif family == "C_CI_PC":
            limits.update(source="1/4503599627370496", carrier="1/281474976710656")
            owner = C_VERIFIERS[family]
        else:
            limits.update(source="1/18446744073709551616")
            owner = C_VERIFIERS[family]
        sources.bind(owner)
        common.update(
            kind="independent_interval_full_formula_error",
            absolute_error_upper_strictly_below=limits,
            comparator_owner=owner,
            norm="max_coordinate_error_to_full_independent_interval; not the section or root norm",
        )
        common["geometry_error_norm"] = (
            "induced_infinity_root_error_bound_in_the_research_comparator"
            if family == "C_CI"
            else "Frobenius_root_error_bound"
            if family == "C_CI_PC"
            else "max_coordinate_H_error_to_independent_section_enclosure"
        )
    return common


def family_inventory(sources):
    inventory = catalog.Catalog(root=sources.root)
    sources.bind(catalog.DEFAULT)
    sources.bind("examples/grcv4/catalog.py")
    families = {}
    for family in FAMILIES:
        item = inventory.entry("native-small-" + family)
        small = inventory.inspect(item["id"])
        raw = sources.read(item["data"]["path"])
        traces = raw.get("side_tool_provenance", [])
        if not traces:
            observations = raw.get("numerical_observations", {})
            traces = observations.get(
                "side_tool_provenance", observations.get("side_tool", [])
            )
        for ref in item["evidence"]:
            sources.bind(ref["path"])
        code = family.lower().replace("_", "")
        native_test = (
            LIFECYCLE
            if family in {"C_OS", "C_PC"}
            else f"tests/models/test_grc_9_v4_{code}.py"
        )
        sources.bind(native_test)
        oracle_owner = (
            VERIFY + f"verify_p983a_{code}_oracle.py"
            if family.startswith("A_")
            else C_VERIFIERS[family]
        )
        sources.bind(oracle_owner)
        if item["format"] == "native-oracle":
            request = raw["request"]
        elif "states" in raw:
            request = raw["states"][family]["request"]
        else:
            request = raw["numerical_observations"]["request"]
        require(
            (
                request["target_effective_degree"],
                request["module_chirality"],
                request["growth_phase"],
            )
            == (52, 1, 3),
            "retained small subject changed",
        )
        realization = family[2:]
        needs = [
            "fresh_graph_profile_reference_and_charge_for_both_roles"
        ] + PREREQUISITES[realization]
        if family.startswith("C_"):
            needs += [
                "strict_C_selector_at_every_required_geometry_and_complete_W_C_tr"
            ]
        else:
            needs += [
                "independent_A_case_oracle_before_runtime_review",
                "fixed_row_incoming_reference_operands_and_positive_W_lineage",
                "final_C_selected_J_A_writer_and_next_read",
            ]
        if "PC" in realization:
            needs += [
                "whole_actual_source_Z_archive_and_whole_target_zero_with_loss_receipt"
            ]
        families[family] = {
            "baseline_catalog_id": item["id"],
            "baseline_data": item["data"],
            "baseline_sides": item["sides"],
            "evidence": item["evidence"],
            "baseline_request": request,
            "runtime_test": native_test,
            "oracle_owner": oracle_owner,
            "retained_claim_traces": traces,
            "claim_trace_scope": "historical_trace_metadata_only; no_new_side_tool_execution_or_status_promotion",
            "reusable_scope": "separately_identified_positive_D52_phase3_native_companion_and_named_pressure_cases; not_frozen_identity_replay",
            "subject_bindings": {
                side: {
                    "profile_id": config["profile"]["complete_profile_id"],
                    "graph_payload_jcs_sha256": digest(config["graph"]),
                    "graph_summary": config["graph_summary"],
                    "scientific_digest": config["scientific_digest"],
                    "reset_digest": config["reset_digest"],
                    "parameters": config["parameters"],
                    "realization_contract": config["profile"]["params_resolved"][
                        "realization"
                    ],
                }
                for side, config in small["configurations"].items()
            },
            "baseline_schedule": {
                "dt": "1/4096",
                "source_current_beats": 1,
                "source_reset_beats": 0,
                "target_beats_per_role": 10,
                "final_read": True,
            },
            "comparison_budget": baseline_budgets(family, raw, sources),
            "prerequisites": needs,
        }
    return families


def coverage_cells(fixtures):
    cells = []
    for fixture in fixtures:
        for family in FAMILIES:
            applicable = (
                fixture["id"] != "G9-EXPAND-C-PC-CARRIER-RESET" or family == "C_PC"
            )
            pinned = fixture["id"] == PINNED
            for role in ROLES:
                disposition = (
                    "pending_case_reconciliation"
                    if pinned
                    else "pending_independent_case_and_admission"
                )
                if not applicable:
                    disposition = "not_applicable_exact_C_PC_identity_fixture"
                cells.append(
                    {
                        "id": f"{fixture['id']}::{family}::{role}",
                        "fixture_id": fixture["id"],
                        "family": family,
                        "role": role,
                        "owner": fixture["owner"],
                        "applicable": applicable,
                        "disposition": disposition,
                        "applicability_reason": "shared_mechanical_case_requires_family_specific_native_companion"
                        if applicable
                        else "literal_C_PC_carrier_reset_fixture_only; this_family_remains_in_all_16_shared_cases_and_3_covariance_cases",
                        "literal_identity_matches_family": family
                        == fixture["literal_family"],
                        "literal_numerical_entry": "blocked_known_frozen_C_OS_source_selector_cutoff"
                        if fixture["literal_family"] == family == "C_OS"
                        else "not_established_for_literal_C_PC_fixture"
                        if applicable and family == fixture["literal_family"]
                        else "other_family_identity_cannot_be_reused",
                        "existing_evidence": ["mechanical_frozen_plan_only"]
                        + (
                            ["native-small-" + family + ":exact_named_companion_only"]
                            if pinned and applicable
                            else []
                        ),
                        "comparison_contracts": [
                            "exact_frozen",
                            "native_companion",
                            "numerical",
                            "history_and_charge",
                        ]
                        + (["covariance"] if fixture["kind"] != "expansion" else []),
                        "stages": {
                            s: "not_applicable"
                            if not applicable
                            else "required_reset_preservation_without_source_beat"
                            if s == "source_schedule" and role == "reset"
                            else "pending_exact_case_mapping"
                            for s in STAGES
                        },
                        "runtime_executed_by_P984a": False,
                    }
                )
    return cells


def larger_inventory(sources):
    inventory = catalog.Catalog(root=sources.root)
    rows = []
    for family in FAMILIES:
        item = inventory.entry("native-large-" + family)
        retained = inventory.inspect(item["id"])
        package = sources.read(item["data"]["path"])
        report = sources.read(item["admission"]["path"])
        for role in ROLES:
            rows.append(
                {
                    "id": f"large::{family}::{role}",
                    "family": family,
                    "role": role,
                    "catalog_id": item["id"],
                    "data": item["data"],
                    "admission": item["admission"],
                    "prepared_digest": package["record_digest"],
                    "numerical_report_digest": report["record_digest"],
                    "recorded_probe_results": {
                        side: report[side][role] for side in ("source", "target")
                    },
                    "recorded_scope": retained["status"],
                    "physical_steps": report["physical_steps"],
                    "events_committed": report["events_committed"],
                    "prerequisite_owner": f"P9-8.4g[{family}]",
                    "execution_owner": f"P9-8.4h[{family}]",
                    "disposition": "blocked_new_cyclic_completion_proof"
                    if family.endswith("RG2b")
                    else "pending_full_admission_and_independent_oracle",
                    "next_requirement": "new_graph_specific_completion_not_tree17_limit_edit"
                    if family.endswith("RG2b")
                    else "resolve_incomplete_probe_then_full_read_step_and_oracle"
                    if retained["status"] == "incomplete"
                    else "certificate_pass_is_not_root_step_event_or_continuation",
                    "runtime_executed_by_P984a": False,
                }
            )
    return rows


def carrier_requirement_crosswalk(fixtures):
    """Keep behavior coverage explicit beside the literal C_PC-only fixture."""
    shared = [
        f["id"]
        for f in fixtures
        if f["kind"] == "expansion" and f["id"] != "G9-EXPAND-C-PC-CARRIER-RESET"
    ]
    covariance = [f["id"] for f in fixtures if f["kind"] != "expansion"]
    rows = []
    for family in ("C_PC", "A_PC", "C_CI_PC", "A_CI_PC"):
        for role in ROLES:
            rows.append(
                {
                    "family": family,
                    "role": role,
                    "owner": "P9-8.4b",
                    "shared_expansion_cells": [
                        f"{f}::{family}::{role}" for f in shared
                    ],
                    "literal_fixture_cells": [
                        f"G9-EXPAND-C-PC-CARRIER-RESET::{family}::{role}"
                    ]
                    if family == "C_PC"
                    else [],
                    "covariance_cells": [f"{f}::{family}::{role}" for f in covariance],
                    "larger_cell": f"large::{family}::{role}",
                    "larger_prerequisite_owner": f"P9-8.4g[{family}]",
                    "larger_execution_owner": f"P9-8.4h[{family}]",
                    "obligations_by_stage": {
                        "mechanical_history_transfer": [
                            "archive_whole_actual_source_Z_for_this_role",
                            "initialize_whole_target_Z_to_canonical_zero",
                            "preserve_unsigned_A_W_by_stable_edge_lineage_and_initialize_new_edges"
                            if family.startswith("A_")
                            else "rederive_C_reference_without_candidate_history",
                        ],
                        "target_readmission": [
                            "fresh_reference_and_full_target_admission_for_this_role",
                            "zero_Z_is_present_carrier_not_absent_history",
                        ],
                        "receipt_publication": [
                            "bind_both_carrier_content_digest_preimages_for_this_role",
                            "declare_carrier_history_loss_without_partial_preservation",
                        ],
                        "target_continuation": [
                            "read_actual_incoming_Z_and_write_Z_once_from_the_same_source",
                        ],
                        "final_read": [
                            "verify_actual_final_carrier_without_history_repair"
                        ],
                    },
                    "disposition": "pending_case_execution_and_independent_comparison",
                    "runtime_executed_by_P984a": False,
                }
            )
    return {
        "authority": {
            "path": "specs/grc-9-v4-spec.md",
            "section": "Whole-lifecycle completion and legacy boundary",
        },
        "applicability_scope": "reviewed_campaign_assignment_not_a_mathematical_impossibility_of_other_family_companions",
        "exclusion_rule": "18_exclusions_apply_only_to_literal_C_PC_fixture; carrier_requirements_remain_mandatory_in_all_four_persistent_families",
        "shared_case_rule": "16_shared_layouts_carry_each_persistent_family_history_requirement; literal_C_PC_fixture_adds_its_frozen_identity_subject",
        "history_policy_scope": "selected_archive_whole_source_and_zero_whole_target_policy; other_admitted_policies_require_separate_case_scope",
        "closure_rule": "every_linked_applicable_cell_must_discharge_its_stage_obligations; a_crosswalk_or_prior_companion_is_not_execution",
        "rows": rows,
    }


def comparison_contracts(bundle):
    return {
        "exact_frozen": {
            "authority": VECTORS,
            "policy": "literal_JCS_bytes_and_exact_discrete_fields; preserve_original_numeric_comparison_policy",
            "compared": [
                "ports_roles_topology_capacity",
                "canonical_preimages_and_digests",
                "resources",
                "history_and_receipts",
            ],
            "resource_atol": 0,
            "resource_rtol": 0,
            "construction_committed_true_is_not_runtime_evidence": True,
        },
        "native_companion": {
            "required_mapping": [
                "base_fixture_binding",
                "new_source_graph_profile_state_reset_specialization",
                "actual_request_and_event_namespace",
                "every_changed_parameter_history_reference_and_resource_share",
                "independent_expected_target_and_numerical_oracle",
            ],
            "identity_rule": "recompute_new_preimages; exact_match_to_the_companion_oracle_not_to_foreign_frozen_digests",
            "source_rule": "derive_target_from_actual_source; expected_target_is_never_supplied_authority",
        },
        "numerical": {
            "preregister": [
                "quantity",
                "stage",
                "role",
                "graph_and_profile",
                "norm",
                "absolute_budget",
                "relative_budget_if_used",
                "full_evaluation_error_method",
                "dt",
                "horizon",
                "oracle_source_binding",
                "precision_and_backend",
                "domain_hypotheses",
            ],
            "new_subject_default_budget": None,
            "rule": "bind_case_specific_budgets_before_runtime_comparison; solver_residual_tolerance_is_not_output_error",
            "certified_comparison": "independent_interval_enclosure_plus_represented_output_error_in_the_declared_norm; require_full_error_within_the_preregistered_budget",
            "bounded_dense_comparison": "abs(actual-reference) <= atol + rtol*abs(reference); explicitly_not_a_certified_full_error_bound",
            "effect_separation": "where_claimed, exceed both full errors plus a separately bound ULP margin; do not borrow a different stage's effect margin",
            "reject": [
                "NaN_or_infinity",
                "shape_or_label_mismatch",
                "unbound_budget_or_norm",
                "missing_role_or_stage",
                "residual_only_error_proxy",
                "certificate_outside_its_domain",
                "posthoc_tolerance_change",
            ],
        },
        "history_and_charge": {
            "roles": list(ROLES),
            "rule": "distinct_immutable_authority_and_charge_targets_for_each_role",
            "transfer": "independent_exact_represented_products_and_declared_rounding; no_resource_repair",
            "A_W": "unsigned_positive_history_by_stable_edge_lineage; never_signed_reference_current",
            "C_W": "absent_history; complete_reference_W_C_tr_is_configuration",
            "Z": "whole_actual_source_archive_and_whole_target_zero_for_selected_loss_policy; absent_is_not_zero",
            "event_time": "no_physical_beat_or_clock_advance_during_event_readmission",
        },
        "covariance": {
            "normalization_policies": bundle["grc9_metamorphic_normalization_policies"],
            "exact": "transport_entire_named_namespace_role_label_port_and_phase_law_then_compare_normalized_discrete_results",
            "numerical": "transport_complete_reference_history_and_operator_operands; use_numerical_contract_per_quantity",
            "signed_edges": "unsigned_W_permutation; signed_J_and_reference_current; matrix_conjugation_for_geometry_and_Z",
            "invalid_controls": [
                "column_only_chart_map",
                "stale_chirality_or_phase",
                "untransported_reference_or_history",
                "raw_digest_equality_substituted_for_covariance",
            ],
        },
    }


def harness_contract():
    return {
        "status": "interface_contract_only; runtime_runner_owned_by_P9-8.4b_and_later_children",
        "input_required": {
            "case_id": "unique_named_case_bound_to_coverage_cell",
            "subject_kind": "literal_frozen | native_companion | larger_proposal | additional_probe",
            "coverage_binding": "record_digest_and_cell_id",
            "source_bindings": "repo_relative_paths_file_hashes_and_selected_JSON_pointers",
            "profile_family_and_id": "exact_family_and_complete_profile_identity",
            "source_state": "complete_native_source_graph_profile_reference_current_reset_specialization_and_charge",
            "source_schedule": "actual_current_beats_and_reset_preservation; do_not_reuse_prebeat_identity",
            "request_recipe": "fresh_trigger_and_request_from_actual_source; expected_IDs_are_assertions_only",
            "oracle_binding": "independent_discrete_and_numerical_expected_subjects; A_acceptance_before_new_runtime_scope",
            "comparison_budgets": "all_numerical.preregister_fields_for_each_quantity_stage_and_role",
            "transformation": "none_or_complete_named_map_and_base_target_subjects",
            "continuation": "explicit_dt_and_finite_steps_for_both_roles_plus_final_reads",
            "execution_budget": "operational_timeout_separate_from_scientific_tolerance",
        },
        "result_required": [
            "case_and_input_binding",
            "code_and_dependency_bindings",
            "actual_owner_and_backend",
            "command",
            "outcome_per_role_graph_stage",
            "actual_input_and_output_identities",
            "actual_receipts_and_commit_state",
            "clock_and_write_counts",
            "independent_comparisons_with_norm_budget_and_error",
            "first_failure_owner_code_stage_and_subject",
            "unexecuted_dependent_stages",
            "elapsed_time_and_operational_budget",
            "review_disposition_and_claim_limits",
        ],
        "outcomes": [
            "passed_named_stage",
            "rejected_by_declared_owner",
            "incomplete_budget",
            "blocked_prerequisite",
            "not_run",
        ],
        "publication_rules": [
            "one_failed_role_prevents_shared_event_success",
            "timeout_or_missing_result_is_never_pass_or_mathematical_rejection",
            "expected_rejection_never_closes_a_required_positive_case",
            "pure_plan_or_certificate_never_sets_event_committed",
            "stage_results_never_imply_user_acceptance",
        ],
    }


def build(root=ROOT):
    sources = Sources(root)
    sources.bind(VERIFY + "prepare_p984a_coverage.py")
    bundle = sources.read(VECTORS)
    for path in (
        "specs/grc-9-v4-spec.md",
        "specs/grc-v4-spec.md",
        DESIGN + "drafts/2026-09-GRC-V4.md",
        BASE + "P9-8.0-AggregateReview.md",
        BASE + "P9-8.0-ReadinessReview.md",
        BASE + "P9-8.3-GraphConfigurationGuide.md",
        BASE + "P9-8.3-CloseoutValidation.json",
        BASE + "P9-8.3-CatalogValidation.json",
        "implementation/phase-9-grcv4/runtime/RuntimeWorkManifest.json",
    ):
        sources.bind(path)
    for path in sorted((Path(root) / "src/pygrc/models").glob("grc*v4*.py")):
        sources.bind(path.relative_to(root).as_posix())
    families = family_inventory(sources)
    fixtures = fixture_inventory(sources, bundle)
    cells = coverage_cells(fixtures)
    claim_path = (
        DESIGN + "decisions/D11G9AxisPreservingExpansionProvenanceSupplement.json"
    )
    claims = sources.read(claim_path)
    atomic = [
        {
            "id": row["fixture_id"],
            "jcs_sha256": digest(row),
            "owner": "P9-8.5",
            "disposition": "outside_P984_runtime_atomicity_campaign",
        }
        for row in bundle["atomic_failure_vectors"]
        if row["fixture_id"].startswith("G9-")
    ]
    result = {
        "schema": "p984a-coverage-and-comparison-contract-v1",
        "date": "2026-10-05",
        "phase": "P9-8.4a",
        "planning_predecessor": "5748b94",
        "disposition": "strengthened_and_own_reviewed; accepted_by_user",
        "acceptance": {
            "date": "2026-10-05",
            "user_instruction": "ok, great, let's strenghten  8.4a, then accept and commit",
            "scope": "P9-8.4a inventory, independent semantic pressure, carrier requirement crosswalk and comparison/harness contracts; P9-8.4b-h runtime and scientific prerequisites remain pending",
        },
        "runtime_executed": False,
        "new_runtime_acceptance": False,
        "hash_convention": "file_bindings_are_SHA256_of_bytes; object_and_record_digests_are_SHA256_of_JCS",
        "counts": {
            "frozen_expansion": 17,
            "frozen_metamorphic": 3,
            "family_role_cells": len(cells),
            "applicable_cells": sum(c["applicable"] for c in cells),
            "explicit_C_PC_fixture_exclusions": sum(not c["applicable"] for c in cells),
            "larger_family_role_cells": 20,
            "atomic_vectors_owned_by_P985": len(atomic),
        },
        "fixture_inventory": fixtures,
        "families": families,
        "coverage_cells": cells,
        "carrier_requirement_crosswalk": carrier_requirement_crosswalk(fixtures),
        "larger_graph_cells": larger_inventory(sources),
        "comparison_contracts": comparison_contracts(bundle),
        "harness_contract": harness_contract(),
        "reusable_pressure": [
            sources.symbol(
                MECHANICS, "test_independent_bfs_oracle_all_small_sizes_and_deep_trees"
            ),
            sources.symbol(
                LIFECYCLE,
                "test_weighted_native_targets_match_paper_equations_and_simplex_extremes",
            ),
            sources.symbol(
                LIFECYCLE,
                "test_weighted_event_covaries_under_order_and_orientation_changes",
            ),
        ],
        "reuse_limit": "existing_pressure_is_named_scope_evidence; inspect_exact_inputs_and_missing_stages_before_marking_a_new_cell_complete",
        "frozen_numerical_obstruction": {
            "family": "C_OS",
            "finding": "unit_reference_star_Lambda_C_1_has_exact_eigenvalue_1; all_literal_C_OS_cases_share_the_blocked_source",
            "checked_source_and_D30_target": sources.symbol(
                VERIFY + "test_p980_readiness.py", "assert_exact_boundary"
            ),
            "native_companion_rule": "preserve_frozen_bytes; separately_identify_and_admit_changed_parameters_histories_shares_and_references",
        },
        "additional_work_register": [
            {
                "owner": "P9-8.4c",
                "required": "D37_D44_and_adjacent_capacity_active_inactive_phase_boundaries",
                "families": list(FAMILIES),
                "roles": list(ROLES),
                "disposition": "pending_named_probe_manifest_and_case_budgets",
            },
            {
                "owner": "P9-8.4d",
                "required": "finite_declared_depths_beyond_D52_and_separately_declared_successive_events_if_claimed",
                "families": list(FAMILIES),
                "roles": list(ROLES),
                "disposition": "pending_size_depth_and_graph_specific_numerical_prerequisites",
            },
            {
                "owner": "P9-8.4e",
                "required": "node_labels_edge_order_and_signed_reorientation_beyond_the_frozen_permutation",
                "families": list(FAMILIES),
                "roles": list(ROLES),
                "disposition": "pending_complete_transform_and_case_contracts",
            },
            {
                "owner": "P9-8.4f",
                "required": "additional_active_inactive_phase_and_partial_transform_controls",
                "families": list(FAMILIES),
                "roles": list(ROLES),
                "disposition": "pending_complete_transform_and_case_contracts",
            },
        ],
        "atomic_handoff": atomic,
        "scientific_claim_mapping": {
            "paper": {
                "path": DESIGN + "drafts/2026-09-GRC-V4.md",
                "sections": [
                    "12.7.1-12.7.5",
                    "Appendix A",
                    "Appendix D",
                    "Appendix E.9-E.10",
                ],
            },
            "side_tool_source": claim_path,
            "equation_contracts": claims["equation_contracts"],
            "status_rule": "retain_support_semantics_verbatim; provenance_and_design_claims_are_not_runtime_proof",
            "per_family_equations": "follow_the_bound_independent_oracle_and_runtime_review; recheck_new_subject_hypotheses",
        },
        "coverage_holds": bundle["coverage_holds"],
        "parent_closure": "no_missing_required_cell_or_silent_family_drop; pending_rejections_and_incompletion_remain_open_without_explicit_scope_change",
    }
    result["source_bindings"] = [sources.bindings[k] for k in sorted(sources.bindings)]
    result["record_digest"] = record_digest(result)
    return result


def validate(record, *, root=ROOT):
    require(
        record.get("record_digest") == record_digest(record), "coverage digest mismatch"
    )
    authoritative = build(root)
    # A rehashed omission, stage promotion, unsupported budget or altered scope
    # must still fail against reconstruction from the bound sources and rules.
    require(
        canonical_json_bytes(record) == canonical_json_bytes(authoritative),
        "coverage differs from source-derived inventory or comparison contracts",
    )
    return record["counts"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the reconstructed inventory; does not execute a case",
    )
    args = parser.parse_args()
    expected = build()
    if args.write:
        (ROOT / OUTPUT).write_text(
            json.dumps(expected, indent=2, allow_nan=False) + "\n"
        )
    else:
        validate(catalog.json_read((ROOT / OUTPUT).read_bytes()))
    print(
        "P984A_COVERAGE_PASS",
        json.dumps(expected["counts"], sort_keys=True),
        "runtime_executed=false",
    )


if __name__ == "__main__":
    main()
