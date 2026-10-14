"""Explicit fixed-256-bit Arb LU research policy; no retries or exact fallback.

Preserves the existing represented matrix solution by certifying a unique
round-to-nearest/even binary64 value for every entry. Conditioning, native exact
rounded-residual checks, Hodge positivity and OS gates remain separate.
No production source is changed. Old scripts and records remain immutable.
"""

from contextlib import contextmanager
import argparse
import hashlib
import math
import multiprocessing as mp
import os
import platform
import struct
import time
from unittest.mock import patch

import flint
from scripts import benchmark_grcv4_hodge_positive as hodge

previous = hodge.previous
prior = previous.prior
base = previous.base
POLICY = "source_os_arb_lu_256_unique_binary64_v1"
METHOD = "arb_lu_256_unique_binary64_v1"
BITS = 256
PREDICTOR_ROUTES = {k: ("exact_diagonal" if v == "exact_diagonal" else METHOD) for k, v in prior.ROUTES.items()}
CORRECTOR_ROUTES = {k: ("exact_diagonal" if v == "exact_diagonal" else METHOD) for k, v in previous.CORRECTOR_ROUTES.items()}
Inconclusive = prior.CertificateInconclusive


def round_interval(lo, hi):
    """Certify the WHOLE closed rational interval belongs to one RN-even cell.

Floating conversion proposes a value only; exact cell boundaries decide.
Canonical positive zero matches native _computed(), including negative underflow.
Overflow cannot produce an admitted represented entry.
"""
    lo, hi = base.q(lo), base.q(hi)
    base.require(lo <= hi, "inverted enclosure")
    try:
        left, right = float(lo), float(hi)
    except OverflowError as exc:
        raise Inconclusive("binary64 overflow boundary unresolved") from exc
    if not math.isfinite(left) or not math.isfinite(right) or left != right:
        raise Inconclusive("enclosure has no unique finite binary64 rounding")
    value = 0. if left == 0 else left
    if value == 0:
        low, high, even = -base.q(2)**-1075, base.q(2)**-1075, True
    else:
        prev, nex = math.nextafter(value, -math.inf), math.nextafter(value, math.inf)
        qprev = base.q(prev) if math.isfinite(prev) else -base.q(2)**1024
        qnext = base.q(nex) if math.isfinite(nex) else base.q(2)**1024
        low, high = (qprev+base.q(value))/2, (base.q(value)+qnext)/2
        even = not (struct.unpack('>Q', struct.pack('>d', value))[0] & 1)
    if not (low <= lo <= hi <= high and (even or (lo > low and hi < high))):
        raise Inconclusive("exact binary64 rounding-cell containment failed")
    return value


def rounded_balls(balls):
    rows = []
    for i in range(balls.nrows()):
        row = []
        for j in range(balls.ncols()):
            ball = balls[i, j]
            if not ball.is_finite():
                raise Inconclusive("nonfinite Arb enclosure")
            row.append(round_interval(ball.lower().fmpq(), ball.upper().fmpq()))
        rows.append(row)
    return base.matrix(rows)


def certified_solve(a, b):
    """One exact-input Arb LU call at one declared precision, then certification."""
    base.require(a.nrows() > 0 and a.nrows() == a.ncols() and b.nrows() == a.nrows()
                 and b.ncols() > 0, "nonempty square system and compatible RHS required")
    with flint.ctx.workprec(BITS):
        start = time.monotonic()
        aa, bb = flint.arb_mat(a), flint.arb_mat(b)
        for exact, ball in ((a, aa), (b, bb)):
            if not all(ball[i, j].is_exact() and ball[i, j].fmpq() == exact[i, j]
                       for i in range(exact.nrows()) for j in range(exact.ncols())):
                raise Inconclusive("fixed precision cannot represent exact input coefficients")
        preparation = time.monotonic()-start
        start = time.monotonic()
        try:
            answer = aa.solve(bb, algorithm="lu")
        except ZeroDivisionError as exc:
            # Arb failure can mean insufficient precision, not necessarily singularity.
            raise Inconclusive("fixed-precision Arb LU could not certify this system") from exc
        solve_time = time.monotonic()-start
        start = time.monotonic()
        result = rounded_balls(answer)
        rounding_time = time.monotonic()-start
    return result, {"method": METHOD, "algorithm": "lu", "precision_bits": BITS,
        "input_coefficients_exact": True, "solution_enclosed": True,
        "all_entries_uniquely_rounded": True, "entries_certified": a.nrows()*b.ncols(),
        "input_conversion_check_seconds": preparation, "enclosure_solve_seconds": solve_time,
        "rounding_certificate_seconds": rounding_time,
        "rounded_solution_digest": base.digest([[float(x) for x in row] for row in result.tolist()]),
        "exact_solution_materialized": False, "fallback_attempted": False}


