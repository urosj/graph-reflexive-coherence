"""Native A_CI pressure against the accepted, immutable A.1 expectations."""

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
from pygrc.models import grc_v4_ci as ci
from pygrc.models.grc_9_v4_expansion import (
    GRC9V4ACIExpansion,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_9_v4_lifecycle import (
    GRC9V4ACIOperation,
    GRC9V4ACIState,
    GRC9V4Specialization,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4CandidateADifferentialReference,
    GRC9V4PortGraph,
)
from pygrc.models.grc_v4_ci import (
    CandidateCIRoot,
    CIStageError,
    ProvisionalCandidateCIStep,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import (
    ExactBackend,
    current_exact_backend,
    exact_backend,
    exact_number,
    integer_ratio,
    is_exact,
)
from pygrc.models.grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4ReferenceGeometry,
    PhysicalFlux,
    VertexScalar,
)
from pygrc.models.grc_v4_profile import list_supported_profiles
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_v4_ci import configure

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "implementation/phase-9-grcv4/verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))
if importlib.util.find_spec("mpmath") is None:
    raise unittest.SkipTest(
        "A.2 interval pressure requires research dependency mpmath==1.3.0"
    )
import verify_p983a_aci_oracle as oracle

RECORD = ROOT / oracle.RECORD
ORACLE_SHA = "846e491b8eaa637ebcdac0a049a26f2192bf1054f0e341af0a8a9e51f70ebb44"


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
        "aci-seed",
        30.140625,
        (),
        1,
        oracle.DT,
        0,
        "pre_read",
        0,
        None,
    )
    return GRC9V4ACIState(inputs, spec), GRC9V4ExpansionRequestInput.from_payload(
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
    root = step.root
    return {
        "C": step.next_inputs.current.C,
        "W_A": step.next_inputs.current.W_A,
        "current": root.current.values,
        "baseline": root.selected.point.baseline.values,
        "H": root.selected.inputs.geometry.one_form_hodge.matrix,
        "source": root.selected.structural_source.increment,
    }


def native_effects(seed, target):
    """Native controls compared with independent full-formula interval bounds."""
    results = []
    for label, state in (("source", seed), ("target", target)):
        graph = state.inputs.geometry.reference.graph.port_graph.to_payload()
        for role in ("current", "reset"):
            inputs = replace(
                state.inputs, current=getattr(state.inputs, role), dt=oracle.DT
            )
            c, w = tuple(inputs.current.C), tuple(inputs.current.W_A)
            backend = state.differential_reference
            step = ProvisionalCandidateCIStep(inputs, backend)
            checked = oracle.check_step(graph, c, w, outputs(step))
            truth = checked["truth"]
            high = truth["high"]
            selected = step.root.selected
            # Fixed selected H controls, with independently declared changed laws.
            for channel, changes in (
                ("geometry", {"kappa_Ah": 0}),
                ("feedback", {"chi_A": 0}),
            ):
                alternate = configure(
                    inputs,
                    radius=oracle.RADIUS,
                    gain=0.5,
                    tolerance=oracle.TOLERANCE,
                    changes={"candidate": changes},
                )
                geometry = replace(
                    selected.inputs.geometry, reference=alternate.geometry.reference
                )
                point = candidate.CandidateACurrent(
                    replace(selected.inputs, geometry=geometry), backend
                )
                exact = high.read(
                    "A", truth["c"], truth["w"], truth["H"], **{channel: False}
                )
                results.append(
                    {
                        "graph": label,
                        "role": role,
                        "effect": channel,
                        **oracle.separation(
                            step.root.current.values,
                            point.current.values,
                            truth["read"]["J"],
                            exact["J"],
                        ),
                    }
                )
            off_inputs = configure(
                inputs, radius=oracle.RADIUS, gain=0, tolerance=oracle.TOLERANCE
            )
            off = CandidateCIRoot(off_inputs, backend)
            exact = high.read("A", truth["c"], truth["w"], high.I)
            results.append(
                {
                    "graph": label,
                    "role": role,
                    "effect": "entire_root_source_off",
                    **oracle.separation(
                        step.root.current.values,
                        off.current.values,
                        truth["read"]["J"],
                        exact["J"],
                    ),
                }
            )
            if label != "target":
                continue
            point = selected.point
            params = inputs.geometry.reference.profile.params_resolved.candidate
            for name, resources, flux, exact_c, exact_j in (
                (
                    "stale_resource_writer",
                    c,
                    step.root.current,
                    truth["c"],
                    truth["read"]["J"],
                ),
                (
                    "baseline_current_writer",
                    step.resource.provisional_state.C,
                    point.baseline,
                    checked["C"],
                    truth["read"]["baseline"],
                ),
            ):
                field = VertexScalar(backend.graph, resources)
                drive = candidate._conductance(
                    backend.graph, params, field, backend.rebuild(field, w), flux
                )
                wrong = candidate.candidate_a_log_interpolation(w, drive, oracle.DT, 1)
                exact = high.write(exact_c, truth["w"], exact_j)
                results.append(
                    {
                        "graph": label,
                        "role": role,
                        "effect": name,
                        **oracle.separation(
                            step.next_inputs.current.W_A, wrong, checked["W_A"], exact
                        ),
                    }
                )
            next_inputs = step.next_inputs
            new = CandidateCIRoot(next_inputs, backend)
            held = CandidateCIRoot(
                replace(next_inputs, current=replace(next_inputs.current, W_A=w)),
                backend,
            )
            # Independent roots own their respective represented next-C / W inputs.
            paper = oracle.PaperACI(graph)

            def root_truth(weights, paper=paper, next_inputs=next_inputs, graph=graph):
                observed = paper.step(next_inputs.current.C, weights)
                return oracle.check_step(
                    graph, next_inputs.current.C, weights, observed
                )["truth"]["read"]["J"]

            results.append(
                {
                    "graph": label,
                    "role": role,
                    "effect": "next_root_consumes_written_W",
                    **oracle.separation(
                        new.current.values,
                        held.current.values,
                        root_truth(next_inputs.current.W_A),
                        root_truth(w),
                    ),
                }
            )
    return results


def simplex_observations(seed, request):
    """Whole-ball interval evidence: event admission is not future positivity."""
    result = []
    for shares in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        owner = GRC9V4ACIOperation(seed)
        outcome = owner.expand(replace(request, resource_distribution=shares))
        oracle.require(outcome.committed, str(outcome.failure))
        graph = owner.state.differential_reference.port_graph.to_payload()
        high = oracle.IntervalRows(oracle.model_for(graph))
        size = len(graph["edges"])
        # This entrywise box encloses the entire declared Frobenius ball.
        box = oracle.IV.matrix(
            [
                [
                    oracle.IV.mpf(
                        [int(i == j) - oracle.RADIUS, int(i == j) + oracle.RADIUS]
                    )
                    if high.mask[i, j]
                    else oracle.number(0)
                    for j in range(size)
                ]
                for i in range(size)
            ]
        )
        checkpoint = owner.checkpoint()
        for role in ("current", "reset"):
            state = getattr(owner.state.inputs, role)
            oracle.require(min(state.C) == 0, "simplex event did not retain exact zero")
            oracle.require(
                sum(map(Fraction, state.C))
                == sum(map(Fraction, getattr(seed.inputs, role).C)),
                "simplex charge drift",
            )
            oracle.frobenius_domain(graph, state.C, state.W_A)
            read = high.read("A", oracle.vector(state.C), oracle.vector(state.W_A), box)
            after = (
                oracle.vector(state.C) - oracle.number(oracle.DT) * high.B * read["J"]
            )
            upper = min(oracle.endpoint(x, 1) for x in after)
            oracle.require(
                upper < 0, "negative future resource not independently certified"
            )
            inputs = replace(owner.state.inputs, current=state, dt=oracle.DT)
            try:
                ProvisionalCandidateCIStep(inputs, owner.state.differential_reference)
            except ResourceBoundaryError as exc:
                failure = {
                    "stage": exc.stage,
                    "code": exc.code,
                    "message": str(exc),
                }
            else:
                raise ValueError("native step admitted a certified negative resource")
            result.append(
                {
                    "shares": shares,
                    "role": role,
                    "negative_coordinate_upper": str(upper),
                    "step_failure": failure,
                    "checkpoint_unchanged": owner.checkpoint() == checkpoint,
                }
            )
    return result


class NativeACIPressure(unittest.TestCase):
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
        cls.owner = GRC9V4ACIOperation(cls.seed)
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
            GRC9V4ACIOperation.replay(owner.checkpoint()).checkpoint(),
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
        step = ProvisionalCandidateCIStep(initial, self.seed.differential_reference)
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
        actual = GRC9V4ACIState(
            replace(step.next_inputs, dt=0), self.seed.specialization
        )
        actual_owner = GRC9V4ACIOperation(actual)
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
                step = ProvisionalCandidateCIStep(
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
                    ("source", oracle.SOURCE_ERROR),
                ]:
                    self.assertClose(observed[key], expected[key], limit)
                inputs = step.next_inputs
            final = CandidateCIRoot(inputs, self.owner.state.differential_reference)
            self.assertClose(
                final.current.values,
                r["continuation"][role][-1]["final_read"]["current"],
                oracle.CURRENT_ERROR,
            )
            self.assertGreater(min(inputs.current.C), 0)
            self.assertGreater(min(inputs.current.W_A), 0)

    def test_real_target_domain_rejects_current_only_and_reset_only(self):
        negative = authority(
            self.record["rejection_expectations"]["target_domain"]["source_role"]
        )
        for role in ("current", "reset"):
            with self.subTest(role=role):
                seed = replace(
                    self.seed, inputs=replace(self.seed.inputs, **{role: negative})
                )
                owner = GRC9V4ACIOperation(seed)  # source's complete CI surfaces pass
                request = request_for(seed, self.request)
                result = self.assertRollback(owner, request, stage="target_readmission")
                self.assertIn("self-map", result.failure.message)

    def test_event_admission_never_advances_or_runs_a_writer(self):
        with (
            patch.object(
                native, "ProvisionalCandidateCIStep", wraps=ProvisionalCandidateCIStep
            ) as zero,
            patch(
                "pygrc.models.grc_v4_ci.CandidateAWriter",
                side_effect=AssertionError("event writer"),
            ),
        ):
            owner = GRC9V4ACIOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)
            self.assertTrue(all(call.args[0].dt == 0 for call in zero.call_args_list))
        self.assertNotEqual(self.seed.inputs.current.W_A, self.seed.inputs.reset.W_A)
        self.assertNotEqual(
            self.record["source_step"]["current"],
            self.record["source_reference_reads"]["current"]["current"],
        )

    def test_policy_rehashed_role_substitutions_fail_at_admission(self):
        owner = GRC9V4ACIOperation(self.seed)
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
        original = GRC9V4ACIExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4ACIOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                value = original(target, state)
                return (
                    replace(value, C=(value.C[0] + 1, *value.C[1:]))
                    if state == chosen
                    else value
                )

            with patch.object(GRC9V4ACIExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, stage="target_readmission")
        owner = GRC9V4ACIOperation(self.seed)
        with patch.object(
            native,
            "make_commit_receipts",
            side_effect=ValueError("late receipt failure"),
        ):
            self.assertRollback(owner, self.request, stage="commit")
        with patch.object(
            GRC9V4ACIExpansion,
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
                GRC9V4ACIOperation.replay(canonical_json_bytes(data))
        data = json.loads(self.committed)
        data["reference_currents"][0]["roles"]["current"] = data["reference_currents"][
            0
        ]["roles"]["reset"]
        with self.assertRaises(ValueError):
            GRC9V4ACIOperation.replay(canonical_json_bytes(data))

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
        passed = CandidateCIRoot(
            replace(self.seed.inputs, dt=oracle.DT), self.seed.differential_reference
        )
        self.assertEqual(
            CandidateCIRoot.from_payload(passed.to_payload()).to_payload(),
            passed.to_payload(),
        )
        step = ProvisionalCandidateCIStep(
            replace(self.seed.inputs, dt=oracle.DT), self.seed.differential_reference
        )
        self.assertEqual(
            ProvisionalCandidateCIStep.from_payload(step.to_payload()).next_inputs,
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
            step = ProvisionalCandidateCIStep(before, state.differential_reference)
        self.assertIn((step.resource.provisional_state.C, before.current.W_A), calls)
        self.assertNotEqual(before.current.W_A, step.next_inputs.current.W_A)
        self.assertIn((step.next_inputs.current.C, step.next_inputs.current.W_A), calls)
        paper = oracle.PaperACI(self.record["target"]["port_graph"])
        self.assertClose(
            step.writer.W_drv_A,
            list(
                map(
                    float,
                    paper.conductance(
                        step.resource.provisional_state.C,
                        before.current.W_A,
                        step.root.current.values,
                    ),
                )
            ),
            oracle.HISTORY_ERROR,
        )

    def test_duplicate_concurrent_event_publishes_only_once(self):
        owner = GRC9V4ACIOperation(self.seed)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(len(owner.receipts), 4)
        self.assertEqual(owner.checkpoint(), self.committed)

    def test_receiver_owns_exact_backend_across_context_changes(self):
        if importlib.util.find_spec("flint") is None:
            self.skipTest("cross-backend ownership requires optional v4-flint")
        owner = GRC9V4ACIOperation(self.seed)
        captured = current_exact_backend()
        other = (
            ExactBackend.PYTHON
            if captured != ExactBackend.PYTHON
            else ExactBackend.FLINT
        )
        seen = []
        real = native._aci_readmit

        def observe(state):
            seen.append(current_exact_backend())
            return real(state)

        with exact_backend(other), patch.object(native, "_aci_readmit", observe):
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
            base = oracle.PaperACI(graph).step(values["C"], values["W_A"])
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
                step = ProvisionalCandidateCIStep(inputs, backend)
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
                    exact = backend.rebuild_exact(resource, weights)
                    self.assertEqual(
                        Fraction(*integer_ratio(exact[0][0])),
                        2
                        * Fraction(weights[0])
                        / (Fraction(weights[0]) + Fraction(weights[1])),
                    )
                    self.assertGreater(exact[0][0], 0)
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
                GRC9V4ACIOperation.replay(canonical_json_bytes(data))
        seed = replace(self.seed, inputs=replace(self.seed.inputs, step_index=0))
        owner = GRC9V4ACIOperation(seed)
        result = self.assertRollback(
            owner, request_for(seed, self.request), stage="admission"
        )
        self.assertIn("postbeat", result.failure.message)
        with self.assertRaises(ValueError):
            inputs = replace(
                self.seed.inputs,
                current=replace(self.seed.inputs.current, Z_4=(0.0,) * 81),
            )
            GRC9V4ACIOperation(replace(self.seed, inputs=inputs))

    def test_A2_authorization_is_exact_and_cannot_replace_accepted_oracle(self):
        import phase9_specialization_acceptance as entry

        self.assertEqual(entry.aci_authorization(ROOT), "P9-8.3A.2")
        for path in entry.ACI_PATHS:
            self.assertTrue(entry.aci_permitted(path, "P9-8.3A.2"))
            self.assertFalse(entry.aci_permitted(path, "P9-8.3A.1"))
        for path in (
            "specs/grc-9-v4-spec.md",
            "src/pygrc/models/grc_9_v3.py",
            "src/pygrc/models/grc_v4_pc.py",
        ):
            self.assertFalse(entry.aci_permitted(path, "P9-8.3A.2"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.aci_authorization(ROOT)

        bad = dict(entry.ACI_ORACLE_HASHES)
        bad[oracle.RECORD] = "0" * 64
        with (
            patch.object(entry, "ACI_ORACLE_HASHES", bad),
            self.assertRaises(ValueError),
        ):
            entry.aci_authorization(ROOT)

    def test_exact_rows_feed_both_analytic_owners_without_rounded_descriptors(self):
        state = self.owner.state
        backend = state.differential_reference
        graph = backend.port_graph.to_payload()
        indices = {n: i for i, n in enumerate(graph["live_node_ids"])}
        observations = []
        for scale in (1, 0.25):
            w = list(state.inputs.current.W_A)
            w[0] *= scale
            authority = replace(state.inputs.current, W_A=tuple(w))
            inputs = replace(state.inputs, current=authority)
            point = candidate.CandidateACurrent(inputs, backend)
            expected = [[Fraction(0) for _ in range(3)] for _ in indices]
            denominators = deepcopy(expected)
            for e, weight in zip(graph["edges"], w):
                for end, other in ((e["tail"], e["head"]), (e["head"], e["tail"])):
                    i, j = indices[end["node_id"]], indices[other["node_id"]]
                    row = (end["port"] - 1) // 3
                    expected[i][row] += Fraction(weight) * (
                        Fraction(authority.C[j]) - Fraction(authority.C[i])
                    )
                    denominators[i][row] += Fraction(weight)
            expected = tuple(
                tuple(n / d if d else Fraction(0) for n, d in zip(row, den))
                for row, den in zip(expected, denominators)
            )
            actual = ci._a_descriptors_exact(point)
            self.assertTrue(all(is_exact(x) for row in actual for x in row))
            self.assertEqual(
                tuple(
                    tuple(Fraction(*integer_ratio(x)) for x in row) for row in actual
                ),
                expected,
            )
            observations.append(actual)
            # Both analytic owners must work without consulting rounded rows.
            with patch.object(
                GRC9V4CandidateADifferentialReference,
                "rebuild",
                side_effect=AssertionError("rounded analytic operand"),
            ):
                ci._analytic_residual(point, point.current)
                bounds = ci._a_read_bounds(
                    point, exact_number(oracle.RADIUS), 1 - exact_number(oracle.RADIUS)
                )
                self.assertGreater(bounds["current_inverse"], 0)
        self.assertNotEqual(observations[0], observations[1])

    def test_rounded_descriptor_corruption_cannot_pass_the_analytic_joint_gate(self):
        state = self.owner.state
        inputs = configure(
            state.inputs,
            radius=oracle.RADIUS,
            gain=0.5,
            tolerance=oracle.TOLERANCE,
            limit=2,
        )
        zeros = tuple((0.0, 0.0, 0.0) for _ in inputs.current.C)
        with (
            patch.object(
                GRC9V4CandidateADifferentialReference, "rebuild", return_value=zeros
            ),
            self.assertRaisesRegex(CIStageError, "joint residual"),
        ):
            CandidateCIRoot(inputs, state.differential_reference)

    def test_native_effects_clear_full_formula_and_ULP_margins(self):
        effects = native_effects(self.seed, self.owner.state)
        self.assertEqual(len(effects), 18)
        self.assertGreater(min(x["minimum_margin_ratio"] for x in effects), 1)

    def test_confirming_recipe_closes_source_reset_precision_gap_and_is_replay_bound(
        self,
    ):
        inputs = replace(self.seed.inputs, current=self.seed.inputs.reset, dt=oracle.DT)
        backend = self.seed.differential_reference
        zero = PhysicalFlux(backend.graph, (0.0,) * 9)
        stage = replace(inputs, stage="ci_trial", trial_current=zero)
        for index in range(2):
            stage = replace(stage, evaluation_index=index)
            point = candidate.CandidateACurrent(stage, backend)
            trial = ci.CITrial(replace(stage, trial_current=point.current), backend)
            stage = replace(stage, geometry=trial.generated, trial_current=zero)
        # The original first-pass stopping rule satisfied the profile's joint
        # tolerance here, while missing the accepted oracle's geometry budget.
        self.assertLessEqual(
            trial.residual_squared, exact_number(oracle.TOLERANCE) ** 2
        )
        old = deepcopy(self.record["source_reference_reads"]["reset"])
        old.update(
            H=trial.inputs.geometry.one_form_hodge.matrix,
            current=trial.point.current.values,
            baseline=trial.point.baseline.values,
            source=trial.structural_source.increment,
        )
        with self.assertRaisesRegex(ValueError, "geometry error budget"):
            oracle.check_step(
                backend.port_graph.to_payload(),
                inputs.current.C,
                inputs.current.W_A,
                old,
            )
        step = ProvisionalCandidateCIStep(inputs, backend)
        self.assertEqual(step.root.evaluations, 3)
        oracle.check_step(
            backend.port_graph.to_payload(),
            inputs.current.C,
            inputs.current.W_A,
            outputs(step),
        )
        for owner in (step.root, step):
            recipe = owner.to_payload()
            self.assertEqual(recipe["numerics"], ci.GRC9_ACI_NUMERICS)
            recipe["numerics"] = ci.NUMERICS
            with self.assertRaisesRegex(ValueError, "recipe"):
                type(owner).from_payload(recipe)
        two = configure(
            inputs, radius=oracle.RADIUS, gain=0.5, tolerance=oracle.TOLERANCE, limit=2
        )
        with self.assertRaisesRegex(CIStageError, "iteration limit"):
            CandidateCIRoot(two, backend)

    def test_iteration_exhaustion_rejects_without_fallback_and_keeps_checkpoint(self):
        # A genuine native joint solve fails when only the initial H=I trial is allowed.
        state = self.owner.state
        inputs = configure(
            state.inputs,
            radius=oracle.RADIUS,
            gain=0.5,
            tolerance=oracle.TOLERANCE,
            limit=1,
        )
        for role in ("current", "reset"):
            with (
                self.subTest(role=role),
                self.assertRaisesRegex(CIStageError, "iteration limit"),
            ):
                CandidateCIRoot(
                    replace(inputs, current=getattr(inputs, role)),
                    state.differential_reference,
                )
        # The receiver also preserves publication on a late selected-root failure.
        owner = GRC9V4ACIOperation(self.seed)
        real = native._aci_readmit

        def exhaust(target):
            if len(target.inputs.current.C) > len(self.seed.inputs.current.C):
                limited = configure(
                    target.inputs,
                    radius=oracle.RADIUS,
                    gain=0.5,
                    tolerance=oracle.TOLERANCE,
                    limit=1,
                )
                CandidateCIRoot(limited, target.differential_reference)
            return real(target)

        with patch.object(native, "_aci_readmit", exhaust):
            failure = self.assertRollback(
                owner, self.request, stage="target_readmission"
            )
            self.assertIn("iteration limit", failure.failure.message)

    def test_root_restart_and_closed_runtime_roles_reject_foreign_or_carrier_inputs(
        self,
    ):
        root = CandidateCIRoot(self.seed.inputs, self.seed.differential_reference)
        with self.assertRaisesRegex(ValueError, "restart"):
            replace(
                self.seed,
                inputs=replace(
                    self.seed.inputs, geometry=root.selected.inputs.geometry
                ),
            )
        with self.assertRaises(TypeError):
            native.GRC9V4AOSOperation(self.seed)
        for role in ("current", "reset"):
            bad = replace(getattr(self.seed.inputs, role), Z_4=(0.0,) * 81)
            with self.assertRaises(ValueError):
                GRC9V4ACIOperation(
                    replace(self.seed, inputs=replace(self.seed.inputs, **{role: bad}))
                )
        with self.assertRaisesRegex(ValueError, "source graph"):
            from pygrc.models.grc_9_v4_expansion import (
                GRC9ExpansionPolicy,
                GRC9V4ExpansionPlan,
            )

            target = GRC9V4ACIExpansion(
                GRC9V4ExpansionPlan(
                    self.seed.differential_reference.port_graph,
                    self.seed.scientific_digest,
                    self.request,
                    GRC9ExpansionPolicy.from_payload(
                        self.seed.specialization.resolved["expansion"]
                    ),
                ),
                self.seed.inputs.geometry.reference,
                self.seed.inputs.current,
                self.seed.inputs.reset,
            )
            target.transfer_reference_current(
                PhysicalFlux(target.target.graph, (0.0,) * 16)
            )

    def test_fixed_row_floor_charts_and_exact_singular_current_are_fail_closed(self):
        graph = GRC9V4PortGraph.from_payload(
            {
                "schema_version": "grc9v4-port-graph-v1",
                "live_node_ids": ["a", "b"],
                "edges": [
                    {
                        "edge_id": "e",
                        "kind": "boundary",
                        "tail": {"node_id": "a", "port": 1},
                        "head": {"node_id": "b", "port": 9},
                    }
                ],
            }
        )
        ref = oracle.reference(graph.to_payload())
        authority = GRCV4AuthoritativeState((1.0, 3.0), (1.0,), None)
        inputs = replace(
            self.seed.inputs,
            geometry=ref.geometry(),
            current=authority,
            reset=authority,
            Q_target=4,
        )
        backend = GRC9V4CandidateADifferentialReference(graph)
        active = configure(
            inputs,
            radius=oracle.RADIUS,
            gain=0,
            tolerance=oracle.TOLERANCE,
            changes={"candidate": {"W_floor": 2}},
        )
        root = CandidateCIRoot(active, backend)
        self.assertEqual(
            tuple(root.certificate.bounds["floor_charts"]), ("floor_active",)
        )
        self.assertEqual(root.selected.point.W_hat_A, (2.0,))
        self.assertEqual(root.current.values, (float(Fraction(384, 97)),))
        crossing = configure(
            inputs,
            radius=1 / 64,
            gain=0,
            tolerance=oracle.TOLERANCE,
            changes={
                "candidate": {"alpha": 0, "beta": 0, "gamma": 1, "W_floor": 0.00034}
            },
        )
        with self.assertRaisesRegex(CIStageError, "floor chart"):
            CandidateCIRoot(crossing, backend)
        singular_state = replace(authority, W_A=(3.0,))
        singular = configure(
            replace(inputs, current=singular_state, reset=singular_state),
            radius=oracle.RADIUS,
            gain=0,
            tolerance=oracle.TOLERANCE,
            changes={
                "candidate": {
                    "alpha": 0,
                    "beta": 0,
                    "gamma": 0,
                    "chi_A": 4,
                    "zeta_A": 0.5,
                }
            },
        )
        with self.assertRaises((candidate.CandidateAStageError, CIStageError)):
            CandidateCIRoot(singular, backend)

    def test_resource_simplex_vertices_admit_events_but_reject_negative_physical_steps(
        self,
    ):
        rows = simplex_observations(self.seed, self.request)
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertLess(
                Fraction(row["negative_coordinate_upper"]), Fraction(-1, 100)
            )
            self.assertEqual(row["step_failure"]["stage"], "charge_admission")
            self.assertTrue(row["checkpoint_unchanged"])


if __name__ == "__main__":
    unittest.main()
