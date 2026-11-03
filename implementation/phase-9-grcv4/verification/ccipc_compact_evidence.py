"""Independent mathematical checking of compact native CI+PC evidence.

Exact states, root witnesses and rounding operands suffice; expanded read/writer
matrices are derived, not stored per beat. No native step/read supplies truth.
"""

from hashlib import sha256

from cci_native_spark_pressure_oracle import read, upper
from ccipc_native_spark_audit import Equations, norm2
from ccipc_native_spark_oracle import CCIPCReference
from ccipc_native_spark_pressure_oracle import domain
from cos_native_spark_oracle import Equations as RootEquations
from cpc_native_spark_pressure_oracle import matrix, round_even, vector
from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from p991a5_native_spark_verify import need
from p991a6_ccipc_campaign_verify import classify_and_membership

from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_carrier import ExactCarrierState, exact_state

ROOT_FIELDS = (
    "root_error",
    "proposal_residual",
    "iterations",
    "residual_upper",
    "conditioning_upper",
    "current_midpoint",
    "subject_digest",
)


def root_witness(payload):
    need(
        all(lo == hi for row in payload["proposal"] for lo, hi in row),
        "proposal must be exact",
    )
    return dict(
        proposal=[row[0][0] for row in payload["proposal"]],
        **{k: payload[k] for k in ROOT_FIELDS},
    )