class ArbSolveMixin:
    def solve(self, rows, rhs, policy, label, certificates):
        from pygrc.models import grc_v4_numerics as numerics
        base.require(label in self.routes, "unregistered Arb policy solve role")
        a, b = base.matrix(rows), base.matrix(rhs)
        certificates.append(self.condition(rows, policy.conditioning_limit, label))
        method = self.routes[label]
        self.emit({"stage": label, "operation": "solve_started", "method": method})
        start = time.monotonic()
        if method == "exact_diagonal":
            base.require(a.nrows() == a.ncols() and a.nrows() == b.nrows()
                         and all(a[i, i] != 0 and all(a[i, j] == 0 for j in range(a.ncols()) if i != j)
                                 for i in range(a.nrows())), "declared diagonal role changed")
            exact = flint.fmpq_mat([[b[i, j]/a[i, i] for j in range(b.ncols())] for i in range(b.nrows())])
            base.verify_exact(a, b, exact)
            result = base.rounded(exact)
            proof = {"method": method, "exact_identity": True, "exact_solution_materialized": True}
        else:
            result, proof = certified_solve(a, b)
        solve_seconds = time.monotonic()-start
        start = time.monotonic()
        residual = a*result-b
        for j in range(b.ncols()):
            if not numerics.residual_pass(tuple(residual[i, j] for i in range(a.nrows())),
                                         tuple(b[i, j] for i in range(b.nrows())), policy):
                raise numerics.MatrixError("no_admitted_root", "declared residual tolerance failed: " + label)
        self.note(stage=label, operation="solve", **proof, solve_seconds=solve_seconds,
                  exact_rounded_residual_seconds=time.monotonic()-start,
                  rounded_residual_pass=True, rhs_columns=b.ncols())
        if label == "physical Q_C similarity":
            self.current_block = base.rounded(prior.eye(a.nrows())-self.beta*result)
        elif label == "retained resolvent" and self.params.tau_C == 0:
            self.current_block = base.rounded((1-self.beta)*prior.eye(a.nrows()))
        return tuple(tuple(float(x) for x in row) for row in result.tolist())


class ArbPredictorPolicy(ArbSolveMixin, prior.PredictorPolicy):
    routes = PREDICTOR_ROUTES


class ArbCorrectorPolicy(ArbSolveMixin, previous.CorrectorPolicy):
    routes = CORRECTOR_ROUTES


@contextmanager
def installed(emit=lambda row: None):
    policy = hodge.HodgePositivePolicy(emit)
    with patch.object(prior, "PredictorPolicy", ArbPredictorPolicy), \
         patch.object(previous, "CorrectorPolicy", ArbCorrectorPolicy), policy.installed():
        yield policy


