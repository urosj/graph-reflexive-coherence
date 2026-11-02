"""Lossless native CI+PC staging captures and independent whole-history audits."""

from contextlib import contextmanager
from hashlib import sha256
from unittest.mock import patch

from ccipc_native_spark_audit import Equations, audit_step, matrix, vector
from ccipc_native_spark_oracle import from_transition
from cos_native_spark_oracle import classify as independent_classify
from flint import ctx
from flint import fmpq as Q
from p991a5_native_spark_verify import need
from p991a6_ccipc_preflight import transition

from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_exact import current_exact_backend
from pygrc.models.grc_v4_spark_carrier import ExactCarrierState
from pygrc.models.grc_v4_spark_ccipc import SparkCCIPCKernel


class Capture:
    def __init__(self):
        self.step = None
        self.active = False
        self.reads = []
        self.writers = []
        self.writes = 0
        self.backends = set()

    @contextmanager
    def installed(self):
        original_step = SparkCCIPCKernel.step
        original_read = SparkCCIPCKernel._admitted_read
        original_writer = SparkCCIPCKernel._writer
        original_write = ExactCarrierState.advance_carrier

        def read(k, state):
            subject = sha256(state.to_canonical_bytes()).hexdigest()
            value = original_read(k, state)
            if self.active:
                self.backends.add(current_exact_backend().value)
                self.reads.append(subject)
            return value

        def writer(k, state, consumed):
            if self.active:
                self.writers.append(
                    {
                        "subject_digest": sha256(
                            state.to_canonical_bytes()
                        ).hexdigest(),
                        "same_read_object": consumed is self.incoming_read,
                        "physical_writes_before": self.writes,
                    }
                )
            return original_writer(k, state, consumed)

        def tracked_read(k, state):
            value = read(k, state)
            if self.active and len(self.reads) == 1:
                self.incoming_read = value
            return value

        def write(state, *args, **kwargs):
            if self.active:
                self.writes += 1
            return original_write(state, *args, **kwargs)

        def step(k, state, *args, **kwargs):
            self.step = None
            self.reads, self.writers, self.writes = [], [], 0
            self.input = state
            self.active = True
            try:
                value = original_step(k, state, *args, **kwargs)
                self.step = value
                need(value.before == self.input, "immutable actual input")
                validate_staging(self.payload())
                return value
            finally:
                self.active = False

        with (
            patch.object(SparkCCIPCKernel, "step", step),
            patch.object(SparkCCIPCKernel, "_admitted_read", tracked_read),
            patch.object(SparkCCIPCKernel, "_writer", writer),
            patch.object(ExactCarrierState, "advance_carrier", write),
        ):
            yield self

    def payload(self):
        need(self.step is not None, "no successful native step capture")
        return dict(
            transition(self.step),
            read_inputs=self.reads,
            writer_inputs=self.writers,
            writer_calls=len(self.writers),
            physical_writes=self.writes,
        )


def decoded(data):
    return from_transition(
        {
            k: v
            for k, v in data.items()
            if k
            not in {"read_inputs", "writer_inputs", "writer_calls", "physical_writes"}
        }
    )


def validate_staging(data):
    step = decoded(data)
    subjects = [
        sha256(s.to_canonical_bytes()).hexdigest() for s in (step.before, step.after)
    ]
    need(
        data["physical_writes"] == 1
        and data["writer_calls"] == 1
        and data["read_inputs"] == subjects,
        "complete read/write staging",
    )
    need(
        data["writer_inputs"]
        == [
            {
                "subject_digest": subjects[0],
                "same_read_object": True,
                "physical_writes_before": 0,
            }
        ],
        "same incoming read and prepublication writer",
    )
    return step


def verify(config, data, certificate=None, role="current"):
    step = validate_staging(data)
    report = audit_step(config, step.before, step, certificate, role)
    if certificate is not None:
        # Both quantities are independent outward bounds; compare only to the
        # common uniform budget, never impose an ordering between upper bounds.
        report["full_step_error_upper"] = str(
            max(Q(report["resource_chart_error"]), Q(report["scaled_carrier_error"]))
        )
    else:
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            exact = Equations(step.before.graph.to_payload()).read(
                vector(step.before.C), matrix(step.before.Z_4)
            )["J"]
            report["edge_current_error_upper"] = [
                str(abs(Q(a) - b).upper().fmpq())
                for a, b in zip(step.flux, exact.entries(), strict=True)
            ]
    return report


def product_norm2(state, operands):
    delta = vector(state["C"]) - vector(operands["center"])
    resource = max(map(abs, (matrix(operands["U"]) * delta).entries())) ** 2
    carrier = (
        sum(Q(x) ** 2 for row in state["Z_4"] for x in row)
        / Q(operands["carrier_radius"]) ** 2
    )
    return max(resource, carrier)


def classify_and_membership(state, policy, certificate):
    expected = independent_classify(
        state.graph.to_payload(), state.C, policy.to_payload()
    )
    actual = classify(state, policy)
    need(
        (actual.basins, actual.terminals, [r.to_dict() for r in actual.rows])
        == expected,
        "independent exhaustive geometric classifier",
    )
    norm = product_norm2(state.to_payload(), certificate.operands)
    need(
        certificate.membership(state) == (norm <= 1, str(norm)), "whole C/Z membership"
    )
    return {
        "norm": str(norm),
        "measure": "squared_max_product_norm",
        "inside": norm <= 1,
        "classification": actual.to_payload(),
    }


def carrier_bits(state):
    return max(
        max(abs(Q(x).numerator).bit_length(), Q(x).denominator.bit_length())
        for row in state.Z_4
        for x in row
    )
