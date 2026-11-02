"""Independent composite pressure constructions, with exact-real input bridges.

Only fixed-H equations construct the manufactured roots. A rounded carrier is a
different exact native subject; its full-input residual certifies that bridge.
"""

from dataclasses import replace

from acipc_native_spark_oracle import Reference, audit_read, frobenius, verify_step
from aos_native_spark_oracle import classify, contains, need, upper
from cos_native_spark_oracle import matrix, vector
from cpc_native_spark_pressure_oracle import decode, intervals, round_even
from flint import arb, arb_mat
from flint import fmpq as Q

__all__ = [
    "Reference",
    "audit_read",
    "classify",
    "contains",
    "frobenius",
    "need",
    "upper",
    "verify_step",
]


def midpoint(A):
    return arb_mat([[x.mid() for x in row] for row in A.tolist()])


def admit_proposal(ref, C, W, Z, proposal):
    need(upper(proposal) < Q(1, 32), "proposal outside declared root ball")
    need(all(0 <= x <= 4 for x in C.entries()), "proposal resource domain")
    need(
        all(arb(Q(99, 100)) <= x <= arb(Q(101, 100)) for x in W.entries()),
        "proposal W domain",
    )
    need(frobenius(Z) <= Q(1, 64), "proposal carrier domain")
    residual = upper(
        ref.read(C, W, ref.composite_geometry(proposal, Z))["causal_flat"] - proposal
    )
    radius = residual / (1 - ref.rate)
    need(upper(proposal) + radius < Q(1, 32), "proposal enclosure outside root ball")
    return residual, radius


def manufacture(state, H):
    """Define real Z=2(H-I)-S and bind its explicitly rounded native counterpart."""
    ref = Reference(state.graph.to_payload())
    C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
    fixed = ref.read(C, W, H)
    flat = fixed["causal_flat"]
    source = ref.source(flat)
    real_Z = 2 * (H - ref.I) - source
    native_Z = tuple(
        tuple(str(round_even(x.mid().fmpq(), 600)) for x in row)
        for row in real_Z.tolist()
    )
    native = replace(state, Z_4=native_Z)
    rounded = arb_mat(matrix(native.Z_4))
    residual, radius = admit_proposal(ref, C, W, rounded, midpoint(flat))
    conversion = upper(rounded - real_Z)
    need(conversion < Q(1, 2**599), "manufactured carrier conversion allowance")
    need(frobenius(real_Z) < Q(1, 64), "manufactured real carrier domain")
    need(upper(flat) < Q(1, 32), "manufactured exact-real flat domain")
    # SPD follows independently from ||H-I||_2 <= ||H-I||_F < 1.
    need(frobenius(H - ref.I) < 1, "manufactured SPD geometry")
    return native, {
        "state": native.to_payload(),
        "H0": intervals(H),
        "fixed_read": {key: intervals(value) for key, value in fixed.items()},
        "source0": intervals(source),
        "exact_real_Z": intervals(real_Z),
        "conversion_error": str(conversion),
        "conversion_bits": 600,
        "bridge_residual": str(residual),
        "bridge_radius": str(radius),
        "exact_real_root_not_identified_with_rounded_subject": True,
    }


def audit_manufactured(payload):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState

    state = ExactAdaptiveCarrierState.from_canonical_bytes(
        canonical_json_bytes(payload["state"])
    )
    ref = Reference(state.graph.to_payload())
    H = decode(payload["H0"])
    C, W, Z = (
        arb_mat(vector(state.C)),
        arb_mat(vector(state.W_A)),
        arb_mat(matrix(state.Z_4)),
    )
    fixed = ref.read(C, W, H)
    source = ref.source(fixed["causal_flat"])
    real_Z = 2 * (H - ref.I) - source
    for key, value in fixed.items():
        need(
            contains(payload["fixed_read"][key], value),
            "manufactured fixed read " + key,
        )
    need(contains(payload["source0"], source), "manufactured source definition")
    need(contains(payload["exact_real_Z"], real_Z), "manufactured carrier definition")
    need(
        upper(Z - real_Z) <= Q(payload["conversion_error"]) < Q(1, 2**599),
        "manufactured conversion bound",
    )
    residual, radius = admit_proposal(ref, C, W, Z, midpoint(fixed["causal_flat"]))
    need(
        residual <= Q(payload["bridge_residual"])
        and radius <= Q(payload["bridge_radius"]),
        "manufactured actual-input bridge",
    )
    need(
        frobenius(real_Z) < Q(1, 64) and frobenius(H - ref.I) < 1, "manufactured domain"
    )
    need(
        payload["exact_real_root_not_identified_with_rounded_subject"] is True,
        "manufactured scope",
    )
    return {
        "fixed_H_construction": True,
        "complete_domain_checked": True,
        "conversion_bits": 600,
        "bridge_radius": str(radius),
    }