def worker(connection):
    from dataclasses import replace
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
    from pygrc.models.grc_v4_realizations import CandidateCOSPass
    try:
        with exact_backend(ExactBackend.FLINT):
            start = time.monotonic()
            inputs = replace(prior.materialize(), stage="pre_read")
            setup_seconds = time.monotonic()-start
            start = time.monotonic()
            with installed(lambda row: connection.send(("progress", row))) as policy:
                result = CandidateCOSPass(inputs)
            pass_seconds = time.monotonic()-start
            old = base.read(base.ROOT/"implementation/evidence/grcv4-performance/exact_policy_predictor_probe.json")["result"]
            predictor = previous.point_summary(result.predictor)
            for key in ("current", "baseline", "read_flux", "causal_flat", "current_block_digest", "closure_residual_squared"):
                base.require(predictor[key] == old[key], "Arb predictor differs from exact retained result: " + key)
            connection.send(("result", {"setup_seconds": setup_seconds, "pass_seconds": pass_seconds,
                "complete_os_pass": True, "instrumented_numerical_policy": True,
                "predictor": predictor, "corrector": previous.point_summary(result.corrector),
                "split_admitted": result.residual.admitted,
                "split_exact_values_digest": base.digest(result.residual.exact_values),
                "selector_path_segments": result.selector_path_segments,
                "predictor_matches_prior_exact": True, "operations": policy.events}))
    except Inconclusive as exc:
        connection.send(("error", {"type": "certificate_inconclusive", "message": str(exc)}))
    except Exception as exc:
        connection.send(("error", {"type": type(exc).__name__, "message": str(exc)}))
    finally:
        connection.close()


def supervised(seconds, target=worker):
    base.require(math.isfinite(seconds) and seconds > 0, "positive finite deadline required")
    context = mp.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(target=target, args=(send,))
    start = time.monotonic()
    process.start()
    send.close()
    result = {"outcome": "resource_limit", "events": []}
    try:
        while time.monotonic()-start < seconds:
            if receive.poll(min(.1, max(0, seconds-(time.monotonic()-start)))):
                try:
                    kind, payload = receive.recv()
                except EOFError:
                    result["outcome"] = "worker_exit_without_result"
                    break
                if kind == "progress":
                    event = {"elapsed_seconds": time.monotonic()-start, **payload}
                    result["events"].append(event)
                    print(base.json.dumps(event), flush=True)
                else:
                    result.update(outcome="completed" if kind == "result" else "failed", **{kind: payload})
                    break
            elif not process.is_alive():
                result["outcome"] = "worker_exit_without_result"
                break
    finally:
        process.join(.1)
        if process.is_alive():
            process.terminate()
            process.join(1)
        if process.is_alive():
            process.kill()
            process.join()
        receive.close()
    return {**result, "worker_wall_seconds": time.monotonic()-start,
            "worker_exitcode": process.exitcode, "deadline_seconds": seconds, "fallback_attempted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, choices=(POLICY,))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--output", type=base.Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve().relative_to(base.ROOT)
    base.require(not (base.ROOT/output).exists(), "report already exists")
    old = base.read(base.ROOT/"implementation/evidence/grcv4-performance/exact_policy_hodge_positive_probe.json")
    sources = list(old["source_bindings"]) + ["scripts/benchmark_grcv4_arb_policy.py"]
    report = {"schema": "grcv4-arb-policy-probe-v1", "policy": POLICY,
              "arb_precision_bits": BITS, "arb_algorithm": "lu", "rounding": "nearest_even_canonical_zero",
              "positivity_method": hodge.METHOD, "positivity_scale": hodge.SCALE,
              "python": platform.python_version(), "python_flint": flint.__version__, "flint_threads": flint.ctx.threads,
              "thread_settings": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
              "source_bindings": {p: hashlib.sha256((base.ROOT/p).read_bytes()).hexdigest() for p in sources},
              "predecessor_record_digest": old["record_digest"],
              "predictor_routes": PREDICTOR_ROUTES, "corrector_routes": CORRECTOR_ROUTES,
              "production_admission": False, "src_changed": False, "native_steps": 0, "native_events": 0,
              **supervised(args.seconds)}
    report["record_digest"] = base.digest(report)
    base.write_new(base.ROOT/output, report)
    print(base.json.dumps({k: report[k] for k in ("outcome", "worker_wall_seconds")}))
    if report["outcome"] != "completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
