"""Small Candidate-A CI/PC/CI+PC comparison on one shared edge.

From the repository root:
    PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/compare_ci_pc.py
    PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/compare_ci_pc.py --zero-gain

This checkout-only experiment uses test helpers to construct declarations, but
executes production provisional steps, including admission and reconstruction.
It does not register new supported profiles or constitute a G2 acceptance.
Default parameters are checked for eight steps, not an indefinite trajectory.

Here H_CI=1+kappa_H*S(H_CI), H_PC=1+kappa_H*Z_old, and
H_CIPC=1+kappa_H*(Z_old+S(H_CIPC)). Both persistent variants write
Z_next=exp(-dt/tau)*Z_old+(1-exp(-dt/tau))*S after the read. Thus zero
initial Z makes CI and CI+PC agree on the first step, not subsequent steps.
All three retain Candidate A's W_A history. root_evals counts inner root
evaluations for the live read, not elapsed physical steps or total work.
"""

import argparse
from dataclasses import replace
import math

from pygrc.models.grc_v4_ci import ProvisionalCandidateCIStep
from pygrc.models.grc_v4_pc import ProvisionalCandidatePCStep
from tests.models.test_grc_v4_ci import fixture as ci_fixture
from tests.models.test_grc_v4_pc import configure as pc_configure
from tests.models.test_grc_v4_cipc import configure as cipc_configure


def initial_conditions(gain):
    # Same graph u -> v, C=(3,1), W_A=(2,), reference h=1, backend and
    # candidate coefficients. No initial carrier history in either PC variant.
    ci, backend = ci_fixture(
        "A",
        C=(3.0, 1.0),
        W=(2.0,),
        gain=gain,
        radius=0.25,
        changes={"candidate": {"eta": 0.025}},
    )
    ci = replace(ci, dt=0.5)
    # At kappa_H=0.25, R=0.5 needs a composite geometry radius >=0.25.
    # That radius also keeps the whole scalar Hodge ball positive (H_ref=1).
    # eta=0.025 gives a certified uniform source bound <R over the base chart;
    # merely shrinking R without checking this bound would not be sufficient.
    pc = pc_configure(
        ci,
        gain=gain,
        radius=0.5,
        resource_radius=4.0,
        weight_lower=0.1,
        weight_upper=2.0,
        tau=0.5,
        z=(0.0,),
    )
    cipc = cipc_configure(pc, domain_radius=0.25)
    # Configuration helpers keep solver_kind and both iteration limits aligned,
    # and recompute parameter digests and declaration identities.
    states = {"CI": ci, "PC": pc, "CI+PC": cipc}
    for value in states.values():
        ref = value.geometry.reference
        assert ref.graph == ci.geometry.reference.graph
        assert (
            ref.profile.params_resolved.candidate
            == ci.geometry.reference.profile.params_resolved.candidate
        )
        assert value.current.C == ci.current.C and value.current.W_A == ci.current.W_A
        assert value.dt == ci.dt and value.reset == value.current
    return states, backend


def compare(*, steps=8, gain=0.25):
    states, backend = initial_conditions(gain)
    history = []
    print(f"A; u -> v; C=(3,1); W_A=(2,); Z_PC=Z_CIPC=0; dt=tau_PC=0.5; kappa_H={gain}")
    print(
        "J is total current, not baseline J0. H and S are read-stage values; C/W/Z are post-step."
    )
    print(
        "step family      J                H_read           S_read           Z_after          C_u_after        W_after       root_evals",
        flush=True,
    )
    for k in range(1, steps + 1):
        row = {}
        for name, before in states.items():
            if name == "PC":
                step = ProvisionalCandidatePCStep(before, backend)
                trial, evaluations = step.read, "direct"
            else:
                step = ProvisionalCandidateCIStep(before, backend)
                trial, evaluations = step.root.selected, str(step.root.evaluations)
            after = step.next_inputs
            current = trial.point.current.values[0]
            h = trial.inputs.geometry.one_form_hodge.matrix[0][0]
            source = trial.structural_source.increment[0][0]
            old_z = 0.0 if before.current.Z_4 is None else before.current.Z_4[0]
            # Independent scalar checks of the distinguishing realization laws.
            expected_h = 1.0 + gain * (
                source if name == "CI" else old_z if name == "PC" else old_z + source
            )
            assert math.isclose(h, expected_h, rel_tol=0.0, abs_tol=2e-11)
            if name == "CI":
                assert after.current.Z_4 is None
                z_text = "--"
            else:
                z = after.current.Z_4[0]
                a = math.exp(-before.dt / 0.5)
                assert math.isclose(
                    z, a * old_z + (1 - a) * source, rel_tol=1e-12, abs_tol=1e-15
                )
                z_text = f"{z:.12f}"
            assert all(c >= 0.0 for c in after.current.C)
            assert math.isclose(sum(after.current.C), 4.0, rel_tol=0.0, abs_tol=1e-12)
            assert after.step_index == before.step_index + 1
            assert after.reset == before.reset
            row[name] = {
                "J": current,
                "H": h,
                "C": after.current.C,
                "W": after.current.W_A,
            }
            states[name] = after
            print(
                f"{k:4d} {name:5s} {current: .12f} {h: .12f} {source: .12f} {z_text:>16s} {after.current.C[0]: .12f} {after.current.W_A[0]: .12f} {evaluations:>7s}",
                flush=True,
            )
        if gain == 0.0:
            for name in ("PC", "CI+PC"):
                for key in ("J", "H"):
                    assert math.isclose(
                        row["CI"][key], row[name][key], rel_tol=0.0, abs_tol=2e-11
                    )
                for key in ("C", "W"):
                    assert all(
                        math.isclose(a, b, rel_tol=0.0, abs_tol=2e-11)
                        for a, b in zip(row["CI"][key], row[name][key], strict=True)
                    )
        elif k == 1:
            # Empty carrier: CI+PC initially has exactly CI's geometry equation.
            assert math.isclose(
                row["CI"]["J"], row["CI+PC"]["J"], rel_tol=0.0, abs_tol=2e-11
            )
            assert abs(row["CI"]["J"] - row["PC"]["J"]) > 1e-8
        else:
            assert all(
                abs(row[a]["J"] - row[b]["J"]) > 1e-10
                for a, b in (("CI", "PC"), ("CI", "CI+PC"), ("PC", "CI+PC"))
            )
        print(
            f"     delta J vs PC: CI={row['CI']['J'] - row['PC']['J']:+.6e}, CI+PC={row['CI+PC']['J'] - row['PC']['J']:+.6e}",
            flush=True,
        )
        history.append(row)
    return history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, choices=range(1, 9), default=8)
    parser.add_argument(
        "--zero-gain",
        action="store_true",
        help="control: remove geometry feedback without disabling carrier writes",
    )
    args = parser.parse_args()
    compare(steps=args.steps, gain=0.0 if args.zero_gain else 0.25)
