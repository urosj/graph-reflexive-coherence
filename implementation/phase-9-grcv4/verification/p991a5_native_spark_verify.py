"""Independent checks on lossless native stage captures, including flux rounding."""

from contextlib import contextmanager
from unittest.mock import patch

from cos_native_spark_oracle import (
    Equations,
    contains,
    incidence,
    infinity,
    matrix,
    vector,
)
from cos_native_spark_oracle import classify as independent_classify
from flint import arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_exact import current_exact_backend
from pygrc.models.grc_v4_spark_cos import SparkCOSKernel


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rows(A):
    return [[str(A[i, j]) for j in range(A.ncols())] for i in range(A.nrows())]


class Capture:
    def __init__(self):
        self.reads, self.step, self.backends = [], None, set()

    @contextmanager
    def installed(self):
        original_read, original_step = SparkCOSKernel._read, SparkCOSKernel.step

        def read(k, C, H, operators):
            self.backends.add(current_exact_backend().value)
            J, f = original_read(k, C, H, operators)
            self.reads.append((M(C), M(H), M(J), M(f)))
            return J, f

        def step(k, *args, **kwargs):
            self.reads = []
            self.step = original_step(k, *args, **kwargs)
            return self.step

        with (
            patch.object(SparkCOSKernel, "_read", read),
            patch.object(SparkCOSKernel, "step", step),
        ):
            yield self

    def payload(self):
        s = self.step
        need(
            s is not None and len(self.reads) == 4,
            "exactly four reads per ordinary step",
        )
        C, after = vector(s.before.C), vector(s.after.C)
        H = matrix(s.selected_geometry)
        I = M([[int(i == j) for j in range(H.nrows())] for i in range(H.nrows())])
        for actual, expected in zip(
            self.reads, ((C, I), (C, H), (after, H), (after, I)), strict=True
        ):
            need(actual[:2] == expected, "wrong predictor/corrector/poststate staging")
        need(
            tuple(map(str, self.reads[1][2].entries())) == s.exact_current,
            "consumed current differs",
        )
        return {
            "before": list(s.before.C),
            "after": list(s.after.C),
            "flux": list(s.flux),
            "H": rows(H),
            "reads": [
                {"J": list(map(str, J.entries())), "f": list(map(str, f.entries()))}
                for _, _, J, f in self.reads
            ],
            "split_squared": s.split_frobenius_squared,
        }


def rounded_flux(q):
    scaled = q * 2**128
    whole = scaled.numerator // scaled.denominator
    remainder = scaled - whole
    if remainder > Q(1, 2) or remainder == Q(1, 2) and whole % 2:
        whole += 1
    return Q(whole, 2**128)


def verify_step(graph, data, U, bound):
    B = incidence(graph)
    before, after, flux = (
        vector(data["before"]),
        vector(data["after"]),
        vector(data["flux"]),
    )
    need(sum(before.entries()) == sum(after.entries()) == 21, "exact charge changed")
    need(after == before - 32 * B * flux, "not the declared single conservative write")
    current = vector(data["reads"][1]["J"])
    need(
        all(
            rounded_flux(q) == f
            for q, f in zip(current.entries(), flux.entries(), strict=True)
        ),
        "flux nearest/even mismatch",
    )
    with _ARB_CONTEXT_LOCK, ctx.workprec(512):
        eq = Equations(graph, outward=True)
        expected = eq.step(data["before"])
        need(
            contains(expected["H"], matrix(data["H"])),
            "independent generated geometry mismatch",
        )
        post = arb_mat(after)
        stages = [
            (expected["predictor_current"], expected["predictor_flat"]),
            (expected["corrector_current"], expected["corrector_flat"]),
            eq.read(post, expected["H"]),
            eq.read(post, eq.I),
        ]
        for name, actual, (J, f) in zip(
            ("predictor", "corrector", "final", "restart"),
            data["reads"],
            stages,
            strict=True,
        ):
            need(contains(J, vector(actual["J"])), name + " current mismatch")
            need(contains(f, vector(actual["f"])), name + " flat mismatch")
        split = sum(x * x for x in expected["split"].entries())
        q = Q(data["split_squared"])
        need(
            split.lower().fmpq() <= q <= split.upper().fmpq(),
            "split predicate mismatch",
        )
        need(q <= Q(*(1e-11).as_integer_ratio()) ** 2, "split tolerance exceeded")
        error = arb_mat(U) * (post - expected["after"])
        upper = max(abs(x).upper().fmpq() for x in error.entries())
        need(upper <= Q(bound), "independent full-step error exceeds bound")
        return str(upper)


def classify_and_membership(state, policy, certificate):
    expected = independent_classify(
        state.graph.to_payload(), state.C, policy.to_payload()
    )
    actual = classify(state, policy)
    need(
        (actual.basins, actual.terminals, [r.to_dict() for r in actual.rows])
        == expected,
        "native geometric classifier differs from exhaustive oracle",
    )
    delta = vector(state.C) - vector(certificate.operands["center"])
    norm = infinity(matrix(certificate.operands["U"]) * delta)
    need(
        certificate.membership(state) == (norm <= 1, str(norm)),
        "membership/charge-chart mismatch",
    )
    return {
        "norm": str(norm),
        "inside": bool(norm <= 1),
        "classification": actual.to_payload(),
    }
