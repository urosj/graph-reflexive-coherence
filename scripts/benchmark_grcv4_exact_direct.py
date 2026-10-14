"""Explicit, bounded exact-direct probe; NOT a production admission path.

Reconstruct only the retained C_OS source/current predictor, preserving its
binary64 stage boundaries. No production monkeypatch, approximate solve,
algorithm auto-selection, inverse fallback, native step or event is performed.
Each CLI command runs in a killable worker, including native FLINT calls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import time

from flint import fmpq, fmpq_mat

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = "implementation/phase-9-grcv4/tranche-8/larger-graph-examples/C_OS.json"
ALGORITHMS = ("fflu", "dixon")


def require(value, message):
    if not value:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def q(value):
    if isinstance(value, fmpq):
        return value
    return fmpq(*value.as_integer_ratio()) if isinstance(value, float) else fmpq(value)


def matrix(rows):
    return fmpq_mat([[q(x) for x in row] for row in rows])


def rounded(a):
    rows = [[float(x) for x in row] for row in a.tolist()]
    require(all(math.isfinite(x) for row in rows for x in row), "nonfinite binary64 output")
    return matrix(rows)


def direct(a, b, algorithm):
    require(algorithm in ALGORITHMS, "an explicit exact algorithm is required")
    require(a.nrows() > 0 and a.nrows() == a.ncols() and b.nrows() == a.nrows()
            and b.ncols() > 0, "nonempty square system and compatible RHS required")
    return a.solve(b, algorithm=algorithm)


def verify_exact(a, b, x):
    require(a * x == b, "exact solve identity failed")


def predictor_block(b, resources, params, algorithm, emit=lambda value: None):
    """Literal identity-Hodge predictor on the proved constant-selector domain.

