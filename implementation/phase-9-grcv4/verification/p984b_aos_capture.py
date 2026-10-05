"""Native A_OS observation and read-only consumption checks for P9-8.4b.

Instrumentation returns production results unchanged. Retained checks rebuild
identities and prescribed arithmetic, never a production current/pass/step.
Interval rechecks are explicit and independent of these consumption checks.
"""

from contextlib import ExitStack
from dataclasses import replace
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import p984b_aos_oracle as oracle
from pygrc.models import grc_v4_candidate_a as candidate
from pygrc.models import grc_v4_realizations as realizations
from pygrc.models import grc_v4_step as steps
from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
from test_p980_os_effect_witness import inverse

base, aos = oracle.common, oracle.aos


def authority(state):
    return base.authority_payload(state)


def close(actual, expected, limit, name):
    a, e = np.asarray(actual), np.asarray(expected)
    base.require(
        a.shape == e.shape
        and a.size > 0
        and np.isfinite(a).all()
        and np.isfinite(e).all(),
        "invalid comparison: " + name,
    )
    error = max(
        abs(Q(float(x)) - Q(float(y))) for x, y in zip(a.flat, e.flat, strict=True)
    )
    base.require(error < limit, "numerical comparison failed: " + name)
    return str(error)


def point_capture(point):
    return {
        "identity": point.identity,
        "inputs_identity": point.inputs.identity,
        "current": list(point.current.values),
        "baseline": list(point.baseline.values),
        "read_current": list(point.read.current.values),
        "read_source": point.read.source_identity,
        "readback": list(point.read.flux.values),
        "flat": list(point.read.causal_flat.values),
    }


class Trace:
    """Observe actual geometry operands, descriptor rebuilds and writer calls."""

    def __init__(self):
        self.value = {
            "geometry": [],
            "writer_targets": [],
            "log_writes": [],
            "rebuilds": [],
        }
        self.active_point = None

    def __enter__(self):
        self.stack = ExitStack()
        source, h_profile = realizations._a_source_geometry, realizations.H_profile
        writer, log = (
            candidate.candidate_a_writer_target,
            candidate.candidate_a_log_interpolation,
        )
        rebuild = GRC9V4CandidateADifferentialReference.rebuild

        def source_call(point):
            previous, self.active_point = self.active_point, point
            try:
                return source(point)
            finally:
                self.active_point = previous

        def geometry_call(tensor, **kwargs):
            result = h_profile(tensor, **kwargs)
            base.require(self.active_point is not None, "unbound geometry caller")
            self.value["geometry"].append(
                {
                    "point_identity": self.active_point.identity,
                    "reference_identity": kwargs["reference"].identity,
                    "base": [list(r) for r in tensor.base],
                    "increment": [list(r) for r in tensor.increment],
                    "H": [list(r) for r in result.one_form_hodge.matrix],
                }
            )
            return result

        def writer_call(point, c):
            result = writer(point, c)
            self.value["writer_targets"].append(
                {
                    "point_identity": point.identity,
                    "C": list(c.values),
                    "W_A": list(point.inputs.current.W_A),
                    "J": list(point.current.values),
                    "drive": list(result[1]),
                }
            )
            return result

        def log_call(old, target, dt, tau):
            result = log(old, target, dt, tau)
            self.value["log_writes"].append(
                {
                    "old": list(old),
                    "target": list(target),
                    "dt": dt,
                    "tau": tau,
                    "output": list(result),
                }
            )
            return result

        def rebuild_call(backend, c, w):
            self.value["rebuilds"].append(
                {"C": list(c.values), "W_A": list(w), "descriptor_id": backend.identity}
            )
            return rebuild(backend, c, w)

        for owner, name, function in (
            (realizations, "_a_source_geometry", source_call),
            (realizations, "H_profile", geometry_call),
            (candidate, "candidate_a_writer_target", writer_call),
            (candidate, "candidate_a_log_interpolation", log_call),
            (GRC9V4CandidateADifferentialReference, "rebuild", rebuild_call),
        ):
            self.stack.enter_context(patch.object(owner, name, function))
        return self

    def __exit__(self, *args):
        return self.stack.__exit__(*args)


