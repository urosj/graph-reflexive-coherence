"""Native A_PC staging, compact evidence and independent full C/logW audits."""

from contextlib import contextmanager
from hashlib import sha256
from unittest.mock import patch

from apc_native_spark_audit import audit_step
from apc_native_spark_pressure_oracle import classify as independent_classify
from apc_native_spark_pressure_oracle import verify_step
from cos_native_spark_oracle import matrix
from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from p991a5_native_spark_verify import need
from p991a6_apc_preflight import compact_transition, transition
from p991a6_apc_preflight import decoded as decode_step

from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_exact import current_exact_backend
from pygrc.models.grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState
from pygrc.models.grc_v4_spark_apc import SparkAPCKernel
from pygrc.models.grc_v4_spark_state import ExactResources


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
        original_step = SparkAPCKernel.step
        original_read = SparkAPCKernel._admitted_read
        original_writer = SparkAPCKernel._conductance_writer
        original_carrier_writer = SparkAPCKernel._carrier_writer
        original_write = ExactAdaptiveCarrierState.advance_histories

        def read(k, state):
            subject = sha256(state.to_canonical_bytes()).hexdigest()
            value = original_read(k, state)
            if self.active:
                self.backends.add(current_exact_backend().value)
                self.reads.append(subject)
                self.sequence.append(
                    "incoming_read" if len(self.reads) == 1 else "returned_read"
                )
            return value

        def writer(k, state, resources, consumed):
            if self.active:
                self.sequence.append("conductance_writer")
                self.writers.append(
                    {
                        "kind": "conductance",
                        "subject_digest": sha256(
                            state.to_canonical_bytes()
                        ).hexdigest(),
                        "same_read_object": consumed is self.incoming_read,
                        "final_resource_digest": sha256(
                            resources.to_canonical_bytes()
                        ).hexdigest(),
                        "physical_writes_before": self.writes,
                    }
                )
            return original_writer(k, state, resources, consumed)

        def carrier_writer(k, state, consumed):
            if self.active:
                self.sequence.append("carrier_writer")
                self.writers.append(
                    {
                        "kind": "carrier",
                        "subject_digest": sha256(
                            state.to_canonical_bytes()
                        ).hexdigest(),
                        "same_read_object": consumed is self.incoming_read,
                        "physical_writes_before": self.writes,
                    }
                )
            return original_carrier_writer(k, state, consumed)

        def tracked_read(k, state):
            value = read(k, state)
            if self.active and len(self.reads) == 1:
                self.incoming_read = value
            return value

        def write(state, *args, **kwargs):
            if self.active:
                self.writes += 1
                self.sequence.append("write")
            return original_write(state, *args, **kwargs)

        def step(k, state, *args, **kwargs):
            self.step = None
            self.reads, self.writers, self.writes = [], [], 0
            self.sequence = []
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
            patch.object(SparkAPCKernel, "step", step),
            patch.object(SparkAPCKernel, "_admitted_read", tracked_read),
            patch.object(SparkAPCKernel, "_conductance_writer", writer),
            patch.object(SparkAPCKernel, "_carrier_writer", carrier_writer),
            patch.object(ExactAdaptiveCarrierState, "advance_histories", write),
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
            sequence=self.sequence,
        )


def decoded(data):
    return decode_step(
        {
            k: v
            for k, v in data.items()
            if k
            not in {
                "read_inputs",
                "writer_inputs",
                "writer_calls",
                "physical_writes",
                "sequence",
            }
        }
    )


def validate_staging(data):
    step = decoded(data)
    subjects = [
        sha256(s.to_canonical_bytes()).hexdigest() for s in (step.before, step.after)
    ]
    need(
        data["physical_writes"] == 1
        and data["writer_calls"] == 2
        and data["sequence"]
        == [
            "incoming_read",
            "conductance_writer",
            "carrier_writer",
            "write",
            "returned_read",
        ]
        and data["read_inputs"] == subjects,
        "complete read/write staging",
    )
    need(
        data["writer_inputs"]
        == [
            {
                "kind": "conductance",
                "subject_digest": subjects[0],
                "same_read_object": True,
                "final_resource_digest": sha256(
                    ExactResources(
                        step.after.graph, step.after.C, step.after.charge
                    ).to_canonical_bytes()
                ).hexdigest(),
                "physical_writes_before": 0,
            },
            {
                "kind": "carrier",
                "subject_digest": subjects[0],
                "same_read_object": True,
                "physical_writes_before": 0,
            },
        ],
        "same incoming read and prepublication writer",
    )
    return step


