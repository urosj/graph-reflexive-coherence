"""Explicit exact weighted split certificate atop the fixed Arb research policy.

No production changes, tolerance change, iteration, inertia fallback or retry.
The sufficient certificate is topology-independent; the enclosing experimental
current solver still has its own restricted selector/reference proof domain.
"""

from contextlib import contextmanager
from dataclasses import dataclass, field
import argparse
import hashlib
import os
import platform
import time
from unittest.mock import patch

import flint
from scripts import benchmark_grcv4_arb_policy as arb
from pygrc.models import grc_v4_realizations as real
from pygrc.models.grc_v4_geometry import GRCV4Geometry
from pygrc.models.grc_v4_profile import OSParams

base = arb.base
POLICY = "source_os_arb_256_exact_weighted_split_v1"
METHOD = "flint_exact_weighted_row_sum_os_split_v1"
NativeSplitResidual = real.OSSplitResidual


def certificate(residual, reference, tolerance):
    """Exact sufficient reference-relative norm bound, including equality.

For symmetric R and D=diag(w)>0, S=D^-1/2 R D^-1/2 is symmetric and
similar to D^-1 R. Thus ||S||_2 = rho(D^-1 R) <= ||D^-1 R||_inf.
The last quantity is max_i sum_j |R_ij|/w_i. No square root is evaluated.
Failure of the bound is inconclusive, NOT proof that ||S||_2 > tolerance.
"""
    r, d, t = base.matrix(residual), base.matrix(reference), base.q(tolerance)
    n = r.nrows()
    base.require(r.ncols() == n and d.nrows() == d.ncols() == n,
                 "square residual/reference with identical dimensions required")
    base.require(r == r.transpose(), "exact residual symmetry required")
    base.require(t >= 0, "nonnegative finite tolerance required")
    base.require(all(d[i, i] > 0 and all(d[i, j] == 0 for j in range(n) if i != j)
                     for i in range(n)), "positive diagonal reference required")
    # These are exact differences of staged binary64 values, not rounded defects.
    for x in [t, *(x for a in (r, d) for row in a.tolist() for x in row)]:
        denominator = int(x.denominator)
        base.require(denominator & (denominator-1) == 0, "exact dyadic operands required")
    ratios = [sum((abs(r[i, j]) for j in range(n)), base.q(0))/d[i, i] for i in range(n)]
    bound = max(ratios, default=base.q(0))
    return {"method": METHOD, "arithmetic": "flint_fmpq", "dimension": n,
            "reference_kind": "positive_diagonal", "symmetry_verified": True,
            "residual_digest": base.digest([[str(x) for x in row] for row in r.tolist()]),
            "reference_digest": base.digest([[str(x) for x in row] for row in d.tolist()]),
            "reference_weights": [str(d[i, i]) for i in range(n)],
            "tolerance_exact": str(t), "weighted_row_bound": str(bound),
            "admission_margin_lower": str(t-bound), "empty_space": n == 0,
            "outcome": "certified" if bound <= t else "inconclusive",
            "reason": "sufficient_bound_within_tolerance" if bound <= t else "sufficient_bound_exceeds_tolerance",
            "inertia_computed": False, "inverse_constructed": False,
            "fallback_attempted": False}


@dataclass(frozen=True, slots=True)
class CertifiedSplitResidual(NativeSplitResidual):
    """Research-only result with native operands/display and a named proof.

This intentionally replaces only the split decision, not global inertia.
The original typed/reference/norm checks and exact defect stages are retained.
"""

    proof: dict = field(init=False)

    def __post_init__(self):
        if type(self.geometry) is not GRCV4Geometry or type(self.regenerated) is not GRCV4Geometry:
            raise TypeError("split residual requires typed geometry operands")
        ref = self.geometry.reference
        if self.regenerated.reference != ref:
            raise ValueError("split residual has foreign reference geometry")
        policy = ref.profile.params_resolved.realization
        if type(policy) is not OSParams or policy.split_residual_norm_id != "edge_l2_v1":
            raise ValueError("unimplemented OS split norm")
        residual = tuple(tuple(base.q(x)-base.q(y) for x, y in zip(row, other, strict=True))
                         for row, other in zip(self.geometry.one_form_hodge.matrix,
                                               self.regenerated.one_form_hodge.matrix, strict=True))
        proof = certificate(residual, ref.pairings.one_form.matrix, policy.tolerance)
        if proof["outcome"] != "certified":
            raise arb.Inconclusive("weighted OS split bound inconclusive; no inertia fallback")
        try:
            values = tuple(tuple(float(x) for x in row) for row in residual)
        except OverflowError:
            values = None  # Presentation never decides the exact norm condition.
        for name, value in (("values", values), ("exact_values", tuple(tuple(str(x) for x in row) for row in residual)),
                            ("admitted", True), ("proof", proof)):
            object.__setattr__(self, name, value)


class SplitPolicy(arb.hodge.HodgePositivePolicy):
    @contextmanager
    def installed(self):
        def split(geometry, regenerated):
            self.note(stage="weighted_split_admission", operation="started", method=METHOD)
            start = time.monotonic()
            result = CertifiedSplitResidual(geometry, regenerated)
            self.note(stage="weighted_split_admission", operation="completed",
                      seconds=time.monotonic()-start, certificate=result.proof)
            return result

        with super().installed(), patch.object(real, "OSSplitResidual", split):
            yield


@contextmanager
def installed(emit=lambda row: None):
    with patch.object(arb.hodge, "HodgePositivePolicy", SplitPolicy), arb.installed(emit) as policy:
        yield policy


def worker(connection):
    # Reuse the exact same native pass, staged arithmetic, summaries and predictor
    # comparison. The sole successor is the explicitly selected split proof.
    with patch.object(arb.hodge, "HodgePositivePolicy", SplitPolicy):
        arb.worker(connection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, choices=(POLICY,))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--output", type=base.Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve().relative_to(base.ROOT)
    base.require(not (base.ROOT/output).exists(), "report already exists")
    old = base.read(base.ROOT/"implementation/evidence/grcv4-performance/arb_policy_os_pass_probe.json")
    sources = list(old["source_bindings"]) + ["scripts/benchmark_grcv4_split_certificate.py"]
    report = {"schema": "grcv4-weighted-split-policy-probe-v1", "policy": POLICY,
              "split_method": METHOD, "arb_precision_bits": arb.BITS, "arb_algorithm": "lu",
              "positivity_method": arb.hodge.METHOD, "positivity_scale": arb.hodge.SCALE,
              "python": platform.python_version(), "python_flint": flint.__version__, "flint_threads": flint.ctx.threads,
              "thread_settings": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
              "source_bindings": {p: hashlib.sha256((base.ROOT/p).read_bytes()).hexdigest() for p in sources},
              "predecessor_record_digest": old["record_digest"],
              "predictor_routes": arb.PREDICTOR_ROUTES, "corrector_routes": arb.CORRECTOR_ROUTES,
              "production_admission": False, "src_changed": False, "native_steps": 0, "native_events": 0,
              **arb.supervised(args.seconds, target=worker)}
    report["record_digest"] = base.digest(report)
    base.write_new(base.ROOT/output, report)
    print(base.json.dumps({k: report[k] for k in ("outcome", "worker_wall_seconds")}))
    if report["outcome"] != "completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
