"""Bounded research-only C_OS pass with explicit stage/role numerical methods.

No production edits, approximate answers, algorithm fallback or relaxed gates.
The generated-geometry corrector uses exact Dixon solves, with exact sufficient
conditioning proofs. Native geometry, selector-path and split admission remain
unchanged. Inconclusive certificates stop, rather than reject the science.
"""

from contextlib import contextmanager
from dataclasses import replace
import argparse
import hashlib
import math
import os
import platform
import time
from unittest.mock import patch

from scripts import benchmark_grcv4_resolvent_predictor as prior

base = prior.base
POLICY = "source_os_exact_generated_geometry_v1"
CORRECTOR_ROUTES = {name: ("exact_diagonal" if name == "vertex Hodge inverse" else "dixon")
                    for name in prior.ROUTES}


class CorrectorPolicy(prior.PredictorPolicy):
    """Fixed corrector methods; inherited installation/recording, not dispatch."""

    def __init__(self, inputs, emit=lambda value: None):
        from pygrc.models.grc_v4_candidate_c import CandidateCSelector
        from pygrc.models.grc_v4_geometry import VertexScalar
        self.inputs, self.emit, self.events = inputs, emit, []
        ref, graph = inputs.geometry.reference, inputs.geometry.reference.graph
        base.require(inputs.stage == "os_corrector", "generated-geometry corrector only")
        self.b = base.matrix(graph.incidence)
        self.params = ref.profile.params_resolved.candidate
        self.vertex = prior.eye(self.b.nrows())
        base.require(base.matrix(inputs.geometry.pairings.vertex.matrix) == self.vertex,
                     "declared identity vertex pairing required")
        selector = CandidateCSelector(VertexScalar(graph, inputs.current.C), inputs.geometry.pairings,
                                     self.params.Lambda_C)
        values = selector.selected.values
        base.require(selector.rank == 1 and all(x == values[0] for x in values),
                     "corrector policy requires constant selector")
        rho = math.tanh(values[0] / self.params.C_ref)
        d = base.q(math.exp((.5 * self.params.kappa_M_C) * (.5 * (rho + rho))))
        self.h = base.q(float(d*d))
        self.retained = base.rounded(d*d * base.matrix(inputs.geometry.one_form_hodge.matrix))
        # This independent exact sufficient SPD proof does not bypass native Hodge validation.
        proof = prior.near_identity.certify(self.retained, self.h, ref.profile.params_resolved.solver.conditioning_limit)
        if self.retained != self.retained.transpose() or proof["outcome"] != "certified":
            raise prior.CertificateInconclusive("symmetric positive retained-Hodge witness unavailable")
        self.beta = base.q(self.params.zeta_C) * base.q(self.params.chi_C)
        self.regularity = ((1-self.beta) * prior.eye(self.b.ncols())
                           + base.q(self.params.tau_C) * self.b.transpose() * self.b * self.retained)
        self.current_block = None
        self.note(stage="corrector_retained_hodge_witness", certificate=proof,
                  symmetry_verified=True, scalar_hodge_assumed=False)

    def inverse(self, rows):
        a = base.matrix(rows)
        if a == self.regularity:
            if not (1-self.beta > 0 and self.params.tau_C >= 0):
                raise prior.CertificateInconclusive("positive similarity regularity proof unavailable")
            # B^T B H is similar to H^(1/2) B^T B H^(1/2), positive semidefinite.
            # H is symmetric positive definite by the exact witness above.
            self.note(stage="discarded_regularity_inverse_guard", method="positive_hodge_similarity",
                      inverse_constructed=False)
            return None
        return super().inverse(rows)

    def condition(self, rows, limit, label):
        from pygrc.models.grc_v4_state import FrozenJSONMap
        a, start = base.matrix(rows), time.monotonic()
        if label == "retained resolvent":
            # The old scalar Hodge is a comparison CENTER, not the actual corrector Hodge.
            # E includes all non-diagonal geometry effects and represented assembly error.
            proof = prior.resolvent_certificate(a, self.b, self.params.tau_C, self.h, limit)
        elif label in CORRECTOR_ROUTES or label in ("physical total-current block", "physical Q_C identification"):
            scale = self.h if label in ("inverse retained identification", "physical Q_C similarity",
                                       "physical Q_C identification") else 1
            proof = prior.near_identity.certify(a, scale, limit)
        else:
            raise prior.CertificateInconclusive("unregistered corrector condition role; no fallback")
        self.note(stage=label, operation="condition", seconds=time.monotonic()-start, certificate=proof)
        if proof["outcome"] != "certified":
            raise prior.CertificateInconclusive("corrector conditioning certificate unavailable: " + label)
        return FrozenJSONMap({"block": label, "norm": "euclidean_2",
                              "condition_upper_squared": proof["condition_upper_squared"], "limit": limit})

    def solve(self, rows, rhs, policy, label, certificates):
        from pygrc.models import grc_v4_numerics as numerics
        base.require(label in CORRECTOR_ROUTES, "unregistered corrector solve role; no fallback")
        a, b = base.matrix(rows), base.matrix(rhs)
        certificates.append(self.condition(rows, policy.conditioning_limit, label))
        method = CORRECTOR_ROUTES[label]
        self.emit({"stage": label, "operation": "solve_started", "method": method})
        start = time.monotonic()
        if method == "exact_diagonal":
            base.require(a == self.vertex, "declared vertex identity changed")
            x = b
        else:
            x = base.direct(a, b, "dixon")
        elapsed = time.monotonic()-start
        start = time.monotonic()
        base.verify_exact(a, b, x)
        result = base.rounded(x)
        residual = a*result-b
        for j in range(b.ncols()):
            if not numerics.residual_pass(tuple(residual[i, j] for i in range(a.nrows())),
                                         tuple(b[i, j] for i in range(b.nrows())), policy):
                raise numerics.MatrixError("no_admitted_root", "declared residual tolerance failed: " + label)
        self.note(stage=label, operation="solve", method=method, solve_seconds=elapsed,
                  verification_rounding_residual_seconds=time.monotonic()-start,
                  exact_identity=True, rounded_residual_pass=True, rhs_columns=b.ncols())
        if label == "physical Q_C similarity":
            self.current_block = base.rounded(prior.eye(a.nrows())-self.beta*result)
        elif label == "retained resolvent" and self.params.tau_C == 0:
            self.current_block = base.rounded((1-self.beta)*prior.eye(a.nrows()))
        return tuple(tuple(float(x) for x in row) for row in result.tolist())


