"""A_RG2b campaign adapter: exact C metric, outward log-W metric.

The independent C quadratic form is rational. Converting it to an Arb ball
introduces an unnecessary positive radius, which cannot certify an exactly
equal native rational upper bound. Preserve exactness before comparing bounds.
The shared C_RG2b campaign source and its ongoing execution remain unchanged.
"""

import argparse
from hashlib import sha256

import p991a6_rg2b_campaign as common
from flint import arb, arb_mat, ctx, fmpq as Q, fmpq_mat as M
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from arg2b_native_spark_pressure_oracle import algebra

SELF = common.HERE + "p991a6_arg2b_campaign.py"
TEST = common.HERE + "test_p991a6_arg2b_campaign_metric.py"
FIXTURE = common.BASE + "P9-9.1a.6-ARG2b.5-MetricRegression.json.xz"
BASE_BINDINGS = common.bindings


def metric_bounds(graph, curve, state, parameter, radius):
    s, radius = Q(parameter), Q(radius)
    common.need(0 <= s <= 1 and radius > 0, "shared parameter/radius")
    coefficients = M(curve)
    t = [Q(1), 2 * s - 1]
    for _ in range(2, coefficients.ncols()):
        t.append(2 * t[1] * t[-1] - t[-2])
    point = coefficients * M([[x] for x in t[: coefficients.ncols()]])
    n = len(state.C)
    dc = M([[Q(c) - point[i, 0]] for i, c in enumerate(state.C)])
    c = (dc.transpose() * algebra(graph)[3] * dc)[0, 0] / radius**2
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        dy = arb_mat(
            [
                [64 * arb(Q(w)).log() - arb(point[n + i, 0])]
                for i, w in enumerate(state.W_A)
            ]
        )
        y = sum(x * x for x in dy.entries()).nonnegative_part()
        lo = max(c, y.lower().fmpq() / radius**2)
        hi = max(c, y.upper().fmpq() / radius**2)
    return lo, hi


def observation(a, state, policy, certificate):
    common.need(a.family == "A_RG2b", "A-only exact joint metric adapter")
    certificate.require_binding(
        a.kernel(state.graph, a.subjects.profile(state.graph)),
        policy,
        certificate.operands["binding"]["role"],
        state.charge,
    )
    actual = a.domain.membership_details(certificate, state)
    lo, hi = metric_bounds(
        state.graph.to_payload(),
        certificate.operands["curve"],
        state,
        actual["parameter"],
        certificate.operands["radius"],
    )
    common.need(hi <= Q(actual["squared_norm"]), "independent joint metric upper bound")
    common.need(
        (actual["inside"] and hi <= 1) or (not actual["inside"] and lo > 1),
        "selected-parameter membership disagreement",
    )
    return dict(
        actual,
        independent_lower=str(lo),
        independent_upper=str(hi),
        classification_digest=common.classification(state, policy),
    )


def bindings(a):
    rows = BASE_BINDINGS(a)
    rows.extend(
        {"path": p, "sha256": sha256((common.ROOT / p).read_bytes()).hexdigest()}
        for p in (SELF, TEST, FIXTURE)
    )
    return sorted(rows, key=lambda row: row["path"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--profile", action="store_true")
    action.add_argument("--run", action="store_true")
    args = parser.parse_args()
    common.observation = observation
    common.bindings = bindings
    a = common.Adapter("A_RG2b")
    (common.profile if args.profile else common.campaign)(a)
