"""Native A_PC pressure against the accepted immutable A.1 oracle."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import numpy as np

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_v4_candidate_a as candidate
from pygrc.models import grc_v4_pc as pc
from pygrc.models.grc_9_v4_expansion import (
    GRC9V4APCExpansion,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_9_v4_lifecycle import (
    GRC9V4APCOperation,
    GRC9V4APCState,
    GRC9V4Specialization,
)
from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import (
    ExactBackend,
    current_exact_backend,
    exact_backend,
    exact_number,
    is_exact,
)
from pygrc.models.grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4ReferenceGeometry,
    VertexScalar,
)
from pygrc.models.grc_v4_profile import list_supported_profiles, resolve_profile
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "implementation/phase-9-grcv4/verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))
if importlib.util.find_spec("mpmath") is None:
    raise unittest.SkipTest(
        "A_PC interval pressure requires research dependency mpmath==1.3.0"
    )
import verify_p983a_apc_oracle as oracle

RECORD = ROOT / oracle.RECORD
ORACLE_SHA = "169554a8b01b99484fba8fcb2b6c1854a8a17b23e0d4c9efe0dd203a26c02eec"


def authority(value):
    return GRCV4AuthoritativeState(
        tuple(value["C"]), tuple(value["W_A"]), tuple(value["Z_4"])
    )


def authority_payload(value):
    return {"C": list(value.C), "W_A": list(value.W_A), "Z_4": list(value.Z_4)}


def role_inputs(inputs, state, *, dt=oracle.DT):
    return replace(
        inputs, current=state, geometry=pc.carrier_geometry(inputs, state), dt=dt
    )


def fixture(record):
    ref = GRCV4ReferenceGeometry.from_payload(record["source"]["reference"])
    spec = GRC9V4Specialization(
        FrozenJSONMap(record["specialization"]["resolved"]),
        FrozenJSONMap(record["specialization"]["identity_payload"]),
    )
    inputs = GeometryStageInputs(
        ref.geometry(),
        ref.context,
        authority(record["source"]["current"]),
        authority(record["source"]["reset"]),
        "apc-seed",
        30.140625,
        (),
        1,
        oracle.DT,
        0,
        "pre_read",
        0,
        None,
    )
    inputs = role_inputs(inputs, inputs.current, dt=0)
    return GRC9V4APCState(inputs, spec), GRC9V4ExpansionRequestInput.from_payload(
        record["request"]
    )


def request_for(state, request):
    data = request.to_payload()
    data.update(
        source_state_digest=state.scientific_digest,
        history_policy=oracle.history_policy(
            authority_payload(state.inputs.current),
            authority_payload(state.inputs.reset),
        ),
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    return GRC9V4ExpansionRequestInput.from_payload(data)


def altered_role(state, role, authority):
    inputs = replace(state.inputs, **{role: authority})
    return replace(state, inputs=role_inputs(inputs, inputs.current, dt=0))


def configure(
    inputs, *, candidate_changes=None, pc_changes=None, geometry_changes=None
):
    ref = inputs.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    ident = ref.profile.identity_payload.to_payload()
    for key, changes in (
        ("candidate", candidate_changes),
        ("realization", pc_changes),
        ("geometry", geometry_changes),
    ):
        if changes:
            params[key].update(changes)
    ident["params_hash"] = payload_identity("resolved_params", params)
    ref = replace(ref, profile=resolve_profile(params, ident))
    out = replace(inputs, geometry=replace(inputs.geometry, reference=ref))
    return role_inputs(out, out.current, dt=out.dt)


def outputs(step):
    return {
        "C": step.next_inputs.current.C,
        "W_A": step.next_inputs.current.W_A,
        "Z_4": step.next_inputs.current.Z_4,
        "current": step.read.point.current.values,
        "baseline": step.read.point.baseline.values,
        "H": step.read.point.inputs.geometry.one_form_hodge.matrix,
        "source": step.read.structural_source.increment,
    }


def checked(inputs, backend):
    step = pc.ProvisionalCandidatePCStep(inputs, backend)
    graph = backend.port_graph.to_payload()
    s = inputs.current
    proof = oracle.check_step(graph, s.C, s.W_A, s.Z_4, outputs(step))
    return step, proof


def native_effects(seed, target):
    effects = []
    for label, state in (("source", seed), ("target", target)):
        backend = state.differential_reference
        for role in ("current", "reset"):
            inputs = role_inputs(state.inputs, getattr(state.inputs, role))
            step, truth = checked(inputs, backend)
            high = truth["high"]
            point = step.read.point

            def compare(name, a, b, ai, bi, label=label, role=role):
                effects.append(
                    dict(
                        graph=label,
                        role=role,
                        effect=name,
                        **oracle.separation(
                            np.asarray(a).reshape(-1),
                            np.asarray(b).reshape(-1),
                            oracle.IV.matrix(list(ai)),
                            oracle.IV.matrix(list(bi)),
                        ),
                    )
                )

            for flag, changes in (
                (("geometry", {"kappa_Ah": 0}), ("feedback", {"chi_A": 0}))
                if label == "source"
                else (("feedback", {"chi_A": 0}),)
            ):
                alt = configure(inputs, candidate_changes=changes)
                off = pc.CandidatePCRead(alt, backend)
                exact = high.read(
                    "A", truth["c"], truth["w"], truth["H"], **{flag: False}
                )
                compare(
                    flag,
                    point.current.values,
                    off.point.current.values,
                    truth["read"]["J"],
                    exact["J"],
                )
            if label == "source":
                continue
            nxt = pc.CandidatePCRead(replace(step.next_inputs, dt=0), backend)
            ni = high.read(
                "A",
                truth["C"],
                truth["W_A"],
                high.I + oracle.number(oracle.KAPPA_H) * truth["Z_4"],
            )["J"]

            def next_read(w, z, inputs=step.next_inputs, backend=backend):
                state = GRCV4AuthoritativeState(inputs.current.C, tuple(w), tuple(z))
                return pc.CandidatePCRead(role_inputs(inputs, state, dt=0), backend)

            def exact_next(w, z, high=high, truth=truth, **flags):
                return high.read(
                    "A",
                    truth["C"],
                    w,
                    high.I + oracle.number(oracle.KAPPA_H) * z,
                    **flags,
                )["J"]

            zero = (0.0,) * len(inputs.current.Z_4)
            off = next_read(step.next_inputs.current.W_A, zero)
            compare(
                "written_carrier_next_current",
                nxt.point.current.values,
                off.point.current.values,
                ni,
                exact_next(truth["W_A"], oracle.IV.zeros(len(inputs.current.W_A))),
            )
            alt = configure(
                replace(step.next_inputs, dt=0), candidate_changes={"kappa_Ah": 0}
            )
            off = pc.CandidatePCRead(alt, backend)
            compare(
                "next_geometry",
                nxt.point.current.values,
                off.point.current.values,
                ni,
                exact_next(truth["W_A"], truth["Z_4"], geometry=False),
            )
            # Recompute a deliberately wrong held source at fresh C/W, old H.
            after = step.next_inputs.current
            wrong_state = GRCV4AuthoritativeState(
                after.C, after.W_A, inputs.current.Z_4
            )
            wrong_read = pc.CandidatePCRead(
                role_inputs(inputs, wrong_state, dt=0), backend
            )
            wrong_source = tuple(
                x for row in wrong_read.structural_source.increment for x in row
            )
            wrong_z = pc.scalar_zoh(inputs.current.Z_4, wrong_source, oracle.DT, 1)
            wrong_si = high.read("A", truth["C"], truth["W_A"], truth["H"])["source"]
            decay = oracle.IV.exp(-oracle.number(oracle.DT))
            wrong_zi = decay * truth["z"] + (1 - decay) * wrong_si
            compare("same_source_carrier", after.Z_4, wrong_z, truth["Z_4"], wrong_zi)
            compare(
                "same_source_next_current",
                nxt.point.current.values,
                next_read(after.W_A, wrong_z).point.current.values,
                ni,
                exact_next(truth["W_A"], wrong_zi),
            )
            params = inputs.geometry.reference.profile.params_resolved.candidate
            for name, c, j, ci, ji in (
                (
                    "stale_resource_writer",
                    inputs.current.C,
                    point.current,
                    truth["c"],
                    truth["read"]["J"],
                ),
                (
                    "baseline_current_writer",
                    after.C,
                    point.baseline,
                    truth["C"],
                    truth["read"]["baseline"],
                ),
            ):
                resources = VertexScalar(backend.graph, c)
                drive = candidate._conductance(
                    backend.graph,
                    params,
                    resources,
                    backend.rebuild(resources, inputs.current.W_A),
                    j,
                )
                wrong_w = candidate.candidate_a_log_interpolation(
                    inputs.current.W_A, drive, oracle.DT, 1
                )
                wi = high.write(ci, truth["w"], ji)
                compare(name + "_W", after.W_A, wrong_w, truth["W_A"], wi)
                compare(
                    name + "_next_current",
                    nxt.point.current.values,
                    next_read(wrong_w, after.Z_4).point.current.values,
                    ni,
                    exact_next(wi, truth["Z_4"]),
                )
            compare(
                "next_current_consumes_written_W",
                nxt.point.current.values,
                next_read(inputs.current.W_A, after.Z_4).point.current.values,
                ni,
                exact_next(truth["w"], truth["Z_4"]),
            )
    return effects


class NativeAPCPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = exact_backend(
            ExactBackend.FLINT
            if importlib.util.find_spec("flint")
            else ExactBackend.PYTHON
        )
        cls.backend.__enter__()
        cls.addClassCleanup(cls.backend.__exit__, None, None, None)
        assert hashlib.sha256(RECORD.read_bytes()).hexdigest() == ORACLE_SHA
        cls.record = json.loads(RECORD.read_text())
        cls.seed, cls.request = fixture(cls.record)
        cls.owner = GRC9V4APCOperation(cls.seed)
        result = cls.owner.expand(cls.request)
        assert result.committed, result.failure
        cls.committed = cls.owner.checkpoint()

    def assertClose(self, observed, expected, limit):
        a, b = np.array(observed), np.array(expected)
        self.assertEqual(a.shape, b.shape)
        self.assertLess(float(np.max(np.abs(a - b))), float(limit))

    def assertRollback(self, owner, request, *, stage=None):
        before = owner.checkpoint()
        state = owner.state
        result = owner.expand(request)
        self.assertFalse(result.committed)
        self.assertIs(owner.state, state)
        self.assertEqual(owner.checkpoint(), before)
        self.assertIsNotNone(result.failure)
        if stage is not None:
            self.assertEqual(result.failure.stage, stage)
        self.assertEqual(
            result.failure.prestate_digest, result.failure.poststate_digest
        )
        self.assertEqual(
            result.failure.pre_lifecycle_digest, result.failure.post_lifecycle_digest
        )
        return result

    def test_exact_native_identity_history_receipts_and_reference_current(self):
        r, owner = self.record, self.owner
        self.assertEqual(self.seed.scientific_digest, r["source"]["scientific_digest"])
        self.assertEqual(
            owner.state.scientific_digest, r["target"]["scientific_digest"]
        )
        self.assertEqual(owner.state.reset_digest, r["target"]["reset_digest"])
        self.assertEqual(
            owner.state.inputs.geometry.reference.to_payload(), r["target"]["reference"]
        )
        checkpoint = json.loads(owner.checkpoint())
        refs = checkpoint["reference_currents"][0]
        for role in ("current", "reset"):
            state = getattr(owner.state.inputs, role)
            self.assertEqual(
                authority_payload(state), r["target"]["roles"][role]["authoritative"]
            )
            self.assertClose(
                refs["roles"][role]["source"],
                r["source_reference_reads"][role]["current"],
                oracle.CURRENT_ERROR,
            )
            self.assertClose(
                refs["roles"][role]["target"],
                r["target"]["roles"][role]["incoming_reference_current"],
                oracle.CURRENT_ERROR,
            )
            edge_ids = owner.state.inputs.geometry.reference.graph.live_edge_ids
            self.assertEqual(
                [
                    v
                    for e, v in zip(edge_ids, refs["roles"][role]["target"])
                    if not e.startswith("old-")
                ],
                [0] * 7,
            )
        event = owner.receipts[0].identity_payload.to_dict()
        expected = r["receipt_expectations"]
        for key in (
            "source_state_digest",
            "target_state_digest",
            "source_model_identity",
            "target_model_identity",
            "source_reset_digest",
            "target_reset_digest",
            "actual_charge_delta",
            "information_losses",
            "operation_id",
        ):
            self.assertEqual(event["core"][key], expected[key])
        self.assertEqual(event["event_id"], r["event_id"])
        for role in ("candidate", "carrier"):
            self.assertEqual(
                event["history"][role], dict(subject=role, **expected[role])
            )
        self.assertEqual(owner.state.inputs.step_index, 1)
        self.assertEqual(owner.state.inputs.time, oracle.DT)
        self.assertEqual(owner.state.inputs.dt, 0)
        self.assertEqual(len(owner.receipts), 4)
        self.assertEqual(
            GRC9V4APCOperation.replay(owner.checkpoint()).checkpoint(),
            owner.checkpoint(),
        )

    def test_policy_rehashed_role_substitutions_fail_at_admission(self):
        owner = GRC9V4APCOperation(self.seed)
        policies = []
        for role in ("current", "reset"):
            values = (
                authority_payload(self.seed.inputs.current),
                authority_payload(self.seed.inputs.reset),
            )
            changed = deepcopy(values)
            changed[role == "reset"]["W_A"][0] += 2**-20
            policies.append(oracle.history_policy(*changed))
        for key, value in [
            ("policy_id", "candidate_a_history_free_v1"),
            ("target_initializer_id", "grc9v3_history_free_v1"),
            ("information_loss", "candidate_history_loss"),
        ]:
            policy = self.request.to_payload()["history_policy"]
            policy["candidate"][key] = value
            policies.append(policy)
        for policy in policies:
            for channel in ("candidate", "carrier"):
                policy[channel + "_history_policy_digest"] = payload_identity(
                    "history_channel_policy_identity_payload",
                    {
                        "schema_version": "grcv4-history-channel-policy-identity-v1",
                        "policy": policy[channel],
                    },
                )
            data = self.request.to_payload()
            data["history_policy"] = policy
            self.assertRollback(
                owner, GRC9V4ExpansionRequestInput.from_payload(data), stage="admission"
            )

    def test_charge_both_roles_and_late_receipt_failures_roll_back(self):
        original = GRC9V4APCExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4APCOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                value = original(target, state)
                return (
                    replace(value, C=(value.C[0] + 1, *value.C[1:]))
                    if state == chosen
                    else value
                )

            with patch.object(GRC9V4APCExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, stage="target_readmission")
        owner = GRC9V4APCOperation(self.seed)
        with patch.object(
            native,
            "make_commit_receipts",
            side_effect=ValueError("late receipt failure"),
        ):
            self.assertRollback(owner, self.request, stage="commit")
        with patch.object(
            GRC9V4APCExpansion,
            "transfer_reference_current",
            side_effect=ValueError("late reference failure"),
        ):
            self.assertRollback(owner, self.request, stage="commit")

    def test_replay_rejects_history_reference_identity_and_receipt_tampering(self):
        for path in [
            ("state", "inputs", "current", "W_A", 0),
            ("state", "inputs", "reset", "W_A", 0),
            ("reference_currents", 0, "roles", "current", "target", 0),
            ("reference_currents", 0, "roles", "reset", "source", 0),
            ("state", "scientific_digest"),
            ("receipts", 0, "receipt_id"),
            ("reference_currents", 0, "target_graph_digest"),
        ]:
            data = json.loads(self.committed)
            target = data
            for key in path[:-1]:
                target = target[key]
            value = target[path[-1]]
            target[path[-1]] = (
                value + 2**-20 if isinstance(value, (int, float)) else value + "x"
            )
            with self.subTest(path=path), self.assertRaises((ValueError, TypeError)):
                GRC9V4APCOperation.replay(canonical_json_bytes(data))
        data = json.loads(self.committed)
        data["reference_currents"][0]["roles"]["current"] = data["reference_currents"][
            0
        ]["roles"]["reset"]
        with self.assertRaises(ValueError):
            GRC9V4APCOperation.replay(canonical_json_bytes(data))

    def test_duplicate_concurrent_event_publishes_only_once(self):
        owner = GRC9V4APCOperation(self.seed)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(len(owner.receipts), 4)
        self.assertEqual(owner.checkpoint(), self.committed)

    def test_receiver_owns_exact_backend_across_context_changes(self):
        if importlib.util.find_spec("flint") is None:
            self.skipTest("cross-backend ownership requires optional v4-flint")
        owner = GRC9V4APCOperation(self.seed)
        captured = current_exact_backend()
        other = (
            ExactBackend.PYTHON
            if captured != ExactBackend.PYTHON
            else ExactBackend.FLINT
        )
        seen = []
        real = native._apc_readmit

        def observe(state):
            seen.append(current_exact_backend())
            return real(state)

        with exact_backend(other), patch.object(native, "_apc_readmit", observe):
            self.assertTrue(owner.expand(self.request).committed)
        self.assertTrue(seen)
        self.assertEqual(set(seen), {captured})

    def test_rehashed_target_authority_and_source_policy_do_not_bypass_replay(self):
        for role in ("current", "reset"):
            data = json.loads(self.committed)
            inputs = self.owner.state.inputs
            old = getattr(inputs, role)
            altered = replace(old, W_A=(old.W_A[0] + 2**-30, *old.W_A[1:]))
            forged = replace(
                self.owner.state, inputs=replace(inputs, **{role: altered})
            )
            data["state"] = forged.to_payload()
            data["lifecycle_digest"] = forged.lifecycle_digest(self.owner.receipts)
            with self.assertRaises(ValueError):
                GRC9V4APCOperation.replay(canonical_json_bytes(data))
        seed = replace(self.seed, inputs=replace(self.seed.inputs, step_index=0))
        owner = GRC9V4APCOperation(seed)
        result = self.assertRollback(
            owner, request_for(seed, self.request), stage="admission"
        )
        self.assertIn("postbeat", result.failure.message)
        with self.assertRaises(ValueError):
            inputs = replace(
                self.seed.inputs,
                current=replace(self.seed.inputs.current, Z_4=(0.0,) * 81),
            )
            GRC9V4APCOperation(replace(self.seed, inputs=inputs))

    def test_A2_authorization_is_exact_and_cannot_replace_accepted_oracle(self):
        import phase9_specialization_acceptance as entry

        self.assertEqual(entry.apc_authorization(ROOT), "P9-8.3A.2")
        for path in entry.APC_PATHS:
            self.assertTrue(entry.apc_permitted(path, "P9-8.3A.2"))
            self.assertFalse(entry.apc_permitted(path, "P9-8.3A.1"))
        for path in (
            "specs/grc-9-v4-spec.md",
            "src/pygrc/models/grc_9_v3.py",
            "src/pygrc/models/grc_v4_ci.py",
        ):
            self.assertFalse(entry.apc_permitted(path, "P9-8.3A.2"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.apc_authorization(ROOT)

        bad = dict(entry.APC_ORACLE_HASHES)
        bad[oracle.RECORD] = "0" * 64
        with (
            patch.object(entry, "APC_ORACLE_HASHES", bad),
            self.assertRaises(ValueError),
        ):
            entry.apc_authorization(ROOT)

    def test_complete_archives_and_rehashed_archive_replay_failures(self):
        self.assertEqual(
            self.owner.carrier_archives[0].to_dict(), self.record["carrier_archive"]
        )
        for action in ("entry", "order", "digest", "source", "omission", "swap_roles"):
            data = json.loads(self.committed)
            archive = data["carrier_archives"][0]
            if action == "entry":
                archive["history_content"]["content"][0] += 2**-30
                archive["history_digest"] = payload_identity(
                    "history_content_identity_payload", archive["history_content"]
                )
            elif action == "order":
                archive["source_edge_ids"].reverse()
            elif action == "source":
                archive["source_state_digest"] = self.owner.state.scientific_digest
            elif action == "omission":
                data["carrier_archives"] = []
            elif action == "swap_roles":
                v = archive["history_content"]["content"]
                archive["history_content"]["content"] = v[81:] + v[:81]
                archive["history_digest"] = payload_identity(
                    "history_content_identity_payload", archive["history_content"]
                )
            else:
                archive["history_digest"] = "grcv4-history-sha256:" + "0" * 64
            with (
                self.subTest(action=action),
                self.assertRaises((ValueError, TypeError)),
            ):
                GRC9V4APCOperation.replay(canonical_json_bytes(data))
        owner = GRC9V4APCOperation(self.seed)
        with patch.object(
            GRC9V4APCExpansion,
            "carrier_archive_payload",
            side_effect=ValueError("late archive failure"),
        ):
            self.assertRollback(owner, self.request, stage="commit")
        self.assertEqual(owner.carrier_archives, ())

    def test_native_source_and_twenty_target_steps_and_exact_archive_stage(self):
        r = self.record
        inputs = replace(
            self.seed.inputs,
            current=authority(r["initial"]["current"]),
            reset=authority(r["initial"]["reset"]),
            step_index=0,
            time=0,
        )
        inputs = role_inputs(inputs, inputs.current)
        step, _proof = checked(inputs, self.seed.differential_reference)
        limits = {
            "C": oracle.RESOURCE_ERROR,
            "W_A": oracle.HISTORY_ERROR,
            "Z_4": oracle.CARRIER_ERROR,
            "current": oracle.CURRENT_ERROR,
            "baseline": oracle.CURRENT_ERROR,
            "H": oracle.GEOMETRY_ERROR,
            "source": oracle.SOURCE_ERROR,
        }
        for key, limit in limits.items():
            self.assertClose(outputs(step)[key], r["source_step"][key], limit)
        actual = GRC9V4APCState(
            replace(step.next_inputs, dt=0), self.seed.specialization
        )
        owner = GRC9V4APCOperation(actual)
        self.assertTrue(owner.expand(request_for(actual, self.request)).committed)
        content = owner.carrier_archives[0]["history_content"]["content"]
        self.assertEqual(
            tuple(content), actual.inputs.current.Z_4 + actual.inputs.reset.Z_4
        )
        # The read-only probe has a distinct hypothetical writer output, never archived.
        hypothetical = pc.ProvisionalCandidatePCStep(
            replace(actual.inputs, dt=oracle.DT), actual.differential_reference
        )
        self.assertNotEqual(tuple(content[:81]), hypothetical.next_inputs.current.Z_4)
        for role in ("current", "reset"):
            state = self.owner.state
            inputs = role_inputs(state.inputs, getattr(state.inputs, role))
            for index in range(10):
                step, _ = checked(inputs, state.differential_reference)
                for key, limit in limits.items():
                    self.assertClose(
                        outputs(step)[key], r["continuation"][role][index][key], limit
                    )
                inputs = step.next_inputs
            step, _ = checked(inputs, state.differential_reference)
            for key, limit in limits.items():
                self.assertClose(
                    outputs(step)[key],
                    r["continuation"][role][-1]["final_read"][key],
                    limit,
                )

    def test_event_admission_runs_neither_W_nor_Z_writer(self):
        with (
            patch.object(
                native,
                "ProvisionalCandidatePCStep",
                wraps=pc.ProvisionalCandidatePCStep,
            ) as zero,
            patch.object(
                pc, "CandidateAWriter", side_effect=AssertionError("event W write")
            ),
            patch.object(pc, "scalar_zoh", side_effect=AssertionError("event Z write")),
        ):
            owner = GRC9V4APCOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)
            self.assertTrue(all(call.args[0].dt == 0 for call in zero.call_args_list))
        self.assertEqual(owner.state.inputs.step_index, self.seed.inputs.step_index)
        self.assertEqual(owner.state.inputs.time, self.seed.inputs.time)
        for role in ("current", "reset"):
            self.assertEqual(getattr(owner.state.inputs, role).Z_4, (0.0,) * 256)

    def test_both_carrier_roles_are_bound_in_request_and_loss_is_separate(self):
        owner = GRC9V4APCOperation(self.seed)
        for role in ("current", "reset"):
            values = [
                authority_payload(self.seed.inputs.current),
                authority_payload(self.seed.inputs.reset),
            ]
            values[role == "reset"]["Z_4"][0] += 2**-20
            data = self.request.to_payload()
            data["history_policy"] = oracle.history_policy(*values)
            self.assertRollback(
                owner, GRC9V4ExpansionRequestInput.from_payload(data), stage="admission"
            )
        for channel, key, value in [
            ("carrier", "information_loss", "none"),
            ("carrier", "target_initializer_id", "partial_preservation"),
            ("carrier", "disposition", "exact_transport"),
            ("candidate", "information_loss", "carrier_history_loss"),
        ]:
            data = self.request.to_payload()
            policy = data["history_policy"]
            policy[channel][key] = value
            with self.subTest(channel=channel, key=key):
                try:
                    policy[channel + "_history_policy_digest"] = payload_identity(
                        "history_channel_policy_identity_payload",
                        {
                            "schema_version": "grcv4-history-channel-policy-identity-v1",
                            "policy": policy[channel],
                        },
                    )
                    req = GRC9V4ExpansionRequestInput.from_payload(data)
                except (ValueError, TypeError):
                    continue
                self.assertRollback(owner, req, stage="admission")

    def test_target_whole_chart_rejection_both_roles_even_when_points_regular(self):
        # The target has a larger W chart than actual entry W. Increase its
        # declared resource radius: regular point solves do not grant a certificate.
        original = GRC9V4APCExpansion.__post_init__

        def oversized(target):
            original(target)
            ref = target.target
            params = ref.profile.params_resolved.to_payload()
            ident = ref.profile.identity_payload.to_payload()
            params["realization"]["source_envelope_id"] = pc.PCBaseChart(
                64, 0.5, 513 / 512
            ).identity
            ident["params_hash"] = payload_identity("resolved_params", params)
            object.__setattr__(
                target, "target", replace(ref, profile=resolve_profile(params, ident))
            )

        owner = GRC9V4APCOperation(self.seed)
        with patch.object(GRC9V4APCExpansion, "__post_init__", oversized):
            failure = self.assertRollback(
                owner, self.request, stage="target_readmission"
            )
        self.assertIn("source envelope", failure.failure.message)
        # Actual bad authority in current-only/reset-only targets rejects atomically.
        transfer = GRC9V4APCExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4APCOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                out = transfer(target, state)
                return (
                    replace(out, W_A=(0.49, *out.W_A[1:])) if state == chosen else out
                )

            with patch.object(GRC9V4APCExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, stage="target_readmission")

    def test_admitted_negative_continuation_rejects_physical_step_both_roles(self):
        negative = authority(
            self.record["boundary_witnesses"]["admitted_event_negative_next_step"][
                "source_role"
            ]
        )
        for role in ("current", "reset"):
            seed = altered_role(self.seed, role, negative)
            owner = GRC9V4APCOperation(seed)
            self.assertTrue(owner.expand(request_for(seed, self.request)).committed)
            before = owner.checkpoint()
            target = owner.state
            inputs = role_inputs(target.inputs, getattr(target.inputs, role))
            high = oracle.IntervalRows(
                oracle.model_for(target.differential_reference.port_graph.to_payload())
            )
            read = high.read(
                "A",
                oracle.vector(inputs.current.C),
                oracle.vector(inputs.current.W_A),
                high.I,
            )
            after = (
                oracle.vector(inputs.current.C)
                - oracle.number(oracle.DT) * high.B * read["J"]
            )
            self.assertLess(min(oracle.endpoint(x, 1) for x in after), 0)
            with self.assertRaises(ResourceBoundaryError) as error:
                pc.ProvisionalCandidatePCStep(inputs, target.differential_reference)
            self.assertEqual(error.exception.stage, "charge_admission")
            self.assertEqual(owner.checkpoint(), before)

    def test_whole_chart_exact_bound_and_closed_replay_without_WLS(self):
        for state in (self.seed, self.owner.state):
            backend = state.differential_reference
            with patch.object(
                candidate.CandidateADifferentialReference,
                "from_payload",
                side_effect=AssertionError("WLS substitution"),
            ):
                step = pc.ProvisionalCandidatePCStep(
                    replace(state.inputs, dt=oracle.DT), backend
                )
                replay = pc.ProvisionalCandidatePCStep.from_payload(step.to_payload())
                self.assertEqual(replay.to_payload(), step.to_payload())
                self.assertEqual(replay.next_inputs, step.next_inputs)
                point = step.read.point
                self.assertEqual(
                    candidate.CandidateACurrent.from_payload(
                        point.to_payload()
                    ).to_payload(),
                    point.to_payload(),
                )
            proof = oracle.whole_chart(backend.port_graph.to_payload())
            bounds = step.read.certificate.bounds
            for native_key, oracle_key in [
                ("source_norm_upper", "source_frobenius_upper"),
                ("current_norm_upper", "current_norm_upper"),
                ("hodge_lower", "hodge_lower"),
                ("descriptor_norm_upper", "descriptor_norm_upper"),
            ]:
                self.assertLessEqual(
                    abs(float(Q(bounds[native_key])) - float(Q(proof[oracle_key]))),
                    2**-38,
                )
            self.assertNotIn(
                state.inputs.geometry.reference.profile.complete_profile_id,
                list_supported_profiles(),
            )
            data = step.to_payload()
            data["differential_reference"]["read_weights"] = "reference_W"
            with self.assertRaises(ValueError):
                pc.ProvisionalCandidatePCStep.from_payload(data)

    def test_no_sampled_row_or_cached_W_enters_uniform_descriptor_bound(self):
        backend = self.seed.differential_reference
        for kind in (
            (ExactBackend.PYTHON, ExactBackend.FLINT)
            if importlib.util.find_spec("flint")
            else (ExactBackend.PYTHON,)
        ):
            with (
                exact_backend(kind),
                patch.object(
                    GRC9V4CandidateADifferentialReference,
                    "rebuild",
                    side_effect=AssertionError("sampled row"),
                ),
                patch.object(
                    GRC9V4CandidateADifferentialReference,
                    "rebuild_exact",
                    side_effect=AssertionError("sampled exact row"),
                ),
            ):
                bound = pc._descriptor_bound(backend, exact_number(16))
                self.assertTrue(is_exact(bound))
                self.assertGreaterEqual(bound**2, exact_number(6 * 16**2))
                for w in (0.5, 1.0, 513 / 512):
                    s = replace(self.seed.inputs.current, W_A=(w,) * 9)
                    certificate = pc.PCEnvelopeCertificate(
                        role_inputs(self.seed.inputs, s, dt=0), backend
                    )
                    self.assertLess(
                        float(Q(certificate.bounds["source_norm_upper"])), oracle.RADIUS
                    )

    def test_PC_fixture_does_not_automatically_admit_the_composite_chart(self):
        from tests.models.test_grc_v4_cipc import configure as composite

        # PC admission alone does not prove a uniform source envelope on the
        # wider composite geometry chart; its original kappa is unchanged.
        inputs = composite(self.seed.inputs, domain_radius=0.25)
        with self.assertRaisesRegex(pc.PCStageError, "source envelope"):
            pc.PCEnvelopeCertificate(inputs, self.seed.differential_reference)

    def test_carrier_sphere_support_boundary_and_stale_geometry(self):
        state = self.owner.state
        inputs = state.inputs
        m = len(inputs.current.W_A)
        z = [0.0] * (m * m)
        z[0] = oracle.RADIUS
        authority_good = replace(inputs.current, Z_4=tuple(z))
        pc.CandidatePCRead(
            role_inputs(inputs, authority_good, dt=0), state.differential_reference
        )
        bad = list(z)
        bad[0] = np.nextafter(float(oracle.RADIUS), np.inf)
        with self.assertRaises(pc.PCStageError):
            pc.CandidatePCRead(
                role_inputs(inputs, replace(authority_good, Z_4=tuple(bad)), dt=0),
                state.differential_reference,
            )
        with self.assertRaises(ValueError):
            GRC9V4APCState(
                replace(inputs, current=authority_good), state.specialization
            )
        bad = list(z)
        bad[1] = 2**-20
        with self.assertRaises(ValueError):
            pc.CandidatePCRead(
                role_inputs(inputs, replace(authority_good, Z_4=tuple(bad)), dt=0),
                state.differential_reference,
            )
        for role in ("current", "reset"):
            with self.assertRaises((ValueError, TypeError)):
                GRC9V4APCOperation(
                    altered_role(
                        self.seed,
                        role,
                        replace(getattr(self.seed.inputs, role), Z_4=None),
                    )
                )

    def test_native_effects_clear_all_twenty_four_full_error_ULP_controls(self):
        effects = native_effects(self.seed, self.owner.state)
        self.assertEqual(len(effects), 24)
        self.assertGreater(min(x["minimum_margin_ratio"] for x in effects), 1)

    def test_signed_permutations_covary_W_Z_geometry_and_source(self):
        for name, state in (("source", self.seed), ("target", self.owner.state)):
            g = state.differential_reference.port_graph.to_payload()
            values = state.inputs.current
            base = outputs(
                pc.ProvisionalCandidatePCStep(
                    replace(state.inputs, dt=oracle.DT), state.differential_reference
                )
            )
            m = len(g["edges"])
            for offset in (0, 1, 3):
                order = list(range(offset, m)) + list(range(offset))
                sign = np.array([-1 if i % 2 else 1 for i in order])
                moved = deepcopy(g)
                moved["edges"] = [deepcopy(g["edges"][i]) for i in order]
                for edge, sigma in zip(moved["edges"], sign, strict=True):
                    if sigma < 0:
                        edge["tail"], edge["head"] = edge["head"], edge["tail"]

                def tensor(x, m=m, order=order, sign=sign):
                    return (
                        np.asarray(x).reshape(m, m)[np.ix_(order, order)]
                        * sign[:, None]
                        * sign[None, :]
                    )

                ref = oracle.reference(moved)
                authority_moved = replace(
                    values,
                    W_A=tuple(values.W_A[i] for i in order),
                    Z_4=tuple(
                        float(x) if x else 0.0 for x in tensor(values.Z_4).reshape(-1)
                    ),
                )
                inputs = replace(
                    state.inputs,
                    geometry=ref.geometry(),
                    current=authority_moved,
                    reset=authority_moved,
                )
                backend = GRC9V4CandidateADifferentialReference(ref.graph.port_graph)
                step, _ = checked(role_inputs(inputs, authority_moved), backend)
                out = outputs(step)
                self.assertClose(out["C"], base["C"], oracle.RESOURCE_ERROR)
                self.assertClose(
                    out["W_A"], np.asarray(base["W_A"])[order], oracle.HISTORY_ERROR
                )
                self.assertClose(
                    out["current"],
                    np.asarray(base["current"])[order] * sign,
                    oracle.CURRENT_ERROR,
                )
                for field in ("Z_4", "H", "source"):
                    self.assertClose(
                        np.asarray(out[field]).reshape(m, m),
                        tensor(base[field]),
                        oracle.CARRIER_ERROR
                        if field == "Z_4"
                        else oracle.GEOMETRY_ERROR,
                    )


if __name__ == "__main__":
    unittest.main()