def capture_pass(passed, trace):
    return {
        "inputs_identity": passed.inputs.identity,
        "predictor": point_capture(passed.predictor),
        "corrector": point_capture(passed.corrector),
        "H": [list(r) for r in passed.residual.geometry.one_form_hodge.matrix],
        "regenerated": [
            list(r) for r in passed.residual.regenerated.one_form_hodge.matrix
        ],
        "split_admitted": passed.residual.admitted,
        "trace": trace.value,
    }


def read_pass(before, backend):
    with Trace() as trace:
        passed = realizations.CandidateAOSPass(before, backend)
    return capture_pass(passed, trace)


def take_step(before, backend):
    with Trace() as trace:
        step = steps.ProvisionalCandidateAOSStep(before, backend)
    passed = capture_pass(step.os_pass, trace)
    value = {
        "entry": authority(before.current),
        "pass": passed,
        "selection_inputs": step.resource.selection.inputs.identity,
        "selection_J": list(step.resource.selection.current.values),
        "resource_prestate": step.resource.prestate.identity,
        "resource": authority(step.resource.provisional_state),
        "continuity_evaluations": step.resource.continuity_evaluations,
        "poststate": authority(step.next_inputs.current),
        "next_inputs_identity": step.next_inputs.identity,
        "final": point_capture(step.final),
        "restart": point_capture(step.restart),
    }
    return value, step.next_inputs


def geometry(before, matrix):
    ref = before.geometry.reference
    return GRCV4Geometry(ref, OneFormHodge(ref.graph, tuple(map(tuple, matrix))))


def check_point(value, inputs, backend):
    payload = {
        "schema_version": "grcv4-a-fixed-stage-v1",
        "numerics": candidate.A_CURRENT_NUMERICS,
        "inputs": inputs.to_payload(),
        "differential_reference": backend.to_payload(),
    }
    identity = "grcv4-a-fixed-stage-sha256:" + base.digest(payload)
    base.require(
        value["identity"] == value["read_source"] == identity
        and value["inputs_identity"] == inputs.identity
        and value["current"] == value["read_current"],
        "foreign/stale current or read operand",
    )
    n = len(inputs.geometry.reference.graph.live_edge_ids)
    for key in ("current", "baseline", "read_current", "readback", "flat"):
        a = np.asarray(value[key])
        base.require(
            a.shape == (n,) and np.isfinite(a).all(), "invalid point quantity: " + key
        )
    # Alternate surface: H * causal_flat must reproduce the observed Read-Back.
    h = inputs.geometry.one_form_hodge.matrix
    sharp = [
        float(sum((Q(x) * Q(y) for x, y in zip(row, value["flat"], strict=True)), Q()))
        for row in h
    ]
    close(sharp, value["readback"], aos.CURRENT_ERROR, "flat/readback")


def expected_increment(graph, flat):
    # All bound layout edges have two distinct endpoints; star multiplicity=2.
    ends = [{e.tail_node_id, e.head_node_id} for e in graph.oriented_edges]
    base.require(all(len(s) == 2 for s in ends), "outside bound loop-free oracle scope")
    return [
        [
            float(Q(1, 2) * Q(float(Q(len(a & b), 2) * Q(x) * Q(y))))
            for b, y in zip(ends, flat, strict=True)
        ]
        for a, x in zip(ends, flat, strict=True)
    ]


