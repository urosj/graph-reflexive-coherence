"""Explicit research numerical policy for one complete C_OS predictor.

No src/ edits. Numerical callbacks are replaced ONLY inside this bounded
worker, explicitly recorded as instrumentation, never as production admission.
Native selector, stage assembly, Read-Back and closure residual remain intact.
Every matrix role has one named algorithm; unknown roles fail without fallback.
"""

from contextlib import contextmanager
from dataclasses import replace
import argparse
import hashlib
import math
import time
from unittest.mock import patch

from flint import fmpq_mat
from scripts import benchmark_grcv4_exact_direct as base
from scripts import benchmark_grcv4_identity_condition as near_identity

POLICY = "source_predictor_exact_gram_perturbation_v1"
ROUTES = {
    "structural flat map": "exact_diagonal",
    "pre-to-retained identification": "exact_diagonal",
    "inverse retained identification": "exact_diagonal",
    "vertex Hodge inverse": "exact_diagonal",
    "retained resolvent": "dixon_with_exact_gram_perturbation",
    "physical Q_C similarity": "exact_diagonal",
    "physical current solve": "dixon_with_exact_identity_norm",
}


class CertificateInconclusive(RuntimeError):
    """A sufficient bound is unavailable; no assertion of scientific rejection."""


def eye(n):
    out = fmpq_mat(n, n)
    for i in range(n):
        out[i, i] = 1
    return out


def norm_bounds(a):
    rows = [sum((abs(x) for x in row), base.q(0)) for row in a.tolist()]
    cols = [sum((abs(a[i, j]) for i in range(a.nrows())), base.q(0)) for j in range(a.ncols())]
    return max(cols, default=base.q(0)), max(rows, default=base.q(0))


def resolvent_certificate(actual, b, tau, retained_scale, limit):
    """Rigorous Euclidean condition bound for the actual represented matrix.

R0=I+tau*h*B^T B, tau>=0, h>0, so sigma_min(R0)>=1 and
sigma_max(R0)<=1+tau*h*||B||_1*||B||_inf. R=R0+E may be
nonsymmetric. Singular-value perturbation by ||E||_2, bounded by
max(||E||_1,||E||_inf), covers EVERY represented assembly error.
"""
    tau, h, limit = map(base.q, (tau, retained_scale, limit))
    m = b.ncols()
    base.require(m > 0 and b.nrows() > 0 and actual.nrows() == actual.ncols() == m,
                 "resolvent coordinate mismatch")
    base.require(tau >= 0 and h > 0 and limit >= 1, "resolvent proof domain")
    ideal = eye(m) + tau * h * b.transpose() * b
    one, infinity = norm_bounds(b)
    eone, einf = norm_bounds(actual - ideal)
    error = max(eone, einf)
    lower, upper = 1 - error, 1 + tau * h * one * infinity + error
    result = {"method": "exact_gram_resolvent_perturbation_v1",
        "tau": str(tau), "retained_scalar_hodge": str(h), "limit": str(limit),
        "incidence_one_norm": str(one), "incidence_infinity_norm": str(infinity),
        "represented_error_one_norm": str(eone), "represented_error_infinity_norm": str(einf),
        "represented_error_norm2_upper": str(error), "singular_value_lower": str(lower),
        "singular_value_upper": str(upper), "inverse_constructed": False}
    if lower <= 0:
        return {**result, "outcome": "inconclusive", "reason": "positive_lower_bound_unavailable"}
    bound = (upper / lower) ** 2
    result.update(condition_upper_squared=str(bound), nonsingular=True)
    if bound > limit**2:
        return {**result, "outcome": "inconclusive", "reason": "sufficient_bound_exceeds_limit"}
    return {**result, "outcome": "certified"}


