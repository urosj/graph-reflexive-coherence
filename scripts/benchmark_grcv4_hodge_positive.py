"""Explicit FLINT exact positivity certificate and bounded OS successor probe.

Research instrumentation only. Both unrounded affine and represented Hodge
positivity calls remain present. One fixed sufficient proof replaces integer
elimination; failure to certify stops without elimination or solver fallback.
Old measured scripts and evidence are unchanged.
"""

from contextlib import contextmanager
import argparse
import hashlib
import os
import platform
import time
from unittest.mock import patch

import flint
from scripts import benchmark_grcv4_os_pass as previous

base = previous.base
POLICY = "source_os_exact_hodge_positive_v1"
METHOD = "flint_exact_symmetric_scaled_identity_positive_v1"
SCALE = 1  # Fixed before execution, never selected by searching for acceptance.


def certificate(rows, scale=SCALE):
    """For symmetric H, ||H/s-I||_2<=max(||.||_1,||.||_inf)=d<1
    and s>0 imply lambda_min(H)>=s(1-d)>0. All operations are fmpq;
    no eigenvalue estimate, rounding, inverse or floating tolerance is used.
    The proof is sufficient, NOT an alternative rejection criterion.
    """
    a, s = base.matrix(rows), base.q(scale)
    n = a.nrows()
    base.require(n == a.ncols() and s > 0, "square Hodge and positive exact scale required")
    base.require(a == a.transpose(), "exact Hodge symmetry required")
    # Preserve the native exact-dyadic input boundary, including affine operands.
    for row in a.tolist():
        for x in row:
            d = int(x.denominator)
            base.require(d & (d-1) == 0, "Hodge certificate requires exact dyadic entries")
    proof = {"method": METHOD, "arithmetic": "flint_fmpq", "dimension": n,
             "scale": str(s), "symmetry_verified": True, "exact_dyadic_entries": True,
             "matrix_digest": base.digest([[str(x) for x in row] for row in a.tolist()]),
             "inverse_constructed": False, "elimination_used": False}
    if not n:
        return {**proof, "outcome": "certified", "empty_space": True}
    e = a/s - previous.prior.eye(n)
    one, infinity = previous.prior.norm_bounds(e)
    d = max(one, infinity)
    proof.update(one_norm_deviation=str(one), infinity_norm_deviation=str(infinity),
                 eigenvalue_lower_bound=str(s*(1-d)), eigenvalue_upper_bound=str(s*(1+d)))
    if d >= 1:
        return {**proof, "outcome": "inconclusive", "reason": "strict_positive_lower_bound_unavailable"}
    return {**proof, "outcome": "certified"}


class HodgePositivePolicy(previous.OSPassPolicy):
    """Fixed scale and methods; native assembly and both positivity sites retained."""

    def __init__(self, emit=lambda row: None):
        super().__init__(emit)
        self.affine_checks = None
        self.affine_call = 0

    def positive(self, rows):
        role = "reconstructed_or_retained_hodge"
        if self.affine_checks is not None:
            labels = ("unrounded_affine_hodge", "represented_affine_hodge")
            base.require(self.affine_checks < len(labels), "unexpected extra affine positivity site")
            role = labels[self.affine_checks]
            self.affine_checks += 1
        self.note(stage="hodge_positivity", operation="started", role=role,
                  affine_call=self.affine_call, dimension=len(rows), method=METHOD)
        start = time.monotonic()
        proof = certificate(rows)
        self.note(stage="hodge_positivity", operation="certificate", role=role,
                  affine_call=self.affine_call, seconds=time.monotonic()-start, certificate=proof)
        if proof["outcome"] != "certified":
            raise previous.prior.CertificateInconclusive("exact Hodge positivity certificate inconclusive: " + role)

    @contextmanager
    def installed(self):
        from pygrc.models import grc_v4_geometry as geometry
        from pygrc.models import grc_v4_realizations as real
        original = geometry.H_profile

        def h_profile(tensor, **kwargs):
            base.require(self.affine_checks is None, "nested affine Hodge assembly is not declared")
            active = kwargs["profile"].params_resolved.geometry.kappa_H != 0 and any(x for row in tensor.increment for x in row)
            self.affine_call += 1
            self.affine_checks = 0
            try:
                result = original(tensor, **kwargs)
                base.require(self.affine_checks == (2 if active else 0), "affine Hodge positivity sites changed")
                return result
            finally:
                self.affine_checks = None

        with patch.object(geometry, "_require_positive_definite", self.positive), \
             patch.object(geometry, "H_profile", h_profile), patch.object(real, "H_profile", h_profile), \
             super().installed():
            yield


def worker(connection, job, algorithm, path):
    # Reuse the actual pass, stage timings, exact solvers and native read/closure checks.
    # This substitution is explicit in the selected policy and retained report.
    with patch.object(previous, "OSPassPolicy", HodgePositivePolicy):
        previous.worker(connection, job, algorithm, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, choices=(POLICY,))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--output", type=base.Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve().relative_to(base.ROOT)
    base.require(not (base.ROOT/output).exists(), "report already exists")
    old = base.read(base.ROOT/"implementation/evidence/grcv4-performance/exact_policy_os_pass_probe.json")
    sources = list(old["source_bindings"]) + ["scripts/benchmark_grcv4_hodge_positive.py"]
    report = {"schema": "grcv4-exact-hodge-positive-probe-v1", "policy": POLICY,
              "positivity_method": METHOD, "positivity_scale": SCALE,
              "python": platform.python_version(), "python_flint": flint.__version__,
              "flint_threads": flint.ctx.threads,
              "thread_settings": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
              "source_bindings": {p: hashlib.sha256((base.ROOT/p).read_bytes()).hexdigest() for p in sources},
              "predecessor_record_digest": old["record_digest"],
              "predictor_routes": previous.prior.ROUTES, "corrector_routes": previous.CORRECTOR_ROUTES,
              "production_admission": False, "src_changed": False, "native_steps": 0, "native_events": 0,
              **base.supervised("pass", "dixon", None, args.seconds, target=worker)}
    report["record_digest"] = base.digest(report)
    base.write_new(base.ROOT/output, report)
    print(base.json.dumps({k: report[k] for k in ("outcome", "worker_wall_seconds")}))
    if report["outcome"] != "completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
