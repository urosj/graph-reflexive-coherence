"""Independent research PC equations at Arb768 on exact captured C/Z subjects."""

import sys
from hashlib import sha256
from pathlib import Path

from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "implementation/investigations/grc9v4-constitutive-design/research"
sys.path[:0] = [
    str(RESEARCH),
    str(RESEARCH.parent / "evidence/spark-completion/review/constructive-candidate"),
]
from spark_completion_pc import CPCReference


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def encloses(rows, A):
    return (
        len(rows) == A.nrows()
        and all(len(r) == A.ncols() for r in rows)
        and all(
            Q(rows[i][j][0]) <= A[i, j].lower().fmpq()
            and A[i, j].upper().fmpq() <= Q(rows[i][j][1])
            for i in range(A.nrows())
            for j in range(A.ncols())
        )
    )


def quantized(q, bits):
    q = Q(q)
    n = q.numerator * 2**bits
    den = q.denominator
    sign = -1 if n < 0 else 1
    a, r = divmod(abs(n), den)
    a += int(2 * r > den or (2 * r == den and a % 2))
    return Q(sign * a, 2**bits)


def exact_matrix(rows):
    return M([[Q(x) for x in row] for row in rows])


def frobenius(A):
    return sum(abs(x).upper() ** 2 for x in A.entries()).sqrt().upper()