def check_pass(value, before, backend, *, step=False):
    base.require(
        value["inputs_identity"] == before.identity, "OS prestate substitution"
    )
    predictor = replace(before, stage="os_predictor")
    corrector = replace(
        before, geometry=geometry(before, value["H"]), stage="os_corrector"
    )
    check_point(value["predictor"], predictor, backend)
    check_point(value["corrector"], corrector, backend)
    calls = value["trace"]["geometry"]
    base.require(len(calls) == 2, "OS must generate and regenerate exactly once")
    ref = before.geometry.reference
    for point, call, matrix in zip(
        (value["predictor"], value["corrector"]),
        calls,
        (value["H"], value["regenerated"]),
        strict=True,
    ):
        increment = expected_increment(ref.graph, point["flat"])
        h = [
            [a + 0.5 * b for a, b in zip(r, s, strict=True)]
            for r, s in zip(ref.pairings.one_form.matrix, increment, strict=True)
        ]
        base.require(
            call["point_identity"] == point["identity"]
            and call["reference_identity"] == ref.identity
            and call["base"] == [list(r) for r in ref.K4_base]
            and call["increment"] == increment
            and call["H"] == h == matrix,
            "geometry did not consume its own predictor/corrector source",
        )
    base.require(
        value["split_admitted"] is True
        and aos.split_admitted(
            value["H"], value["regenerated"], ref.pairings.one_form.matrix, Q(aos.SPLIT)
        ),
        "represented OS split failed",
    )
    if not step:
        base.require(
            not value["trace"]["writer_targets"] and not value["trace"]["log_writes"],
            "read-only OS evaluation advanced history",
        )
        expected = [
            {
                "C": list(before.current.C),
                "W_A": list(before.current.W_A),
                "descriptor_id": backend.identity,
            }
        ] * 2
        base.require(
            value["trace"]["rebuilds"] == expected, "OS descriptor operand substitution"
        )
    return corrector


def outputs(value):
    p = value["pass"] if "pass" in value else value
    result = {
        "current": p["corrector"]["current"],
        "baseline": p["corrector"]["baseline"],
        "H": p["H"],
        "regenerated": p["regenerated"],
        "predictor_current": p["predictor"]["current"],
        "predictor_readback": p["predictor"]["readback"],
        "corrector_readback": p["corrector"]["readback"],
    }
    if "poststate" in value:
        result.update(C=value["poststate"]["C"], W_A=value["poststate"]["W_A"])
    return result


def check_step(value, before, backend):
    base.require(value["entry"] == authority(before.current), "step entry drift")
    corrector = check_pass(value["pass"], before, backend, step=True)
    selected = value["pass"]["corrector"]
    base.require(
        value["selection_inputs"] == corrector.identity
        and value["selection_J"] == selected["current"]
        and value["resource_prestate"] == before.identity
        and value["continuity_evaluations"] == 1,
        "continuity selection/count drift",
    )
    b = before.geometry.reference.graph.incidence
    # Native divergence is a binary64 sum in live-edge order, then dt product/subtraction.
    divergence = [
        sum(x * y for x, y in zip(row, selected["current"], strict=True)) for row in b
    ]
    c = [x - before.dt * y for x, y in zip(before.current.C, divergence, strict=True)]
    base.require(
        value["resource"] == aos.authority(c, before.current.W_A),
        "continuity resource drift",
    )
    trace = value["pass"]["trace"]
    base.require(
        len(trace["writer_targets"]) == len(trace["log_writes"]) == 1,
        "history writer count drift",
    )
    writer, log = trace["writer_targets"][0], trace["log_writes"][0]
    base.require(
        writer["point_identity"] == selected["identity"]
        and writer["J"] == selected["current"]
        and writer["C"] == c
        and writer["W_A"] == list(before.current.W_A),
        "writer operand substitution",
    )
    base.require(
        log["old"] == writer["W_A"]
        and log["target"] == writer["drive"]
        and log["dt"] == before.dt
        and log["tau"] == 1
        and value["poststate"] == aos.authority(c, log["output"]),
        "log writer/poststate drift",
    )
    state = base.GRCV4AuthoritativeState(tuple(c), tuple(log["output"]), None)
    following = replace(
        before,
        current=state,
        step_index=before.step_index + 1,
        time=float(Q(before.time) + Q(before.dt)),
    )
    base.require(
        value["next_inputs_identity"] == following.identity,
        "delivered next inputs drift",
    )
    check_point(
        value["final"],
        replace(corrector, current=state, stage="post_continuity"),
        backend,
    )
    check_point(
        value["restart"], replace(following, dt=0, stage="target_readmission"), backend
    )
    pairs = [
        (before.reset.C, before.reset.W_A),
        (before.current.C, before.current.W_A),
        (before.current.C, before.current.W_A),
        (c, before.current.W_A),
        (c, state.W_A),
        (c, state.W_A),
    ]
    expected = [
        {"C": list(c0), "W_A": list(w0), "descriptor_id": backend.identity}
        for c0, w0 in pairs
    ]
    base.require(
        trace["rebuilds"] == expected, "writer/final/restart descriptor operand drift"
    )
    return following


