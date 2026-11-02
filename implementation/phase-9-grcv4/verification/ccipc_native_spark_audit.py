"""Composite pressure oracle: full tuple, shared-source writer and exact subjects.

Independent graph algebra and fresh Arb768 Newton roots; native proposals are
certified separately. No native read/source/derivative supplies expected values.
"""

import json
from hashlib import sha256

from ccipc_native_spark_oracle import CCIPCReference
from ccipc_native_spark_pressure_oracle import audit_root as original_audit_root
from ccipc_native_spark_pressure_oracle import domain
from cpc_native_spark_pressure_oracle import (
    Equations as FixedEquations,
)
from cpc_native_spark_pressure_oracle import (
    audit_writer,
    contains_ball,
    decode,
    frobenius,
    matrix,
    need,
    norm2,
    round_even,
    upper,
    vector,
)
from flint import arb, arb_mat, ctx
from flint import fmpq as Q

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

POLICY = "spark_ccipc_arb256_certified_root_flux128_carrier192_v1"


class Equations(FixedEquations):
    def source(self, flat):
        return arb_mat(
            [
                [
                    self.O[i, j] * flat[i, 0] * flat[j, 0] / 4
                    for j in range(self.I.ncols())
                ]
                for i in range(self.I.nrows())
            ]
        )

    def fixed_ball(self, C, H):
        B, I, L = map(arb_mat, (self.B, self.I, self.L))
        site = arb_mat([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
        j0 = -B.transpose() * (B * H * B.transpose() * C / 64 - site) / 1024
        y = (3 * I / 4 + H * L).solve(j0)
        flat = H.solve(y) / 2
        return {
            "H": H,
            "j0": j0,
            "y": y,
            "J": j0 + y / 4,
            "flat": flat,
            "S": self.source(flat),
        }

    def read(self, C, Z):
        root = CCIPCReference(self.graph).root(arb_mat(C), arb_mat(Z))
        return {
            "H": root["geometry"],
            "J": root["selected"]["current"],
            "flat": root["flat"],
            "S": root["source"],
        }

    def audit_read(self, state, payload):
        return audit_root(state, payload)[0]


def audit_root(state, payload):
    e = Equations(state.graph.to_payload())
    m = e.I.nrows()
    saved = payload["root_domain"]
    expected = dict(
        domain(state.graph.to_payload()),
        domain_id="cipc_quartic_flat_inf_ball_1_over_32_carrier_1_over_128_v1",
        carrier_radius="1/128",
        carrier_norm="symmetric_star_frobenius_v1",
        resource_box=["0", "4"],
        H_eigenvalue_lower="255/256",
        H_eigenvalue_upper=str(1 + Q(1, 256) + Q(m, 4096)),
        invariant_carrier_ball=True,
        resource_box_invariance_claimed=False,
        uniqueness="one root in the declared flat ball",
        stationary_composite_gain=2,
    )
    normalized = saved.to_dict() if hasattr(saved, "to_dict") else saved
    need(normalized == expected, "complete composite domain binding including radius")
    need(norm2(matrix(state.Z_4)) <= Q(1, 128) ** 2, "actual composite carrier domain")
    # This primitive proves the exact proposal with an independently reconstructed
    # residual, not merely interval overlap or the displayed iteration count.
    fresh, report = original_audit_root(state, payload)
    C, Z = arb_mat(vector(state.C)), arb_mat(matrix(state.Z_4))
    H, J, flat, S = (decode(payload[k]) for k in ("H", "J", "flat", "S"))
    need((S.nrows(), S.ncols()) == (m, m), "complete source coordinate coverage")
    need(
        contains_ball(payload["S"], fresh["source"]),
        "fresh selected-root containment: S",
    )
    baseline = e.fixed_ball(C, H)
    y = 4 * (J - baseline["j0"])
    defects = {
        "source": S - e.source(flat),
        "geometry_source": H - arb_mat(e.I) - (Z + S) / 2,
        "linear_current": (3 * arb_mat(e.I) / 4 + H * arb_mat(e.L)) * y
        - baseline["j0"],
        "flat": 2 * H * flat - y,
        "current": J - baseline["j0"] - baseline["y"] / 4,
    }
    for key, A in defects.items():
        need(
            all(x.is_finite() and x.contains(0) for x in A.entries()),
            "coherent composite tuple: " + key,
        )
        need(upper(A) < Q(1, 10**11), "composite tuple residual: " + key)
    need(
        all(S[i, j].is_zero() for i in range(m) for j in range(m) if not e.O[i, j]),
        "source star support",
    )
    need(all(x.contains(0) for x in (S - S.transpose()).entries()), "source symmetry")
    need(frobenius(S) < arb(Q(1, 128)), "composite source envelope")
    for row, mid in zip(payload["J"], payload["current_midpoint"], strict=True):
        lo, hi = map(Q, row[0])
        q = Q(mid)
        need(
            lo <= q <= hi and max(q - lo, hi - q) <= Q(1, 2**192),
            "whole current midpoint budget",
        )
    report["tuple_residuals"] = {k: str(upper(A)) for k, A in defects.items()}
    return {
        "H": fresh["geometry"],
        "J": fresh["selected"]["current"],
        "flat": fresh["flat"],
        "S": fresh["source"],
    }, report


def audit_step(config, captured, step, certificate=None, role="current"):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        need(
            step.before == captured
            and captured.graph == config.reference.graph
            and step.after.graph == captured.graph,
            "immutable input and graph binding",
        )
        need(
            config.reference.profile.FAMILY == "C_CI_PC"
            and step.profile_id == config.reference.profile.complete_profile_id,
            "explicit composite profile binding",
        )
        need(
            step.duration == "32"
            and step.numerical_policy_id == config.policy.numerical_policy_id == POLICY,
            "fixed duration and policy binding",
        )
        params = config.reference.profile.baseline.params_resolved
        need(
            params.realization.tau_PC == 32 and params.candidate.tau_C == 1,
            "separate PC and resolvent time constants",
        )
        eq = Equations(captured.graph.to_payload())
        exact, incoming = audit_root(captured, step.consumed_read)
        _, returned = audit_root(step.after, step.restart_read)
        errZ = audit_writer(captured, exact["S"], step.writer, step.after)
        need(
            contains_ball(
                [[x] for x in step.final_current],
                eq.fixed_ball(arb_mat(vector(step.after.C)), exact["H"])["J"],
            ),
            "consumed-H diagnostic label",
        )
        need(
            vector(step.reference_current) == eq.fixed(vector(step.after.C), eq.I)["J"],
            "exact reference diagnostic",
        )
        C, C1 = vector(captured.C), vector(step.after.C)
        need(
            all(
                Q(q) == round_even(mid, 128)
                for q, mid in zip(
                    step.flux, step.consumed_read["current_midpoint"], strict=True
                )
            ),
            "nearest-even conservative flux",
        )
        need(C1 == C - 32 * eq.B * vector(step.flux), "one conservative resource write")
        need(
            sum(C.entries())
            == sum(C1.entries())
            == Q(step.after.charge)
            == Q(captured.charge),
            "exact resource-only charge",
        )
        errC = C1 - (C - 32 * eq.B * exact["J"])
        need(
            all(
                abs(x).upper().fmpq() <= Q(b)
                for x, b in zip(
                    errC.entries(), step.componentwise_error_bounds, strict=True
                )
            ),
            "complete resource error",
        )
        need(
            Q(step.carrier_component_error) == Q(1, 2**193) + Q(1, 2**224),
            "carrier numerical budget",
        )
        a = (-arb(1)).exp()
        cross = (2 * a - 1) * arb_mat(matrix(captured.Z_4)) + 2 * (1 - a) * (
            decode(step.consumed_read["H"]) - arb_mat(eq.I)
        )
        cross_error = arb_mat(matrix(step.after.Z_4)) - cross
        need(
            all(
                abs(x).upper().fmpq() <= Q(1, 2**193) + Q(1, 2**224)
                for x in cross_error.entries()
            ),
            "consumed geometry/carrier cross-consistency",
        )
        result = {
            "full_composite_roots": True,
            "incoming_root": incoming,
            "returned_root": returned,
            "same_source_two_uses": True,
            "geometry_writer_cross_identity": True,
            "whole_writer": True,
            "full_returned_state": True,
            "carrier_coordinates": len(eq.pairs),
            "charge": captured.charge,
            "resource_error_max": str(
                max(abs(x).upper().fmpq() for x in errC.entries())
            ),
            "carrier_error_F_upper": str(frobenius(errZ).upper().fmpq()),
        }
        if certificate:
            b = certificate.operands["binding"]
            need(
                b["role"] == role
                and b["profile"].to_dict() == config.reference.profile.to_payload()
                and b["policy"].to_dict() == config.policy.to_payload()
                and b["graph"].to_dict() == captured.graph.to_payload()
                and b["charge"] == captured.charge
                and b["state_channels"] == ("C", "Z_4"),
                "full-state certificate binding",
            )
            U = matrix(certificate.operands["U"])
            r = Q(certificate.operands["carrier_radius"])
            ec = max(abs(x).upper().fmpq() for x in (U * errC).entries())
            ez = (frobenius(errZ) / r).upper().fmpq()
            uniform = max(
                32
                * max(
                    sum(abs((U * eq.B)[i, j]) for j in range(eq.B.ncols()))
                    for i in range(U.nrows())
                )
                * (Q(1, 2**129) + Q(1, 2**192)),
                eq.B.ncols() * (Q(1, 2**193) + Q(1, 2**224)) / r,
            )
            need(
                max(ec, ez)
                <= uniform
                == Q(certificate.proof["full_step_error"])
                < Q(certificate.proof["image_margin"]),
                "independent joint uniform error budget",
            )
            result.update(
                resource_chart_error=str(ec),
                scaled_carrier_error=str(ez),
                uniform_error=str(uniform),
            )
        return result


def audit_event(source_config, target_config, event):
    archive = event["carrier_history"]["source_archive"]
    need(
        event["carrier_history"]["native_release"] is False,
        "event loss differs from release",
    )
    need(
        event["carrier_history"]["policy_id"] == "event_loss_and_zero_target_carrier_v1"
        and event["carrier_history"]["information_loss"] == "carrier_history_loss",
        "explicit event loss policy",
    )
    nodes = target_config.reference.graph.live_node_ids
    module = tuple(event["module"])
    for role in ("current", "reset"):
        before = getattr(source_config, role)
        after = getattr(target_config, role)
        need(
            archive[role] == before.to_payload(), "whole actual source archive: " + role
        )
        need(
            all(Q(x) == 0 for row in after.Z_4 for x in row),
            "whole target carrier zero: " + role,
        )
        values = dict(zip(before.graph.live_node_ids, map(Q, before.C), strict=True))
        resource = values["v"]
        expected = [0, resource / 64, 31 * resource / 32, resource / 64]
        for n, x in zip(nodes, map(Q, after.C), strict=True):
            need(
                x == (expected[module.index(n)] if n in module else values[n]),
                "literal role-specific allocation: " + role,
            )
        need(sum(map(Q, after.C)) == sum(values.values()), "event charge")
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            Equations(before.graph.to_payload()).audit_read(
                before, event["carrier_history"]["fresh_source_reads"][role]
            )
    content = {
        "schema_version": "grcv4-exact-carrier-history-v1",
        "subject": "carrier",
        "content": archive,
    }
    history_digest = (
        "grcv4-history-content-sha256:"
        + sha256(
            json.dumps(
                content, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ).hexdigest()
    )
    need(
        event["carrier_history"]["history_policy"]["carrier"]["source_history_digest"]
        == history_digest,
        "retrievable whole-history digest",
    )
    return {
        "source_coordinates": len(
            Equations(source_config.reference.graph.to_payload()).pairs
        ),
        "target_coordinates": len(
            Equations(target_config.reference.graph.to_payload()).pairs
        ),
        "whole_archives": True,
        "whole_target_zero": True,
        "allocation": True,
    }