class OSPassPolicy:
    """Run the real OS driver; scope each numerical callback to its native stage."""

    def __init__(self, emit=lambda value: None):
        self.events, self.emit, self.stages = [], emit, []

    def note(self, **row):
        self.events.append(row)
        self.emit(row)

    def timed(self, name, operation):
        def call(*args, **kwargs):
            self.note(stage=name, operation="started")
            start = time.monotonic()
            result = operation(*args, **kwargs)
            self.note(stage=name, operation="completed", seconds=time.monotonic()-start)
            return result
        return call

    @contextmanager
    def installed(self):
        from pygrc.models import grc_v4_realizations as real
        original = real.CandidateCCurrent

        def current(inputs):
            expected = ("os_predictor", "os_corrector")
            base.require(len(self.stages) < 2 and inputs.stage == expected[len(self.stages)],
                         "exactly one predictor followed by one corrector required")
            self.stages.append(inputs.stage)
            start = time.monotonic()
            self.note(stage=inputs.stage, operation="policy_setup_started")
            emit = lambda row: self.note(native_stage=inputs.stage, **row)
            policy_type = prior.PredictorPolicy if inputs.stage == "os_predictor" else CorrectorPolicy
            policy = policy_type(inputs, emit)
            self.note(stage=inputs.stage, operation="policy_setup_completed", seconds=time.monotonic()-start)
            start = time.monotonic()
            with policy.installed():
                point = original(inputs)
            self.note(stage=inputs.stage, operation="native_current_completed", seconds=time.monotonic()-start,
                      closure_residual_squared=point.closure_residual_squared, selector_rank=point.algebra.selector.rank)
            return point

        with patch.object(real, "CandidateCCurrent", current), \
             patch.object(real, "_source_geometry", self.timed("native_source_geometry", real._source_geometry)), \
             patch.object(real, "_selector_path_segments", self.timed("native_selector_path", real._selector_path_segments)), \
             patch.object(real, "OSSplitResidual", self.timed("native_split_admission", real.OSSplitResidual)):
            yield


