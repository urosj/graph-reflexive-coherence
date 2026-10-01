"""Configurable Candidate C grids with strict public OS/CI/PC/CI+PC/RG2b steps.

The floating eigenspectrum proposes a nontrivial selector cutoff during setup.
Production's exact inertia and stage certificates decide admission. No profile
changes after the first public step, and no provisional step is counted as a run.
Run with PYTHONPATH=src:.:tests from the repository root.
"""

import argparse
import hashlib
import json
import math
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

from examples.grcv4.grid_transport import (
    DEFAULT_COLS,
    DEFAULT_ROWS,
    grid_spec,
    run_inputs,
)
from pygrc.models import grc_v4_rg2b_graph as rg
from pygrc.models.grc_v4_candidate_c import CandidateCStageError
from pygrc.models.grc_v4_ci import CIContractionCertificate, CIStageError
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_pc import PCEnvelopeCertificate
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models.grc_v4_realizations import CandidateCOSPass, OSStageError
from pygrc.models.grc_v4_rg2b import RG2bCertificate, RG2bStageError
from tests.models.test_grc_v4_candidate_c import current_fixture
from tests.models.test_grc_v4_ci import configure as ci_configure
from tests.models.test_grc_v4_cipc import configure as cipc_configure
from tests.models.test_grc_v4_pc import configure as pc_configure
from tests.models.test_grc_v4_profile import reidentify

REALIZATIONS = ("OS", "CI", "PC", "CI+PC", "RG2b")
CERTIFICATES = {
    "OS": CandidateCOSPass,
    "CI": CIContractionCertificate,
    "PC": PCEnvelopeCertificate,
    "CI+PC": CIContractionCertificate,
    "RG2b": RG2bCertificate,
}


def _selector_cutoff(graph, weights):
    """Choose between the first two positive reference eigenvalues."""
    incidence = np.asarray(graph.incidence, dtype=float)
    hodge = np.diag([weights[e] for e in graph.live_edge_ids])
    eigenvalues = np.linalg.eigvalsh(incidence @ hodge @ incidence.T)
    if len(eigenvalues) < 3 or eigenvalues[1] <= 0 or eigenvalues[2] <= eigenvalues[1]:
        raise ValueError("grid lacks a separated nonconstant selector sector")
    return float((eigenvalues[1] + eigenvalues[2]) / 2), float(
        eigenvalues[2] - eigenvalues[1]
    )


def _os_inputs(before, scale, shrink):
    ref = before.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    identity = ref.profile.identity_payload.to_payload()
    params["geometry"]["kappa_H"] = 2**-12 / scale**4 * shrink
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    return replace(before, geometry=ref.geometry())


def _ci_inputs(before, scale, shrink):
    return ci_configure(
        before, gain=2**-10 / scale**2 * shrink, radius=0.0078125, tolerance=1e-8
    )


def _pc_inputs(before, scale, shrink):
    n = len(before.current.C)
    return pc_configure(
        before,
        gain=2**-12 / scale**4 * shrink,
        radius=1.0 * scale**2,
        resource_radius=10.0 * max(1.0, math.sqrt(n / 20)),
        tau=2 * before.dt,
    )


def _cipc_inputs(before, scale, shrink):
    return cipc_configure(
        _pc_inputs(before, scale, shrink),
        domain_radius=0.0078125,
        tolerance=1e-8,
    )


def _rg_inputs(before, scale, shrink):
    ref = before.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    identity = ref.profile.identity_payload.to_payload()
    dt = 2**-16 / scale**2 * shrink
    domain = rg.RG2bGraphDomain(
        2.0, 1.0, 0.375, 0.5, 0.75, 2**-17 / scale**4 * shrink, 0.125, dt
    )
    params["candidate"]["eta_C"] = 0.02
    params["geometry"]["kappa_H"] = 2**-16 / scale**4 * shrink
    params["realization"] = {
        "schema_version": "grcv4-rg2b-params-v1",
        "extension_evaluator_id": domain.identity,
        "approximation_policy_id": rg.APPROXIMATION,
        "error_norm_id": rg.ERROR_NORM,
        "error_tolerance": 1e-8,
        "containment_certificate_id": rg.CONTAINMENT,
        "iteration_limit": 4000,
        "failure_policy_id": "fail_closed_on_uncertified_section_v1",
    }
    identity.update(
        realization="RG2b", profile_family_id="C_RG2b", solver_id="direct_unique_root_v1"
    )
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    return replace(before, geometry=ref.geometry(), dt=dt)


BUILDERS = {
    "OS": _os_inputs,
    "CI": _ci_inputs,
    "PC": _pc_inputs,
    "CI+PC": _cipc_inputs,
    "RG2b": _rg_inputs,
}


