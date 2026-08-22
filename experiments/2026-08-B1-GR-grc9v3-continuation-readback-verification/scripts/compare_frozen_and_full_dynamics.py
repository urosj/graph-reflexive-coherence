"""Execute GRV4 fixed-conductance sign and full-recurrence comparisons."""

from __future__ import annotations

from copy import deepcopy
import math
import sys
from typing import Any, Iterable

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
from state_codec import BranchCoordinateChart

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402
from pygrc.models.grc_9_v3_runtime import compute_flux, compute_potential  # noqa: E402


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV4"
)
EXPERIMENT_RELATIVE = repo_relative(EXPERIMENT_ROOT)
GRV3_RESULT_REVISION = "0dedbf96f2a067442ec42ab67707aa694a35fdec"
GRV3_RECEIPT_SHA256 = "83a2650f57fe3d1a814155bf6e8621881d01468b36cde0f1b460af02339b92cc"
GRV3_ACCEPTANCE_COMMIT = "8b82df4f077cecf3af780165e71bfb42b6bf5575"


def _linf(left: Iterable[float], right: Iterable[float]) -> float:
    return max(
        (abs(float(a) - float(b)) for a, b in zip(left, right, strict=True)),
        default=0.0,
    )


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _ordered_eigenvalues(matrix: np.ndarray) -> list[complex]:
    return sorted(
        (complex(value) for value in np.linalg.eigvals(matrix)),
        key=lambda value: (abs(value), value.real, value.imag),
    )


def eigenvalue_set_error(left: np.ndarray, right: np.ndarray) -> float | None:
    left_values = list(np.linalg.eigvals(left))
    unmatched = list(np.linalg.eigvals(right))
    if len(left_values) != len(unmatched):
        return None
    maximum = 0.0
    for value in left_values:
        index = min(
            range(len(unmatched)), key=lambda item: abs(value - unmatched[item])
        )
        maximum = max(maximum, float(abs(value - unmatched[index])))
        unmatched.pop(index)
    return maximum


def multiplier_classification(
    matrix: np.ndarray, *, unstable_slack: float, neutral_tolerance: float
) -> dict[str, Any]:
    rows = []
    for index, value in enumerate(_ordered_eigenvalues(matrix)):
        magnitude = abs(value)
        if magnitude > 1.0 + unstable_slack:
            classification = "unstable"
        elif abs(magnitude - 1.0) <= neutral_tolerance:
            classification = "neutral_or_marginal"
        else:
            classification = "stable"
        rows.append(
            {
                "mode_index": index,
                "eigenvalue": _complex_record(value),
                "magnitude": float(magnitude),
                "classification": classification,
            }
        )
    classes = {row["classification"] for row in rows}
    dominant = (
        "unstable"
        if "unstable" in classes
        else (
            "neutral_or_marginal"
            if "neutral_or_marginal" in classes
            else "stable"
        )
    )
    return {
        "modes": rows,
        "dominant_stability_class": dominant,
        "spectral_radius": max((row["magnitude"] for row in rows), default=0.0),
    }


def _slow_subspace(
    matrix: np.ndarray, minimum_magnitude: float
) -> tuple[np.ndarray, list[complex]]:
    values, vectors = np.linalg.eig(matrix)
    indices = [
        index for index, value in enumerate(values) if abs(value) >= minimum_magnitude
    ]
    if not indices:
        return np.zeros((matrix.shape[0], 0), dtype=complex), []
    selected = vectors[:, indices]
    basis, _ = np.linalg.qr(selected)
    return basis[:, : len(indices)], [complex(values[index]) for index in indices]


def principal_subspace_angle(left: np.ndarray, right: np.ndarray) -> float | None:
    if left.shape[1] != right.shape[1] or left.shape[1] == 0:
        return None
    singular_values = np.linalg.svd(left.conj().T @ right, compute_uv=False)
    minimum = float(np.clip(min(singular_values), 0.0, 1.0))
    return float(math.acos(minimum))


