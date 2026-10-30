"""Real branch crossings: exact legacy parity and independently staged return."""

from copy import deepcopy
from dataclasses import asdict, replace
import json
from fractions import Fraction
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from pygrc.models import grc_9_v4_crossing as c
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_certification import NumericalPolicy, numerical_policy
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_9_v4_legacy import config

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "implementation/phase-9-grcv4/tranche-9"
EVIDENCE = {}


def step_request(name, dt=2**-12):
    return GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", name, dt, FrozenJSONMap({})
    )


def initializer_oracle(native, evolution):
    """Scalar Eq G2 and native exponent; no production gradient/initializer calls."""
    state = native.get_state()
    rows = {i: [] for i in state.nodes}
    for i in state.nodes:
        for row in range(3):
            terms = []
            for _, edge in sorted(state.port_edges.items()):
                if edge.node_u == i:
                    port, neighbor = edge.port_u, edge.node_v
                elif edge.node_v == i:
                    port, neighbor = edge.port_v, edge.node_u
                else:
                    continue
                if (port - 1) // 3 == row:
                    terms.append(
                        (
                            edge.conductance,
                            state.nodes[neighbor].coherence - state.nodes[i].coherence,
                        )
                    )
            rows[i].append(
                sum(w * d for w, d in terms) / sum(w for w, _ in terms)
                if terms
                else 0.0
            )
    out = []
    for _, e in sorted(state.port_edges.items()):
        gap = sum((a - b) ** 2 for a, b in zip(rows[e.node_u], rows[e.node_v]))
        out.append(
            max(
                1e-12,
                math.exp(
                    -evolution["alpha"]
                    * (
                        state.nodes[e.node_u].coherence
                        + state.nodes[e.node_v].coherence
                    )
                    / 2
                    - evolution["beta"] * gap / 2
                    - evolution["gamma"] * e.flux_uv**2 / 2
                ),
            )
        )
    return tuple(out), rows