class Evidence:
    def __init__(self, inputs):
        self.inputs = inputs
        self.config = GRC9V4SparkConfiguration.from_payload(
            inputs["target_configuration"]
        )
        self.graph = self.config.reference.graph
        self.certs = dict(
            zip(
                ("current", "reset"),
                map(CompletionCertificate.from_payload, inputs["certificates"]),
                strict=True,
            )
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            graph = self.graph.to_payload()
            self.eq = Equations(graph)
            self.e = RootEquations(graph, outward=True)
            self.ref = CCIPCReference(graph)
            self.d = domain(graph)
            self.decay = (-arb(1)).exp()
        self.pairs = self.eq.pairs
        self.m = self.eq.I.nrows()
        self.charge = self.config.current.charge
        self.domain = dict(
            self.d,
            domain_id="cipc_quartic_flat_inf_ball_1_over_32_carrier_1_over_128_v1",
            carrier_radius="1/128",
            carrier_norm="symmetric_star_frobenius_v1",
            resource_box=["0", "4"],
            H_eigenvalue_lower="255/256",
            H_eigenvalue_upper=str(1 + Q(1, 256) + Q(self.m, 4096)),
            invariant_carrier_ball=True,
            resource_box_invariance_claimed=False,
            uniqueness="one root in the declared flat ball",
            stationary_composite_gain=2,
        )

    def initial(self, role):
        return exact_state(self.inputs["initial_roles"][role])

    def state(self, row):
        need(
            len(row["C"]) == len(self.graph.live_node_ids)
            and len(row["Z"]) == len(self.pairs),
            "complete compact C/Z coordinates",
        )
        Z = [["0"] * self.m for _ in range(self.m)]
        for (i, j), value in zip(self.pairs, row["Z"], strict=True):
            Z[i][j] = Z[j][i] = value
        return ExactCarrierState(
            self.graph, tuple(row["C"]), self.charge, tuple(map(tuple, Z))
        )

    def project(self, original):
        stage = original["stage"]
        for name in ("consumed_read", "restart_read"):
            need(
                stage[name]["root_domain"] == self.domain, "complete shared root domain"
            )
            need(
                stage[name]["precision_bits"] == 256
                and stage[name]["numerical_policy_id"]
                == self.config.policy.numerical_policy_id,
                "fixed numerical declaration",
            )
        Z = stage["after"]["Z_4"]
        row = {
            k: original[k]
            for k in (
                "beat",
                "step_index",
                "time",
                "ordinary_seconds",
                "local_gain",
                "native_window_observations",
                "receipts",
            )
        }
        row.update(
            C=stage["after"]["C"],
            Z=[Z[i][j] for i, j in self.pairs],
            flux=stage["flux"],
            roots=[root_witness(stage[k]) for k in ("consumed_read", "restart_read")],
            writer_midpoint=[stage["writer"]["midpoint"][i][j] for i, j in self.pairs],
            staging={
                k: stage[k]
                for k in (
                    "read_inputs",
                    "writer_inputs",
                    "writer_calls",
                    "physical_writes",
                )
            },
            membership={
                "norm": original["membership"]["norm"],
                "inside": original["membership"]["inside"],
                "classifier_digest": sha256(
                    canonical_json_bytes(original["membership"]["classification"])
                ).hexdigest(),
            },
            original_record_digest=original["record_digest"],
            original_previous_record_digest=original["previous_record_digest"],
        )
        need(
            self.state(row).to_payload() == stage["after"],
            "lossless exact state projection",
        )
        return row

    def root(self, state, witness):
        need(set(witness) == {"proposal", *ROOT_FIELDS}, "closed root witness")
        need(
            witness["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
            "complete root subject",
        )
        C, Z = arb_mat(vector(state.C)), arb_mat(matrix(state.Z_4))
        need(
            all(0 <= Q(x) <= 4 for x in state.C)
            and norm2(matrix(state.Z_4)) <= Q(1, 128) ** 2,
            "composite state domain",
        )
        need(
            len(witness["proposal"]) == self.m
            and len(witness["current_midpoint"]) == self.m,
            "complete root witness coordinates",
        )
        proposal = arb_mat(vector(witness["proposal"]))
        error_lo, error = map(Q, witness["root_error"])
        residual_lo, residual = map(Q, witness["proposal_residual"])
        need(
            0 <= error_lo <= error and 0 <= residual_lo <= residual,
            "ordered root witness intervals",
        )
        _, _, _, F = read(self.e, C, self.e.geometry(proposal) + Z / 2)
        actual_residual = upper(F - proposal)
        need(actual_residual <= residual, "independent proposal residual")
        need(
            error >= residual / (1 - Q(self.d["contraction"]))
            and upper(proposal) + error < Q(1, 32),
            "Banach error and selected flat ball",
        )
        need(
            type(witness["iterations"]) is int and 1 <= witness["iterations"] <= 60,
            "proposal work metadata",
        )
        fresh = self.ref.root(C, Z)
        need(
            upper(fresh["flat"] - proposal) <= error,
            "independent root inside witness ball",
        )
        J = fresh["selected"]["current"]
        need(
            upper(arb_mat(vector(witness["current_midpoint"])) - J) <= Q(1, 2**192),
            "certified current midpoint",
        )
        A = 3 * self.e.I / 4 + fresh["geometry"] * self.e.L
        need(
            self.m * upper(A) * upper(A.inv())
            <= Q(witness["conditioning_upper"])
            < 10**12,
            "independent conditioning",
        )
        joint = arb(sum((x / 8) ** 2 for x in self.eq.O.entries())).sqrt() * (
            2 * arb(upper(proposal)) * arb(actual_residual) + arb(actual_residual) ** 2
        )
        need(
            joint.upper().fmpq() <= Q(witness["residual_upper"]) < Q(1, 10**11),
            "joint residual provenance",
        )
        return fresh

    def verify(self, before, row, role, numerical=True):
        after = self.state(row)
        subjects = [sha256(s.to_canonical_bytes()).hexdigest() for s in (before, after)]
        need(
            row["staging"]
            == {
                "read_inputs": subjects,
                "physical_writes": 1,
                "writer_calls": 1,
                "writer_inputs": [
                    {
                        "subject_digest": subjects[0],
                        "same_read_object": True,
                        "physical_writes_before": 0,
                    }
                ],
            },
            "full-state staging witness",
        )
        need(
            len(row["roots"]) == 2
            and len(row["flux"]) == self.m
            and len(row["writer_midpoint"]) == len(self.pairs),
            "complete transition witnesses",
        )
        C, C1 = vector(before.C), vector(after.C)
        need(C1 == C - 32 * self.eq.B * vector(row["flux"]), "exact incidence write")
        need(
            sum(C.entries()) == sum(C1.entries()) == Q(self.charge),
            "exact resource charge",
        )
        need(
            all(
                Q(q) == round_even(mid, 128)
                for q, mid in zip(
                    row["flux"], row["roots"][0]["current_midpoint"], strict=True
                )
            ),
            "nearest-even flux128",
        )
        need(
            all(
                Q(q) == round_even(mid, 192)
                for q, mid in zip(row["Z"], row["writer_midpoint"], strict=True)
            ),
            "nearest-even carrier192",
        )
        observed = classify_and_membership(after, self.config.policy, self.certs[role])
        need(
            row["membership"]
            == {
                "norm": observed["norm"],
                "inside": observed["inside"],
                "classifier_digest": sha256(
                    canonical_json_bytes(observed["classification"])
                ).hexdigest(),
            },
            "exact joint membership and complete classifier",
        )
        if not numerical:
            return after, None
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            incoming = self.root(before, row["roots"][0])
            self.root(after, row["roots"][1])
            ideal = (
                self.decay * arb_mat(matrix(before.Z_4))
                + (1 - self.decay) * incoming["source"]
            )
            need(
                all(
                    abs(arb(Q(mid)) - ideal[i, j]).upper().fmpq() <= Q(1, 2**224)
                    for (i, j), mid in zip(
                        self.pairs, row["writer_midpoint"], strict=True
                    )
                ),
                "same-root exponential writer midpoint",
            )
            ec = C1 - (C - 32 * self.eq.B * incoming["selected"]["current"])
            ez = arb_mat(matrix(after.Z_4)) - ideal
            U = matrix(self.certs[role].operands["U"])
            radius = Q(self.certs[role].operands["carrier_radius"])
            Cerror = upper(U * ec)
            Zerror = (
                (sum(abs(x).upper() ** 2 for x in ez.entries()).sqrt() / arb(radius))
                .upper()
                .fmpq()
            )
            uniform = max(
                32
                * max(
                    sum(abs((U * self.eq.B)[i, j]) for j in range(self.m))
                    for i in range(U.nrows())
                )
                * (Q(1, 2**129) + Q(1, 2**192)),
                self.m * (Q(1, 2**193) + Q(1, 2**224)) / radius,
            )
            need(
                max(Cerror, Zerror)
                <= uniform
                == Q(self.certs[role].proof["full_step_error"])
                < Q(self.certs[role].proof["image_margin"]),
                "independent full C/Z error budget",
            )
            return after, {
                "resource_chart_error": str(Cerror),
                "scaled_carrier_error": str(Zerror),
                "full_step_error_upper": str(max(Cerror, Zerror)),
            }