def read_certificate(before, value):
    """Read-only pass quantities, without fictional native C/W advancement."""
    graph = before.geometry.reference.graph.port_graph.to_payload()
    high = aos.IntervalRows(
        aos.StagedRows(graph["live_node_ids"], graph["edges"], aos.PARAMS)
    )
    c, w = aos.vector(before.current.C), aos.vector(before.current.W_A)
    _, _, s = high.ordinary_os("A", c, w)
    truths = {
        "current": s["read"]["J"],
        "baseline": s["read"]["baseline"],
        "H": s["H"],
        "regenerated": high.I + s["read"]["source"] / 2,
        "predictor_current": s["predictor"]["J"],
    }
    for name, point in (("predictor", s["predictor"]), ("corrector", s["read"])):
        drive = high.conductance(c, w, point["baseline"])
        truths[name + "_readback"] = aos.IV.matrix(
            [
                (x - g) / (x + g) * j / 16
                for x, g, j in zip(w, drive, point["J"], strict=True)
            ]
        )
    errors = error_bounds(outputs(value), truths)
    base.require(
        s["split_bound"] < Q(aos.SPLIT)
        and s["geometry_bound"] < Q(1, 2)
        and s["read"]["regularity"] > Q(1, 2),
        "independent read domain not certified",
    )
    return {
        "kind": "read_only",
        "errors": errors,
        "split_upper": str(s["split_bound"]),
        "input_identity": before.identity,
        "output_digest": base.digest(outputs(value)),
    }


def error_bounds(output, truths):
    errors = {}
    for name, truth in truths.items():
        values = np.asarray(output[name]).reshape(-1)
        error = aos.full_error(values, aos.IV.matrix(list(truth)))
        base.require(
            error < oracle.LIMITS.get(name, aos.CURRENT_ERROR),
            "interval error: " + name,
        )
        errors[name] = str(error)
    return errors


def final_certificate(before, value):
    """Written-state final and restart reads, at their respective native H."""
    graph = before.geometry.reference.graph.port_graph.to_payload()
    high = aos.IntervalRows(
        aos.StagedRows(graph["live_node_ids"], graph["edges"], aos.PARAMS)
    )
    c, w = aos.vector(value["poststate"]["C"]), aos.vector(value["poststate"]["W_A"])
    result = {}
    for name, h in (("final", aos.IV.matrix(value["pass"]["H"])), ("restart", high.I)):
        point = high.read("A", c, w, h)
        drive = high.conductance(c, w, point["baseline"])
        flux = aos.IV.matrix(
            [
                (x - g) / (x + g) * j / 16
                for x, g, j in zip(w, drive, point["J"], strict=True)
            ]
        )
        truths = {
            "current": point["J"],
            "baseline": point["baseline"],
            "readback": flux,
            "flat": inverse(h) * flux,
        }
        result[name] = error_bounds(value[name], truths)
    return {
        "kind": "written_state_fixed_geometry_reads",
        "errors": result,
        "input_digest": base.digest(
            {"state": value["poststate"], "H": value["pass"]["H"]}
        ),
        "output_digest": base.digest({k: value[k] for k in ("final", "restart")}),
    }