def verify_step(step, certificate=None, role="current"):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        graph = step.before.graph.to_payload()
        m = CPCReference(graph)
        C = arb_mat([[Q(x)] for x in step.before.C])
        Z = arb_mat(exact_matrix(step.before.Z_4))
        expected = m.pc_step(C, Z)
        read = expected["read"]
        post = arb_mat([[Q(x)] for x in step.after.C])
        zpost = arb_mat(exact_matrix(step.after.Z_4))
        fresh = m.pc_read(post, zpost)
        for native, independent, state in [
            (step.consumed_read, read, step.before),
            (step.restart_read, fresh, step.after),
        ]:
            need(
                native["subject_digest"]
                == sha256(state.to_canonical_bytes()).hexdigest(),
                "read subject binding",
            )
            for key, reference in [
                ("H", independent["geometry"]),
                ("J", independent["selected"]["current"]),
                ("flat", independent["selected"]["causal_flat"]),
                ("S", independent["source"]),
            ]:
                need(
                    encloses(native[key], reference),
                    "complete read containment: " + key,
                )

            # Recompute both defining residuals at high precision from decoded intervals.
            def decode(rows):
                return arb_mat(
                    [
                        [
                            arb((Q(p[0]) + Q(p[1])) / 2, (Q(p[1]) - Q(p[0])) / 2)
                            for p in row
                        ]
                        for row in rows
                    ]
                )

            H, flat, J = (decode(native[key]) for key in ("H", "flat", "J"))
            e = independent
            j0 = e["selected"]["baseline"]
            y = 2 * H * flat
            defects = [(3 * m.I / 4 + H * m.Le) * y - j0, J - j0 - y / 4]
            need(
                all(frobenius(x) < arb(Q(1, 10**11)) for x in defects),
                "fresh full read residual",
            )
        need(
            encloses(step.writer["ideal"], expected["carrier_after"]),
            "full same-read writer enclosure",
        )
        need(
            encloses(step.writer["source"], read["source"]),
            "writer used different flat/source",
        )
        need(
            step.writer["consumed_state_digest"]
            == step.consumed_read["subject_digest"],
            "writer freshness",
        )
        need(
            Q(step.writer["decay"][0]) <= m.decay.lower().fmpq()
            and m.decay.upper().fmpq() <= Q(step.writer["decay"][1]),
            "decay enclosure",
        )
        for mid, q in zip(
            step.consumed_read["current_midpoint"], step.flux, strict=True
        ):
            need(quantized(mid, 128) == Q(q), "nearest-even flux")
        for i, j in m.pairs:
            mid = Q(step.writer["midpoint"][i][j])
            lo, hi = map(Q, step.writer["ideal"][i][j])
            need(
                lo <= mid <= hi and max(mid - lo, hi - mid) <= Q(1, 2**224),
                "whole writer midpoint enclosure",
            )
            need(
                quantized(mid, 192) == Q(step.after.Z_4[i][j]),
                "nearest-even symmetric carrier",
            )
        actual = exact_matrix([[x] for x in step.after.C])
        before = exact_matrix([[x] for x in step.before.C])
        B = exact_matrix(
            [
                [
                    str(int(e.tail_node_id == v) - int(e.head_node_id == v))
                    for e in step.before.graph.oriented_edges
                ]
                for v in step.before.graph.live_node_ids
            ]
        )
        need(
            actual == before - 32 * B * exact_matrix([[x] for x in step.flux]),
            "single exact incidence write",
        )
        need(sum(map(Q, step.after.C)) == Q(step.after.charge) == 21, "exact charge")
        cerror = post - expected["after"]
        zerror = zpost - expected["carrier_after"]
        for x, bound in zip(
            cerror.entries(), step.componentwise_error_bounds, strict=True
        ):
            need(abs(x).upper().fmpq() <= Q(bound), "resource output error")
        need(
            all(
                abs(x).upper().fmpq() <= Q(step.carrier_component_error)
                for x in zerror.entries()
            ),
            "carrier output error",
        )
        final = m.read(post, read["geometry"], eta=m.q(1, 1024))
        need(
            encloses([[x] for x in step.final_current], final["current"]),
            "consumed-H final diagnostic",
        )
        reference = m.read(post, m.I, eta=m.q(1, 1024))
        # Compare exact endpoints: arb.contains(fmpq) first rounds the target
        # to a ball, which can protrude despite containing the exact rational.
        need(
            all(
                x.lower().fmpq() <= Q(q) <= x.upper().fmpq()
                for x, q in zip(
                    reference["current"].entries(), step.reference_current, strict=True
                )
            ),
            "exact reference diagnostic",
        )
        report = {
            "independent_precision_bits": 768,
            "whole_read_and_writer_containment": True,
            "full_step_bound": True,
            "exact_charge": True,
            "fresh_poststate_read": True,
            "same_read_writer": True,
            "carrier_dimension": len(m.pairs),
            "maximum_carrier_error": str(
                max(abs(x).upper().fmpq() for x in zerror.entries())
            ),
        }
        if certificate is not None:
            b = certificate.operands["binding"]
            need(
                b["role"] == role
                and b["graph"].to_dict() == graph
                and b["charge"] == step.before.charge
                and b["state_channels"] == ("C", "Z_4")
                and b["profile"]["complete_profile_id"] == step.profile_id
                and b["duration"] == step.duration
                and b["policy"]["numerical_policy_id"] == step.numerical_policy_id,
                "certificate full-state binding",
            )
            U = arb_mat(exact_matrix(certificate.operands["U"]))
            resource = max(abs(x).upper().fmpq() for x in (U * cerror).entries())
            carrier = (
                (frobenius(zerror) / Q(certificate.operands["carrier_radius"]))
                .upper()
                .fmpq()
            )
            bound = max(resource, carrier)
            need(
                bound
                <= Q(certificate.proof["full_step_error"])
                < Q(certificate.proof["image_margin"]),
                "independent complete product-norm error",
            )
            report.update(
                full_step_error_upper=str(bound),
                resource_error_upper=str(resource),
                scaled_carrier_error_upper=str(carrier),
            )
        return report


def from_transition(value):
    """Decode retained audit operands; never advance a public model from them."""
    from pygrc.models.grc_v4_spark_carrier import exact_state
    from pygrc.models.grc_v4_spark_cpc import SparkCPCStep
    from pygrc.models.grc_v4_state import FrozenJSONMap

    data = dict(value)
    policy = data.pop("numerical_policy_id")
    for key in ("before", "after"):
        data[key] = exact_state(data[key])
    for key in ("consumed_read", "writer", "restart_read"):
        data[key] = FrozenJSONMap(data[key])
    for key in (
        "flux",
        "componentwise_error_bounds",
        "final_current",
        "reference_current",
    ):
        data[key] = tuple(data[key])
    step = SparkCPCStep(**data)
    need(step.numerical_policy_id == policy, "retained numerical policy")
    return step
