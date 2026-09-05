#!/usr/bin/env python3
"""Deterministic algebra witness for accepted-bounded D11-C T3a."""

from __future__ import annotations

import json

import numpy as np


def main() -> int:
    incidence = np.array(
        [
            [-1.0, 0.0],
            [1.0, -1.0],
            [0.0, 1.0],
        ]
    )
    differential = incidence.T
    h0 = np.diag([1.0, 1.5, 0.8])
    transport_reference = np.array([2.0, 3.0])
    h1 = np.diag(transport_reference)
    g_j = np.diag(1.0 / transport_reference)
    mobility = 0.6 * np.diag(transport_reference)

    h0_inverse_sqrt = np.diag(1.0 / np.sqrt(np.diag(h0)))
    h0_sqrt = np.diag(np.sqrt(np.diag(h0)))
    laplacian_symmetric = (
        h0_inverse_sqrt @ incidence @ h1 @ incidence.T @ h0_inverse_sqrt
    )
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian_symmetric)
    spectral_projector = eigenvectors[:, :2] @ eigenvectors[:, :2].T
    weighted_projector = h0_inverse_sqrt @ spectral_projector @ h0_sqrt

    resource = np.array([1.2, 1.0, 0.8])
    selected_content = weighted_projector @ resource
    retained_nodes = np.tanh(selected_content)
    retained_edges = np.array(
        [
            0.5 * (retained_nodes[0] + retained_nodes[1]),
            0.5 * (retained_nodes[1] + retained_nodes[2]),
        ]
    )

    kappa_m = 0.35
    deformation = np.diag(np.exp(0.5 * kappa_m * retained_edges))
    h1_retained = deformation @ h1 @ deformation
    potential = incidence @ h1_retained @ differential @ resource
    baseline_current = -mobility @ differential @ potential

    identification = h1_retained @ np.linalg.inv(h1)
    delta1_retained = differential @ np.linalg.inv(h0) @ incidence @ h1_retained
    retained_response = np.linalg.inv(np.eye(2) + 0.2 * delta1_retained)
    q_c = identification @ g_j
    flux_response = np.linalg.inv(q_c) @ retained_response @ q_c

    zeta = 0.4
    chi = 1.0
    current_block = np.eye(2) - zeta * chi * flux_response
    total_current = np.linalg.solve(current_block, baseline_current)
    read_current = chi * flux_response @ total_current

    closure_residual = float(
        np.linalg.norm(total_current - baseline_current - zeta * read_current)
    )
    charge_residual = float(abs(np.ones(3) @ incidence @ total_current))
    dissipation_left = float(-(differential @ potential) @ baseline_current)
    dissipation_right = float(
        (differential @ potential) @ mobility @ (differential @ potential)
    )

    potential_off = incidence @ h1 @ differential @ resource
    baseline_off = -mobility @ differential @ potential_off
    direct_path_effect = float(np.linalg.norm(baseline_current - baseline_off))

    edge_reversal = np.diag([1.0, -1.0])
    incidence_reversed = incidence @ edge_reversal
    h1_retained_reversed = edge_reversal @ h1_retained @ edge_reversal.T
    mobility_reversed = edge_reversal @ mobility @ edge_reversal.T
    potential_reversed = (
        incidence_reversed
        @ h1_retained_reversed
        @ incidence_reversed.T
        @ resource
    )
    baseline_reversed = (
        -mobility_reversed @ incidence_reversed.T @ potential_reversed
    )
    orientation_error = float(
        np.linalg.norm(baseline_reversed - edge_reversal @ baseline_current)
    )

    assert closure_residual < 1e-12
    assert charge_residual < 1e-12
    assert np.min(np.linalg.eigvalsh(h1_retained)) > 0
    assert np.min(np.linalg.eigvalsh(mobility)) > 0
    assert abs(dissipation_left - dissipation_right) < 1e-12
    assert direct_path_effect > 0
    assert orientation_error < 1e-12

    result = {
        "profile_id": "C-HM-STIFFNESS-BASELINE-v1",
        "selector_eigenvalues": eigenvalues.tolist(),
        "selected_content": selected_content.tolist(),
        "retained_edge_values": retained_edges.tolist(),
        "retained_h1_diagonal": np.diag(h1_retained).tolist(),
        "baseline_potential": potential.tolist(),
        "baseline_current": baseline_current.tolist(),
        "total_current": total_current.tolist(),
        "read_current": read_current.tolist(),
        "closure_residual_l2": closure_residual,
        "charge_residual_absolute": charge_residual,
        "baseline_dissipation": dissipation_right,
        "retained_geometry_off_effect_l2": direct_path_effect,
        "orientation_covariance_error_l2": orientation_error,
        "claim_ceiling": "finite_algebra_typing_and_control_witness_not_runtime_or_stability_evidence",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