def frozen_components(model: GRC9V3) -> dict[str, Any]:
    chart = BranchCoordinateChart.from_model(model, ("C",))
    state = model.get_state()
    node_index = {node_id: index for index, node_id in enumerate(chart.node_order)}
    incidence = np.zeros((len(chart.node_order), len(chart.edge_order)), dtype=float)
    conductance = np.zeros(len(chart.edge_order), dtype=float)
    for edge_index, edge_id in enumerate(chart.edge_order):
        edge = state.port_edges[edge_id]
        incidence[node_index[edge.node_u], edge_index] = 1.0
        incidence[node_index[edge.node_v], edge_index] = -1.0
        conductance[edge_index] = float(state.base_conductance[edge_id])
    params = chart.params
    evolution = params["evolution"]
    if evolution.get("site_potential_selection") != "quadratic":
        raise ValueError("GRV4 frozen comparator requires the quadratic site potential")
    site = evolution["site_potential_params"]
    kappa = float(evolution["kappa_c"])
    eta = float(evolution["eta"])
    scale = float(site.get("scale", 1.0))
    mu = float(site.get("mu", 0.0))
    dt = float(params["dt"])
    laplacian = incidence @ np.diag(conductance) @ incidence.T
    hessian = kappa * laplacian - 2.0 * scale * np.eye(len(chart.node_order))
    mobility = eta * laplacian
    basis = chart.coherence_basis
    hessian_tangent = basis.T @ hessian @ basis
    mobility_tangent = basis.T @ mobility @ basis
    generator = mobility_tangent @ hessian_tangent
    multiplier = np.eye(generator.shape[0]) + dt * generator
    coherence = np.asarray(
        [float(state.nodes[node_id].coherence) for node_id in chart.node_order],
        dtype=float,
    )
    gradient = kappa * laplacian @ coherence - (2.0 * scale * coherence + mu)
    return {
        "chart": chart,
        "node_order": list(chart.node_order),
        "edge_order": list(chart.edge_order),
        "coherence": coherence,
        "incidence": incidence,
        "conductance": conductance,
        "laplacian": laplacian,
        "hessian": hessian,
        "mobility": mobility,
        "basis": basis,
        "hessian_tangent": hessian_tangent,
        "mobility_tangent": mobility_tangent,
        "generator": generator,
        "multiplier": multiplier,
        "gradient": gradient,
        "branch_velocity": mobility @ gradient,
        "kappa": kappa,
        "eta": eta,
        "scale": scale,
        "mu": mu,
        "dt": dt,
    }


def functional_value(coherence: np.ndarray, components: dict[str, Any]) -> float:
    return float(
        0.5
        * components["kappa"]
        * coherence.T
        @ components["laplacian"]
        @ coherence
        - np.sum(components["scale"] * coherence**2 + components["mu"] * coherence)
    )


def runtime_compatible_frozen_step(
    components: dict[str, Any], coherence: np.ndarray, dt: float
) -> dict[str, Any]:
    chart: BranchCoordinateChart = components["chart"]
    state = deepcopy(chart.base_state)
    for node_id, value in zip(chart.node_order, coherence, strict=True):
        state.nodes[node_id].coherence = float(value)
    params = dict(chart.params)
    params["dt"] = float(dt)
    evolution = params["evolution"]
    compute_potential(state, evolution=evolution)
    compute_flux(state, evolution=evolution)
    potential = np.asarray(
        [float(state.potential[node_id]) for node_id in chart.node_order], dtype=float
    )
    flux = np.asarray(
        [float(state.port_edges[edge_id].flux_uv) for edge_id in chart.edge_order],
        dtype=float,
    )
    staged = GRC9V3.from_state(state, params)
    staged.apply_continuity()
    result_state = staged.get_state()
    result = np.asarray(
        [float(result_state.nodes[node_id].coherence) for node_id in chart.node_order],
        dtype=float,
    )
    return {"potential": potential, "flux": flux, "coherence": result}