def point_summary(point):
    return {"current": list(point.current.values), "baseline": list(point.algebra.baseline.values),
            "read_flux": list(point.read.flux.values), "causal_flat": list(point.read.causal_flat.values),
            "closure_residual_squared": point.closure_residual_squared,
            "selector_rank": point.algebra.selector.rank,
            "current_block_digest": base.digest(point.algebra.current_block),
            "input_hodge_digest": base.digest(point.inputs.geometry.one_form_hodge.matrix),
            "retained_hodge_digest": base.digest(point.algebra.retained_hodge.matrix)}


def worker(connection, job, algorithm, path):
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
    from pygrc.models.grc_v4_realizations import CandidateCOSPass
    try:
        base.require(job == "pass" and algorithm == "dixon", "explicit pass/Dixon selection required")
        with exact_backend(ExactBackend.FLINT):
            emit = lambda row: connection.send(("progress", row))
            start = time.monotonic()
            inputs = replace(prior.materialize(), stage="pre_read")
            setup_seconds = time.monotonic()-start
            policy = OSPassPolicy(emit)
            start = time.monotonic()
            with policy.installed():
                result = CandidateCOSPass(inputs)
            elapsed = time.monotonic()-start
            prior_result = base.read(base.ROOT / "implementation/evidence/grcv4-performance/exact_policy_predictor_probe.json")["result"]
            base.require(list(result.predictor.current.values) == prior_result["current"], "predictor differs from prior measured result")
            connection.send(("result", {"setup_seconds": setup_seconds, "pass_seconds": elapsed,
                "complete_os_pass": True, "instrumented_numerical_policy": True,
                "predictor": point_summary(result.predictor), "corrector": point_summary(result.corrector),
                "split_admitted": result.residual.admitted,
                "split_exact_values_digest": base.digest(result.residual.exact_values),
                "selector_path_segments": result.selector_path_segments,
                "predictor_matches_prior": True, "operations": policy.events}))
    except prior.CertificateInconclusive as exc:
        connection.send(("error", {"type": "certificate_inconclusive", "message": str(exc)}))
    except Exception as exc:
        connection.send(("error", {"type": type(exc).__name__, "message": str(exc)}))
    finally:
        connection.close()


def main():
    import flint
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, choices=(POLICY,))
    parser.add_argument("--seconds", required=True, type=float)
    parser.add_argument("--output", required=True, type=base.Path)
    args = parser.parse_args()
    output = args.output.resolve().relative_to(base.ROOT)
    base.require(not (base.ROOT/output).exists(), "report already exists")
    sources = ["scripts/benchmark_grcv4_os_pass.py", "scripts/benchmark_grcv4_resolvent_predictor.py",
               "scripts/benchmark_grcv4_exact_direct.py", "scripts/benchmark_grcv4_identity_condition.py",
               base.DECLARATION, "implementation/phase-9-grcv4/verification/prepare_p983_all_realizations.py",
               "implementation/phase-9-grcv4/verification/prepare_p983_graph_admission.py",
               "src/pygrc/models/grc_v4_candidate_c.py", "src/pygrc/models/grc_v4_realizations.py",
               "src/pygrc/models/grc_v4_geometry.py", "src/pygrc/models/grc_v4_numerics.py",
               "src/pygrc/models/grc_v4_exact.py", "src/pygrc/models/_grc_v4_matrix.py",
               "src/pygrc/models/_grc_v4_matrix_flint.py"]
    report = {"schema": "grcv4-exact-os-pass-probe-v1", "policy": POLICY,
              "python": platform.python_version(), "python_flint": flint.__version__,
              "flint_threads": flint.ctx.threads,
              "thread_settings": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
              "source_bindings": {p: hashlib.sha256((base.ROOT/p).read_bytes()).hexdigest() for p in sources},
              "predictor_routes": prior.ROUTES, "corrector_routes": CORRECTOR_ROUTES,
              "production_admission": False, "src_changed": False, "native_steps": 0, "native_events": 0,
              **base.supervised("pass", "dixon", None, args.seconds, target=worker)}
    report["record_digest"] = base.digest(report)
    base.write_new(base.ROOT/output, report)
    print(base.json.dumps({k: report[k] for k in ("outcome", "worker_wall_seconds")}))
    if report["outcome"] != "completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