class CrossingTests(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select bounded family")
        value = json.loads((BASE / f"P9-9.1b-{cls.FAMILY}.json").read_bytes())
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.LEGACY_EXACT),
        ):
            cls.seed = c.enabled._decode_state(
                value["evidence"]["mixed_snapshot"]["initial"], cls.FAMILY
            )
        cls.ref = cls.seed.inputs.geometry.reference

    def owner(self):
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.LEGACY_EXACT),
        ):
            return c.GRC9V4BranchOperation(c.enabled.GRC9V4EnabledOperation(self.seed))

    def request(self, owner, direction, name=None, declaration=None):
        if declaration is None:
            if direction == "enable":
                declaration = dict(target_reference=self.ref.to_payload())
            else:
                cfg = config(self.FAMILY)
                del cfg["state"]
                cfg["dt"] = 2**-12
                # A definite incoming native stage, independent of dropped V4 histories.
                declaration = dict(
                    legacy_config=cfg,
                    current_incoming_weights=[1.0 + i / 16 for i in range(9)],
                    reset_incoming_weights=[0.75 + i / 32 for i in range(9)],
                    current_incoming_flux=[0.01 * (i + 1) for i in range(9)],
                    reset_incoming_flux=[-0.02 * (i + 1) for i in range(9)],
                )
        return c.GRC9V4BranchRequest(
            name or direction, owner.lifecycle_digest, direction, declaration
        )

    def cross(self, owner, direction):
        r = owner.migrate(self.request(owner, direction))
        self.assertTrue(r.committed, r.failure)
        return r

    def test_roundtrip_both_roles_native_parity_and_continuation(self):
        owner = self.owner()
        self.assertNotEqual(owner.state.inputs.current, owner.state.inputs.reset)
        # Ledger prefix must survive both crossings, reset and a later enabled step.
        self.assertTrue(owner.step_enabled(step_request("prefix", 0)).committed)
        original = owner.state.inputs
        enter = self.cross(owner, "disable")
        pub = owner._published
        native = c.GRC9V3._from_snapshot(
            deepcopy(pub.owner.snapshot()), restore_reset_baseline=True
        )
        reset_native = c._reset_delegate(native)
        self.assertEqual(c._same_coordinates(self.ref, native), original.current.C)
        self.assertEqual(c._same_coordinates(self.ref, reset_native), original.reset.C)
        # Native incoming stage and the transfer are independently evaluated.
        d = self.request(self.owner(), "disable").declaration
        for role, direct in [("current", native), ("reset", reset_native)]:
            incoming = deepcopy(direct.get_state())
            for i, edge in incoming.port_edges.items():
                incoming.port_edges[i] = replace(
                    edge,
                    conductance=d[role + "_incoming_weights"][i],
                    flux_uv=d[role + "_incoming_flux"][i],
                )
            incoming.base_conductance = {
                i: e.conductance for i, e in incoming.port_edges.items()
            }
            probe = c.GRC9V3(params=direct.get_params(), state=incoming)
            expected, _ = initializer_oracle(probe, direct.get_params().evolution)
            self.assertEqual(
                tuple(direct.get_state().base_conductance[i] for i in range(9)),
                expected,
            )
        losses = enter.emitted_receipts[0].identity_payload["core"][
            "information_losses"
        ]
        self.assertEqual(
            "candidate_history_loss" in losses, self.FAMILY.startswith("A_")
        )
        self.assertEqual("carrier_history_loss" in losses, self.FAMILY in ("A_PC", "C_PC", "C_CI_PC", "A_CI_PC"))
        disabled_snapshot = owner.snapshot()
        self.assertEqual(
            c.GRC9V4BranchOperation.from_state(disabled_snapshot).snapshot(),
            disabled_snapshot,
        )
        source_charge = sum(
            Fraction(v.coherence) for v in native.get_state().nodes.values()
        )
        actual, expected = owner.legacy_operation("native-step"), native.step()
        target_charge = sum(
            Fraction(v.coherence) for v in native.get_state().nodes.values()
        )
        self.assertEqual(
            owner.receipts[-1].identity_payload["core"]["actual_charge_delta"],
            float(target_charge - source_charge),
        )
        self.assertEqual(asdict(actual), asdict(expected))
        self.assertEqual(
            c._bytes(owner._published.owner.snapshot()), c._bytes(native.snapshot())
        )
        self.assertEqual(
            owner._published.owner.compute_observables(), native.compute_observables()
        )
        owner.legacy_operation("native-reset", "reset")
        native.reset()
        self.assertEqual(
            c._bytes(owner._published.owner.snapshot()), c._bytes(native.snapshot())
        )
        self.assertEqual(
            owner._published.owner.get_state().step_index, original.step_index
        )
        # Evolve after native reset so return current/reset again differ.
        self.assertEqual(
            asdict(owner.legacy_operation("native-after-reset")), asdict(native.step())
        )
        before_return = owner._published
        roles = (native, c._reset_delegate(native))
        initializers = []
        if self.FAMILY.startswith("A_"):
            par = self.ref.profile.params_resolved.candidate
            initializers = [
                initializer_oracle(
                    n, dict(alpha=par.alpha, beta=par.beta, gamma=par.gamma)
                )[0]
                for n in roles
            ]
        self.cross(owner, "enable")
        for i, role in enumerate(("current", "reset")):
            state = getattr(owner.state.inputs, role)
            self.assertEqual(state.C, c._same_coordinates(self.ref, roles[i]))
            if initializers:
                self.assertEqual(state.W_A, initializers[i])
                self.assertNotEqual(state.W_A, getattr(original, role).W_A)
            else:
                self.assertIsNone(state.W_A)
            if self.FAMILY in ("A_PC", "C_PC", "C_CI_PC", "A_CI_PC"):
                self.assertTrue(any(getattr(original, role).Z_4))
                self.assertEqual(set(state.Z_4), {0.0})
        self.assertEqual(
            c._bytes(before_return.owner.snapshot()), c._bytes(native.snapshot())
        )
        returned = owner.state.inputs
        result = owner.step_enabled(step_request("enabled-after-return"))
        self.assertTrue(result.committed, result.failure)
        self.assertNotEqual(owner.state.inputs.current, returned.current)
        clock = (owner.state.inputs.step_index, owner.state.inputs.time)
        self.assertTrue(owner.reset_enabled().committed)
        self.assertEqual(owner.state.inputs.current, returned.reset)
        self.assertEqual(
            (owner.state.inputs.step_index, owner.state.inputs.time), clock
        )
        groups = []
        for r in owner.receipts:
            if not groups or groups[-1][0].commit_id != r.commit_id:
                groups.append([])
            groups[-1].append(r)
        for i, group in enumerate(groups):
            for r in group:
                self.assertEqual(
                    list(r.identity_payload["core"]["parent_receipt_ids"]),
                    [] if i == 0 else [groups[i - 1][0].receipt_id],
                )
        snapshot = owner.snapshot()
        clone = owner.duplicate()
        self.assertEqual(clone.snapshot(), snapshot)
        clone.step_enabled(step_request("clone", 0))
        self.assertEqual(owner.snapshot(), snapshot)
        EVIDENCE["roundtrip"] = dict(
            final_checkpoint=json.loads(snapshot),
            disabled_checkpoint=json.loads(disabled_snapshot),
            commits=len(groups),
            exact_native_step_and_snapshot=True,
            independent_initializer=bool(initializers),
            current_reset_independently_admitted=True,
            enabled_positive_step=True,
        )

    def test_rejection_and_whole_publication_rollback(self):
        owner = self.owner()
        snapshot = owner.snapshot()
        before = owner._published
        declaration = self.request(owner, "disable").declaration.to_dict()
        # Only reset's stage is invalid: a current-only implementation would pass.
        declaration["reset_incoming_weights"][0] = 0
        failed = owner.migrate(self.request(owner, "disable", declaration=declaration))
        self.assertFalse(failed.committed)
        self.assertEqual(failed.failure.stage, "target_readmission")
        self.assertIs(owner._published, before)
        self.assertEqual(owner.snapshot(), snapshot)
        for key, val in [
            ("current_incoming_weights", [True] * 9),
            ("reset_incoming_flux", []),
        ]:
            d = self.request(owner, "disable").declaration.to_dict()
            d[key] = val
            self.assertFalse(
                owner.migrate(self.request(owner, "disable", declaration=d)).committed
            )
            self.assertEqual(owner.snapshot(), snapshot)
        with patch.object(
            owner, "_publish", side_effect=RuntimeError("late publication failure")
        ):
            with self.assertRaises(RuntimeError):
                self.cross(owner, "disable")
        self.assertIs(owner._published, before)
        self.assertEqual(owner.snapshot(), snapshot)
        stale = self.request(owner, "disable")
        self.cross(owner, "disable")
        disabled = owner.snapshot()
        before = owner._published
        self.assertFalse(owner.migrate(stale).committed)
        # Corrupt reset readmission only; no alteration of the live native state.
        original_return = c._return_role

        def reject_reset(ref, native, role):
            if role == "reset":
                raise ValueError("reset-only resource chart exclusion")
            return original_return(ref, native, role)

        with patch.object(c, "_return_role", side_effect=reject_reset):
            r = owner.migrate(self.request(owner, "enable"))
            self.assertFalse(r.committed)
        self.assertIs(owner._published, before)
        self.assertEqual(owner.snapshot(), disabled)
        with patch.object(
            owner, "_publish", side_effect=RuntimeError("late publication failure")
        ):
            with self.assertRaises(RuntimeError):
                self.cross(owner, "enable")
        self.assertIs(owner._published, before)
        self.assertEqual(owner.snapshot(), disabled)
        # Extra or altered port coordinates cannot be guessed on return.
        direct = c.GRC9V3._from_snapshot(
            deepcopy(owner._published.owner.snapshot()), restore_reset_baseline=True
        )
        state = direct.get_state()
        e = state.port_edges[0]
        state.port_edges[0] = replace(e, port_u=9 if e.port_u != 9 else 8)
        with self.assertRaises(ValueError):
            c._same_coordinates(self.ref, direct)
        EVIDENCE["rollback"] = dict(
            reset_only_entry_rejected=True,
            reset_only_return_injected=True,
            late_entry_and_return_failures_atomic=True,
            stale_source_rejected=True,
            altered_ports_rejected=True,
        )

    def test_excluded_legacy_timestep_returns_honest_failure(self):
        owner = self.owner()
        d = self.request(owner, "disable").declaration.to_dict()
        d["legacy_config"]["dt"] = 0.03125
        r = owner.migrate(self.request(owner, "disable", declaration=d))
        self.assertTrue(r.committed, r.failure)
        owner.legacy_operation("reset-for-exclusion", "reset")
        owner.legacy_operation("large-native-step")
        if self.FAMILY == "C_CI":
            before = owner._published
            snapshot = owner.snapshot()
            r = owner.migrate(self.request(owner, "enable"))
            expected_stage, solver = "target_readmission", None
        else:
            self.cross(owner, "enable")
            before = owner._published
            snapshot = owner.snapshot()
            r = owner.step_enabled(step_request("excluded-resource"))
            expected_stage, solver = "charge_admission", "valid_root"
        self.assertFalse(r.committed)
        self.assertEqual(r.failure.stage, expected_stage)
        self.assertEqual(r.failure.solver_disposition, solver)
        self.assertIs(owner._published, before)
        self.assertEqual(owner.snapshot(), snapshot)
        self.assertEqual(r.emitted_receipts, (r.failure.failure_receipt,))
        EVIDENCE["excluded_domain"] = dict(
            legacy_dt=0.03125,
            stage=r.failure.stage,
            solver_disposition=r.failure.solver_disposition,
            whole_publication_unchanged=True,
        )

    def test_replay_tamper_and_wire_pressure(self):
        owner = self.owner()
        self.cross(owner, "disable")
        snapshot = owner.snapshot()
        data = json.loads(snapshot)
        variants = []
        altered = deepcopy(data)
        altered["archives"][0]["current"]["C"][0] += 1
        variants.append(altered)
        altered = deepcopy(data)
        altered["receipts"][0]["identity_payload"]["core"]["parent_receipt_ids"] = []
        altered["receipts"][0]["receipt_id"] = "grc-receipt-sha256:" + "0" * 64
        variants.append(altered)
        altered = deepcopy(data)
        altered["journal"][0]["request"]["declaration"]["reset_incoming_flux"][0] += 1
        variants.append(altered)
        for v in variants:
            with self.assertRaises(ValueError):
                c.GRC9V4BranchOperation.from_state(c._bytes(v))
        with self.assertRaises(ValueError):
            c.GRC9V4BranchOperation.from_state(b'{"x":1,"x":2}')
        with self.assertRaises(ValueError):
            c.GRC9V4BranchRequest.from_payload(
                {**self.request(owner, "enable").to_payload(), "unchecked": True}
            )
        self.assertEqual(owner.snapshot(), snapshot)
        EVIDENCE["replay_pressure"] = dict(
            mutated_archives_receipts_requests_rejected=3,
            duplicate_keys_rejected=True,
            unknown_request_fields_rejected=True,
        )


class COSCrossing(CrossingTests):
    FAMILY = "C_OS"


class CCICrossing(CrossingTests):
    FAMILY = "C_CI"


class ACICrossing(CrossingTests):
    FAMILY = "A_CI"


class APCCrossing(CrossingTests):
    FAMILY = "A_PC"
