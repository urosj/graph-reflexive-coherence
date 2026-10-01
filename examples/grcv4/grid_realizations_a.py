"""Configurable A_CI, A_PC, A_CI+PC and A_RG2b grids with strict public steps.

Like compare_five.py, checkout fixtures only build identity-bound declarations.
Grid dimensions are parameters. Certificate-guided setup selects conservative
nonzero gains; it never changes declarations after evolution starts.
Run with PYTHONPATH=src:.:tests from the repository root.
"""

import argparse
import hashlib
import json
import math
import time
from dataclasses import replace
from pathlib import Path

from examples.grcv4.grid_transport import DEFAULT_COLS, DEFAULT_ROWS, run_inputs
from examples.grcv4.grid_transport import make_inputs as transport_inputs
from pygrc.models import grc_v4_rg2b_graph as rg
from pygrc.models.grc_v4_ci import CIContractionCertificate, CIStageError
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_pc import PCEnvelopeCertificate
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models.grc_v4_rg2b import RG2bCertificate, RG2bStageError
from tests.models.test_grc_v4_ci import configure as ci_configure
from tests.models.test_grc_v4_cipc import configure as cipc_configure
from tests.models.test_grc_v4_pc import configure as pc_configure
from tests.models.test_grc_v4_profile import reidentify

REALIZATIONS = ("CI", "PC", "CI+PC", "RG2b")
CERTIFICATES = {
    "CI": CIContractionCertificate,
    "PC": PCEnvelopeCertificate,
    "CI+PC": CIContractionCertificate,
    "RG2b": RG2bCertificate,
}


def _rg_inputs(before, scale, shrink, _controls):
    ref = before.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    identity = ref.profile.identity_payload.to_payload()
    dt = 2**-16 / scale**2 * shrink
    domain = rg.RG2bGraphDomain(
        2.0, 1.625, 0.375, 0.5, 0.75, 2**-17, 0.125, dt
    )
    params["candidate"]["eta"] = 0.02
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
        realization="RG2b",
        profile_family_id="A_RG2b",
        solver_id="direct_unique_root_v1",
    )
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    return replace(before, geometry=ref.geometry(), dt=dt)


def _ci_inputs(before, scale, shrink, controls):
    return ci_configure(
        before,
        gain=0.09375 / scale**2 * shrink,
        radius=0.125,
        tolerance=1e-8,
        changes=controls,
    )


def _pc_inputs(before, scale, shrink, controls):
    # The whole-chart source bound grows with graph size. Expand the carrier
    # ball while reducing its geometry gain, then certify the actual envelope.
    n = len(before.current.C)
    return pc_configure(
        before,
        gain=2**-12 / scale**4 * shrink,
        radius=32.0 * scale**2 / shrink,
        resource_radius=10.0 * max(1.0, math.sqrt(n / 20)),
        weight_lower=1.0,
        weight_upper=2.0,
        tau=2 * before.dt,
        changes=controls,
    )


def _cipc_inputs(before, scale, shrink, controls):
    return cipc_configure(
        _pc_inputs(before, scale, shrink, controls),
        domain_radius=0.03125,
        tolerance=1e-8,
        changes=controls,
    )


BUILDERS = {
    "CI": _ci_inputs,
    "PC": _pc_inputs,
    "CI+PC": _cipc_inputs,
    "RG2b": _rg_inputs,
}


def make_inputs(realization, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
    """Build and certify a declaration; return its complete setup audit."""
    if realization not in REALIZATIONS:
        raise ValueError(f"unknown A realization: {realization}")
    if rows < 2 or cols < 2:
        raise ValueError("grid dimensions must each be at least two")
    # Keep the pulse and spatial gradient bounded on larger grids. At 4x5
    # this is exactly the existing A_OS initial resource, not a new trajectory.
    before, backend = transport_inputs(rows, cols, resource_span=0.34375)
    ref = before.geometry.reference
    size = len(ref.graph.live_node_ids) + len(ref.graph.live_edge_ids)
    # Powers of two keep all time steps exactly representable and repeatable.
    scale = 2.0 ** max(0, math.ceil(math.log2(size / 51)))
    solver = ref.profile.params_resolved.solver
    controls = {
        "solver": {
            "absolute_tolerance": solver.absolute_tolerance,
            "relative_tolerance": solver.relative_tolerance,
            "conditioning_limit": solver.conditioning_limit,
        }
    }
    attempts = []
    for index in range(12):
        shrink = 2.0**-index
        inputs = BUILDERS[realization](before, scale, shrink, controls)
        started = time.perf_counter()
        try:
            certificate = CERTIFICATES[realization](inputs, backend)
        except (CIStageError, RG2bStageError) as exc:
            attempts.append(
                {
                    "attempt": index + 1,
                    "shrink": shrink,
                    "admitted": False,
                    "reason": str(exc),
                    "seconds": time.perf_counter() - started,
                }
            )
        else:
            attempts.append(
                {
                    "attempt": index + 1,
                    "shrink": shrink,
                    "admitted": True,
                    "seconds": time.perf_counter() - started,
                }
            )
            return inputs, backend, {
                "dimension_scale": scale,
                "resource_span_limit": 0.34375,
                "attempts": attempts,
                "certificate_bounds": certificate.bounds.to_dict(),
                "policy": (
                    "Bound resource contrast and scale conservative declarations with "
                    "grid size; on certificate rejection, reduce geometry gain before "
                    "the run (also reduce RG2b dt or expand PC carrier radius). "
                    "Keep all selected declarations fixed during public evolution. "
                    "Abort if no declaration is certified within twelve attempts."
                ),
            }
    raise RuntimeError(f"{realization} grid declaration rejected: {attempts}")


def run(realization, steps=5, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
    if steps < 1:
        raise ValueError("steps must be positive")
    started = time.perf_counter()
    inputs, backend, admission = make_inputs(realization, rows, cols)
    declaration_seconds = time.perf_counter() - started
    print(
        json.dumps({
            "family": inputs.geometry.reference.profile.identity_payload.profile_family_id,
            "rows": rows, "cols": cols, "declaration_seconds": declaration_seconds,
            "declaration_attempts": len(admission["attempts"]),
            "dt": inputs.dt,
            "geometry_gain": inputs.geometry.reference.profile.params_resolved.geometry.kappa_H,
        }),
        flush=True,
    )
    report = run_inputs(inputs, backend, steps, rows, cols)
    report.update(
        declaration_seconds=declaration_seconds,
        declaration_admission=admission,
        example_total_wall_seconds=time.perf_counter() - started,
        declaration_sha256=hashlib.sha256(
            canonical_json_bytes(inputs.to_payload())
        ).hexdigest(),
        comparison_scope=(
            "Same grid dimensions, reference geometry, initial resources and edge "
            "history across these A cases. Realization declarations and geometry "
            "gains differ; RG2b also uses smaller eta and dt. These are workload "
            "timings, not a controlled comparison of identical physical dynamics."
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
    output = args.output or (
        Path(__file__).parent / "results" /
        f"grid_transport_a_{name}_{args.rows}x{args.cols}_{args.steps}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        key: report[key]
        for key in (
            "family", "nodes", "edges", "steps", "dt", "declaration_seconds",
            "setup_seconds", "total_step_seconds", "mean_step_seconds",
            "example_total_wall_seconds", "max_resource_change",
            "max_history_change", "max_carrier_magnitude",
        )
    }, indent=2))
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