def scalar_hodge(inputs):
    """Restricted predictor witness, checked before installing callbacks."""
    ref = inputs.geometry.reference
    params = ref.profile.params_resolved.candidate
    graph = ref.graph
    base.require(inputs.stage == "os_predictor" and inputs.geometry == ref.geometry(),
                 "reference-geometry predictor only")
    base.require(base.matrix(ref.pairings.one_form.matrix) == eye(len(graph.oriented_edges))
                 and base.matrix(ref.pairings.vertex.matrix) == eye(len(graph.live_node_ids)),
                 "identity reference pairings required")
    from pygrc.models.grc_v4_candidate_c import CandidateCSelector
    from pygrc.models.grc_v4_geometry import VertexScalar
    selector = CandidateCSelector(VertexScalar(graph, inputs.current.C), inputs.geometry.pairings, params.Lambda_C)
    values = selector.selected.values
    base.require(selector.rank == 1 and all(x == values[0] for x in values), "constant selector required")
    rho = math.tanh(values[0] / params.C_ref)
    deformation = math.exp((.5 * params.kappa_M_C) * (.5 * (rho + rho)))
    h = base.q(float(base.q(deformation) ** 2))
    base.require(h > 0 and math.isfinite(float(h)), "positive finite scalar Hodge required")
    return h


class PredictorPolicy:
    """Experimental fixed per-role algorithms; not a production dispatch API."""

    def __init__(self, inputs, emit=lambda value: None):
        self.inputs, self.emit = inputs, emit
        self.b = base.matrix(inputs.geometry.reference.graph.incidence)
        self.params = inputs.geometry.reference.profile.params_resolved.candidate
        self.h = scalar_hodge(inputs)
        self.beta = base.q(self.params.zeta_C) * base.q(self.params.chi_C)
        self.regularity = (1 - self.beta) * eye(self.b.ncols()) + base.q(self.params.tau_C) * self.h * self.b.transpose() * self.b
        self.vertex = eye(self.b.nrows())
        self.current_block = None
        self.events = []

    def note(self, **event):
        self.events.append(event)
        self.emit(event)

    def inverse(self, rows):
        """Explicitly replace two DISCARDED inverse calls with boolean proofs.

Return None for those two guarded call sites, not a fabricated inverse.
This callback must never be published as a generic inverse implementation.
The only value-producing inverse allowed here is the declared vertex identity.
"""
        a = base.matrix(rows)
        if a == self.vertex:
            self.note(stage="vertex_identity_inverse", method="exact_identity", dimension=a.nrows())
            return tuple(tuple(row) for row in a.tolist())
        if a == self.regularity:
            if not (1 - self.beta > 0 and self.params.tau_C >= 0 and self.h > 0):
                raise CertificateInconclusive("positive Gram regularity proof unavailable")
            self.note(stage="discarded_regularity_inverse_guard", method="positive_gram", inverse_constructed=False)
            return None
        if self.current_block is not None and a == self.current_block:
            proof = near_identity.certify(a, 1, self.inputs.geometry.reference.profile.params_resolved.solver.conditioning_limit)
            if proof["outcome"] != "certified":
                raise CertificateInconclusive("physical current guard certificate unavailable")
            self.note(stage="discarded_physical_inverse_guard", method=proof["method"], inverse_constructed=False)
            return None
        raise CertificateInconclusive("unregistered inverse role; no fallback")

    def condition(self, rows, limit, label):
        from pygrc.models.grc_v4_state import FrozenJSONMap
        a = base.matrix(rows)
        start = time.monotonic()
        if label == "retained resolvent":
            proof = resolvent_certificate(a, self.b, self.params.tau_C, self.h, limit)
        elif label in ("physical total-current block", "physical current solve"):
            proof = near_identity.certify(a, 1, limit)
        elif label in ROUTES or label == "physical Q_C identification":
            base.require(a.nrows() > 0 and a.nrows() == a.ncols() and
                         all(a[i, j] == 0 for i in range(a.nrows()) for j in range(a.ncols()) if i != j),
                         "declared diagonal role is not diagonal")
            diagonal = [abs(a[i, i]) for i in range(a.nrows())]
            if not min(diagonal):
                raise CertificateInconclusive("diagonal block has zero singular value")
            bound = (max(diagonal) / min(diagonal)) ** 2
            proof = {"method": "exact_diagonal_condition", "condition_upper_squared": str(bound),
                     "outcome": "certified" if bound <= base.q(limit)**2 else "inconclusive"}
        else:
            raise CertificateInconclusive("unregistered conditioning role; no fallback")
        self.note(stage=label, operation="condition", seconds=time.monotonic() - start, certificate=proof)
        if proof["outcome"] != "certified":
            raise CertificateInconclusive("conditioning certificate unavailable: " + label)
        return FrozenJSONMap({"block": label, "norm": "euclidean_2",
                              "condition_upper_squared": proof["condition_upper_squared"], "limit": limit})

    def solve(self, rows, rhs, policy, label, certificates):
        from pygrc.models import grc_v4_numerics as numerics
        base.require(label in ROUTES, "unregistered solve role; no fallback")
        a, b = base.matrix(rows), base.matrix(rhs)
        certificates.append(self.condition(rows, policy.conditioning_limit, label))
        self.emit({"stage": label, "operation": "solve_started", "method": ROUTES[label]})
        start = time.monotonic()
        if ROUTES[label] == "exact_diagonal":
            # condition() has checked the explicitly declared diagonal structure.
            x = fmpq_mat([[b[i, j] / a[i, i] for j in range(b.ncols())] for i in range(b.nrows())])
        else:
            x = base.direct(a, b, "dixon")
        solve_seconds = time.monotonic() - start
        start = time.monotonic()
        base.verify_exact(a, b, x)
        result = base.rounded(x)
        residual = a * result - b
        for j in range(b.ncols()):
            if not numerics.residual_pass(tuple(residual[i, j] for i in range(a.nrows())),
                                         tuple(b[i, j] for i in range(b.nrows())), policy):
                raise numerics.MatrixError("no_admitted_root", "declared residual tolerance failed: " + label)
        self.note(stage=label, operation="solve", method=ROUTES[label], solve_seconds=solve_seconds,
                  verification_rounding_residual_seconds=time.monotonic() - start,
                  exact_identity=True, rounded_residual_pass=True, rhs_columns=b.ncols())
        if label == "physical Q_C similarity":
            self.current_block = base.rounded(eye(a.nrows()) - self.beta * result)
        elif label == "retained resolvent" and self.params.tau_C == 0:
            self.current_block = base.rounded((1 - self.beta) * eye(a.nrows()))
        return tuple(tuple(float(x) for x in row) for row in result.tolist())

    @contextmanager
    def installed(self):
        from pygrc.models import grc_v4_numerics as numerics
        with patch.object(numerics, "inverse", self.inverse), patch.object(numerics, "condition", self.condition), patch.object(numerics, "solve", self.solve):
            yield


