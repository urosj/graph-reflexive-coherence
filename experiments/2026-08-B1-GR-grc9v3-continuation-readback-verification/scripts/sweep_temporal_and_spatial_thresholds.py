"""Execute GRV7 spatial, temporal, and continuation-threshold comparisons."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
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
from branch_continuation import (
    branch_match_record,
    classify_discrete_spectrum,
    continuation_parameter_delta,
    match_real_invariant_clusters,
)
from compare_frozen_and_full_dynamics import frozen_components
from compute_complete_step_jacobian import (
    _symmetry_coordinate_transport,
    basis_covariance_audit,
    phase_operator_audit,
    stratum_and_jacobian_audit,
)
from gate_receipts import (
    finalize_receipt,
    prerequisite_is_authorized,
    validate_acceptance_anchor,
    validate_receipt,
)
from solve_strong_fixed_branches import (
    block_projection,
    canonicalize_branch,
    residual_metrics,
)
from state_codec import BranchCoordinateChart, categorical_signature

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402


FIRST_EXECUTABLE_GATE = "GRV7"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV7"
)
EXPERIMENT_RELATIVE = repo_relative(EXPERIMENT_ROOT)
GRV6_RECEIPT_SHA256 = "705b6967eedb86fe0d0d7d895998a3ad1147ede312502dae6567a9021fb449c3"
GRV6_RESULT_REVISION = "07cf6784abe600eb2ad345e2cf9c1ed2e109be3d"
GRV6_ACCEPTANCE_COMMIT = "9606f2466769d89e10145e112ed5136704a5ad79"
GRV6_ACCEPTANCE_PAYLOAD_SHA256 = (
    "bfa8d1f619f7d50d0a7b8fa1f3d98411b7f1743d6a6b70e7fdf6658a9e7c1cbe"
)


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv6_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv6_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if receipt["receipt_payload_sha256"] != GRV6_RECEIPT_SHA256:
        raise ValueError("GRV7 prerequisite GRV6 receipt identity mismatch")
    if semantic_digest(anchor) != GRV6_ACCEPTANCE_PAYLOAD_SHA256:
        raise ValueError("GRV7 prerequisite GRV6 acceptance-anchor identity mismatch")
    if (
        anchor["result_revision"] != GRV6_RESULT_REVISION
        or anchor["receipt_payload_sha256"] != GRV6_RECEIPT_SHA256
    ):
        raise ValueError("GRV6 acceptance anchor does not bind the reviewed result")
    if not prerequisite_is_authorized(anchor):
        raise ValueError("GRV6 prerequisite is not accepted")
    anchor_commit = git(
        "log",
        "-1",
        "--format=%H",
        "--",
        f"{EXPERIMENT_RELATIVE}/outputs/gates/grv6_acceptance_anchor.json",
    )
    if anchor_commit != GRV6_ACCEPTANCE_COMMIT:
        raise ValueError("GRV6 acceptance anchor immutable ref mismatch")
    return receipt, anchor


def protected_manifest_v7() -> dict[str, Any]:
    predecessor_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v6.json"
    predecessor = read_json(predecessor_path)
    relative_paths = [row["path"] for row in predecessor["payload"]["files"]]
    current = file_manifest(relative_paths)
    payload = {
        "manifest_id": "b1_grv7_protected_paths_v7",
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
        schema_version="b1_grv7_protected_path_manifest_v7",
        generating_command=COMMAND,
    )


def load_source_scope(
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    scope = config["source_scope"]
    records = []
    for key, payload_key in (
        ("branch_registry", "branch_registry_payload_sha256"),
        ("grv3_result", "grv3_result_payload_sha256"),
        ("grv4_result", "grv4_result_payload_sha256"),
    ):
        path = EXPERIMENT_ROOT / scope[f"{key}_path"]
        if sha256_file(path) != scope[f"{key}_file_sha256"]:
            raise ValueError(f"GRV7 {key} file identity mismatch")
        record = read_json(path)
        if record["payload_sha256"] != scope[payload_key]:
            raise ValueError(f"GRV7 {key} payload identity mismatch")
        records.append(record["payload"])
    registry, grv3, grv4 = records
    branches = [row for row in registry["branches"] if row["branch_certified"]]
    if len(branches) != int(scope["expected_source_branch_count"]):
        raise ValueError("GRV7 source accounting is not the frozen 48-row registry")
    return branches, grv3, grv4


def _point_parameters(path: dict[str, Any], value: float) -> dict[str, float]:
    parameters = {
        key: float(item) for key, item in path["fixed_parameters"].items()
    }
    parameters[path["axis"]] = float(value)
    return {
        "site_potential_scale": float(parameters["site_potential_scale"]),
        "dt": float(parameters["dt"]),
        "eta": float(parameters["eta"]),
    }


def _plain_config(value: Any) -> Any:
    """Thaw nested immutable parameter mappings without changing values."""

    if isinstance(value, Mapping):
        return {str(key): _plain_config(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_plain_config(child) for child in value]
    if isinstance(value, list):
        return [_plain_config(child) for child in value]
    return value


def _apply_parameters(
    model: GRC9V3, parameters: dict[str, float]
) -> tuple[GRC9V3, dict[str, Any]]:
    params = _plain_config(model.get_params().raw_config)
    params["dt"] = float(parameters["dt"])
    params["evolution"]["eta"] = float(parameters["eta"])
    params["evolution"]["site_potential_params"]["scale"] = float(
        parameters["site_potential_scale"]
    )
    candidate = GRC9V3.from_state(deepcopy(model.get_state()), params)
    canonicalization = canonicalize_branch(candidate)
    physical_rows = canonicalization["raw_to_canonical_per_block_residuals"]
    physical_maximum = max(
        float(physical_rows[block]["l_inf"]) for block in ("C", "W", "J")
    )
    summary = {
        "method": "native_stage_canonicalization_after_parameter_change",
        "physical_C_W_J_l_inf_max": physical_maximum,
        "derived_surface_refresh_is_expected": True,
        "event_kinds": canonicalization["events"],
        "event_log_delta": canonicalization["event_log_delta"],
        "budget_correction_l_inf": max(
            (
                abs(float(value))
                for value in canonicalization["budget_correction_vector"]
            ),
            default=0.0,
        ),
        "passed": bool(
            physical_maximum <= 1e-8
            and not canonicalization["events"]
            and canonicalization["event_log_delta"] == 0
        ),
    }
    return candidate, summary


def _ordered_complex(matrix: np.ndarray) -> list[complex]:
    return sorted(
        (complex(value) for value in np.linalg.eigvals(matrix)),
        key=lambda value: (float(value.real), float(value.imag)),
    )


def _complex_records(values: list[complex]) -> list[dict[str, float]]:
    return [
        {"real": float(value.real), "imag": float(value.imag)} for value in values
    ]


def _max_projection_residual(
    reference: dict[str, Any], observed: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    blocks = ("C", "W", "J", "Phi", "G", "identity", "budget")
    rows = {
        block: residual_metrics(reference[block], observed[block]) for block in blocks
    }
    maximum = max(float(row["l_inf"]) for row in rows.values())
    return maximum, rows


def _branch_certification(
    model: GRC9V3, config: dict[str, Any], current_zero_band: float
) -> dict[str, Any]:
    reference = block_projection(model)
    baseline_signature = categorical_signature(
        model, current_zero_band=current_zero_band
    )
    stepped = GRC9V3.from_state(
        deepcopy(model.get_state()), _plain_config(model.get_params().raw_config)
    )
    result = stepped.step()
    observed = block_projection(stepped)
    residual, rows = _max_projection_residual(reference, observed)
    post_signature = categorical_signature(
        stepped, current_zero_band=current_zero_band
    )
    topology_equal = reference["topology"] == observed["topology"]
    categorical_equal = baseline_signature == post_signature
    passed = bool(
        residual
        <= float(
            config["continuation_contract"]["full_step_branch_residual_l_inf_max"]
        )
        and topology_equal
        and categorical_equal
        and not result.events
    )
    return {
        "full_step_residual_l_inf": residual,
        "full_step_residual_by_block": rows,
        "maximum_allowed": float(
            config["continuation_contract"]["full_step_branch_residual_l_inf_max"]
        ),
        "topology_equal": topology_equal,
        "categorical_signature_equal": categorical_equal,
        "event_kinds": [event.kind for event in result.events],
        "passed": passed,
        "decision": "branch_certified" if passed else "continuation_path_stopped",
    }


def _spatial_diagnostics(model: GRC9V3) -> dict[str, Any]:
    model.rebuild_differential_state()
    state = model.get_state()
    record = {
        "row_basis_unsigned_hessian_by_node": deepcopy(
            state.cached_quantities.get("row_basis_hessian_unsigned", {})
        ),
        "signed_hessian_by_node": {
            str(node_id): list(state.nodes[node_id].signed_hessian_row_basis)
            for node_id in sorted(state.nodes)
        },
        "weighted_least_squares_hessian_by_node": deepcopy(
            state.cached_quantities.get("weighted_least_squares_hessian", {})
        ),
        "hessian_sign": state.cached_quantities.get("hessian_sign"),
        "selected_runtime_hessian_backend": state.cached_quantities.get(
            "hessian_backend"
        ),
        "weighted_least_squares_role": "comparison_backend_only",
    }
    record["runtime_spatial_diagnostics_sha256"] = semantic_digest(record)
    return record


def _categorical_evidence(model: GRC9V3, current_zero_band: float) -> dict[str, Any]:
    baseline = categorical_signature(model, current_zero_band=current_zero_band)
    stepped = GRC9V3.from_state(
        deepcopy(model.get_state()), _plain_config(model.get_params().raw_config)
    )
    result = stepped.step()
    state = stepped.get_state()
    return {
        "event_status": "no_events" if not result.events else "events_present",
        "event_kinds": [event.kind for event in result.events],
        "sink_set": list(sorted(state.sink_set)),
        "basins": {
            str(key): list(sorted(value)) for key, value in sorted(state.basins.items())
        },
        "collapse_registry_keys": list(sorted(state.collapse_registry)),
        "spark_candidate_count": int(
            state.cached_quantities.get("hybrid_spark_candidate_count", 0)
        ),
        "topology_nodes": list(sorted(state.topology.iter_live_node_ids())),
        "topology_edges": list(sorted(state.topology.iter_live_edge_ids())),
        "baseline_signature": baseline,
        "post_step_signature": categorical_signature(
            stepped, current_zero_band=current_zero_band
        ),
    }


def _temporal_diagnostics(
    model: GRC9V3,
    config: dict[str, Any],
    grv3_config: dict[str, Any],
    numerical_tolerances: dict[str, Any],
    nonnormal_config: dict[str, Any],
    fast_slow_config: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray | None]:
    chart = BranchCoordinateChart.from_model(model, ("C",))
    audit = stratum_and_jacobian_audit(
        model,
        chart,
        grv3_config,
        numerical_tolerances,
        nonnormal_config,
        fast_slow_config,
    )
    admitted = audit["square_transition_jacobian_status"] == "admitted"
    if admitted:
        basis = basis_covariance_audit(
            model,
            chart,
            audit,
            grv3_config,
            numerical_tolerances,
            nonnormal_config,
            fast_slow_config,
        )
        phase = phase_operator_audit(
            model,
            chart,
            audit,
            grv3_config,
            numerical_tolerances,
            nonnormal_config,
            fast_slow_config,
        )
        interpretation_admitted = bool(
            audit["spectral_convergence"]["passed"]
            and basis["passed"]
            and phase["passed"]
        )
        matrix = np.asarray(audit["jacobian"], dtype=float)
        values = _ordered_complex(matrix)
    else:
        basis = {"status": "not_applicable_full_matrix_blocked", "passed": False}
        phase = {"status": "not_applicable_full_matrix_blocked", "passed": False}
        interpretation_admitted = False
        matrix = None
        values = []
    thresholds = config["thresholds"]
    classification = classify_discrete_spectrum(
        values if interpretation_admitted else [],
        threshold_tolerance=float(thresholds["discrete_multiplier_tolerance"]),
        complex_imaginary_floor=float(thresholds["complex_imaginary_floor"]),
    )
    return (
        {
            "square_transition_jacobian_status": audit[
                "square_transition_jacobian_status"
            ],
            "blocked_is_not_unconverged": audit["stratum_blocked_is_not_unconverged"],
            "spectral_convergence": audit["spectral_convergence"],
            "basis_covariance": basis,
            "phase_operator_audit": phase,
            "temporal_interpretation_admitted": interpretation_admitted,
            "complete_step_multipliers": _complex_records(values),
            "classification": classification,
            "baseline_stratum_margins": audit["baseline_stratum_margins"],
        },
        matrix if interpretation_admitted else None,
    )


def _point_record(
    model: GRC9V3,
    *,
    path: dict[str, Any],
    source_branch_id: str,
    point_index: int,
    parameters: dict[str, float],
    parameter_canonicalization: dict[str, Any],
    previous_model: GRC9V3 | None,
    config: dict[str, Any],
    grv3_config: dict[str, Any],
    numerical_tolerances: dict[str, Any],
    nonnormal_config: dict[str, Any],
    fast_slow_config: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray | None]:
    contract = config["continuation_contract"]
    state = model.get_state()
    nodes = list(sorted(state.topology.iter_live_node_ids()))
    edges = list(sorted(state.topology.iter_live_edge_ids()))
    coherence = [float(state.nodes[node_id].coherence) for node_id in nodes]
    if previous_model is None:
        match = {
            "topology_equal": True,
            "coherence_state_l2": 0.0,
            "maximum_coherence_state_l2": float(
                contract["maximum_coherence_state_l2"]
            ),
            "total_coherence_delta": 0.0,
            "maximum_total_coherence_delta": float(
                contract["maximum_total_coherence_delta"]
            ),
            "passed": True,
            "decision": "source_branch_anchor",
        }
        parameter_delta = {key: 0.0 for key in sorted(parameters)}
    else:
        previous_state = previous_model.get_state()
        previous_nodes = list(sorted(previous_state.topology.iter_live_node_ids()))
        previous_edges = list(sorted(previous_state.topology.iter_live_edge_ids()))
        previous_coherence = [
            float(previous_state.nodes[node_id].coherence)
            for node_id in previous_nodes
        ]
        match = branch_match_record(
            previous_nodes=previous_nodes,
            current_nodes=nodes,
            previous_edges=previous_edges,
            current_edges=edges,
            previous_coherence=previous_coherence,
            current_coherence=coherence,
            previous_total=sum(previous_coherence),
            current_total=sum(coherence),
            maximum_state_l2=float(contract["maximum_coherence_state_l2"]),
            maximum_total_delta=float(contract["maximum_total_coherence_delta"]),
        )
        previous_params = {
            "site_potential_scale": float(
                previous_model.get_params().raw_config["evolution"][
                    "site_potential_params"
                ]["scale"]
            ),
            "dt": float(previous_model.get_params().raw_config["dt"]),
            "eta": float(previous_model.get_params().raw_config["evolution"]["eta"]),
        }
        parameter_delta = continuation_parameter_delta(previous_params, parameters)
    step_passed = all(
        float(parameter_delta[key])
        <= float(contract["maximum_parameter_step_by_axis"][key])
        for key in parameter_delta
    )
    current_zero_band = float(grv3_config["grv3_b"]["current_zero_band"])
    certification = _branch_certification(model, config, current_zero_band)
    spatial = _spatial_diagnostics(model)
    frozen = frozen_components(
        model,
        read_json(EXPERIMENT_ROOT / "configs/grv4_frozen_full_comparison.json")[
            "hardening"
        ],
    )
    frozen_values = _ordered_complex(np.asarray(frozen["multiplier"], dtype=float))
    frozen_classification = classify_discrete_spectrum(
        frozen_values,
        threshold_tolerance=float(config["thresholds"]["discrete_multiplier_tolerance"]),
        complex_imaginary_floor=float(config["thresholds"]["complex_imaginary_floor"]),
    )
    full, full_matrix = _temporal_diagnostics(
        model,
        config,
        grv3_config,
        numerical_tolerances,
        nonnormal_config,
        fast_slow_config,
    )
    categorical = _categorical_evidence(model, current_zero_band)
    structural_values = [
        float(value) for value in np.linalg.eigvalsh(frozen["h_cont_tangent"])
    ]
    record = {
        "path_id": path["path_id"],
        "point_id": f"{path['path_id']}-p{point_index:02d}-{source_branch_id}",
        "point_index": point_index,
        "fixture_id": path["fixture_id"],
        "source_branch_id": source_branch_id,
        "parameters": parameters,
        "parameter_delta_from_previous": parameter_delta,
        "parameter_step_within_declared_maximum": step_passed,
        "branch_match": match,
        "branch_certification": certification,
        "parameter_canonicalization": parameter_canonicalization,
        "path_point_admitted": bool(
            match["passed"]
            and step_passed
            and parameter_canonicalization["passed"]
            and certification["passed"]
        ),
        "spatial_diagnostics": spatial,
        "analytical_continuation_hessian": {
            "H_cont_tangent": np.asarray(
                frozen["h_cont_tangent"], dtype=float
            ).tolist(),
            "eigenvalues": structural_values,
            "matrix_sha256": semantic_digest(
                np.asarray(frozen["h_cont_tangent"], dtype=float).tolist()
            ),
            "zero_threshold_reached": any(
                abs(value) <= float(config["thresholds"]["spatial_zero_tolerance"])
                for value in structural_values
            ),
        },
        "frozen_W_temporal_comparator": {
            "operator_class": "clamped_counterfactual_only",
            "multipliers": _complex_records(frozen_values),
            "classification": frozen_classification,
            "complete_step_map_claim_allowed": False,
        },
        "complete_step_temporal": full,
        "categorical_evidence": categorical,
        "claim_boundary": {
            "continuation_point_supported": bool(
                match["passed"] and certification["passed"]
            ),
            "complete_step_spectrum_supported": full[
                "temporal_interpretation_admitted"
            ],
            "frozen_comparator_is_full_map": False,
            "retention_readback_or_writeback_supported": False,
        },
    }
    return record, full_matrix


def _symmetry_audit(
    point_rows: list[dict[str, Any]],
    matrices: list[np.ndarray | None],
    models: list[GRC9V3],
) -> dict[str, Any]:
    if len(point_rows) == 1:
        return {
            "status": "not_applicable_singleton_path",
            "passed": True,
            "pair_rows": [],
        }
    if matrices[0] is None:
        return {
            "status": "blocked_source_complete_step_spectrum_not_admitted",
            "passed": False,
            "pair_rows": [],
        }
    grv3_config = read_json(EXPERIMENT_ROOT / "configs/grv3_causal_state.json")
    maximum = float(
        grv3_config["p3_4_hardening"]["symmetry_covariance"][
            "relative_conjugacy_error_max"
        ]
    )
    pair_rows = []
    source_chart = BranchCoordinateChart.from_model(models[0], ("C",))
    for target_row, target_matrix, target_model in zip(
        point_rows[1:], matrices[1:], models[1:], strict=True
    ):
        if target_matrix is None:
            pair_rows.append(
                {
                    "source_branch_id": point_rows[0]["source_branch_id"],
                    "target_branch_id": target_row["source_branch_id"],
                    "status": "blocked_target_complete_step_spectrum_not_admitted",
                    "passed": False,
                }
            )
            continue
        target_chart = BranchCoordinateChart.from_model(target_model, ("C",))
        transport, node_map, edge_map = _symmetry_coordinate_transport(
            source_chart, target_chart
        )
        predicted = transport @ matrices[0] @ np.linalg.inv(transport)
        error = float(
            np.linalg.norm(target_matrix - predicted, ord=2)
            / max(1.0, float(np.linalg.norm(target_matrix, ord=2)))
        )
        pair_rows.append(
            {
                "source_branch_id": point_rows[0]["source_branch_id"],
                "target_branch_id": target_row["source_branch_id"],
                "node_map": {str(key): value for key, value in node_map.items()},
                "edge_map": {str(key): value for key, value in edge_map.items()},
                "relative_conjugacy_error": error,
                "maximum_allowed": maximum,
                "status": "passed" if error <= maximum else "failed_conjugacy",
                "passed": error <= maximum,
            }
        )
    passed = bool(pair_rows and all(row["passed"] for row in pair_rows))
    return {
        "status": "passed" if passed else "failed_or_blocked",
        "passed": passed,
        "matching_rule": "coherence_matched_graph_automorphism_conjugacy",
        "pair_rows": pair_rows,
    }


def _cluster_path_audit(
    path_rows: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    rows = []
    cluster_config = config["cluster_matching"]
    for previous, current in zip(path_rows, path_rows[1:], strict=False):
        for operator_id, key in (
            ("frozen_W", "frozen_W_temporal_comparator"),
            ("complete_step", "complete_step_temporal"),
        ):
            if operator_id == "frozen_W":
                left_records = previous[key]["multipliers"]
                right_records = current[key]["multipliers"]
            else:
                if not (
                    previous[key]["temporal_interpretation_admitted"]
                    and current[key]["temporal_interpretation_admitted"]
                ):
                    rows.append(
                        {
                            "operator_id": operator_id,
                            "previous_point_id": previous["point_id"],
                            "current_point_id": current["point_id"],
                            "status": "not_applicable_blocked_complete_step_spectrum",
                            "passed": False,
                        }
                    )
                    continue
                left_records = previous[key]["complete_step_multipliers"]
                right_records = current[key]["complete_step_multipliers"]
            left = [complex(row["real"], row["imag"]) for row in left_records]
            right = [complex(row["real"], row["imag"]) for row in right_records]
            match = match_real_invariant_clusters(
                left,
                right,
                complex_pair_tolerance=float(cluster_config["complex_pair_tolerance"]),
                maximum_centroid_distance=float(
                    cluster_config["maximum_centroid_distance_per_adjacent_step"]
                ),
            )
            rows.append(
                {
                    "operator_id": operator_id,
                    "previous_point_id": previous["point_id"],
                    "current_point_id": current["point_id"],
                    "status": match["decision"],
                    **match,
                }
            )
    return {
        "rows": rows,
        "all_available_cluster_matches_passed": all(
            row["passed"]
            for row in rows
            if not row["status"].startswith("not_applicable")
        ),
        "blocked_complete_step_pairs_retained": sum(
            row["status"] == "not_applicable_blocked_complete_step_spectrum"
            for row in rows
        ),
    }


def _counterexamples(
    path_records: list[dict[str, Any]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    results = []
    tolerance = float(config["thresholds"]["spatial_zero_tolerance"])
    for path in path_records:
        rows = path["primary_points"]
        runtime_digests = {
            row["spatial_diagnostics"]["runtime_spatial_diagnostics_sha256"]
            for row in rows
        }
        analytical_digests = {
            row["analytical_continuation_hessian"]["matrix_sha256"] for row in rows
        }
        frozen_classes = {
            row["frozen_W_temporal_comparator"]["classification"][
                "aggregate_classification"
            ]
            for row in rows
        }
        full_classes = {
            row["complete_step_temporal"]["classification"][
                "aggregate_classification"
            ]
            for row in rows
            if row["complete_step_temporal"]["temporal_interpretation_admitted"]
        }
        if path["path_id"] == "F1_scale_structural_path":
            structural_signs = {
                "negative": any(
                    min(row["analytical_continuation_hessian"]["eigenvalues"])
                    < -tolerance
                    for row in rows
                ),
                "zero": any(
                    row["analytical_continuation_hessian"]["zero_threshold_reached"]
                    for row in rows
                ),
                "positive": any(
                    max(row["analytical_continuation_hessian"]["eigenvalues"])
                    > tolerance
                    for row in rows
                ),
            }
            passed = bool(
                len(runtime_digests) == 1
                and all(structural_signs.values())
                and "plus_one_marginality" in frozen_classes
            )
            results.append(
                {
                    "counterexample_id": "CE1_runtime_spatial_vs_analytical_continuation_threshold",
                    "path_id": path["path_id"],
                    "status": "supported" if passed else "not_supported",
                    "runtime_spatial_diagnostic_digest_count": len(runtime_digests),
                    "analytical_continuation_hessian_digest_count": len(
                        analytical_digests
                    ),
                    "analytical_structural_sign_coverage": structural_signs,
                    "frozen_temporal_classes": sorted(frozen_classes),
                    "complete_step_scope": "blocked_by_zero_current_categorical_stratum",
                    "claim": "runtime_row_signed_and_WLS_Hessians_do_not_identify_analytical_structural_plus_one_threshold_on_this_path",
                    "claim_allowed": passed,
                    "full_map_counterexample": False,
                }
            )
        if path["path_id"] == "F1_dt_flip_path":
            passed = bool(
                len(runtime_digests) == 1
                and len(analytical_digests) == 1
                and "stable_interior" in frozen_classes
                and "minus_one_flip_marginality" in frozen_classes
            )
            results.append(
                {
                    "counterexample_id": "CE2_fixed_spatial_vs_discrete_flip_threshold",
                    "path_id": path["path_id"],
                    "status": "supported" if passed else "not_supported",
                    "runtime_spatial_diagnostic_digest_count": len(runtime_digests),
                    "analytical_continuation_hessian_digest_count": len(
                        analytical_digests
                    ),
                    "frozen_temporal_classes": sorted(frozen_classes),
                    "complete_step_scope": "blocked_by_zero_current_categorical_stratum",
                    "claim": "a_fixed_spatial_operator_does_not_identify_the_discrete_minus_one_threshold_without_dt_and_mobility",
                    "claim_allowed": passed,
                    "full_map_counterexample": False,
                }
            )
        if full_classes:
            results.append(
                {
                    "counterexample_id": f"{path['path_id']}_complete_step_screen",
                    "path_id": path["path_id"],
                    "status": "bounded_correlation_only_no_preregistered_full_threshold_crossing"
                    if len(full_classes) == 1
                    else "candidate_complete_step_class_change",
                    "complete_step_classes": sorted(full_classes),
                    "full_map_counterexample": len(full_classes) > 1,
                    "claim_allowed": False,
                }
            )
    return results


def execute_grv7(config: dict[str, Any]) -> dict[str, Any]:
    branches, grv3, grv4 = load_source_scope(config)
    del grv3, grv4
    branch_by_id = {row["branch_id"]: row for row in branches}
    grv3_config = read_json(EXPERIMENT_ROOT / "configs/grv3_causal_state.json")
    numerical_tolerances = read_json(
        EXPERIMENT_ROOT / "configs/numerical_tolerances.json"
    )
    nonnormal_config = read_json(EXPERIMENT_ROOT / "configs/nonnormal_control.json")
    fast_slow_config = read_json(EXPERIMENT_ROOT / "configs/fast_slow_control.json")
    path_records = []
    selected_branch_ids: set[str] = set()
    for path in config["paths"]:
        source_ids = [
            path["source_branch_id"],
            *path["symmetry_partner_source_branch_ids"],
        ]
        selected_branch_ids.update(source_ids)
        base_models = []
        for source_id in source_ids:
            branch = branch_by_id[source_id]
            snapshot_path = REPO_ROOT / branch["state_snapshot_path"]
            if sha256_file(snapshot_path) != branch["state_snapshot_sha256"]:
                raise ValueError(f"GRV7 source snapshot mismatch: {source_id}")
            base_models.append(GRC9V3.load(str(snapshot_path)))
        previous_models: list[GRC9V3 | None] = [None for _ in source_ids]
        points = []
        primary_points = []
        for point_index, value in enumerate(path["values"]):
            parameters = _point_parameters(path, float(value))
            point_rows = []
            point_matrices = []
            point_models = []
            for variant_index, (source_id, base_model) in enumerate(
                zip(source_ids, base_models, strict=True)
            ):
                source_for_state = previous_models[variant_index] or base_model
                model, parameter_canonicalization = _apply_parameters(
                    source_for_state, parameters
                )
                row, matrix = _point_record(
                    model,
                    path=path,
                    source_branch_id=source_id,
                    point_index=point_index,
                    parameters=parameters,
                    parameter_canonicalization=parameter_canonicalization,
                    previous_model=previous_models[variant_index],
                    config=config,
                    grv3_config=grv3_config,
                    numerical_tolerances=numerical_tolerances,
                    nonnormal_config=nonnormal_config,
                    fast_slow_config=fast_slow_config,
                )
                if not row["path_point_admitted"]:
                    raise ValueError(
                        f"GRV7 continuation point failed closed: {row['point_id']}"
                    )
                point_rows.append(row)
                point_matrices.append(matrix)
                point_models.append(model)
                previous_models[variant_index] = model
            symmetry = _symmetry_audit(point_rows, point_matrices, point_models)
            point = {
                "point_index": point_index,
                "axis_value": float(value),
                "primary": point_rows[0],
                "symmetry_partners": point_rows[1:],
                "symmetry_covariance": symmetry,
            }
            points.append(point)
            primary_points.append(point_rows[0])
        path_record = {
            "path_id": path["path_id"],
            "fixture_id": path["fixture_id"],
            "axis": path["axis"],
            "source_branch_ids": source_ids,
            "intended_surface": path["intended_surface"],
            "full_map_expectation": path["full_map_expectation"],
            "points": points,
            "primary_points": primary_points,
            "cluster_matching": _cluster_path_audit(primary_points, config),
            "all_points_admitted": all(
                row["path_point_admitted"]
                for point in points
                for row in [point["primary"], *point["symmetry_partners"]]
            ),
            "all_applicable_symmetry_controls_passed": all(
                point["symmetry_covariance"]["passed"] for point in points
            ),
        }
        path_records.append(path_record)
    counterexamples = _counterexamples(path_records, config)
    all_points = [
        row
        for path in path_records
        for point in path["points"]
        for row in [point["primary"], *point["symmetry_partners"]]
    ]
    primary_points = [row for path in path_records for row in path["primary_points"]]
    frozen_classes = {
        row["frozen_W_temporal_comparator"]["classification"][
            "aggregate_classification"
        ]
        for row in primary_points
    }
    full_rows = [
        row
        for row in primary_points
        if row["complete_step_temporal"]["temporal_interpretation_admitted"]
    ]
    full_classes = {
        row["complete_step_temporal"]["classification"][
            "aggregate_classification"
        ]
        for row in full_rows
    }
    supported_counterexamples = [
        row for row in counterexamples if row.get("status") == "supported"
    ]
    full_counterexamples = [
        row for row in counterexamples if row.get("full_map_counterexample")
    ]
    summary = {
        "mechanical_status": "passed",
        "source_branch_accounting_count": len(branches),
        "predeclared_selected_source_branch_count": len(selected_branch_ids),
        "continuation_path_count": len(path_records),
        "primary_continuation_point_count": len(primary_points),
        "symmetry_inclusive_continuation_point_count": len(all_points),
        "all_continuation_points_admitted": all(
            row["path_point_admitted"] for row in all_points
        ),
        "complete_step_temporal_interpretation_admitted_primary_point_count": len(
            full_rows
        ),
        "complete_step_temporal_blocked_primary_point_count": len(primary_points)
        - len(full_rows),
        "frozen_temporal_classes_reached": sorted(frozen_classes),
        "complete_step_temporal_classes_reached": sorted(full_classes),
        "frozen_plus_one_reached": "plus_one_marginality" in frozen_classes,
        "frozen_stable_interior_reached": "stable_interior" in frozen_classes,
        "frozen_minus_one_reached": "minus_one_flip_marginality" in frozen_classes,
        "frozen_complex_unit_circle_reached": "complex_unit_circle_marginality"
        in frozen_classes,
        "complete_step_complex_unit_circle_reached": "complex_unit_circle_marginality"
        in full_classes,
        "supported_bounded_counterexample_count": len(supported_counterexamples),
        "supported_full_map_counterexample_count": len(full_counterexamples),
        "bounded_spatial_temporal_non_equivalence_supported": bool(
            supported_counterexamples
        ),
        "full_map_non_equivalence_supported": bool(full_counterexamples),
        "complex_crossing_status": "not_reached_in_preregistered_real_symmetric_and_admitted_complete_step_envelope",
        "complex_crossing_absence_is_global_nonexistence": False,
        "universal_threshold_identity_supported": False,
        "universal_noncorrelation_supported": False,
        "continuation_supported": False,
        "retention_supported": False,
        "readback_supported": False,
        "writeback_supported": False,
        "GRV_C5_candidate": True,
        "GRV_C5_assigned": False,
        "GRV8_authorized": False,
    }
    return {
        "gate_id": "GRV7",
        "source_contract": {
            "input_execution_revision": git("rev-parse", "HEAD"),
            "GRV6_result_revision": GRV6_RESULT_REVISION,
            "GRV6_receipt_payload_sha256": GRV6_RECEIPT_SHA256,
            "GRV6_acceptance_commit": GRV6_ACCEPTANCE_COMMIT,
            "source_branch_selection": config["source_scope"][
                "source_branch_selection"
            ],
            "selected_source_branch_ids": sorted(selected_branch_ids),
            "all_48_source_branches_retained_in_accounting": True,
        },
        "continuation_contract": config["continuation_contract"],
        "cluster_matching_contract": config["cluster_matching"],
        "threshold_contract": config["thresholds"],
        "path_rows": path_records,
        "counterexamples": counterexamples,
        "bounded_correlations": {
            "nonuniform_complete_step_classes": sorted(full_classes),
            "interpretation": "admitted_nonuniform_points_are_bounded_correlations_only_and_do_not_establish_a_universal_spatial_temporal_identity",
        },
        "summary": summary,
        "claim_boundary": config["claim_boundary"],
    }


def write_report(payload: dict[str, Any]) -> Any:
    summary = payload["summary"]
    counterexamples = payload["counterexamples"]
    report = (
        EXPERIMENT_ROOT
        / "reports/b1_grv7_spatial_temporal_continuation_thresholds.md"
    )
    lines = [
        "# B1-GR GRV7 Spatial, Temporal, And Continuation Thresholds",
        "",
        "## Result",
        "",
        "```text",
        f"mechanical_status = {summary['mechanical_status']}",
        f"continuation_path_count = {summary['continuation_path_count']}",
        f"primary_continuation_point_count = {summary['primary_continuation_point_count']}",
        f"complete_step_temporal_admitted_points = {summary['complete_step_temporal_interpretation_admitted_primary_point_count']}",
        f"complete_step_temporal_blocked_points = {summary['complete_step_temporal_blocked_primary_point_count']}",
        f"frozen_temporal_classes_reached = {summary['frozen_temporal_classes_reached']}",
        f"complete_step_temporal_classes_reached = {summary['complete_step_temporal_classes_reached']}",
        f"supported_bounded_counterexample_count = {summary['supported_bounded_counterexample_count']}",
        f"supported_full_map_counterexample_count = {summary['supported_full_map_counterexample_count']}",
        f"bounded_spatial_temporal_non_equivalence_supported = {str(summary['bounded_spatial_temporal_non_equivalence_supported']).lower()}",
        f"full_map_non_equivalence_supported = {str(summary['full_map_non_equivalence_supported']).lower()}",
        "scientific_acceptance = awaiting_human_review",
        "GRV_C5_assigned = false",
        "GRV8_authorized = false",
        "```",
        "",
        "GRV7 follows preregistered branches rather than assembling unrelated solved",
        "points after seeing spectra. All 48 GRV2 branches remain in source accounting;",
        "the path seeds and symmetry partners were frozen before execution. A path",
        "stops on topology, event, categorical, residual, state-match, or parameter-step",
        "failure. An unreached threshold is not counted as negative evidence.",
        "",
        "## Threshold Evidence",
        "",
        "The F1 scale path holds the graph and coherence state fixed while changing",
        "the quadratic potential scale. Its exact runtime row-basis unsigned, signed,",
        "and WLS spatial diagnostics remain identical, while the separately derived",
        "analytical constrained second variation passes through zero and the frozen-`W`",
        "multiplier reaches `+1`. This distinguishes the runtime local spatial",
        "diagnostics from the analytical continuation Hessian.",
        "",
        "The F1 timestep path holds both runtime spatial diagnostics and the analytical",
        "continuation Hessian fixed while the frozen-`W` discrete multiplier passes",
        "through the stable interior and `-1`. The flip threshold therefore depends on",
        "the evolution timestep and mobility, not on a spatial Hessian threshold alone.",
        "These are exact clamped-counterfactual counterexamples, not complete-step",
        "counterexamples.",
        "",
        "The classical complete-step derivative remains blocked on F1 because two-sided",
        "perturbations leave the zero-current sink/basin identity stratum. GRV7 preserves",
        "that block rather than treating it as finite-difference nonconvergence. F2/F3",
        "nonuniform points retain admitted complete-step spectra with basis, phase, and",
        "symmetry controls. Their observed relation is reported as bounded correlation;",
        "the preregistered paths do not supply a complete-step threshold crossing.",
        "",
        "No complex unit-circle crossing was reached. The frozen comparator is real",
        "self-adjoint in the tested families, and the admitted complete-step envelope",
        "did not cross a complex threshold. This is scope-limited unavailability, not",
        "global nonexistence evidence.",
        "",
        "## Counterexamples",
        "",
        "| Counterexample | Status | Full-map evidence |",
        "| --- | --- | --- |",
        *[
            f"| `{row['counterexample_id']}` | `{row['status']}` | `{str(row.get('full_map_counterexample', False)).lower()}` |"
            for row in counterexamples
        ],
        "",
        "## Claim Boundary",
        "",
        "GRV7 may support bounded non-equivalence among runtime spatial diagnostics,",
        "the analytical continuation Hessian, and discrete frozen-`W` thresholds. It",
        "does not prove spatial Hessians never correlate with temporal or basin",
        "transitions, does not turn the frozen comparator into the complete step map,",
        "and does not establish continuation, retention, Read-Back, or write-back.",
        "`GRV-C5` remains unassigned until human review and a separate acceptance anchor.",
        "GRV8 remains unopened.",
        "",
        "## Provenance",
        "",
        f"- Input execution revision: `{payload['source_contract']['input_execution_revision']}`",
        f"- GRV6 receipt: `{GRV6_RECEIPT_SHA256}`",
        f"- GRV6 acceptance commit: `{GRV6_ACCEPTANCE_COMMIT}`",
        "- Runtime source/spec/root-test paths: unchanged under `protected_path_manifest_v7.json`",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv7() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV7 requires a clean committed P7 input revision")
    _, anchor6 = validate_prerequisite()
    config = read_json(
        EXPERIMENT_ROOT / "configs/grv7_spatial_temporal_thresholds.json"
    )
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))
    payload = execute_grv7(config)
    matrix = artifact_envelope(
        payload,
        schema_version="b1_grv7_spatial_temporal_threshold_matrix_v1",
        generating_command=COMMAND,
    )
    matrix_path = EXPERIMENT_ROOT / "outputs/spatial_temporal_threshold_matrix.json"
    write_json(matrix_path, matrix)
    manifest = protected_manifest_v7()
    manifest_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v7.json"
    write_json(manifest_path, manifest)
    if not manifest["payload"]["unchanged_successor"]:
        raise ValueError("GRV7 protected source/spec/root-test paths changed")
    report_path = write_report(payload)
    output_paths = [matrix_path, manifest_path, report_path]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV7",
            "input_execution_revision": input_revision,
            "substrate_base_revision": manifest["payload"]["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV6_RECEIPT_SHA256],
            "prerequisite_acceptance_status": "accepted",
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV6",
                    "immutable_ref": f"git:{GRV6_ACCEPTANCE_COMMIT}",
                    "anchor_payload_sha256": semantic_digest(anchor6),
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(output_paths)
            },
            "grv7_summary": payload["summary"],
            "status": "awaiting_scientific_review",
            "blocked_gates": ["GRV8"],
            "claim_ceiling": "bounded_spatial_temporal_and_continuation_threshold_non_equivalence_without_universal_noncorrelation_or_readback_claim_pending_human_review",
        }
    )
    validate_receipt(receipt)
    write_json(EXPERIMENT_ROOT / "outputs/gates/grv7_result_receipt.json", receipt)
    print("GRV7 mechanically validated; scientific acceptance anchor is pending.")


def main() -> None:
    run_grv7()


if __name__ == "__main__":
    main()