def frozen_reference_root(ref, C, W, Z):
    """Deliberate wrong equation: fix G at an admitted nonzero trial and converge."""
    first = arb_mat([[Q((-1) ** i, 128)] for i in range(ref.m)])
    old_G = ref.read(C, W, ref.composite_geometry(first, Z))["drive"]
    theta = arb_mat(
        [[(W[i, 0] - old_G[i, 0]) / (W[i, 0] + old_G[i, 0])] for i in range(ref.m)]
    )

    def wrong(flat):
        H = ref.composite_geometry(flat, Z)
        selected = ref.read(C, W, H)
        j0 = selected["baseline"]
        J = arb_mat([[j0[i, 0] / (1 - theta[i, 0] / 4)] for i in range(ref.m)])
        F = H.inv() * arb_mat([[theta[i, 0] * J[i, 0] / 2] for i in range(ref.m)])
        return (
            F,
            H,
            selected | {"drive": old_G, "q": theta, "current": J, "causal_flat": F},
        )

    flat = arb_mat(ref.m, 1)
    for iteration in range(60):
        F, H, selected = wrong(flat)
        if upper(F - flat) < Q(1, 2**640):
            break
        flat = midpoint(F)
    else:
        raise AssertionError("counterfeit iteration did not converge")
    residual = upper(F - flat)
    actual = upper(
        ref.read(C, W, ref.composite_geometry(flat, Z))["causal_flat"] - flat
    )
    need(
        actual > Q(1, 2**192) and residual < Q(1, 2**640),
        "counterfeit must be resolved despite its convergence",
    )
    return {
        "flat": flat,
        "H": H,
        "selected": selected,
        "source": ref.source(flat),
        "iterations": iteration + 1,
        "wrong_residual": residual,
        "actual_residual": actual,
    }


def audit_twins(records):
    from p991a6_acipc_preflight import decoded

    a, b = (records[name] for name in ("reference_cancellation", "equal_current_twin"))
    for row in (a, b):
        audit_manufactured(row)
        verify_step(decoded(row["step"]))
    one, two = decoded(a["step"]), decoded(b["step"])
    need(
        one.before.C == two.before.C and one.before.W_A == two.before.W_A,
        "manufactured same C/W inputs",
    )
    need(
        one.after.C == two.after.C and one.after.W_A == two.after.W_A,
        "manufactured equal represented C/W",
    )
    need(one.after.Z_4 != two.after.Z_4, "manufactured distinct represented Z")
    ref = Reference(one.before.graph.to_payload())
    H0, H1 = decode(a["H0"]), decode(b["H0"])
    E = 2 * (H1 - H0)
    need(
        all(x.is_zero() for x in (H0 - ref.I).entries()),
        "manufactured reference geometry",
    )
    need(
        all(
            x.is_zero()
            for x in (E * ref.B.transpose() * arb_mat(vector(one.before.C))).entries()
        ),
        "exact current-invisible E",
    )
    S0, S1 = decode(a["source0"]), decode(b["source0"])
    gap = max(abs(x).lower().fmpq() for x in (S1 - S0).entries())
    need(gap > Q(1, 2**192), "resolved twin source separation")
    decay = (-arb(1)).exp()
    budget = 2 * (
        Q(one.carrier_component_error)
        + Q(a["bridge_radius"])
        + Q(b["bridge_radius"])
        + Q(a["conversion_error"])
        + Q(b["conversion_error"])
    )
    Z0, Z1 = arb_mat(matrix(one.after.Z_4)), arb_mat(matrix(two.after.Z_4))
    need(
        upper(Z0 - (1 - 2 * decay) * S0) < budget,
        "cancellation root held-source writer",
    )
    need(
        upper(Z1 - Z0 - decay * E - (1 - 2 * decay) * (S1 - S0)) < budget,
        "twin carrier difference identity",
    )
    return {
        "same_native_C_W": True,
        "distinct_native_Z": True,
        "resolved_source_gap": str(gap),
        "exact_current_invisible_geometry": True,
        "conversion_and_writer_errors_accounted": True,
    }


def audit_counterfeit(record):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState

    state = ExactAdaptiveCarrierState.from_canonical_bytes(
        canonical_json_bytes(record["state"])
    )
    ref = Reference(state.graph.to_payload())
    C, W, Z = (
        arb_mat(vector(state.C)),
        arb_mat(vector(state.W_A)),
        arb_mat(matrix(state.Z_4)),
    )
    bad = frozen_reference_root(ref, C, W, Z)
    need(
        record["wrong_residual"] == str(bad["wrong_residual"])
        and record["actual_residual"] == str(bad["actual_residual"]),
        "counterfeit independent residuals",
    )
    need(
        contains(record["payload"]["proposal"], bad["flat"]),
        "counterfeit actual proposal",
    )
    try:
        audit_read(ref, state, record["payload"], compact=True)
    except AssertionError as error:
        need(
            str(error) == "actual full-input root residual",
            "counterfeit intended detector",
        )
    else:
        raise AssertionError("counterfeit incorrectly admitted")
    return {
        "converged_wrong_equation": True,
        "actual_input_residual_rejected": True,
        "difference_exceeds_native_budget": True,
    }
