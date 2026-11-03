"""Lossless native CI captures and independent whole-root campaign checks."""

from contextlib import contextmanager
from unittest.mock import patch

from cci_native_spark_pressure_oracle import audit_step, read
from cos_native_spark_oracle import Equations, vector
from flint import arb_mat, ctx
from flint import fmpq as Q
from p991a5_native_spark_verify import need, rounded_flux
from p991a6_cci_preflight import transition

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_exact import current_exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_cci import SparkCCIKernel, SparkCCIStep
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap


class Capture:
    def __init__(self):
        self.step = None
        self.active = False
        self.roots = []
        self.writes = 0
        self.backends = set()

    @contextmanager
    def installed(self):
        original_step = SparkCCIKernel.step
        original_root = SparkCCIKernel._admitted_root
        original_write = ExactResources.advance

        def root(k, state):
            value = original_root(k, state)
            if self.active:
                self.backends.add(current_exact_backend().value)
                self.roots.append(
                    {
                        "C": list(state.C),
                        "current_midpoint": [
                            str(x.mid().fmpq()) for x in value["J"].entries()
                        ],
                    }
                )
            return value

        def write(state, *args, **kwargs):
            if self.active:
                self.writes += 1
            return original_write(state, *args, **kwargs)

        def step(k, *args, **kwargs):
            self.step = None
            self.roots = []
            self.writes = 0
            self.active = True
            try:
                value = original_step(k, *args, **kwargs)
                self.step = value
                need(
                    self.writes == 1 and len(self.roots) == 2,
                    "one write and two joint-root admissions required",
                )
                need(
                    self.roots[0]["C"] == list(value.before.C)
                    and self.roots[1]["C"] == list(value.after.C),
                    "stale root input",
                )
                return value
            finally:
                self.active = False

        with (
            patch.object(SparkCCIKernel, "step", step),
            patch.object(SparkCCIKernel, "_admitted_root", root),
            patch.object(ExactResources, "advance", write),
        ):
            yield self

    def payload(self):
        need(self.step is not None, "no successful native step capture")
        return dict(
            transition(self.step), root_inputs=self.roots, physical_writes=self.writes
        )


def decoded(data):
    def state(x):
        return ExactResources(
            GRCV4Graph.from_payload(x["graph"]), tuple(x["C"]), x["charge"]
        )

    return SparkCCIStep(
        state(data["before"]),
        state(data["after"]),
        data["profile_id"],
        data["duration"],
        tuple(data["flux"]),
        tuple(data["componentwise_error_bounds"]),
        FrozenJSONMap(data["root"]),
        FrozenJSONMap(data["restart_root"]),
        tuple(tuple(x) for x in data["final_current"]),
        tuple(data["reference_current"]),
    )


def verify(config, data, certificate=None, role="current"):
    step = decoded(data)
    need(
        data["physical_writes"] == 1 and len(data["root_inputs"]) == 2,
        "invalid captured staging",
    )
    need(
        data["root_inputs"][0]["C"] == list(step.before.C)
        and data["root_inputs"][1]["C"] == list(step.after.C),
        "wrong root subjects",
    )
    for q, f in zip(data["root_inputs"][0]["current_midpoint"], step.flux, strict=True):
        need(rounded_flux(Q(q)) == Q(f), "nearest/even flux mismatch")
    for payload, read_capture in zip(
        (step.root, step.restart_root), data["root_inputs"], strict=True
    ):
        for row, q in zip(
            payload["current"], read_capture["current_midpoint"], strict=True
        ):
            lo, hi = map(Q, row[0])
            need(
                lo <= Q(q) <= hi and max(Q(q) - lo, hi - Q(q)) <= Q(1, 2**192),
                "consumed midpoint lacks certified current budget",
            )
    report = audit_step(config, step.before, step, certificate, role=role)
    # Validate the two diagnostic reads without using them as restart authority.
    # The whole fresh poststate root is already independently certified above.
    from cci_native_spark_pressure_oracle import encloses

    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        eq = Equations(step.before.graph.to_payload(), outward=True)
        post = arb_mat(vector(step.after.C))
        # Reconstruct exact-root H freshly, not from supplied saved H.
        from cci_native_spark_oracle import CCIReference

        exact = CCIReference(step.before.graph.to_payload()).root(
            arb_mat(vector(step.before.C))
        )
        _, _, J, _ = read(eq, post, exact["geometry"])
        need(
            encloses([[x] for x in step.final_current], J),
            "consumed-H final diagnostic mismatch",
        )
        _, _, J, _ = read(eq, post, eq.I)
        need(
            all(
                x.contains(Q(q))
                for x, q in zip(J.entries(), step.reference_current, strict=True)
            ),
            "reference diagnostic mismatch",
        )
    return report
