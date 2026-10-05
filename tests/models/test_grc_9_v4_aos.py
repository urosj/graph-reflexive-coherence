"""Native A_OS pressure against the accepted, immutable A.1 expectations."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import numpy as np

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_v4_candidate_a as candidate
from pygrc.models.grc_9_v4_expansion import (
    GRC9V4AOSExpansion,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_9_v4_lifecycle import (
    GRC9V4AOSOperation,
    GRC9V4AOSState,
    GRC9V4Specialization,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4CandidateADifferentialReference,
    GRC9V4PortGraph,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import ExactBackend, current_exact_backend, exact_backend
from pygrc.models.grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4ReferenceGeometry,
    VertexScalar,
)
from pygrc.models.grc_v4_profile import list_supported_profiles
from pygrc.models.grc_v4_realizations import CandidateAOSPass
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ProvisionalCandidateAOSStep

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "implementation/phase-9-grcv4/verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))
if importlib.util.find_spec("mpmath") is None:
    raise unittest.SkipTest(
        "A.2 interval pressure requires research dependency mpmath==1.3.0"
    )
import verify_p983a_aos_oracle as oracle

RECORD = ROOT / oracle.RECORD
ORACLE_SHA = "ce7f4ae309d9256d93ce7d96f10073e4380f92b26a9af548df1269f98507a06e"


def authority(value):
    return GRCV4AuthoritativeState(tuple(value["C"]), tuple(value["W_A"]), None)


def authority_payload(state):
    return {"C": list(state.C), "W_A": list(state.W_A), "Z_4": None}


def fixture(record):
    r = record
    reference = GRCV4ReferenceGeometry.from_payload(r["source"]["reference"])
    spec = GRC9V4Specialization(
        FrozenJSONMap(r["specialization"]["resolved"]),
        FrozenJSONMap(r["specialization"]["identity_payload"]),
    )
    inputs = GeometryStageInputs(
        reference.geometry(),
        reference.context,
        authority(r["source"]["current"]),
        authority(r["source"]["reset"]),
        "aos-seed",
        30.140625,
        (),
        1,
        oracle.DT,
        0,
        "pre_read",
        0,
        None,
    )
    return GRC9V4AOSState(inputs, spec), GRC9V4ExpansionRequestInput.from_payload(
        r["request"]
    )


def request_for(state, original):
    # Compute altered fixture declarations independently of the native policy helper.
    data = original.to_payload()
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


def outputs(step):
    p = step.os_pass
    assert p is not None
    return {
        "C": step.next_inputs.current.C,
        "W_A": step.next_inputs.current.W_A,
        "current": p.corrector.current.values,
        "baseline": p.corrector.baseline.values,
        "H": p.residual.geometry.one_form_hodge.matrix,
        "regenerated": p.residual.regenerated.one_form_hodge.matrix,
    }


class NativeAOSPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert hashlib.sha256(RECORD.read_bytes()).hexdigest() == ORACLE_SHA
        cls.record = json.loads(RECORD.read_text())
        cls.seed, cls.request = fixture(cls.record)
        cls.owner = GRC9V4AOSOperation(cls.seed)
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
            GRC9V4AOSOperation.replay(owner.checkpoint()).checkpoint(),
            owner.checkpoint(),
        )

    def test_native_source_beat_and_both_ten_step_continuations(self):
        r = self.record
        initial = replace(
            self.seed.inputs,
            current=authority(r["initial"]["current"]),
            reset=authority(r["initial"]["reset"]),
            step_index=0,
            time=0,
            dt=oracle.DT,
        )
        step = ProvisionalCandidateAOSStep(initial, self.seed.differential_reference)
        oracle.check_step(
            r["source"]["port_graph"],
            initial.current.C,
            initial.current.W_A,
            outputs(step),
        )
        for key, limit in [
            ("C", oracle.RESOURCE_ERROR),
            ("W_A", oracle.HISTORY_ERROR),
            ("current", oracle.CURRENT_ERROR),
            ("H", oracle.HISTORY_ERROR),
        ]:
            self.assertClose(outputs(step)[key], r["source_step"][key], limit)
        # Actual ordinary output owns its own source/event identities, even if rounding differs.
        actual = GRC9V4AOSState(
            replace(step.next_inputs, dt=0), self.seed.specialization
        )
        actual_owner = GRC9V4AOSOperation(actual)
        self.assertTrue(
            actual_owner.expand(request_for(actual, self.request)).committed
        )
        for role in ("current", "reset"):
            inputs = replace(
                self.owner.state.inputs,
                current=getattr(self.owner.state.inputs, role),
                dt=oracle.DT,
            )
            graph = inputs.geometry.reference.graph.port_graph.to_payload()
            for index in range(10):
                saved = inputs.current
                step = ProvisionalCandidateAOSStep(
                    inputs, self.owner.state.differential_reference
                )
                observed = outputs(step)
                oracle.check_step(graph, saved.C, saved.W_A, observed)
                expected = r["continuation"][role][index]
                for key, limit in [
                    ("C", oracle.RESOURCE_ERROR),
                    ("W_A", oracle.HISTORY_ERROR),
                    ("current", oracle.CURRENT_ERROR),
                    ("baseline", oracle.CURRENT_ERROR),
                    ("H", oracle.HISTORY_ERROR),
                    ("regenerated", oracle.HISTORY_ERROR),
                ]:
                    self.assertClose(observed[key], expected[key], limit)
                inputs = step.next_inputs
            final = CandidateAOSPass(inputs, self.owner.state.differential_reference)
            self.assertClose(
                final.corrector.current.values,
                r["continuation"][role][-1]["final_read"]["current"],
                oracle.CURRENT_ERROR,
            )
            self.assertGreater(min(inputs.current.C), 0)
            self.assertGreater(min(inputs.current.W_A), 0)

    def test_real_target_split_rejects_current_only_and_reset_only(self):
        negative = authority(
            self.record["rejection_expectations"]["target_split"]["source_role"]
        )
        for role in ("current", "reset"):
            with self.subTest(role=role):
                seed = replace(
                    self.seed, inputs=replace(self.seed.inputs, **{role: negative})
                )
                owner = GRC9V4AOSOperation(seed)  # source's complete OS surfaces pass
                request = request_for(seed, self.request)
                result = self.assertRollback(owner, request, stage="target_readmission")
                self.assertIn("split tolerance", result.failure.message)

    def test_event_admission_never_advances_or_runs_a_writer(self):
        with (
            patch.object(
                native, "ProvisionalCandidateAOSStep", wraps=ProvisionalCandidateAOSStep
            ) as zero,
            patch(
                "pygrc.models.grc_v4_step.CandidateAWriter",
                side_effect=AssertionError("event writer"),
            ),
        ):
            owner = GRC9V4AOSOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)
            self.assertTrue(all(call.args[0].dt == 0 for call in zero.call_args_list))
        self.assertNotEqual(self.seed.inputs.current.W_A, self.seed.inputs.reset.W_A)
        self.assertNotEqual(
            self.record["source_step"]["current"],
            self.record["source_reference_reads"]["current"]["current"],
        )

    def test_policy_rehashed_role_substitutions_fail_at_admission(self):
        owner = GRC9V4AOSOperation(self.seed)
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
        original = GRC9V4AOSExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4AOSOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                value = original(target, state)
                return (
                    replace(value, C=(value.C[0] + 1, *value.C[1:]))
                    if state == chosen
                    else value
                )

            with patch.object(GRC9V4AOSExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, stage="target_readmission")
        owner = GRC9V4AOSOperation(self.seed)
        with patch.object(
            native,
            "make_commit_receipts",
            side_effect=ValueError("late receipt failure"),
        ):
            self.assertRollback(owner, self.request, stage="commit")
        with patch.object(
            GRC9V4AOSExpansion,
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
                GRC9V4AOSOperation.replay(canonical_json_bytes(data))
        data = json.loads(self.committed)
        data["reference_currents"][0]["roles"]["current"] = data["reference_currents"][
            0
        ]["roles"]["reset"]
        with self.assertRaises(ValueError):
            GRC9V4AOSOperation.replay(canonical_json_bytes(data))

    def test_closed_descriptor_identity_roundtrip_and_wls_separation(self):
        for part in ("source", "target"):
            payload = self.record[part]["descriptor"]
            backend = GRC9V4CandidateADifferentialReference.from_payload(payload)
            self.assertEqual(backend.to_payload(), payload)
            self.assertEqual(
                candidate.candidate_a_differential_from_payload(payload), backend
            )
            with self.assertRaises(ValueError):
                candidate.CandidateADifferentialReference.from_payload(payload)
            for field in payload.keys() - {"port_graph"}:
                changed = deepcopy(payload)
                changed[field] = "wrong"
                with self.subTest(field=field), self.assertRaises(ValueError):
                    GRC9V4CandidateADifferentialReference.from_payload(changed)
            self.assertNotIn(
                self.record[part]["reference"]["profile"]["complete_profile_id"],
                list_supported_profiles(),
            )
        point = candidate.CandidateACurrent(
            self.seed.inputs, self.seed.differential_reference
        )
        self.assertEqual(
            candidate.CandidateACurrent.from_payload(point.to_payload()).to_payload(),
            point.to_payload(),
        )
        passed = CandidateAOSPass(
            replace(self.seed.inputs, dt=oracle.DT), self.seed.differential_reference
        )
        self.assertEqual(
            CandidateAOSPass.from_payload(passed.to_payload()).to_payload(),
            passed.to_payload(),
        )
        step = ProvisionalCandidateAOSStep(
            replace(self.seed.inputs, dt=oracle.DT), self.seed.differential_reference
        )
        self.assertEqual(
            ProvisionalCandidateAOSStep.from_payload(step.to_payload()).next_inputs,
            step.next_inputs,
        )

    def test_writer_uses_incoming_W_fresh_C_and_selected_current(self):
        state = self.owner.state
        before = replace(state.inputs, dt=oracle.DT)
        real = GRC9V4CandidateADifferentialReference.rebuild
        calls = []

        def observe(backend, c, w):
            calls.append((c.values, w))
            return real(backend, c, w)

        with patch.object(GRC9V4CandidateADifferentialReference, "rebuild", observe):
            step = ProvisionalCandidateAOSStep(before, state.differential_reference)
        self.assertIn((step.resource.provisional_state.C, before.current.W_A), calls)
        self.assertNotEqual(before.current.W_A, step.next_inputs.current.W_A)
        self.assertIn((step.next_inputs.current.C, step.next_inputs.current.W_A), calls)
        paper = oracle.PaperAOS(self.record["target"]["port_graph"])
        self.assertClose(
            step.writer.W_drv_A,
            list(
                map(
                    float,
                    paper.conductance(
                        step.resource.provisional_state.C,
                        before.current.W_A,
                        step.os_pass.corrector.current.values,
                    ),
                )
            ),
            oracle.HISTORY_ERROR,
        )

    def test_duplicate_concurrent_event_publishes_only_once(self):
        owner = GRC9V4AOSOperation(self.seed)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(len(owner.receipts), 4)
        self.assertEqual(owner.checkpoint(), self.committed)

    def test_receiver_owns_exact_backend_across_context_changes(self):
        if importlib.util.find_spec("flint") is None:
            self.skipTest("cross-backend ownership requires optional v4-flint")
        owner = GRC9V4AOSOperation(self.seed)
        captured = current_exact_backend()
        other = (
            ExactBackend.PYTHON
            if captured != ExactBackend.PYTHON
            else ExactBackend.FLINT
        )
        seen = []
        real = native._aos_readmit

        def observe(state):
            seen.append(current_exact_backend())
            return real(state)

        with exact_backend(other), patch.object(native, "_aos_readmit", observe):
            self.assertTrue(owner.expand(self.request).committed)
        self.assertTrue(seen)
        self.assertEqual(set(seen), {captured})

    def test_native_equations_covary_under_signed_edge_permutations(self):
        for part in ("source", "target"):
            graph = self.record[part]["port_graph"]
            values = (
                self.record["source"]["current"]
                if part == "source"
                else self.record["target"]["roles"]["current"]["authoritative"]
            )
            base = oracle.PaperAOS(graph).step(values["C"], values["W_A"])
            n = len(graph["edges"])
            for reverse, reorder in ((True, False), (False, True), (True, True)):
                permutation = list(reversed(range(n))) if reorder else list(range(n))
                changed = deepcopy(graph)
                changed["edges"] = [deepcopy(graph["edges"][i]) for i in permutation]
                signs = [-1 if reverse and i % 2 == 0 else 1 for i in permutation]
                for edge, sign in zip(changed["edges"], signs):
                    if sign < 0:
                        edge["tail"], edge["head"] = edge["head"], edge["tail"]
                ref = oracle.reference(changed)
                state = GRCV4AuthoritativeState(
                    tuple(values["C"]),
                    tuple(values["W_A"][i] for i in permutation),
                    None,
                )
                inputs = replace(
                    self.seed.inputs,
                    geometry=ref.geometry(),
                    current=state,
                    reset=state,
                    dt=oracle.DT,
                )
                backend = GRC9V4CandidateADifferentialReference(ref.graph.port_graph)
                step = ProvisionalCandidateAOSStep(inputs, backend)
                observed = outputs(step)
                oracle.check_step(changed, state.C, state.W_A, observed)
                self.assertClose(observed["C"], base["C"], oracle.RESOURCE_ERROR)
                self.assertClose(
                    observed["W_A"],
                    [base["W_A"][i] for i in permutation],
                    oracle.HISTORY_ERROR,
                )
                self.assertClose(
                    observed["current"],
                    [base["current"][i] * sign for i, sign in zip(permutation, signs)],
                    oracle.CURRENT_ERROR,
                )

    def test_descriptor_extremes_empty_rows_loops_and_explicit_weights(self):
        graph = GRC9V4PortGraph.from_payload(
            {
                "schema_version": "grc9v4-port-graph-v1",
                "live_node_ids": ["a", "b", "isolated"],
                "edges": [
                    {
                        "edge_id": "link",
                        "kind": "boundary",
                        "tail": {"node_id": "a", "port": 1},
                        "head": {"node_id": "b", "port": 9},
                    },
                    {
                        "edge_id": "loop",
                        "kind": "spine",
                        "tail": {"node_id": "a", "port": 2},
                        "head": {"node_id": "a", "port": 4},
                    },
                ],
            }
        )
        backend = GRC9V4CandidateADifferentialReference(graph)
        resource = VertexScalar(backend.graph, (1.0, 3.0, 7.0))
        backends = [ExactBackend.PYTHON]
        if importlib.util.find_spec("flint") is not None:
            backends.append(ExactBackend.FLINT)
        for kind in backends:
            with exact_backend(kind):
                for weights in (
                    (5e-324, 5e-324),
                    (1e308, 1e308),
                    (5e-324, 1e308),
                    (0.25, 1.0),
                ):
                    expected = float(
                        2
                        * Fraction(weights[0])
                        / (Fraction(weights[0]) + Fraction(weights[1]))
                    )
                    self.assertEqual(
                        backend.rebuild(resource, weights),
                        ((expected, 0.0, 0.0), (0.0, 0.0, -2.0), (0.0, 0.0, 0.0)),
                    )
        for weights in (
            (0.0, 1.0),
            (-0.0, 1.0),
            (-1.0, 1.0),
            (float("nan"), 1.0),
            (float("inf"), 1.0),
            (1.0,),
            (True, 1.0),
        ):
            with (
                self.subTest(weights=weights),
                self.assertRaises((ValueError, TypeError)),
            ):
                backend.rebuild(resource, weights)
        with self.assertRaises(TypeError):
            backend.rebuild(resource)  # no cached/default weight authority

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
                GRC9V4AOSOperation.replay(canonical_json_bytes(data))
        seed = replace(self.seed, inputs=replace(self.seed.inputs, step_index=0))
        owner = GRC9V4AOSOperation(seed)
        result = self.assertRollback(
            owner, request_for(seed, self.request), stage="admission"
        )
        self.assertIn("postbeat", result.failure.message)
        with self.assertRaises(ValueError):
            inputs = replace(
                self.seed.inputs,
                current=replace(self.seed.inputs.current, Z_4=(0.0,) * 81),
            )
            GRC9V4AOSOperation(replace(self.seed, inputs=inputs))

    def test_A2_authorization_is_exact_and_cannot_replace_accepted_oracle(self):
        import phase9_specialization_acceptance as entry

        self.assertEqual(entry.aos_authorization(ROOT), "P9-8.3A.2")
        for path in entry.AOS_PATHS:
            self.assertTrue(entry.aos_permitted(path, "P9-8.3A.2"))
            self.assertFalse(entry.aos_permitted(path, "P9-8.3A.1"))
        for path in (
            "specs/grc-9-v4-spec.md",
            "src/pygrc/models/grc_9_v3.py",
            "src/pygrc/models/grc_v4_ci.py",
        ):
            self.assertFalse(entry.aos_permitted(path, "P9-8.3A.2"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.aos_authorization(ROOT)
        bad = dict(entry.AOS_PREDECESSOR_HASHES)
        bad[oracle.RECORD] = "0" * 64
        with (
            patch.object(entry, "AOS_PREDECESSOR_HASHES", bad),
            self.assertRaises(ValueError),
        ):
            entry.aos_authorization(ROOT)


if __name__ == "__main__":
    unittest.main()
