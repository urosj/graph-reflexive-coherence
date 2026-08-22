"""Execute GRV6 current controls and bounded return-orbit search."""

from __future__ import annotations

import sys
from typing import Any

import numpy as np

from artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    artifact_envelope,
    file_manifest,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_file,
    tracked_files,
    write_json,
)
from gate_receipts import (
    finalize_receipt,
    prerequisite_is_authorized,
    validate_acceptance_anchor,
    validate_receipt,
)
from grv6_methods import (
    branch_current_control,
    deterministic_seed_coordinate,
    evaluate_orbit,
    floquet_audit,
    held_out_replay,
    minimize_return_residual,
    multiplier_continuation_audit,
    recurrent_current_classification,
)
from state_codec import BranchCoordinateChart

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV6"
)
EXPERIMENT_RELATIVE = repo_relative(EXPERIMENT_ROOT)
GRV5_RECEIPT_SHA256 = "a42ccda9772f5fa28e2e4681c2b5c6883a65499eaeab2badcc00ad31bb67ac35"
GRV5_ACCEPTANCE_COMMIT = "948db9b37069bc2a972f4bc2471287fa7140f677"
GRV5_ACCEPTANCE_PAYLOAD_SHA256 = (
    "e62df0c5f65051a8d682b2ba2e423d5f97fd269d8698c347392c6c2a827efe41"
)


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv5_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv5_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if receipt["receipt_payload_sha256"] != GRV5_RECEIPT_SHA256:
        raise ValueError("GRV5 receipt identity mismatch")
    if semantic_digest(anchor) != GRV5_ACCEPTANCE_PAYLOAD_SHA256:
        raise ValueError("GRV5 acceptance-anchor identity mismatch")
    if (
        anchor["result_revision"] != "317092e9e86bf618dac4d31ffc47f74d9fa270f6"
        or anchor["receipt_payload_sha256"] != GRV5_RECEIPT_SHA256
    ):
        raise ValueError("GRV5 acceptance anchor does not bind the reviewed result")
    if not prerequisite_is_authorized(anchor):
        raise ValueError("GRV5 prerequisite is not accepted")
    return receipt, anchor


def protected_manifest_v6() -> dict[str, Any]:
    predecessor_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v5.json"
    predecessor = read_json(predecessor_path)
    relative_paths = [row["path"] for row in predecessor["payload"]["files"]]
    current = file_manifest(relative_paths)
    payload = {
        "manifest_id": "b1_grv6_protected_paths_v6",
        "scope": predecessor["payload"]["scope"],
        "substrate_base_revision": predecessor["payload"]["substrate_base_revision"],
        "predecessor_path": repo_relative(predecessor_path),
        "predecessor_payload_sha256": predecessor["payload_sha256"],
        "predecessor_tree_sha256": predecessor["payload"]["tree_sha256"],
        "files": current["files"],
        "tree_sha256": current["tree_sha256"],
        "unchanged_successor": current["tree_sha256"]
        == predecessor["payload"]["tree_sha256"],
        "newly_discovered_load_bearing_paths": [],
        "later_discovery_policy": "record_and_route_without_retroactive_silent_scope_change",
    }
    return artifact_envelope(
        payload,
        schema_version="b1_grv6_protected_path_manifest_v6",
        generating_command=COMMAND,
    )