def sign_audit_rows(
    branch_id: str, components: dict[str, Any], config: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    rows = []
    maxima = {
        "runtime_stage_equivalence_linf": 0.0,
        "potential_identity_linf": 0.0,
        "flux_identity_linf": 0.0,
        "functional_formula_error": 0.0,
    }
    base = components["coherence"]
    basis = components["basis"]
    hessian = components["hessian"]
    mobility = components["mobility"]
    sign_config = config["sign_audit"]
    for direction_index in range(basis.shape[1]):
        direction = basis[:, direction_index]
        for amplitude in sign_config["tangent_amplitudes"]:
            for direction_sign in (-1.0, 1.0):
                coherence = base + direction_sign * float(amplitude) * direction
                gradient = components["kappa"] * components["laplacian"] @ coherence - (
                    2.0 * components["scale"] * coherence + components["mu"]
                )
                velocity = mobility @ gradient
                semidiscrete_rate = float(gradient.T @ mobility @ gradient)
                expected_flux = (
                    -components["eta"]
                    * np.diag(components["conductance"])
                    @ components["incidence"].T
                    @ gradient
                )
                for dt_multiplier in sign_config["runtime_dt_multipliers"]:
                    dt = components["dt"] * float(dt_multiplier)
                    expected = coherence + dt * velocity
                    staged = runtime_compatible_frozen_step(components, coherence, dt)
                    direct_delta = functional_value(expected, components) - functional_value(
                        coherence, components
                    )
                    formula_delta = float(
                        dt * semidiscrete_rate
                        + 0.5 * dt**2 * velocity.T @ hessian @ velocity
                    )
                    stage_error = _linf(expected, staged["coherence"])
                    potential_error = _linf(gradient, staged["potential"])
                    flux_error = _linf(expected_flux, staged["flux"])
                    formula_error = abs(direct_delta - formula_delta)
                    maxima["runtime_stage_equivalence_linf"] = max(
                        maxima["runtime_stage_equivalence_linf"], stage_error
                    )
                    maxima["potential_identity_linf"] = max(
                        maxima["potential_identity_linf"], potential_error
                    )
                    maxima["flux_identity_linf"] = max(
                        maxima["flux_identity_linf"], flux_error
                    )
                    maxima["functional_formula_error"] = max(
                        maxima["functional_formula_error"], formula_error
                    )
                    rows.append(
                        {
                            "branch_id": branch_id,
                            "direction_index": direction_index,
                            "direction_sign": int(direction_sign),
                            "amplitude": float(amplitude),
                            "dt_multiplier": float(dt_multiplier),
                            "dt": float(dt),
                            "semidiscrete_dP_dt": semidiscrete_rate,
                            "finite_step_P_delta_formula": formula_delta,
                            "finite_step_P_delta_direct": direct_delta,
                            "runtime_stage_equivalence_linf": stage_error,
                            "potential_identity_linf": potential_error,
                            "flux_identity_linf": flux_error,
                            "functional_formula_error": formula_error,
                        }
                    )
    return rows, maxima


def compare_temporal_operator(
    frozen: np.ndarray,
    full: np.ndarray,
    config: dict[str, Any],
    *,
    embed_frozen_in_full: bool,
) -> dict[str, Any]:
    policy = config["full_map_comparison"]
    frozen_class = multiplier_classification(
        frozen,
        unstable_slack=float(policy["unstable_multiplier_slack"]),
        neutral_tolerance=float(policy["neutral_magnitude_tolerance"]),
    )
    full_class = multiplier_classification(
        full,
        unstable_slack=float(policy["unstable_multiplier_slack"]),
        neutral_tolerance=float(policy["neutral_magnitude_tolerance"]),
    )
    threshold = float(policy["slow_subspace_minimum_multiplier_magnitude"])
    frozen_basis, frozen_values = _slow_subspace(frozen, threshold)
    full_basis, full_values = _slow_subspace(full, threshold)
    if embed_frozen_in_full:
        embedded = np.zeros((full.shape[0], frozen_basis.shape[1]), dtype=complex)
        embedded[: frozen.shape[0], :] = frozen_basis
        frozen_basis = embedded
    angle = principal_subspace_angle(frozen_basis, full_basis)
    value_error = eigenvalue_set_error(
        np.diag(np.asarray(frozen_values, dtype=complex)),
        np.diag(np.asarray(full_values, dtype=complex)),
    )
    stability_agrees = (
        frozen_class["dominant_stability_class"]
        == full_class["dominant_stability_class"]
    )
    subspace_agrees = bool(
        angle is not None
        and angle <= float(policy["principal_subspace_angle_max_radians"])
    )
    eigenvalues_agree = bool(
        value_error is not None
        and value_error <= float(policy["eigenvalue_set_error_max"])
    )
    return {
        "frozen_multiplier_classification": frozen_class,
        "full_multiplier_classification": full_class,
        "frozen_slow_multiplier_values": [_complex_record(v) for v in frozen_values],
        "full_slow_multiplier_values": [_complex_record(v) for v in full_values],
        "slow_subspace_dimension_frozen": len(frozen_values),
        "slow_subspace_dimension_full": len(full_values),
        "slow_multiplier_set_error": value_error,
        "principal_subspace_angle_radians": angle,
        "stability_classification_agrees": stability_agrees,
        "slow_multiplier_values_agree": eigenvalues_agree,
        "slow_subspace_agrees": subspace_agrees,
        "verified_stability_or_slow_subspace_disagreement": bool(
            not stability_agrees or (angle is not None and not subspace_agrees)
        ),
        "bounded_relation": (
            "agreement"
            if stability_agrees and eigenvalues_agree and subspace_agrees
            else "bounded_difference"
        ),
    }


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv3_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv3_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if receipt["receipt_payload_sha256"] != GRV3_RECEIPT_SHA256:
        raise ValueError("GRV3 receipt identity mismatch")
    if (
        anchor["result_revision"] != GRV3_RESULT_REVISION
        or anchor["receipt_payload_sha256"] != GRV3_RECEIPT_SHA256
    ):
        raise ValueError("GRV3 acceptance anchor does not bind the required result")
    if not prerequisite_is_authorized(anchor):
        raise ValueError("GRV3 prerequisite is not accepted")
    return receipt, anchor


def protected_manifest_v4() -> dict[str, Any]:
    predecessor_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v3.json"
    predecessor = read_json(predecessor_path)
    relative_paths = [row["path"] for row in predecessor["payload"]["files"]]
    current = file_manifest(relative_paths)
    payload = {
        "manifest_id": "b1_grv4_protected_paths_v4",
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
        schema_version="b1_grv4_protected_path_manifest_v4",
        generating_command=COMMAND,
    )


def _symmetry_audit(branch_rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in branch_rows:
        groups.setdefault(row["symmetry_orbit_id"], []).append(row)
    rows = []
    for orbit_id, members in sorted(groups.items()):
        if len(members) == 1:
            rows.append(
                {
                    "symmetry_orbit_id": orbit_id,
                    "member_branch_ids": [members[0]["branch_id"]],
                    "status": "not_applicable_singleton_orbit",
                    "passed": True,
                }
            )
            continue
        reference = np.asarray(members[0]["frozen_explicit_multiplier"], dtype=float)
        comparisons = []
        for member in members[1:]:
            candidate = np.asarray(member["frozen_explicit_multiplier"], dtype=float)
            error = eigenvalue_set_error(reference, candidate)
            comparisons.append(
                {
                    "branch_id": member["branch_id"],
                    "frozen_multiplier_spectrum_error": error,
                    "passed": bool(error is not None and error <= tolerance),
                }
            )
        rows.append(
            {
                "symmetry_orbit_id": orbit_id,
                "member_branch_ids": [member["branch_id"] for member in members],
                "comparisons": comparisons,
                "status": "passed" if all(row["passed"] for row in comparisons) else "failed",
                "passed": all(row["passed"] for row in comparisons),
            }
        )
    return {
        "rows": rows,
        "orbit_count": len(rows),
        "multirow_orbit_count": sum(len(row["member_branch_ids"]) > 1 for row in rows),
        "failed_orbit_count": sum(not row["passed"] for row in rows),
    }


def write_report(payload: dict[str, Any]):
    summary = payload["summary"]
    report = EXPERIMENT_ROOT / "reports/b1_grv4_frozen_conductance_full_recurrence.md"
    lines = [
        "# B1-GR GRV4 Frozen-Conductance Versus Full Recurrence",
        "",
        "## Result",
        "",
        "```text",
        "gate = GRV4",
        f"mechanical_status = {summary['mechanical_status']}",
        "scientific_acceptance = awaiting_human_review",
        f"branches_audited = {summary['branch_count']}",
        f"standalone_frozen_comparators = {summary['standalone_frozen_comparator_count']}",
        f"primary_full_map_comparisons = {summary['primary_full_comparison_count']}",
        f"full_map_comparisons_blocked_by_GRV3 = {summary['full_comparison_blocked_count']}",
        f"primary_agreement_count = {summary['primary_agreement_count']}",
        f"primary_bounded_difference_count = {summary['primary_bounded_difference_count']}",
        f"verified_strong_disagreement_count = {summary['verified_strong_disagreement_count']}",
        f"runtime_sign_classification = {summary['runtime_sign_classification']}",
        f"GRV_C4_candidate = {str(summary['grv_c4_candidate']).lower()}",
        "continuation = unsupported",
        "retention = unsupported",
        "readback = unsupported",
        "writeback = unsupported",
        "runtime_change_authorized = false",
        "```",
        "",
        "GRV4 constructs an experiment-local fixed-conductance comparator. It does",
        "not alter `GRC9V3.step()` and does not treat the comparator as native runtime",
        "state. The runtime sign follows directly from the implemented equations:",
        "`Phi = gradient(P_G)`, `J = -eta W grad(Phi)`, and continuity therefore",
        "gives `dC/dt = eta L_W gradient(P_G)`. Thus `P_G` is weakly",
        "nondecreasing in the semidiscrete fixed-`W` reduction and `-P_G` is weakly",
        "nonincreasing. Stationary rows count as equality, not strict increase.",
        "",
        "## Discrete And Runtime-Stage Audit",
        "",
        f"The preregistered amplitude/timestep matrix contains {summary['sign_audit_row_count']} rows.",
        f"The maximum staged-runtime versus explicit-map error is `{summary['maximum_runtime_stage_equivalence_linf']:.6g}`.",
        f"The minimum finite-step functional delta is `{summary['minimum_finite_step_P_delta']:.6g}`.",
        "The audit calls the existing potential, flux, and continuity stages while",
        "holding the accepted branch conductance fixed; it excludes conductance",
        "reconstruction and every semantic/topology stage by declaration.",
        "",
        "## Frozen/Full Boundary",
        "",
        "All 48 accepted branches receive a frozen structural comparator. Only the",
        "32 branches with a GRV3-admitted `C` transition matrix receive the primary",
        "full-recurrence comparison. The 16 exact-zero-current boundary branches are",
        "retained as blocked comparisons rather than silently removed. `C-W` is a",
        "secondary diagnostic of evolving-conductance recurrence and never supports",
        "a joint mode or conductance-eliminability claim.",
        "",
        "## Interpretation",
        "",
        (
            "At least one verified branch changes stability class or slow-subspace identity between the two operators."
            if summary["verified_strong_disagreement_count"]
            else "No verified branch changes stability class or slow-subspace identity within the admitted comparison envelope."
        ),
        "Agreement is a bounded result, not proof that frozen conductance is the full",
        "core continuation operator. GRV4 opens no continuation, retention, read-back,",
        "or write-back claim and does not establish global `W` eliminability.",
        "",
        "## Provenance",
        "",
        f"- Input execution revision: `{payload['source_contract']['input_execution_revision']}`",
        f"- GRV3 result revision: `{GRV3_RESULT_REVISION}`",
        f"- GRV3 receipt: `{GRV3_RECEIPT_SHA256}`",
        f"- GRV3 acceptance anchor commit: `{GRV3_ACCEPTANCE_COMMIT}`",
        "- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v4.json`",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv4() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV4 requires a clean committed P4 input revision")
    receipt3, anchor3 = validate_prerequisite()
    config = read_json(EXPERIMENT_ROOT / "configs/grv4_frozen_full_comparison.json")
    scope = config["branch_scope"]
    registry_path = EXPERIMENT_ROOT / scope["source_registry_path"]
    grv3_path = EXPERIMENT_ROOT / scope["grv3_result_path"]
    if sha256_file(registry_path) != scope["source_registry_sha256"]:
        raise ValueError("GRV2 fixed-branch registry file digest mismatch")
    if sha256_file(grv3_path) != scope["grv3_result_sha256"]:
        raise ValueError("GRV3 result file digest mismatch")
    registry = read_json(registry_path)["payload"]
    grv3 = read_json(grv3_path)["payload"]
    branches = [row for row in registry["branches"] if row["branch_certified"]]
    if len(branches) != int(scope["expected_branch_count"]):
        raise ValueError("GRV4 branch scope is not the frozen 48-row registry")
    grv3_by_id = {row["branch_id"]: row for row in grv3["branches"]}
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))
    branch_rows = []
    all_sign_rows = []
    global_maxima = {
        "runtime_stage_equivalence_linf": 0.0,
        "potential_identity_linf": 0.0,
        "flux_identity_linf": 0.0,
        "functional_formula_error": 0.0,
    }
    policy = config["full_map_comparison"]
    for branch in branches:
        snapshot_path = REPO_ROOT / branch["state_snapshot_path"]
        if sha256_file(snapshot_path) != branch["state_snapshot_sha256"]:
            raise ValueError(f"branch snapshot digest mismatch: {branch['branch_id']}")
        model = GRC9V3.load(str(snapshot_path))
        components = frozen_components(model)
        sign_rows, maxima = sign_audit_rows(branch["branch_id"], components, config)
        all_sign_rows.extend(sign_rows)
        for key in global_maxima:
            global_maxima[key] = max(global_maxima[key], maxima[key])
        grv3_row = grv3_by_id[branch["branch_id"]]
        full_audits = grv3_row["coordinate_stratum_and_jacobian_audits"]
        primary_audit = full_audits["C"]
        if primary_audit["square_transition_jacobian_status"] == "admitted":
            primary = {
                "status": "compared",
                "GRV3_temporal_interpretation_allowed": "C"
                in grv3_row["convergence_and_nonnormal_admitted_temporal_coordinates"],
                **compare_temporal_operator(
                    components["multiplier"],
                    np.asarray(primary_audit["jacobian"], dtype=float),
                    config,
                    embed_frozen_in_full=False,
                ),
            }
        else:
            primary = {
                "status": "blocked_by_GRV3_C_coordinate_admission",
                "blocked_reason": primary_audit["square_transition_jacobian_status"],
                "GRV3_temporal_interpretation_allowed": False,
                "verified_stability_or_slow_subspace_disagreement": False,
            }
        secondary_audit = full_audits["C_W"]
        secondary_temporal_allowed = "C_W" in grv3_row[
            "convergence_and_nonnormal_admitted_temporal_coordinates"
        ]
        if (
            secondary_audit["square_transition_jacobian_status"] == "admitted"
            and secondary_temporal_allowed
        ):
            secondary = {
                "status": "compared_as_diagnostic_evolving_conductance_coordinate",
                "GRV3_temporal_interpretation_allowed": True,
                **compare_temporal_operator(
                    components["multiplier"],
                    np.asarray(secondary_audit["jacobian"], dtype=float),
                    config,
                    embed_frozen_in_full=True,
                ),
                "joint_C_W_mode_claim_allowed": False,
            }
        elif secondary_audit["square_transition_jacobian_status"] == "admitted":
            secondary = {
                "status": "diagnostic_matrix_only_GRV3_temporal_interpretation_blocked",
                "GRV3_temporal_interpretation_allowed": False,
                "blocked_reason": secondary_audit["slow_cluster_status"],
                "verified_stability_or_slow_subspace_disagreement": False,
                "joint_C_W_mode_claim_allowed": False,
            }
        else:
            secondary = {
                "status": "blocked_by_GRV3_C_W_coordinate_admission",
                "GRV3_temporal_interpretation_allowed": False,
                "blocked_reason": secondary_audit["square_transition_jacobian_status"],
                "verified_stability_or_slow_subspace_disagreement": False,
                "joint_C_W_mode_claim_allowed": False,
            }
        structural_values = np.linalg.eigvalsh(components["hessian_tangent"])
        branch_rows.append(
            {
                "branch_id": branch["branch_id"],
                "fixture_id": branch["fixture_id"],
                "symmetry_orbit_id": branch["symmetry_orbit_id"],
                "source_snapshot_path": branch["state_snapshot_path"],
                "source_snapshot_sha256": branch["state_snapshot_sha256"],
                "node_order": components["node_order"],
                "edge_order": components["edge_order"],
                "basis_id": config["frozen_comparator"]["basis_id"],
                "coherence_basis": components["basis"].tolist(),
                "fixed_conductance": components["conductance"].tolist(),
                "graph_laplacian": components["laplacian"].tolist(),
                "constrained_second_variation": components["hessian_tangent"].tolist(),
                "fixed_W_mobility": components["mobility_tangent"].tolist(),
                "semidiscrete_generator": components["generator"].tolist(),
                "frozen_explicit_multiplier": components["multiplier"].tolist(),
                "frozen_structural_eigenvalues": [float(value) for value in structural_values],
                "frozen_semidiscrete_rates": [
                    _complex_record(value)
                    for value in _ordered_eigenvalues(components["generator"])
                ],
                "frozen_branch_velocity_linf": float(
                    np.linalg.norm(components["branch_velocity"], ord=np.inf)
                ),
                "frozen_branch_residual_passed": bool(
                    np.linalg.norm(components["branch_velocity"], ord=np.inf)
                    <= float(config["frozen_comparator"]["branch_residual_linf_max"])
                ),
                "sign_audit_row_count": len(sign_rows),
                "sign_audit_maxima": maxima,
                "primary_C_full_recurrence_comparison": primary,
                "secondary_C_W_full_recurrence_comparison": secondary,
                "reduction_and_elimination_assumptions": {
                    "fixed_topology": "satisfied_on_GRV2_branch",
                    "fixed_W": "experiment_local_counterfactual_reduction",
                    "quadratic_site_potential": "satisfied",
                    "conserved_zero_sum_C_tangent": "same_basis_as_GRV3",
                    "identity_spark_choice_growth_boundary_budget_stages": "excluded_from_frozen_comparator",
                    "full_runtime_recurrence_source": "unchanged_GRV3_complete_step_matrix",
                    "W_elimination": "not_claimed",
                    "joint_C_W_mode": "not_claimed"
                },
                "frozen_operator_class": "substrate_reduced",
                "full_core_continuation_operator_claim_allowed": False,
            }
        )
    symmetry = _symmetry_audit(
        branch_rows, float(policy["symmetry_spectrum_error_max"])
    )
    sign_tolerance = float(config["sign_audit"]["functional_delta_tolerance"])
    minimum_delta = min(
        (row["finite_step_P_delta_formula"] for row in all_sign_rows), default=0.0
    )
    positive_delta_count = sum(
        row["finite_step_P_delta_formula"] > sign_tolerance for row in all_sign_rows
    )
    negative_delta_count = sum(
        row["finite_step_P_delta_formula"] < -sign_tolerance for row in all_sign_rows
    )
    if negative_delta_count == 0:
        sign_classification = "P_G_increases_and_negative_P_G_decreases_weakly_over_tested_discrete_sweep"
    else:
        runtime_rows = [row for row in all_sign_rows if row["dt_multiplier"] == 1.0]
        sign_classification = (
            "neither_is_monotone_at_runtime_timestep"
            if any(
                row["finite_step_P_delta_formula"] < -sign_tolerance
                for row in runtime_rows
            )
            else "monotonicity_holds_only_in_small_step_limit"
        )
    primary_rows = [
        row["primary_C_full_recurrence_comparison"]
        for row in branch_rows
        if row["primary_C_full_recurrence_comparison"]["status"] == "compared"
    ]
    disagreements = sum(
        row["verified_stability_or_slow_subspace_disagreement"] for row in primary_rows
    )
    agreements = sum(row["bounded_relation"] == "agreement" for row in primary_rows)
    source_stage_pass = bool(
        global_maxima["runtime_stage_equivalence_linf"]
        <= float(config["sign_audit"]["runtime_stage_equivalence_linf_max"])
        and global_maxima["functional_formula_error"]
        <= float(config["sign_audit"]["functional_formula_consistency_max"])
    )
    primary_count = len(primary_rows)
    blocked_count = len(branch_rows) - primary_count
    mechanical_pass = bool(
        source_stage_pass
        and negative_delta_count == 0
        and all(row["frozen_branch_residual_passed"] for row in branch_rows)
        and primary_count == int(scope["expected_primary_full_comparison_count"])
        and symmetry["failed_orbit_count"] == 0
    )
    summary = {
        "mechanical_status": "passed" if mechanical_pass else "failed",
        "branch_count": len(branch_rows),
        "standalone_frozen_comparator_count": len(branch_rows),
        "primary_full_comparison_count": primary_count,
        "full_comparison_blocked_count": blocked_count,
        "primary_agreement_count": agreements,
        "primary_bounded_difference_count": primary_count - agreements,
        "verified_strong_disagreement_count": disagreements,
        "strong_result_supported": disagreements > 0,
        "runtime_sign_classification": sign_classification,
        "sign_audit_row_count": len(all_sign_rows),
        "positive_functional_delta_row_count": positive_delta_count,
        "stationary_within_tolerance_row_count": len(all_sign_rows)
        - positive_delta_count
        - negative_delta_count,
        "negative_functional_delta_row_count": negative_delta_count,
        "minimum_finite_step_P_delta": minimum_delta,
        "maximum_runtime_stage_equivalence_linf": global_maxima[
            "runtime_stage_equivalence_linf"
        ],
        "maximum_potential_identity_linf": global_maxima["potential_identity_linf"],
        "maximum_flux_identity_linf": global_maxima["flux_identity_linf"],
        "maximum_functional_formula_error": global_maxima["functional_formula_error"],
        "symmetry_orbit_count": symmetry["orbit_count"],
        "symmetry_failed_orbit_count": symmetry["failed_orbit_count"],
        "grv_c4_candidate": mechanical_pass,
        "continuation_supported": False,
        "retention_supported": False,
        "readback_supported": False,
        "writeback_supported": False,
    }
    if not mechanical_pass:
        raise ValueError(f"GRV4 mechanical gates failed: {summary}")
    payload = {
        "gate_id": "GRV4",
        "source_contract": {
            "input_execution_revision": input_revision,
            "GRV3_result_revision": GRV3_RESULT_REVISION,
            "GRV3_receipt_payload_sha256": GRV3_RECEIPT_SHA256,
            "GRV3_acceptance_anchor_commit": GRV3_ACCEPTANCE_COMMIT,
            "branch_registry_path": scope["source_registry_path"],
            "GRV3_result_path": scope["grv3_result_path"],
        },
        "sign_contract": config["sign_audit"],
        "frozen_comparator_contract": config["frozen_comparator"],
        "full_map_comparison_contract": config["full_map_comparison"],
        "branch_rows": branch_rows,
        "sign_audit_rows": all_sign_rows,
        "symmetry_covariance_audit": symmetry,
        "summary": summary,
        "claim_boundary": {
            **config["claim_boundary"],
            "GRV_C4_candidate_pending_human_review": mechanical_pass,
            "full_core_continuation_operator_supported": False,
        },
    }
    output_root = EXPERIMENT_ROOT / "outputs"
    result_path = output_root / "frozen_full_comparison.json"
    write_json(
        result_path,
        artifact_envelope(
            payload,
            schema_version="b1_grv4_frozen_full_comparison_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    protected_path = output_root / "protected_path_manifest_v4.json"
    protected = protected_manifest_v4()
    if not protected["payload"]["unchanged_successor"]:
        raise ValueError("protected source/spec/test paths changed since GRV3")
    write_json(protected_path, protected)
    report_path = write_report(payload)
    artifacts = [result_path, protected_path, report_path]
    baseline = read_json(output_root / "baseline_manifest.json")["payload"]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV4",
            "input_execution_revision": input_revision,
            "substrate_base_revision": baseline["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV3_RECEIPT_SHA256],
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV3",
                    "immutable_ref": f"git:{GRV3_ACCEPTANCE_COMMIT}",
                    "anchor_payload_sha256": semantic_digest(anchor3),
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(artifacts)
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": [f"GRV{index}" for index in range(5, 9)],
            "claim_ceiling": "substrate_reduced_frozen_W_comparator_and_bounded_full_recurrence_relation_pending_human_review",
            "prerequisite_receipt_status": receipt3["status"],
            "grv4_summary": summary,
        }
    )
    validate_receipt(receipt)
    write_json(output_root / "gates/grv4_result_receipt.json", receipt)


def main() -> None:
    run_grv4()
    print("GRV4 mechanically validated; scientific acceptance anchor is pending.")


if __name__ == "__main__":
    main()