def materialize():
    import sys
    sys.path.insert(0, str(base.ROOT / "implementation/phase-9-grcv4/verification"))
    import prepare_p983_all_realizations as preparation
    record = base.read(base.ROOT / base.DECLARATION)
    state = preparation.materialize(record, "source")
    return replace(state.inputs, stage="os_predictor", dt=record["selected_configuration"]["ordinary_dt"])


def worker(connection, job, algorithm, path):
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
    try:
        with exact_backend(ExactBackend.FLINT):
            emit = lambda row: connection.send(("progress", row))
            start = time.monotonic()
            inputs = materialize()
            setup_seconds = time.monotonic() - start
            start = time.monotonic()
            policy = PredictorPolicy(inputs, emit)
            policy_setup_seconds = time.monotonic() - start
            if job == "certificate":
                # Reproduce both production product rounds before resolvent rounding.
                b, h = policy.b, policy.h * eye(policy.b.ncols())
                laplacian = base.rounded(b.transpose() * base.rounded(b * h))
                represented = base.rounded(eye(b.ncols()) + base.q(policy.params.tau_C) * laplacian)
                start = time.monotonic()
                cert = resolvent_certificate(represented, b, policy.params.tau_C, policy.h,
                                             inputs.geometry.reference.profile.params_resolved.solver.conditioning_limit)
                result = {"certificate": cert, "certificate_seconds": time.monotonic() - start,
                    "represented_resolvent_digest": base.digest([[float(x) for x in row] for row in represented.tolist()])}
                if cert["outcome"] != "certified":
                    raise CertificateInconclusive("resolvent certificate unavailable")
            else:
                from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
                start = time.monotonic()
                with policy.installed():
                    point = CandidateCCurrent(inputs)
                result = {"predictor_seconds": time.monotonic() - start,
                    "closure_residual_squared": point.closure_residual_squared,
                    "selector_rank": point.algebra.selector.rank,
                    "current": list(point.current.values), "baseline": list(point.algebra.baseline.values),
                    "read_flux": list(point.read.flux.values), "causal_flat": list(point.read.causal_flat.values),
                    "predictor_completed": True, "instrumented_numerical_policy": True,
                    "current_block_digest": base.digest([list(row) for row in point.algebra.current_block]),
                    "operations": policy.events}
                prior, _, _ = base.load_block(base.ROOT / "implementation/evidence/grcv4-performance/direct_source_predictor_block.json.xz")
                direct = base.read(base.ROOT / "implementation/evidence/grcv4-performance/direct_source_predictor_dixon.json")
                base.require(point.algebra.current_block == tuple(tuple(r) for r in prior["matrix"]), "prior represented block mismatch")
                base.require(point.algebra.baseline.values == tuple(r[0] for r in prior["rhs"]), "prior baseline mismatch")
                base.require(point.current.values == tuple(r[0] for r in direct["result"]["rounded_solution"]), "prior exact-direct output mismatch")
                result["prior_block_baseline_and_rounded_current_match"] = True
            result.update(setup_seconds=setup_seconds, policy_setup_seconds=policy_setup_seconds)
            connection.send(("result", result))
    except CertificateInconclusive as exc:
        connection.send(("error", {"type": "certificate_inconclusive", "message": str(exc)}))
    except Exception as exc:
        connection.send(("error", {"type": type(exc).__name__, "message": str(exc)}))
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", choices=("certificate", "predictor"))
    parser.add_argument("--policy", required=True, choices=(POLICY,))
    parser.add_argument("--seconds", required=True, type=float)
    parser.add_argument("--output", required=True, type=base.Path)
    args = parser.parse_args()
    output = args.output.resolve().relative_to(base.ROOT)
    base.require(not (base.ROOT / output).exists(), "report already exists")
    sources = ["scripts/benchmark_grcv4_resolvent_predictor.py", "scripts/benchmark_grcv4_exact_direct.py",
        "scripts/benchmark_grcv4_identity_condition.py", base.DECLARATION,
        "implementation/phase-9-grcv4/verification/prepare_p983_all_realizations.py",
        "implementation/phase-9-grcv4/verification/prepare_p983_graph_admission.py",
        "src/pygrc/models/grc_v4_candidate_c.py", "src/pygrc/models/grc_v4_numerics.py",
        "src/pygrc/models/grc_v4_geometry.py", "src/pygrc/models/grc_v4_exact.py"]
    report = {"schema": "grcv4-resolvent-predictor-probe-v1", "job": args.job, "policy": args.policy,
        "source_bindings": {p: hashlib.sha256((base.ROOT / p).read_bytes()).hexdigest() for p in sources},
        "solve_routes": ROUTES, "production_admission": False, "src_changed": False,
        "complete_os_pass": False, "native_steps": 0, "native_events": 0,
        **base.supervised(args.job, "dixon", None, args.seconds, target=worker)}
    report["record_digest"] = base.digest(report)
    base.write_new(base.ROOT / output, report)
    print(base.json.dumps({k: v for k, v in report.items() if k in ("job", "outcome", "worker_wall_seconds", "error")}))
    if report["outcome"] != "completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
