"""Verification-only fresh Newton oracle, independent of native fixed-point proposals."""

import sys
from pathlib import Path

import flint
from flint import arb_mat, ctx, fmpq

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "implementation/investigations/grc9v4-constitutive-design/research"
sys.path.insert(0, str(RESEARCH))
sys.path.insert(
    0, str(RESEARCH.parent / "evidence/spark-completion/review/constructive-candidate")
)
from spark_completion_ci import CCIReference


def contains(pair, ball):
    return fmpq(pair[0]) <= ball.lower().fmpq() and ball.upper().fmpq() <= fmpq(pair[1])


def verify_step(step):
    """Fresh higher-precision roots on the exact before AND after states."""
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        m = CCIReference(step.before.graph.to_payload())
        C = arb_mat([[fmpq(x)] for x in step.before.C])
        expected = m.ci_step(C)
        for label, native, reference in (
            ("flat", step.root["flat"], expected["root"]["flat"]),
            ("geometry", step.root["geometry"], expected["root"]["geometry"]),
            ("current", step.root["current"], expected["root"]["selected"]["current"]),
        ):
            if not all(
                contains(native[i][j], reference[i, j])
                for i in range(reference.nrows())
                for j in range(reference.ncols())
            ):
                raise AssertionError("independent CI containment failed: " + label)
        for i, (value, bound) in enumerate(
            zip(step.after.C, step.componentwise_error_bounds, strict=True)
        ):
            if not abs(expected["after"][i, 0] - fmpq(value)) < flint.arb(fmpq(bound)):
                raise AssertionError("whole-step error failed")
        after = arb_mat([[fmpq(x)] for x in step.after.C])
        restart = m.root(after)
        if not all(
            contains(step.restart_root["current"][i][0], x)
            for i, x in enumerate(restart["selected"]["current"].entries())
        ):
            raise AssertionError("poststate fresh root failed")
        final = m.read(after, expected["root"]["geometry"], eta=m.q(1, 1024))
        if not all(
            contains(step.final_current[i], x)
            for i, x in enumerate(final["current"].entries())
        ):
            raise AssertionError("consumed-geometry poststate read failed")
        reference = m.read(after, m.I, eta=m.q(1, 1024))
        if not all(
            x.contains(fmpq(step.reference_current[i]))
            for i, x in enumerate(reference["current"].entries())
        ):
            raise AssertionError("exact reference poststate read failed")
        if step.after.charge != step.before.charge or sum(
            map(fmpq, step.after.C)
        ) != fmpq(step.after.charge):
            raise AssertionError("exact charge failed")
        return {
            "independent_precision_bits": 768,
            "proposal_method": "fresh Newton",
            "root_enclosure_containment": True,
            "full_step_bound": True,
            "fresh_poststate_root": True,
            "poststate_diagnostics": True,
            "exact_charge": True,
            "newton_iterations": expected["root"]["iterations"],
        }