def make_inputs(realization, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
    """Build one strict C declaration, recording every rejected attempt."""
    if realization not in REALIZATIONS:
        raise ValueError(f"unknown C realization: {realization}")
    if rows < 2 or cols < 2:
        raise ValueError("grid dimensions must each be at least two")
    graph, _, weights, resource, _ = grid_spec(rows, cols, resource_span=0.34375)
    cutoff, gap = _selector_cutoff(graph, weights)
    base = current_fixture(
        graph=graph,
        weights=weights,
        resource=resource,
        changes={
            "candidate": {
                "eta_C": 0.05,
                "kappa_Phi_C": 0.1,
                "kappa_M_C": 0.1,
                "tau_C": 0.1,
                "chi_C": 0.1,
                "zeta_C": 0.1,
                "Lambda_C": cutoff,
            },
            "geometry": {"kappa_H": 2**-12},
            "solver": {"conditioning_limit": 1e8},
            "charge": {"absolute_tolerance": 1e-11},
            "realization": {"tolerance": 1e-8},
        },
    )
    base = replace(base, dt=2**-10)
    size = len(graph.live_node_ids) + len(graph.live_edge_ids)
    scale = 2.0 ** max(0, math.ceil(math.log2(size / 51)))
    attempts = []
    for index in range(12):
        shrink = 2.0**-index
        inputs = BUILDERS[realization](base, scale, shrink)
        started = time.perf_counter()
        try:
            certificate = CERTIFICATES[realization](inputs, None) if realization == "RG2b" else CERTIFICATES[realization](inputs)
        except (CandidateCStageError, CIStageError, OSStageError, RG2bStageError) as exc:
            attempts.append({
                "attempt": index + 1,
                "shrink": shrink,
                "admitted": False,
                "reason": str(exc),
                "seconds": time.perf_counter() - started,
            })
        else:
            attempts.append({
                "attempt": index + 1,
                "shrink": shrink,
                "admitted": True,
                "seconds": time.perf_counter() - started,
            })
            bounds = (
                {"split_residual_admitted": certificate.residual.admitted,
                 "selector_path_segments": certificate.selector_path_segments}
                if realization == "OS"
                else certificate.bounds.to_dict()
            )
            return inputs, None, {
                "dimension_scale": scale,
                "resource_span_limit": 0.34375,
                "selector_cutoff": cutoff,
                "reference_selector_gap_estimate": gap,
                "attempts": attempts,
                "certificate_bounds": bounds,
                "policy": (
                    "Select a nonconstant reference sector using a spectral-gap proposal; "
                    "the runtime certifies its exact rank. Reduce only geometry gain "
                    "before the run if declaration certification rejects it. Keep "
                    "all selected declarations fixed during public evolution."
                ),
            }
    raise RuntimeError(f"{realization} grid declaration rejected: {attempts}")


def run(realization, steps=5, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
    if steps < 1:
        raise ValueError("steps must be positive")
    started = time.perf_counter()
    inputs, backend, admission = make_inputs(realization, rows, cols)
    declaration_seconds = time.perf_counter() - started
    print(json.dumps({
        "family": inputs.geometry.reference.profile.identity_payload.profile_family_id,
        "rows": rows,
        "cols": cols,
        "declaration_seconds": declaration_seconds,
        "declaration_attempts": len(admission["attempts"]),
        "dt": inputs.dt,
        "geometry_gain": inputs.geometry.reference.profile.params_resolved.geometry.kappa_H,
        "selector_cutoff": admission["selector_cutoff"],
    }), flush=True)
    report = run_inputs(inputs, backend, steps, rows, cols)
    report.update(
        declaration_seconds=declaration_seconds,
        declaration_admission=admission,
        example_total_wall_seconds=time.perf_counter() - started,
        declaration_sha256=hashlib.sha256(canonical_json_bytes(inputs.to_payload())).hexdigest(),
        comparison_scope=(
            "Same configurable grid topology, reference edge weights and initial "
            "resource as A. C has no A edge history and uses its own nonconstant "
            "spectral sector and strict declarations; timings are workloads, not "
            "a controlled comparison of identical physical dynamics."
        ),
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--realization", choices=REALIZATIONS, required=True)
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS)
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.steps < 1 or args.rows < 2 or args.cols < 2:
        parser.error("steps must be positive and each grid dimension at least two")
    report = run(args.realization, args.steps, args.rows, args.cols)
    name = args.realization.lower().replace("+", "_")
    output = args.output or Path(__file__).parent / "results" / f"grid_transport_c_{name}_{args.rows}x{args.cols}_{args.steps}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        key: report[key] for key in (
            "family", "nodes", "edges", "steps", "dt", "declaration_seconds",
            "setup_seconds", "total_step_seconds", "mean_step_seconds",
            "example_total_wall_seconds", "max_resource_change",
            "max_history_change", "max_carrier_magnitude",
        )
    }, indent=2))
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
