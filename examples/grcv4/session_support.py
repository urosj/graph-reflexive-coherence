"""Checkout-only numerical building blocks for the executable API sessions.

No profile registration or production API is added. Diagnostics are captured
from an executed pure step; inspecting a saved diagnostic does not solve again.
"""

import math
from dataclasses import replace

import numpy as np

from examples.grcv4 import compare_five as comparison
from pygrc.models.grc_v4_ci import ProvisionalCandidateCIStep
from pygrc.models.grc_v4_migration import map_migration, migration_history_policy
from pygrc.models.grc_v4_pc import ProvisionalCandidatePCStep, carrier_geometry
from pygrc.models.grc_v4_rg2b import ProvisionalCandidateRG2bStep
from pygrc.models.grc_v4_step import (
    ProvisionalCandidateAOSStep,
    ProvisionalCandidateCOSStep,
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def family(inputs):
    return inputs.geometry.reference.profile.identity_payload.profile_family_id


def fresh(inputs):
    """Reconstruct PC's old-Z geometry after an edit/map; never repair authority."""
    geometry = (
        carrier_geometry(inputs, inputs.current)
        if inputs.geometry.reference.profile.identity_payload.realization == "PC"
        else inputs.geometry.reference.geometry()
    )
    return replace(inputs, geometry=geometry)


def transfer(inputs, amount, *, conserve=True):
    """Move resource from node index 1 to 0; reset baseline stays untouched."""
    values = list(inputs.current.C)
    values[0] += amount
    if conserve:
        values[1] -= amount
    return fresh(replace(inputs, current=replace(inputs.current, C=tuple(values))))


class Session:
    """One explicit model/configuration; retains no cross-run validation cache."""

    def __init__(self):
        self._fixtures = {}

    def fixtures(self, candidate):
        # Only immutable declaration construction is shared within this session.
        if candidate not in self._fixtures:
            self._fixtures[candidate] = comparison.make_inputs(candidate)
        return self._fixtures[candidate]

    def state_record(self, inputs):
        result = {
            "family": family(inputs),
            "kernel_digest": inputs.scientific_state_id,
            "step": inputs.step_index,
            "time": inputs.time,
            "Q_target": inputs.Q_target,
            "current": {k: getattr(inputs.current, k) for k in ("C", "W_A", "Z_4")},
            "reset": {k: getattr(inputs.reset, k) for k in ("C", "W_A", "Z_4")},
        }
        return result

    def advance(self, inputs, backend):
        name = inputs.geometry.reference.profile.identity_payload.realization
        if name == "OS":
            step = (
                ProvisionalCandidateAOSStep(inputs, backend)
                if backend is not None
                else ProvisionalCandidateCOSStep(inputs)
            )
            point = step.os_pass.corrector
            diagnostic = {
                "split_defect": step.os_pass.residual.values,
                "split_admitted": step.os_pass.residual.admitted,
            }
        elif name in ("CI", "CI+PC"):
            step = ProvisionalCandidateCIStep(inputs, backend)
            point = step.root.selected.point
            diagnostic = {
                "root_evaluations": step.root.evaluations,
                "joint_residual_l2": math.sqrt(
                    float(step.root.selected.residual_squared)
                ),
            }
        elif name == "PC":
            step = ProvisionalCandidatePCStep(inputs, backend)
            point, diagnostic = step.read.point, {}
        elif name == "RG2b":
            step = ProvisionalCandidateRG2bStep(inputs, backend)
            point = step.point
            diagnostic = {
                "section_evaluations": step.section.evaluations,
                "section_error_upper": step.section.error_upper,
            }
        else:
            raise ValueError("unsupported realization: " + name)
        after = fresh(step.next_inputs)
        read = comparison.read_diagnostics(point)
        if backend is None:
            read["structural_hodge"] = point.algebra.transport.structural_hodge.matrix
        else:
            diagnostic["writer_target"] = step.writer.W_drv_A
            diagnostic["writer_descriptors"] = step.writer.descriptors
        p = inputs.geometry.reference.profile.params_resolved
        zeta = p.candidate.zeta_A if backend is not None else p.candidate.zeta_C
        np.testing.assert_allclose(
            read["J"],
            np.array(read["J0"]) + zeta * np.array(read["read_flux"]),
            rtol=0,
            atol=1e-11,
        )
        np.testing.assert_allclose(
            after.current.C,
            np.array(inputs.current.C)
            - inputs.dt
            * np.array(inputs.geometry.reference.graph.incidence)
            @ np.array(read["J"]),
            rtol=0,
            atol=1e-11,
        )
        require(abs(sum(after.current.C) - inputs.Q_target) < 1e-11, "charge mismatch")
        require(
            after.reset == inputs.reset and after.receipt_ids == inputs.receipt_ids,
            "pure step changed reset/ledger",
        )
        require(
            after.step_index == inputs.step_index + 1
            and after.time == inputs.time + inputs.dt,
            "step clock mismatch",
        )
        diagnostic["carrier_writes"] = int(name in ("PC", "CI+PC"))
        if after.current.Z_4 is not None:
            n = len(inputs.geometry.reference.graph.live_edge_ids)
            decay = math.exp(-inputs.dt / p.realization.tau_PC)
            expected = decay * np.array(inputs.current.Z_4).reshape(n, n) + (
                1 - decay
            ) * np.array(read["source"])
            np.testing.assert_allclose(
                np.array(after.current.Z_4).reshape(n, n),
                expected,
                rtol=1e-10,
                atol=1e-14,
            )
            diagnostic["carrier_write_residual"] = float(
                np.max(np.abs(np.array(after.current.Z_4).reshape(n, n) - expected))
            )
        if backend is not None:
            decay = math.exp(-inputs.dt / p.candidate.tau_A)
            expected = np.exp(
                decay * np.log(inputs.current.W_A)
                + (1 - decay) * np.log(step.writer.W_drv_A)
            )
            np.testing.assert_allclose(
                after.current.W_A, expected, rtol=1e-12, atol=1e-14
            )
        # Reuse final readmission where the production step already did it.
        continuation = None
        if name in ("CI", "CI+PC"):
            continuation = comparison.read_diagnostics(step.restart.selected.point)
        elif name == "PC":
            continuation = comparison.read_diagnostics(step.restart.point)
        elif name == "RG2b":
            continuation = comparison.read_diagnostics(step.restart_point)
        return after, {
            "before": self.state_record(inputs),
            "after": self.state_record(after),
            "read": read,
            "diagnostics": diagnostic,
            "continuation": continuation,
        }

    def migrate(self, before, target):
        policy = migration_history_policy(before, target)
        after = fresh(map_migration(before, target, policy))
        require(
            (after.step_index, after.time, after.Q_target)
            == (before.step_index, before.time, before.Q_target),
            "migration advanced clock or charge",
        )
        for role in ("current", "reset"):
            a, b = getattr(before, role), getattr(after, role)
            require(a.C == b.C and a.W_A == b.W_A, "same-A migration lost C/W")
        return after, {
            "source": self.state_record(before),
            "target": self.state_record(after),
            "policy": policy.to_payload(),
            "scope": "pure_map_not_lifecycle_commit_or_target_admission",
        }


def differences(before, after):
    """Compare only matching physical times; absent channels stay absent."""
    require(
        (before.step_index, before.time) == (after.step_index, after.time),
        "comparison requires equal physical step/time",
    )
    require(
        before.geometry.reference.graph == after.geometry.reference.graph,
        "comparison requires the same graph and ordering",
    )
    result = {
        "same_kernel_digest": before.scientific_state_id == after.scientific_state_id,
        "step": before.step_index,
        "time": before.time,
    }
    for key in ("C", "W_A", "Z_4"):
        a, b = getattr(before.current, key), getattr(after.current, key)
        result[key] = (
            {"before_present": a is not None, "after_present": b is not None}
            if a is None or b is None
            else {
                "delta": (np.array(b) - np.array(a)).tolist(),
                "l2": float(np.linalg.norm(np.array(b) - np.array(a))),
                "exactly_equal": a == b,
            }
        )
    return result