Caller establishes a connected simple unit-weight graph and cutoff below
1/(n(n-1)); these are restrictions of this benchmark, NOT a general solver.
"""
    n, m = b.nrows(), b.ncols()
    require(n > 1 and m > 0 and len(resources) == n, "predictor coordinate mismatch")
    require(0 < q(params["Lambda_C"]) < fmpq(1, n * (n - 1)), "kernel-only cutoff required")
    mean = float(sum((q(x) for x in resources), fmpq(0)) / n)
    rho = math.tanh(mean / params["C_ref"])
    deformation = math.exp((0.5 * params["kappa_M_C"]) * (0.5 * (rho + rho)))
    require(math.isfinite(deformation) and deformation > 0, "invalid deformation")
    retained_scale = q(float(q(deformation) ** 2))
    eye = fmpq_mat(m, m)
    for i in range(m):
        eye[i, i] = 1
    retained = retained_scale * eye
    c = matrix([[x] for x in resources])
    phi = rounded(q(params["kappa_Phi_C"]) * b * retained * b.transpose() * c)
    baseline = rounded(-q(params["eta_C"]) * b.transpose() * phi)
    # Keep both production product rounding stages; do not fuse B^T B Hm.
    laplacian = rounded(b.transpose() * rounded(b * retained))
    resolvent = rounded(eye + q(params["tau_C"]) * laplacian)
    emit({"stage": "prepare_retained_resolvent", "algorithm": algorithm, "rhs_columns": m})
    start = time.monotonic()
    response_exact = direct(resolvent, eye, algorithm)
    solve_seconds = time.monotonic() - start
    verify_exact(resolvent, eye, response_exact)
    response = rounded(response_exact)
    # At H=I, Q=Hm is scalar diagonal. Preserve the rounded similarity RHS.
    flux_response = eye if params["tau_C"] == 0 else rounded(rounded(response * retained) / retained_scale)
    block = rounded(eye - q(params["zeta_C"]) * q(params["chi_C"]) * flux_response)
    return block, baseline, {"deformation": deformation,
        "retained_resolvent_exact_solve_seconds": solve_seconds,
        "retained_resolvent_exact_identity": True}


def read(path):
    raw = path.read_bytes()
    return json.loads(lzma.decompress(raw) if path.suffix == ".xz" else raw)


def write_new(path, value):
    raw = encoded(value) + b"\n"
    require(len(raw) <= 1_000_000 or path.suffix == ".xz", "outputs over 1 MB require .xz")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(lzma.compress(raw) if path.suffix == ".xz" else raw)


def prepare(algorithm, path, emit):
    import sys
    sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
    import p984g_cos as fixture

    subject = read(ROOT / DECLARATION)["source"]
    b, params = fixture.graph_data(subject)  # connected simple unit-weight graph
    require(params["common"]["measure_profile_id"] == "unit_vertex_measure_v1", "unit measure required")
    block, rhs, details = predictor_block(matrix(b.tolist()), subject["roles"]["current"]["C"],
                                          params["candidate"], algorithm, emit)
    value = {"schema": "grcv4-exact-direct-block-v1", "scope": "source_current_predictor_only",
        "declaration": DECLARATION,
        "declaration_sha256": hashlib.sha256((ROOT / DECLARATION).read_bytes()).hexdigest(),
        "matrix": [[float(x) for x in row] for row in block.tolist()],
        "rhs": [[float(x) for x in row] for row in rhs.tolist()],
        "policy": params["solver"], "details": details,
        "production_admission": False, "native_steps": 0, "native_events": 0}
    value["block_digest"] = digest(value)
    write_new(path, value)
    return {"block_digest": value["block_digest"], "dimension": block.nrows(), **details,
            "artifact_bytes": path.stat().st_size}


def load_block(path):
    value = read(path)
    payload = {k: v for k, v in value.items() if k != "block_digest"}
    require(value["block_digest"] == digest(payload), "block digest mismatch")
    require(value["declaration"] == DECLARATION and value["declaration_sha256"] ==
            hashlib.sha256((ROOT / DECLARATION).read_bytes()).hexdigest(), "declaration drift")
    return value, matrix(value["matrix"]), matrix(value["rhs"])


def measure(job, algorithm, path, emit):
    from pygrc.models import grc_v4_numerics as numerics
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
    from pygrc.models.grc_v4_profile import SolverPolicy

    value, a, b = load_block(path)
    policy = SolverPolicy.from_payload(value["policy"])
    if job == "condition":
        emit({"stage": "physical_current_condition", "method": "existing_exact_gram_psd"})
        with exact_backend(ExactBackend.FLINT):
            start = time.monotonic()
            certificate = numerics.condition(tuple(tuple(row) for row in value["matrix"]),
                                             policy.conditioning_limit, "physical current probe")
            elapsed = time.monotonic() - start
        return {"condition_seconds": elapsed, "certificate": certificate.to_payload(),
                "block_digest": value["block_digest"]}
    emit({"stage": "physical_current_exact_solve", "algorithm": algorithm})
    start = time.monotonic()
    x = direct(a, b, algorithm)
    solve_seconds = time.monotonic() - start
    start = time.monotonic()
    verify_exact(a, b, x)
    identity_seconds = time.monotonic() - start
    start = time.monotonic()
    represented = rounded(x)
    rounding_seconds = time.monotonic() - start
    start = time.monotonic()
    residual = a * represented - b
    with exact_backend(ExactBackend.FLINT):
        passed = all(numerics.residual_pass(tuple(residual[i, j] for i in range(a.nrows())),
                         tuple(b[i, j] for i in range(b.nrows())), policy) for j in range(b.ncols()))
    require(passed, "rounded current failed existing residual policy")
    residual_seconds = time.monotonic() - start
    return {"block_digest": value["block_digest"], "solve_seconds": solve_seconds,
        "exact_identity_seconds": identity_seconds, "rounding_seconds": rounding_seconds,
        "rounded_residual_seconds": residual_seconds, "exact_identity": True,
        "rounded_residual_pass": passed, "conditioning_checked_in_this_job": False,
        "rounded_solution": [[float(x) for x in row] for row in represented.tolist()],
        "exact_solution_digest": digest([[str(x) for x in row] for row in x.tolist()]),
        "maximum_solution_denominator_bits": max(int(x.denominator).bit_length() for row in x.tolist() for x in row)}


def worker(connection, job, algorithm, path):
    try:
        emit = lambda value: connection.send(("progress", value))
        result = prepare(algorithm, path, emit) if job == "prepare" else measure(job, algorithm, path, emit)
        connection.send(("result", result))
    except Exception as exc:
        # Traceback paths are not retained; failures do not trigger another method.
        connection.send(("error", {"type": type(exc).__name__, "message": str(exc)}))
    finally:
        connection.close()


def supervised(job, algorithm, path, seconds, target=worker):
    require(algorithm in ALGORITHMS, "an explicit exact algorithm is required")
    require(math.isfinite(seconds) and seconds > 0, "positive finite deadline required")
    context = mp.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(target=target, args=(send, job, algorithm, path))
    start = time.monotonic()
    process.start()
    send.close()
    result = {"outcome": "resource_limit", "events": []}
    try:
        while time.monotonic() - start < seconds:
            if receive.poll(min(0.1, max(0, seconds - (time.monotonic() - start)))):
                try:
                    kind, payload = receive.recv()
                except EOFError:
                    result["outcome"] = "worker_exit_without_result"
                    break
                if kind == "progress":
                    event = {"elapsed_seconds": time.monotonic() - start, **payload}
                    result["events"].append(event)
                    print(json.dumps(event), flush=True)
                else:
                    result.update(outcome="completed" if kind == "result" else "failed", **{kind: payload})
                    break
            elif not process.is_alive():
                result["outcome"] = "worker_exit_without_result"
                break
    finally:
        process.join(0.1)
        if process.is_alive():
            process.terminate()
            process.join(1)
        if process.is_alive():
            process.kill()
            process.join()
        receive.close()
    return {**result, "worker_wall_seconds": time.monotonic() - start,
            "worker_exitcode": process.exitcode, "deadline_seconds": seconds, "fallback_attempted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", choices=("prepare", "solve", "condition"))
    parser.add_argument("--algorithm", required=True, choices=ALGORITHMS)
    parser.add_argument("--seconds", required=True, type=float)
    parser.add_argument("--block", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), "report already exists")
    require(args.block.suffix == ".xz", "block artifact must be compressed .xz")
    require(not args.block.exists() if args.job == "prepare" else args.block.is_file(), "block availability mismatch")
    # Commands/evidence use repository-relative paths only.
    block, output = args.block.resolve().relative_to(ROOT), args.output.resolve().relative_to(ROOT)
    import flint
    sources = ["scripts/benchmark_grcv4_exact_direct.py", DECLARATION,
        "implementation/phase-9-grcv4/verification/p984g_cos.py",
        "src/pygrc/models/_grc_v4_matrix.py", "src/pygrc/models/_grc_v4_matrix_flint.py",
        "src/pygrc/models/grc_v4_numerics.py", "src/pygrc/models/grc_v4_exact.py",
        "src/pygrc/models/grc_v4_candidate_c.py"]
    report = {"schema": "grcv4-exact-direct-probe-v1", "job": args.job,
        "algorithm": args.algorithm if args.job != "condition" else "existing_exact_gram_psd",
        "block_path": block.as_posix(), "python": platform.python_version(),
        "python_flint": flint.__version__, "platform": platform.system(),
        "thread_settings": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
        "source_bindings": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
        "production_admission": False, "native_steps": 0, "native_events": 0,
        **supervised(args.job, args.algorithm, ROOT / block, args.seconds)}
    report["record_digest"] = digest(report)
    write_new(ROOT / output, report)
    print(json.dumps({k: v for k, v in report.items() if k in
                     ("job", "algorithm", "outcome", "worker_wall_seconds", "error")}), flush=True)


if __name__ == "__main__":
    main()