def verify(config, data, certificate=None, role="current", *, compact=False):
    step = validate_staging(data)
    if compact:
        need(
            step.profile_id == config.reference.profile.complete_profile_id,
            "compact complete profile",
        )
        for read in (step.consumed_read, step.restart_read):
            need(
                read["precision_bits"] == 256
                and read["numerical_policy_id"] == step.numerical_policy_id,
                "compact numerical policy",
            )
        report = verify_step(step, certificate, role, compact=True)
        report["actual_profile_verified"] = True
    else:
        report = audit_step(config, step.before, step, certificate, role)
    report.pop("exact_weighted_classification", None)
    report["weighted_classification_digest"] = classification_digest(
        step.after, config.policy
    )
    if certificate is not None:
        report["full_step_error_upper"] = report["full_chart_error_upper"]
    return report


def compact(data, previous_restart=None):
    """Keep represented states and numerical witnesses; declarations live once."""
    value = compact_transition(validate_staging(data))
    value.pop("before")
    value["after"] = {k: value["after"][k] for k in ("C", "W_A", "Z_4")}
    for key in (
        "read_inputs",
        "writer_inputs",
        "writer_calls",
        "physical_writes",
        "sequence",
    ):
        value[key] = data[key]
    # Only reuse the complete, byte-identical witnessed read. Equality of
    # subjects alone would not justify discarding a different read witness.
    if previous_restart is not None and value["consumed_read"] == previous_restart:
        value["consumed_read"] = {"previous_restart": True}
    return value


def expand(data, before, previous_restart=None):
    from copy import deepcopy

    value = deepcopy(data)
    value["before"] = before
    value["after"] = dict(before, **value["after"])
    if value["consumed_read"] == {"previous_restart": True}:
        need(previous_restart is not None, "missing preceding read witness")
        value["consumed_read"] = deepcopy(previous_restart)
    return value


def membership_bounds(state, operands):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        delta = arb_mat(
            [[Q(x) - Q(c)] for x, c in zip(state.C, operands["center"], strict=True)]
            + [
                [arb(Q(w)).log() - Q(c)]
                for w, c in zip(state.W_A, operands["logW_center"], strict=True)
            ]
        )
        coordinates = arb_mat(matrix(operands["U"])) * delta
        lower = max(abs(x).lower().fmpq() for x in coordinates.entries())
        upper = max(abs(x).upper().fmpq() for x in coordinates.entries())
        zsq = (
            sum(Q(x) ** 2 for row in state.Z_4 for x in row)
            / Q(operands["carrier_radius"]) ** 2
        )
        return max(lower * lower, zsq), max(upper * upper, zsq)


def classify_and_membership(state, policy, certificate):
    expected = independent_classify(
        state.graph.to_payload(), state.C, state.W_A, policy.to_payload()
    )
    actual = classify(state, policy)
    need(
        (actual.basins, actual.terminals, [r.to_dict() for r in actual.rows])
        == expected,
        "independent exhaustive weighted classifier",
    )
    inside, native_upper = certificate.membership(state)
    lower, upper = membership_bounds(state, certificate.operands)
    need(
        upper <= Q(native_upper)
        and ((inside and upper <= 1) or (not inside and lower > 1)),
        "complete independent C/logW/Z membership",
    )
    return {
        "norm": native_upper,
        "measure": "squared_max_C_logW_carrier_product_upper",
        "independent_lower": str(lower),
        "independent_upper": str(upper),
        "inside": inside,
        "classification_digest": classification_digest(state, policy),
    }


def conductance_bits(state):
    return max(
        max(abs(Q(x).numerator).bit_length(), Q(x).denominator.bit_length())
        for x in state.W_A
    )


def classification_digest(state, policy):
    expected = independent_classify(
        state.graph.to_payload(), state.C, state.W_A, policy.to_payload()
    )
    return sha256(canonical_json_bytes(expected)).hexdigest()


def carrier_bits(state):
    return max(
        max(abs(Q(x).numerator).bit_length(), Q(x).denominator.bit_length())
        for row in state.Z_4
        for x in row
    )