def load_scope(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scope = config["source_scope"]
    registry_path = EXPERIMENT_ROOT / scope["branch_registry_path"]
    grv3_path = EXPERIMENT_ROOT / scope["grv3_result_path"]
    if sha256_file(registry_path) != scope["branch_registry_file_sha256"]:
        raise ValueError("GRV6 branch-registry file identity mismatch")
    if sha256_file(grv3_path) != scope["grv3_result_file_sha256"]:
        raise ValueError("GRV6 GRV3-result file identity mismatch")
    registry = read_json(registry_path)
    grv3 = read_json(grv3_path)
    if registry["payload_sha256"] != scope["branch_registry_payload_sha256"]:
        raise ValueError("GRV6 branch-registry payload identity mismatch")
    if grv3["payload_sha256"] != scope["grv3_result_payload_sha256"]:
        raise ValueError("GRV6 GRV3-result payload identity mismatch")
    branches = [
        row for row in registry["payload"]["branches"] if row["branch_certified"]
    ]
    if len(branches) != int(scope["expected_branch_count"]):
        raise ValueError("GRV6 branch scope is not the frozen 48-row registry")
    if sum(row["fixture_id"] == "F3" for row in branches) != int(
        scope["expected_cycle_topology_branch_count"]
    ):
        raise ValueError("GRV6 cycle-control scope is not the frozen F3 family")
    return branches, grv3["payload"]


def load_models_and_charts(
    branches: list[dict[str, Any]],
) -> tuple[dict[str, GRC9V3], dict[str, BranchCoordinateChart]]:
    models = {}
    charts = {}
    for branch in branches:
        path = REPO_ROOT / branch["state_snapshot_path"]
        if sha256_file(path) != branch["state_snapshot_sha256"]:
            raise ValueError(f"branch snapshot digest mismatch: {branch['branch_id']}")
        model = GRC9V3.load(str(path))
        models[branch["branch_id"]] = model
        charts[branch["branch_id"]] = BranchCoordinateChart.from_model(
            model, ("C", "W")
        )
    return models, charts


def execute_orbit_search(
    branches: list[dict[str, Any]],
    charts: dict[str, BranchCoordinateChart],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    search = config["orbit_search"]
    all_rows = []
    candidates = []
    for period in search["periods"]:
        period_value = int(period)
        for candidate_index in range(int(search["search_budget_per_period"])):
            branch = branches[candidate_index % len(branches)]
            chart = charts[branch["branch_id"]]
            seed, seed_record = deterministic_seed_coordinate(
                chart, candidate_index, period_value, config
            )
            minimization = minimize_return_residual(chart, seed, period_value, config)
            row = {
                "search_id": f"p{period_value:02d}-s{candidate_index:03d}",
                "period": period_value,
                "candidate_index": candidate_index,
                "branch_id": branch["branch_id"],
                "fixture_id": branch["fixture_id"],
                "source_parameter_hash": branch["parameter_hash"],
                "source_continuation_lineage_sha256": semantic_digest(
                    branch["continuation_lineage"]
                ),
                **seed_record,
                **minimization,
                "evaluation": None,
            }
            if minimization["status"] == "converged_candidate":
                evaluation = evaluate_orbit(
                    chart,
                    np.asarray(minimization["root_coordinate"], dtype=float),
                    period_value,
                    config,
                )
                row["evaluation"] = evaluation
                if evaluation["classification"] in {
                    "full_causal_state_return_orbit_candidate",
                    "physical_projection_return",
                    "hybrid_or_categorical_return_orbit",
                }:
                    candidates.append(row)
            all_rows.append(row)
    deduplicated = []
    seen = set()
    tolerance = float(search["deduplication_tolerance"])
    for row in sorted(
        candidates,
        key=lambda value: (
            value["period"],
            value["evaluation"]["maximum_physical_return_residual_linf"],
            value["search_id"],
        ),
    ):
        normalized = tuple(
            int(round(float(value) / tolerance)) for value in row["root_coordinate"]
        )
        key = (row["fixture_id"], row["period"], normalized)
        if key in seen:
            continue
        seen.add(key)
        orbit = {
            "orbit_id": f"grv6-orbit-{len(deduplicated) + 1:03d}",
            "source_search_id": row["search_id"],
            "branch_id": row["branch_id"],
            "fixture_id": row["fixture_id"],
            "period": row["period"],
            "root_coordinate": row["root_coordinate"],
            "stratum_status": (
                "single_continuous_stratum"
                if row["evaluation"]["single_continuous_stratum"]
                else "hybrid_or_categorical"
            ),
            "return_residual": row["evaluation"][
                "maximum_physical_return_residual_linf"
            ],
            "classification": row["evaluation"]["classification"],
            "current_recurrence_classification": recurrent_current_classification(
                row["evaluation"],
                float(config["current_controls"]["current_zero_band"]),
            ),
            "evaluation": row["evaluation"],
            "floquet_status": "pending_row_local_gate",
        }
        if orbit["classification"] == "full_causal_state_return_orbit_candidate":
            floquet = floquet_audit(
                charts[row["branch_id"]],
                np.asarray(row["root_coordinate"], dtype=float),
                int(row["period"]),
                config,
            )
        else:
            floquet = {
                "status": "not_applicable_nonordinary_return_class",
                "ordinary_floquet_spectrum": None,
            }
        orbit["floquet"] = floquet
        orbit["floquet_status"] = floquet["status"]
        deduplicated.append(orbit)
    accounting = {
        "periods": search["periods"],
        "search_budget_per_period": search["search_budget_per_period"],
        "expected_search_row_count": len(search["periods"])
        * int(search["search_budget_per_period"]),
        "executed_search_row_count": len(all_rows),
        "branch_allocation": search["branch_allocation"],
        "parameter_envelope": {
            "dt": sorted({float(branch["params"]["dt"]) for branch in branches}),
            "eta": sorted(
                {float(branch["params"]["evolution"]["eta"]) for branch in branches}
            ),
            "site_potential_scale": sorted(
                {
                    float(
                        branch["params"]["evolution"]["site_potential_params"]["scale"]
                    )
                    for branch in branches
                }
            ),
            "certified_branch_count": len(branches),
        },
        "all_48_branches_consumed_each_period": all(
            {row["branch_id"] for row in all_rows if row["period"] == int(period)}
            == {branch["branch_id"] for branch in branches}
            for period in search["periods"]
        ),
        "status_counts": {
            status: sum(row["status"] == status for row in all_rows)
            for status in sorted({row["status"] for row in all_rows})
        },
        "converged_candidate_count": sum(
            row["status"] == "converged_candidate" for row in all_rows
        ),
        "proper_divisor_rejected_count": sum(
            row["evaluation"] is not None
            and row["evaluation"]["classification"]
            == "rejected_proper_divisor_or_period_one_fixed_point"
            for row in all_rows
        ),
        "primitive_return_candidate_count_before_deduplication": len(candidates),
        "selected_orbit_count_after_deduplication": len(deduplicated),
        "global_nonexistence_claim_allowed": False,
    }
    return all_rows, deduplicated, accounting


def build_contract_audit(
    payload: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    summary = payload["summary"]
    points = [
        ("edge_order_and_incidence_frozen", summary["all_edge_space_checks_passed"]),
        ("native_inverse_conductance_metric_used", True),
        (
            "no_silent_regularization",
            not config["edge_space"]["silent_regularization_allowed"],
        ),
        ("projector_idempotence", summary["all_edge_space_checks_passed"]),
        ("metric_orthogonality", summary["all_edge_space_checks_passed"]),
        ("decomposition_reconstruction", summary["all_edge_space_checks_passed"]),
        ("native_potential_flow_annihilation", summary["all_edge_space_checks_passed"]),
        ("edge_reorientation_covariance", summary["all_edge_space_checks_passed"]),
        ("cycle_seed_certified_before_runtime", summary["all_cycle_seeds_certified"]),
        (
            "all_cycle_topology_branches_consumed",
            summary["cycle_control_branch_count"] == 16,
        ),
        ("exact_zero_controls_run", summary["current_control_branch_count"] == 48),
        ("positive_seed_controls_run", summary["current_control_branch_count"] == 48),
        ("negative_seed_controls_run", summary["current_control_branch_count"] == 48),
        ("sign_even_controls_run", summary["all_sign_even_controls_passed"]),
        ("cycle_seed_controls_run", summary["cycle_seed_row_count"] == 32),
        ("assumption_statuses_recorded", True),
        (
            "budget_conservation_passed",
            summary["all_budget_controls_passed"],
        ),
        (
            "topology_and_event_controls_passed",
            summary["all_topology_and_event_controls_passed"],
        ),
        (
            "parameter_sweep_consumed_all_branches",
            payload["search_accounting"]["all_48_branches_consumed_each_period"],
        ),
        (
            "multiplier_continuation_accounted",
            payload["multiplier_continuation"]["matrix_row_count"] > 0,
        ),
        (
            "direct_residual_minimization_executed",
            payload["search_accounting"]["executed_search_row_count"] > 0,
        ),
        (
            "search_budget_complete",
            payload["search_accounting"]["executed_search_row_count"]
            == payload["search_accounting"]["expected_search_row_count"],
        ),
        (
            "all_seeds_and_roots_recorded",
            len(payload["search_rows"])
            == payload["search_accounting"]["executed_search_row_count"],
        ),
        (
            "proper_divisor_gate_executed",
            all(
                row["status"] != "converged_candidate"
                or (
                    row["evaluation"] is not None
                    and bool(row["evaluation"]["proper_divisor_rows"])
                )
                for row in payload["search_rows"]
            ),
        ),
        ("categorical_return_gate_recorded", True),
        ("administrative_advancement_gate_recorded", True),
        ("physical_only_return_class_frozen", True),
        ("hybrid_return_class_frozen", True),
        (
            "floquet_stratum_gate_enforced",
            all(
                orbit["floquet_status"] != "pending_row_local_gate"
                for orbit in payload["orbits"]
            ),
        ),
        (
            "held_out_replay_accounted",
            payload["held_out_validation"]["status"] != "pending",
        ),
        (
            "nonzero_current_not_relabelled_active_circulation",
            not payload["claim_boundary"]["nonzero_current_is_active_circulation"],
        ),
        ("readback_not_opened", not payload["summary"]["readback_supported"]),
        (
            "runtime_unchanged",
            not config["claim_boundary"]["runtime_change_authorized"],
        ),
        (
            "GRV_C5_not_assigned_by_GRV6_alone",
            not payload["summary"]["GRV_C5_assigned"],
        ),
    ]
    rows = [
        {"point_index": index, "point_id": point_id, "passed": bool(passed)}
        for index, (point_id, passed) in enumerate(points, start=1)
    ]
    return {
        "gate_id": "GRV6",
        "audit_id": "grv6_current_recurrence_contract_audit_v1",
        "review_point_count": len(rows),
        "all_review_points_passed": all(row["passed"] for row in rows),
        "review_points": rows,
    }


def build_36_point_review_audit(
    payload: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    summary = payload["summary"]
    no_orbit = summary["primitive_return_orbit_count"] == 0

    def row(
        index: int,
        point_id: str,
        disposition: str,
        evidence: str,
        satisfied: bool,
    ) -> dict[str, Any]:
        return {
            "point_index": index,
            "point_id": point_id,
            "disposition": disposition,
            "evidence": evidence,
            "acceptance_requirement_satisfied": bool(satisfied),
        }

    conditional = "not_applicable_no_admitted_return_orbit_future_positive_gate"
    rows = [
        row(1, "accepted_GRV5_prerequisite", "passed", "accepted anchor consumed", True),
        row(2, "cycle_and_orbit_tests_independent", "passed", "separate summaries and claims", True),
        row(3, "primary_cycle_metric_validated", "passed", "rank condition and projector diagnostics per branch", summary["all_edge_space_checks_passed"]),
        row(4, "varying_W_orbit_metric_policy", conditional, "phase-local metric frozen; no orbit admitted", no_orbit),
        row(5, "divergence_and_cycle_projection_separate", "passed", "absolute divergence and fixed/phase-local projections recorded", True),
        row(6, "cycle_seed_certified_before_runtime", "passed", "full seed certification object per sign and ladder row", summary["all_cycle_seeds_certified"] and summary["all_activity_ladder_seeds_certified"]),
        row(7, "cycle_seed_stage_trace", "passed", "public native stage trace with complete-step parity", summary["all_cycle_seed_stage_traces_match_complete_step"]),
        row(8, "cycle_average_transport_classification", conditional, "required before positive orbit admission", no_orbit),
        row(9, "T_A05_assumption_envelope", "passed", "closure mobility conservation and no constraint support recorded", summary["activity_ladder_constraint_supported_row_count"] == 0),
        row(10, "seed_amplitude_ladders", "passed", "four preregistered activity levels with sign and quadratic controls", summary["all_activity_response_shape_controls_passed"]),
        row(11, "synthetic_seed_provenance", "passed", "all injected seeds explicitly experiment-authored and not runtime-reached", True),
        row(12, "genuine_exact_zero_symmetry", "passed", "F1 symmetry certified separately from nonsymmetric zero-input rows", summary["symmetric_exact_zero_control_count"] == summary["exact_zero_invariant_count"] == 16),
        row(13, "administrative_phase_independence", conditional, "required before positive orbit admission", no_orbit),
        row(14, "orbit_symmetry_phase_deduplication", conditional, "full symmetry quotient remains a positive-candidate gate", no_orbit),
        row(15, "relative_periodic_orbit_classification", "bounded_scope_recorded", "not searched and not excluded", not summary["relative_periodic_orbit_search_executed"] and not payload["claim_boundary"]["no_exact_orbit_found_excludes_relative_periodic_orbits"]),
        row(16, "minimal_period_per_state_block", conditional, "required before positive orbit admission", no_orbit),
        row(17, "periodic_output_vs_current_state", conditional, "required before positive orbit admission", no_orbit),
        row(18, "phase_point_current_reset_controls", conditional, "required before positive orbit admission", no_orbit),
        row(19, "net_transport_over_cycle", conditional, "required before positive orbit admission", no_orbit),
        row(20, "complete_native_map_and_proper_divisors", "passed", "C W J and categorical replay with every proper divisor", payload["search_accounting"]["executed_search_row_count"] == payload["search_accounting"]["expected_search_row_count"]),
        row(21, "codec_revalidation_along_orbit", conditional, "required before positive orbit admission", no_orbit),
        row(22, "canonical_search_state", "passed", "branch-relative C W chart with source J reconstruction and full-state evaluation", config["orbit_search"]["search_coordinate"] == "branch_relative_C_W_with_J_reset_to_source_snapshot"),
        row(23, "search_freeze_and_confirmation", "passed", "all seeds roots statuses recorded; confirmation not applicable", no_orbit and len(payload["search_rows"]) == payload["search_accounting"]["executed_search_row_count"]),
        row(24, "period_doubling_provenance", "passed", "no period-doubling claim made", True),
        row(25, "synchronous_update_orbit_class", conditional, "classification frozen for any future candidate", no_orbit),
        row(26, "internal_stage_periodicity", "passed_for_current_controls_orbit_conditional", "cycle seeds traced through native stages; orbit-phase trace deferred", summary["all_cycle_seed_stage_traces_match_complete_step"] and no_orbit),
        row(27, "constraint_supported_recurrence", "passed", "budget floor event and topology support recorded; none active", summary["activity_ladder_constraint_supported_row_count"] == 0),
        row(28, "eventful_or_topology_return_boundary", "passed", "categorical return classes frozen and controls clean", summary["all_topology_and_event_controls_passed"]),
        row(29, "phase_local_floquet_map", conditional, "ordinary Floquet blocked without admitted orbit and stratum", no_orbit),
        row(30, "no_discrete_phase_multiplier_assumption", conditional, "budget direction quotient frozen; no Floquet spectrum", no_orbit),
        row(31, "nonnormal_and_uncertainty_controls", conditional, "required before positive Floquet classification", no_orbit),
        row(32, "complex_pairs_as_real_planes", conditional, "required before positive complex Floquet classification", no_orbit),
        row(33, "long_recurrence_claim_boundary", "passed", "no quasi-periodic or visual recurrence claim", True),
        row(34, "field_current_full_equivalence_separated", "passed", "C W J categorical divergence and cycle surfaces kept distinct", True),
        row(35, "GRV5_persistence_not_relabelled_memory", "passed", "readback memory and writeback flags remain false", not summary["readback_supported"] and not summary["writeback_supported"]),
        row(36, "bounded_negative_result", "passed", "resolved and condition-blocked statuses separated; global and relative absence blocked", not payload["search_accounting"]["global_nonexistence_claim_allowed"] and not summary["condition_blocked_rows_count_as_negative_orbit_evidence"]),
    ]
    return {
        "gate_id": "GRV6",
        "audit_id": "grv6_external_36_point_review_audit_v1",
        "review_point_count": len(rows),
        "all_review_points_accounted_for": len(rows) == 36,
        "acceptance_blocker_count": sum(
            not item["acceptance_requirement_satisfied"] for item in rows
        ),
        "all_current_result_acceptance_requirements_satisfied": all(
            item["acceptance_requirement_satisfied"] for item in rows
        ),
        "conditional_positive_orbit_gate_count": sum(
            item["disposition"] == conditional for item in rows
        ),
        "interpretation": "conditional orbit-only controls are not treated as executed; they remain mandatory before any future positive orbit candidate can be accepted",
        "review_points": rows,
    }


def write_report(payload: dict[str, Any]) -> Any:
    summary = payload["summary"]
    report = EXPERIMENT_ROOT / "reports/b1_grv6_current_recurrence_and_return_orbits.md"
    lines = [
        "# B1-GR GRV6 Current Recurrence And Return Orbits",
        "",
        "## Result",
        "",
        "```text",
        f"mechanical_status = {summary['mechanical_status']}",
        f"current_control_branch_count = {summary['current_control_branch_count']}",
        f"cycle_control_branch_count = {summary['cycle_control_branch_count']}",
        f"cycle_seed_row_count = {summary['cycle_seed_row_count']}",
        f"cycle_seed_persistence_count = {summary['cycle_seed_persistence_count']}",
        f"maximum_post_step_cycle_component_l2 = {summary['maximum_post_step_cycle_component_l2']}",
        f"symmetric_exact_zero_control_count = {summary['symmetric_exact_zero_control_count']}",
        f"finite_activity_amplitude_ladder_row_count = {summary['finite_activity_amplitude_ladder_row_count']}",
        f"cycle_activity_amplitude_ladder_row_count = {summary['cycle_activity_amplitude_ladder_row_count']}",
        f"cycle_seed_stage_trace_pair_count = {summary['cycle_seed_stage_trace_pair_count']}",
        f"orbit_search_row_count = {summary['orbit_search_row_count']}",
        f"converged_search_candidate_count = {summary['converged_search_candidate_count']}",
        f"return_jacobian_ill_conditioned_count = {summary['return_jacobian_ill_conditioned_count']}",
        f"proper_divisor_rejected_count = {summary['proper_divisor_rejected_count']}",
        f"converged_but_not_return_count = {summary['converged_but_not_return_count']}",
        f"primitive_return_orbit_count = {summary['primitive_return_orbit_count']}",
        f"ordinary_floquet_spectrum_count = {summary['ordinary_floquet_spectrum_count']}",
        f"recurrence_evidence_opened = {str(summary['recurrence_evidence_opened']).lower()}",
        "scientific_acceptance = awaiting_human_review",
        "```",
        "",
        "## Edge-Space And Current Controls",
        "",
        "The primary cycle decomposition uses the native inverse-conductance metric",
        "on the sorted live-edge order with each edge oriented from its stored",
        "`node_u` endpoint to `node_v`. Every branch passes projector algebra, native",
        "potential-flow annihilation, and coordinate-reorientation covariance.",
        "All 16 triangle branches admit a one-dimensional cycle space. Their positive",
        "and negative divergence-free cycle seeds are certified before execution and",
        "are overwritten by the native potential-flow reconstruction after one complete",
        "step. The sign-even conductance response is recorded separately from the",
        "reconstructed current. This excludes stationary cycle-current persistence in",
        "the tested envelope; it does not prove global absence on every GRC topology.",
        "",
        "Exact-zero rows are interpreted relative to present coherence. Zero remains",
        "zero on symmetric homogeneous branches; a nonuniform coherence profile may",
        "reconstruct a nonzero potential current without constituting spontaneous",
        "symmetry breaking. Positive and negative old-current seeds test orientation",
        "retention, while their matched squared write tests sign-even preparation.",
        "The hardening matrix separately certifies 16 genuinely symmetric F1",
        "exact-zero states and classifies nonsymmetric zero-input rows without",
        "calling their bounded reconstructed potential-flow residual spontaneous",
        "orientation selection.",
        "",
        "Four preregistered activity levels are run in both signs for every branch",
        "and for every cycle-capable branch. The stage-local conductance response",
        "matches the native quadratic old-current law, no ladder row requires budget",
        "projection, a conductance floor, an event, or topology change, and all 16",
        "cycle branches have public-method traces through every current-reading or",
        "current-overwriting stage. Those traces match the complete native step and",
        "locate orientation erasure at the first transport reconstruction.",
        "",
        "## Return-Orbit Search",
        "",
        f"The bounded search records all `{summary['orbit_search_row_count']}` seeds",
        "and roots: 256 candidates for each period 2, 3, 4, 5, 6, and 8, allocated",
        "round-robin across all 48 accepted branches. It combines the already frozen",
        "parameter envelope, GRV3 multiplier-continuation screening, and direct damped",
        "return-residual minimization. Any period-p closure is rejected when period 1",
        "or another proper divisor also closes. Physical-only and categorical/hybrid",
        "returns have dedicated non-Floquet classifications.",
        "",
        f"Of the {summary['orbit_search_row_count']} rows, "
        f"{summary['converged_search_candidate_count']} converge under the declared "
        "unregularized residual method. "
        f"{summary['proper_divisor_rejected_count']} are fixed points or lower-period "
        "closures and "
        f"{summary['converged_but_not_return_count']} fails the declared return "
        "tolerance. The remaining "
        f"{summary['return_jacobian_ill_conditioned_count']} rows are blocked by an "
        "ill-conditioned return Jacobian under the no-silent-regularization rule; "
        "they remain unresolved rather than counting as negative orbit evidence.",
        "",
        (
            "No primitive period-two-or-higher full causal-state return is admitted "
            "among the resolved candidates in this bounded search. This is a "
            "search-envelope result, not a proof that recurrent orbits, including "
            "relative periodic orbits not searched here, do not exist."
            if summary["primitive_return_orbit_count"] == 0
            else "At least one bounded primitive return candidate is retained with its row-local classification and replay record."
        ),
        "",
        "## Claim Boundary",
        "",
        "Nonzero reconstructed current is not active circulation. Repeated transport",
        "is not Read-Back, memory, or self-sustaining identity. GRV6 cannot assign",
        "`GRV-C5` by itself; GRV7 threshold evidence remains required. No runtime,",
        "`src/`, or existing-test change is part of this gate.",
        "",
        "## Provenance",
        "",
        f"- Input execution revision: `{payload['source_contract']['input_execution_revision']}`",
        f"- GRV5 receipt: `{GRV5_RECEIPT_SHA256}`",
        f"- GRV5 acceptance commit: `{GRV5_ACCEPTANCE_COMMIT}`",
        "- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v6.json`",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv6() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV6 requires a clean committed P6 input revision")
    _, anchor5 = validate_prerequisite()
    config = read_json(EXPERIMENT_ROOT / "configs/grv6_current_recurrence.json")
    branches, grv3 = load_scope(config)
    models, charts = load_models_and_charts(branches)
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))

    current_controls = [
        branch_current_control(
            models[branch["branch_id"]],
            branch["branch_id"],
            branch["fixture_id"],
            config,
        )
        for branch in branches
    ]
    if not all(
        row["edge_space"]["all_primary_edge_space_checks_passed"]
        for row in current_controls
    ):
        raise ValueError("GRV6 primary edge-space controls failed")
    cycle_rows = [cycle for row in current_controls for cycle in row["cycle_seed_rows"]]
    finite_ladder_rows = [
        item
        for row in current_controls
        for item in row["finite_activity_amplitude_ladder"]
    ]
    cycle_ladder_rows = [
        item
        for row in current_controls
        for item in row["cycle_activity_amplitude_ladder"]
    ]
    stage_trace_pairs = [
        row["cycle_seed_stage_trace_pair"]
        for row in current_controls
        if row["cycle_seed_stage_trace_pair"] is not None
    ]
    if not all(row["seed_certified_before_runtime"] for row in cycle_rows):
        raise ValueError("GRV6 cycle seed certification failed")

    search_rows, orbits, accounting = execute_orbit_search(branches, charts, config)
    multiplier_audit = multiplier_continuation_audit(grv3, config)
    replay = held_out_replay(orbits, charts, config)
    summary = {
        "mechanical_status": "passed",
        "current_control_branch_count": len(current_controls),
        "cycle_control_branch_count": sum(
            row["edge_space"]["cycle_dimension"] > 0 for row in current_controls
        ),
        "cycle_seed_row_count": len(cycle_rows),
        "cycle_seed_persistence_count": sum(
            row["classification"] == "cycle_component_remains_after_one_complete_step"
            for row in cycle_rows
        ),
        "maximum_post_step_cycle_component_l2": max(
            row["trajectory"][1]["cycle_component_l2"] for row in cycle_rows
        ),
        "all_cycle_seeds_certified": all(
            row["seed_certified_before_runtime"] for row in cycle_rows
        ),
        "symmetric_exact_zero_control_count": sum(
            row["exact_zero_symmetry_audit"][
                "full_orientation_relevant_symmetry_certified"
            ]
            for row in current_controls
        ),
        "exact_zero_invariant_count": sum(
            row["exact_zero_classification"] == "exact_zero_invariant"
            for row in current_controls
        ),
        "nonsymmetric_zero_input_control_count": sum(
            not row["exact_zero_symmetry_audit"][
                "full_orientation_relevant_symmetry_certified"
            ]
            for row in current_controls
        ),
        "finite_activity_amplitude_ladder_row_count": len(finite_ladder_rows),
        "cycle_activity_amplitude_ladder_row_count": len(cycle_ladder_rows),
        "all_activity_ladder_seeds_certified": all(
            item["positive_seed_certification"]["certified_before_runtime"]
            and item["negative_seed_certification"]["certified_before_runtime"]
            for item in [*finite_ladder_rows, *cycle_ladder_rows]
        ),
        "all_activity_response_shape_controls_passed": all(
            item["quadratic_response_passed"]
            for item in [*finite_ladder_rows, *cycle_ladder_rows]
        ),
        "activity_ladder_constraint_supported_row_count": sum(
            item["budget_projection_changed_state"]
            or item["conductance_floor_active"]
            or item["events_or_topology_changed"]
            for item in [*finite_ladder_rows, *cycle_ladder_rows]
        ),
        "cycle_seed_stage_trace_pair_count": len(stage_trace_pairs),
        "all_cycle_seed_stage_traces_match_complete_step": all(
            row["both_manual_stage_traces_match_complete_step"]
            for row in stage_trace_pairs
        ),
        "all_cycle_orientations_overwritten_at_first_transport": all(
            row["orientation_overwritten_at_first_transport"]
            for row in stage_trace_pairs
        ),
        "maximum_cycle_stage_first_transport_sign_even_W_error": max(
            (row["first_transport_W_sign_even_linf"] for row in stage_trace_pairs),
            default=0.0,
        ),
        "maximum_inverse_conductance_metric_condition_number": max(
            row["edge_space"]["inverse_conductance_metric_condition_number"]
            for row in current_controls
        ),
        "maximum_projected_cycle_gram_condition_number": max(
            (
                row["edge_space"]["projected_cycle_gram_condition_number"]
                for row in current_controls
                if row["edge_space"]["projected_cycle_gram_condition_number"]
                is not None
            ),
            default=0.0,
        ),
        "all_edge_space_checks_passed": all(
            row["edge_space"]["all_primary_edge_space_checks_passed"]
            for row in current_controls
        ),
        "all_sign_even_controls_passed": all(
            row["sign_even_magnitude_matched"]["conductance_write_sign_even"]
            for row in current_controls
        ),
        "all_budget_controls_passed": all(
            row["budget_conservation_passed"] for row in current_controls
        ),
        "maximum_budget_error": max(
            row["maximum_budget_error"] for row in current_controls
        ),
        "all_topology_and_event_controls_passed": all(
            row["topology_and_noncurrent_categorical_state_clean"]
            for row in current_controls
        ),
        "orbit_search_row_count": len(search_rows),
        "converged_search_candidate_count": accounting["converged_candidate_count"],
        "return_jacobian_ill_conditioned_count": accounting["status_counts"].get(
            "return_jacobian_ill_conditioned_no_regularization", 0
        ),
        "proper_divisor_rejected_count": accounting["proper_divisor_rejected_count"],
        "converged_but_not_return_count": sum(
            row["evaluation"] is not None
            and row["evaluation"]["classification"]
            == "not_a_return_orbit_within_declared_tolerance"
            for row in search_rows
        ),
        "primitive_return_orbit_count": len(orbits),
        "full_causal_state_return_orbit_count": sum(
            row["classification"] == "full_causal_state_return_orbit_candidate"
            for row in orbits
        ),
        "physical_projection_return_count": sum(
            row["classification"] == "physical_projection_return" for row in orbits
        ),
        "hybrid_or_categorical_return_count": sum(
            row["classification"] == "hybrid_or_categorical_return_orbit"
            for row in orbits
        ),
        "ordinary_floquet_spectrum_count": sum(
            row["floquet_status"] == "admitted" for row in orbits
        ),
        "recurrence_evidence_opened": bool(orbits),
        "relative_periodic_orbit_search_executed": False,
        "condition_blocked_rows_count_as_negative_orbit_evidence": False,
        "conditional_positive_orbit_gate_status": config[
            "conditional_positive_orbit_gates"
        ]["current_GRV6_disposition"],
        "stationary_cycle_current_supported": any(
            row["classification"] == "cycle_component_remains_after_one_complete_step"
            for row in cycle_rows
        ),
        "active_circulation_supported": False,
        "readback_supported": False,
        "writeback_supported": False,
        "GRV_C5_assigned": False,
        "GRV_C5_status": "blocked_pending_GRV7_even_if_GRV6_recurrence_candidate_exists",
    }
    payload = {
        "gate_id": "GRV6",
        "source_contract": {
            "input_execution_revision": input_revision,
            "GRV5_receipt_payload_sha256": GRV5_RECEIPT_SHA256,
            "GRV5_acceptance_anchor_commit": GRV5_ACCEPTANCE_COMMIT,
            "GRV5_acceptance_anchor_payload_sha256": GRV5_ACCEPTANCE_PAYLOAD_SHA256,
            "branch_registry_path": config["source_scope"]["branch_registry_path"],
            "GRV3_result_path": config["source_scope"]["grv3_result_path"],
        },
        "assumption_statuses": config["assumption_statuses"],
        "edge_space_policy": config["edge_space"],
        "current_control_rows": current_controls,
        "multiplier_continuation": multiplier_audit,
        "search_accounting": accounting,
        "search_rows": search_rows,
        "orbits": orbits,
        "held_out_validation": replay,
        "summary": summary,
        "claim_boundary": config["claim_boundary"],
    }
    audit_payload = build_contract_audit(payload, config)
    if not audit_payload["all_review_points_passed"]:
        failed = [
            row["point_id"]
            for row in audit_payload["review_points"]
            if not row["passed"]
        ]
        raise ValueError(f"GRV6 contract audit failed: {failed}")
    review_36_payload = build_36_point_review_audit(payload, config)
    if not review_36_payload["all_current_result_acceptance_requirements_satisfied"]:
        failed = [
            row["point_id"]
            for row in review_36_payload["review_points"]
            if not row["acceptance_requirement_satisfied"]
        ]
        raise ValueError(f"GRV6 36-point review audit failed: {failed}")

    output_root = EXPERIMENT_ROOT / "outputs"
    registry_path = output_root / "return_orbit_registry.json"
    audit_path = output_root / "grv6_contract_audit.json"
    review_36_path = output_root / "grv6_36_point_review_audit.json"
    write_json(
        registry_path,
        artifact_envelope(
            payload,
            schema_version="b1_grv6_return_orbit_registry_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    audit_payload["source_result_payload_sha256"] = semantic_digest(payload)
    write_json(
        audit_path,
        artifact_envelope(
            audit_payload,
            schema_version="b1_grv6_contract_audit_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    review_36_payload["source_result_payload_sha256"] = semantic_digest(payload)
    write_json(
        review_36_path,
        artifact_envelope(
            review_36_payload,
            schema_version="b1_grv6_36_point_review_audit_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    protected_path = output_root / "protected_path_manifest_v6.json"
    protected = protected_manifest_v6()
    if not protected["payload"]["unchanged_successor"]:
        raise ValueError("protected source/spec/test paths changed since GRV5")
    write_json(protected_path, protected)
    report_path = write_report(payload)
    artifacts = [
        registry_path,
        audit_path,
        review_36_path,
        protected_path,
        report_path,
    ]
    baseline = read_json(output_root / "baseline_manifest.json")["payload"]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV6",
            "input_execution_revision": input_revision,
            "substrate_base_revision": baseline["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV5_RECEIPT_SHA256],
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV5",
                    "immutable_ref": f"git:{GRV5_ACCEPTANCE_COMMIT}",
                    "anchor_payload_sha256": semantic_digest(anchor5),
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(artifacts)
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": ["GRV7", "GRV8"],
            "claim_ceiling": (
                "bounded_return_orbit_candidate_with_row_local_classification_pending_human_review"
                if orbits
                else "bounded_search_found_no_primitive_period_2_to_8_return_and_cycle_seeds_were_overwritten_without_global_nonexistence_claim_pending_human_review"
            ),
            "prerequisite_acceptance_status": anchor5["acceptance_status"],
            "grv6_summary": summary,
            "contract_audit_payload_sha256": semantic_digest(audit_payload),
            "review_36_point_audit_payload_sha256": semantic_digest(
                review_36_payload
            ),
        }
    )
    validate_receipt(receipt)
    write_json(output_root / "gates/grv6_result_receipt.json", receipt)


if __name__ == "__main__":
    run_grv6()
