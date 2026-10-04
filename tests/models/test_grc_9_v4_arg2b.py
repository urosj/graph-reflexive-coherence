"""Native A_RG2b pressure against the immutable accepted A.1 oracle."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import numpy as np

from pygrc.models import grc_9_v4_arg2b as signed
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import (
    GRC9V4ARG2bExpansion,
    GRC9V4ExpansionRequestInput,
    arg2b_profile_template,
)
from pygrc.models.grc_9_v4_lifecycle import (
    GRC9V4ARG2bOperation,
    GRC9V4ARG2bState,
    GRC9V4Specialization,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4CandidateADifferentialReference,
    GRC9V4PortGraph,
)
from pygrc.models.grc_v4_candidate_a import CandidateACurrent
from pygrc.models.grc_v4_ci import _source
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4ReferenceGeometry,
)
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models.grc_v4_rg2b import (
    CandidateRG2bSection,
    ProvisionalCandidateRG2bStep,
    RG2bCertificate,
    RG2bStageError,
)
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_v4_profile import reidentify

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "implementation/phase-9-grcv4/verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))
import verify_p983a_arg2b_oracle as oracle

RECORD = ROOT / oracle.RECORD
ORACLE_SHA = "521787954476c351e5fc99e492ce0e00f1a972255c8274729c7d0c03098ffbc9"
DT = 2**-12


def authority(data):
    return GRCV4AuthoritativeState(tuple(data["C"]), tuple(data["W_A"]), None)


def fixture(record=None):
    if record is None:
        record = json.loads(RECORD.read_text())
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
        "arg2b-seed",
        30.140625,
        (),
        1,
        DT,
        0,
        "pre_read",
        0,
        None,
    )
    return GRC9V4ARG2bState(inputs, spec), GRC9V4ExpansionRequestInput.from_payload(
        record["request"]
    )


def history_authority(state):
    return oracle.authority(state.C, state.W_A)


def request_for(state, original):
    data = original.to_payload()
    data.update(
        source_state_digest=state.scientific_digest,
        target_profile_template_id=arg2b_profile_template(
            state.inputs.geometry.reference
        ).profile_template_id,
        history_policy=oracle.history_policy(
            oracle.authority(state.inputs.current.C, state.inputs.current.W_A),
            oracle.authority(state.inputs.reset.C, state.inputs.reset.W_A),
        ),
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    return GRC9V4ExpansionRequestInput.from_payload(data)


def configure(inputs, changes):
    ref = inputs.geometry.reference
    params, ident = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    for key, values in changes.items():
        params[key].update(values)
    reidentify(params, ident)
    return replace(
        inputs, geometry=replace(ref, profile=resolve_profile(params, ident)).geometry()
    )


def read(inputs):
    backend = GRC9V4CandidateADifferentialReference(
        inputs.geometry.reference.graph.port_graph
    )
    section = CandidateRG2bSection(inputs, backend)
    return section, CandidateACurrent(
        replace(inputs, geometry=section.geometry, stage="rg2b_section"), backend
    )


def values(section, point, following=None):
    out = {
        "H": section.geometry.one_form_hodge.matrix,
        "current": point.current.values,
        "baseline": point.baseline.values,
        "source": _source(point, point.current).increment,
    }
    if following is not None:
        out.update(C=following.current.C, W_A=following.current.W_A)
    return out


def check(inputs, section, point, following=None, *, ci=None, wi=None):
    graph = inputs.geometry.reference.graph.port_graph.to_payload()
    c, w = tuple(inputs.current.C), tuple(inputs.current.W_A)
    expected = oracle.PaperARG(graph).step(c, w)
    checked = oracle.check_step(graph, c, w, expected, ci=ci, wi=wi)
    limits = {
        "C": oracle.RESOURCE_ERROR,
        "W_A": oracle.HISTORY_ERROR,
        "H": oracle.SECTION_ERROR,
        "current": oracle.CURRENT_ERROR,
        "baseline": oracle.CURRENT_ERROR,
        "source": oracle.SOURCE_ERROR,
    }
    errors = {}
    for k, v in values(section, point, following).items():
        errors[k] = oracle.full_error(
            np.array(v).ravel(), oracle.IV.matrix(list(checked["truth"][k]))
        )
        if errors[k] >= limits[k]:
            raise AssertionError(
                f"native {k} full error {float(errors[k])} >= {float(limits[k])}"
            )
    return checked, errors


class NativeARG2bPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = exact_backend(ExactBackend.FLINT)
        cls.backend.__enter__()
        cls.addClassCleanup(cls.backend.__exit__, None, None, None)
        assert hashlib.sha256(RECORD.read_bytes()).hexdigest() == ORACLE_SHA
        cls.record = json.loads(RECORD.read_text())
        cls.seed, cls.request = fixture(cls.record)
        cls.owner = GRC9V4ARG2bOperation(cls.seed)
        result = cls.owner.expand(cls.request)
        assert result.committed, result.failure
        cls.checkpoint = cls.owner.checkpoint()

    def test_event_identity_exact_history_and_no_carrier(self):
        r = self.record
        target = self.owner.state
        self.assertEqual(target.scientific_digest, r["target"]["scientific_digest"])
        self.assertEqual(target.reset_digest, r["target"]["reset_digest"])
        for role in ("current", "reset"):
            observed = getattr(target.inputs, role)
            expected = r["target"]["roles"][role]["authoritative"]
            self.assertEqual(observed, authority(expected))
            self.assertIsNone(observed.Z_4)
        cp = json.loads(self.checkpoint)
        self.assertNotIn("carrier_archives", cp)
        self.assertEqual(cp["reference_currents"][0]["event_id"], r["event_id"])
        self.assertEqual(target.inputs.step_index, 1)
        self.assertEqual(target.inputs.time, DT)

    def test_actual_source_step_reproduces_exact_event_seed(self):
        initial = replace(
            self.seed.inputs,
            current=authority(self.record["initial"]["current"]),
            reset=authority(self.record["initial"]["reset"]),
            dt=DT,
            step_index=0,
            time=0,
        )
        step = ProvisionalCandidateRG2bStep(initial, self.seed.differential_reference)
        self.assertEqual(step.next_inputs.current, self.seed.inputs.current)
        self.assertEqual(step.next_inputs.reset, self.seed.inputs.reset)
        self.assertEqual(step.next_inputs.step_index, self.seed.inputs.step_index)
        self.assertEqual(step.next_inputs.time, self.seed.inputs.time)

    def test_log_constant_cache_preserves_backend_and_original_enclosure(self):
        from pygrc.models import grc_v4_rg2b as rg
        from pygrc.models.grc_v4_exact import exact_number, is_exact

        for order in (
            (ExactBackend.FLINT, ExactBackend.PYTHON),
            (ExactBackend.PYTHON, ExactBackend.FLINT),
        ):
            rg._ln2_for_backend.cache_clear()
            results = []
            for backend in (*order, *order):
                with exact_backend(backend):
                    bound = rg._ln2()
                    fresh = rg._log_unit(exact_number(2))
                    self.assertTrue(is_exact(bound.lo) and is_exact(bound.hi))
                    self.assertEqual((bound.lo, bound.hi), (fresh.lo, fresh.hi))
                    results.append((str(bound.lo), str(bound.hi)))
                    for q in (exact_number(1, 8), exact_number(1), exact_number(17)):
                        cached = rg._log_point(q)
                        uncached = rg._Interval(*rg._log_point_endpoints.__wrapped__(q))
                        self.assertEqual(cached, uncached)
            self.assertTrue(all(v == results[0] for v in results))
            self.assertEqual(rg._ln2_for_backend.cache_info().currsize, 2)

    def test_complete_native_step_is_identical_across_exact_backends(self):
        inputs = replace(self.seed.inputs, dt=DT)
        with exact_backend(ExactBackend.FLINT):
            flint = ProvisionalCandidateRG2bStep(
                inputs, self.seed.differential_reference
            )
        with exact_backend(ExactBackend.PYTHON):
            python = ProvisionalCandidateRG2bStep(
                inputs, self.seed.differential_reference
            )
        self.assertEqual(flint.next_inputs, python.next_inputs)
        self.assertEqual(flint.section.geometry, python.section.geometry)
        self.assertEqual(flint.point.current, python.point.current)
        self.assertEqual(flint.diagnostics, python.diagnostics)

    def test_native_step_full_interval_smoke(self):
        inputs = replace(self.owner.state.inputs, dt=DT)
        step = ProvisionalCandidateRG2bStep(
            inputs, self.owner.state.differential_reference
        )
        check(inputs, step.section, step.point, step.next_inputs)
        self.assertEqual(step.section.levels, 4)
        self.assertEqual(step.section.evaluations, 148)
        self.assertLessEqual(
            Q(step.diagnostics["invariance_residual"]),
            Q(step.diagnostics["invariance_error_bound"]),
        )

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

    def test_policy_rehashed_role_substitutions_fail_at_admission(self):
        owner = GRC9V4ARG2bOperation(self.seed)
        policies = []
        for role in ("current", "reset"):
            values = (
                history_authority(self.seed.inputs.current),
                history_authority(self.seed.inputs.reset),
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
        original = GRC9V4ARG2bExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4ARG2bOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                value = original(target, state)
                return (
                    replace(value, C=(value.C[0] + 1, *value.C[1:]))
                    if state == chosen
                    else value
                )

            with patch.object(GRC9V4ARG2bExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, stage="target_readmission")
        owner = GRC9V4ARG2bOperation(self.seed)
        with patch.object(
            native,
            "make_commit_receipts",
            side_effect=ValueError("late receipt failure"),
        ):
            self.assertRollback(owner, self.request, stage="commit")
        with patch.object(
            GRC9V4ARG2bExpansion,
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
            data = json.loads(self.checkpoint)
            target = data
            for key in path[:-1]:
                target = target[key]
            value = target[path[-1]]
            target[path[-1]] = (
                value + 2**-20 if isinstance(value, (int, float)) else value + "x"
            )
            with self.subTest(path=path), self.assertRaises((ValueError, TypeError)):
                GRC9V4ARG2bOperation.replay(canonical_json_bytes(data))
        data = json.loads(self.checkpoint)
        data["reference_currents"][0]["roles"]["current"] = data["reference_currents"][
            0
        ]["roles"]["reset"]
        with self.assertRaises(ValueError):
            GRC9V4ARG2bOperation.replay(canonical_json_bytes(data))

    def test_rehashed_target_authority_and_source_policy_do_not_bypass_replay(self):
        for role in ("current", "reset"):
            data = json.loads(self.checkpoint)
            inputs = self.owner.state.inputs
            old = getattr(inputs, role)
            altered = replace(old, W_A=(old.W_A[0] + 2**-30, *old.W_A[1:]))
            forged = replace(
                self.owner.state, inputs=replace(inputs, **{role: altered})
            )
            data["state"] = forged.to_payload()
            data["lifecycle_digest"] = forged.lifecycle_digest(self.owner.receipts)
            with self.assertRaises(ValueError):
                GRC9V4ARG2bOperation.replay(canonical_json_bytes(data))
        seed = replace(self.seed, inputs=replace(self.seed.inputs, step_index=0))
        owner = GRC9V4ARG2bOperation(seed)
        result = self.assertRollback(
            owner, request_for(seed, self.request), stage="admission"
        )
        self.assertIn("postbeat", result.failure.message)

    def test_fresh_reference_currents_receipts_and_explicit_replay(self):
        cp = json.loads(self.checkpoint)
        for role in ("current", "reset"):
            inputs = replace(self.seed.inputs, current=getattr(self.seed.inputs, role))
            _, point = read(inputs)
            recorded = cp["reference_currents"][0]["roles"][role]
            self.assertEqual(recorded["source"], list(point.current.values))
            old = dict(
                zip(
                    inputs.geometry.reference.graph.live_edge_ids,
                    point.current.values,
                    strict=True,
                )
            )
            self.assertEqual(
                recorded["target"],
                [
                    old.get(e, 0.0)
                    for e in self.owner.state.inputs.geometry.reference.graph.live_edge_ids
                ],
            )
            self.assertLess(
                np.max(
                    np.abs(
                        np.array(recorded["source"])
                        - self.record["source_reference_reads"][role]["current"]
                    )
                ),
                float(oracle.CURRENT_ERROR),
            )
        event = self.owner.receipts[0].identity_payload.to_dict()
        expected = self.record["receipt_expectations"]
        for key in (
            "actual_charge_delta",
            "information_losses",
            "source_model_identity",
            "target_model_identity",
            "source_state_digest",
            "target_state_digest",
            "source_reset_digest",
            "target_reset_digest",
        ):
            self.assertEqual(event["core"][key], expected[key])
        for channel in ("candidate", "carrier"):
            self.assertEqual(
                event["history"][channel], dict(subject=channel, **expected[channel])
            )
        self.assertEqual(
            GRC9V4ARG2bOperation.replay(self.checkpoint).checkpoint(), self.checkpoint
        )
        section, _ = read(self.seed.inputs)
        self.assertEqual(
            CandidateRG2bSection.from_payload(section.to_payload()).identity,
            section.identity,
        )
        step = ProvisionalCandidateRG2bStep(
            replace(self.seed.inputs, dt=DT), self.seed.differential_reference
        )
        self.assertEqual(
            ProvisionalCandidateRG2bStep.from_payload(step.to_payload()).next_inputs,
            step.next_inputs,
        )

    def test_event_runs_no_physical_step_or_history_writer(self):
        with (
            patch(
                "pygrc.models.grc_v4_rg2b.ProvisionalCandidateRG2bStep",
                side_effect=AssertionError("ordinary beat"),
            ),
            patch(
                "pygrc.models.grc_v4_rg2b.CandidateAWriter",
                side_effect=AssertionError("writer"),
            ),
            patch.object(native, "CandidateAOSPass", side_effect=AssertionError("OS")),
        ):
            owner = GRC9V4ARG2bOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)
            self.assertEqual(owner.state.inputs.time, self.seed.inputs.time)

    def test_global_exact_bounds_match_accepted_independent_proof(self):
        import test_p980_rg2b_completion as proof

        from pygrc.models.grc_v4_exact import current_exact_backend

        inputs = self.owner.state.inputs
        cert = RG2bCertificate(inputs, self.owner.state.differential_reference)
        b = proof.global_bounds("A")
        sb = proof.section_budgets(b)
        for key, field in (
            ("base_X_lipschitz", "A_X"),
            ("base_h_lipschitz", "A_H"),
            ("source_X_lipschitz", "B_X"),
            ("source_h_lipschitz", "B_H"),
            ("base_displacement_upper", "M_f"),
            ("source_upper", "M_S"),
            ("resource_displacement_upper", "M_C"),
            ("scaled_log_displacement_upper", "M_Y"),
        ):
            self.assertEqual(Q(cert.bounds[key]), b[field])
        self.assertEqual(Q(cert.bounds["contraction_upper"]), sb["q_section"])
        self.assertEqual(Q(cert.bounds["section_value_radius"]), sb["value_radius"])
        with exact_backend(ExactBackend.PYTHON):
            other = RG2bCertificate(inputs, self.owner.state.differential_reference)
        self.assertEqual(cert.bounds, other.bounds)
        captured = current_exact_backend()
        seen = []
        real = native._arg2b_readmit

        def observe(state):
            seen.append(current_exact_backend())
            return real(state)

        owner = GRC9V4ARG2bOperation(self.seed)
        with (
            exact_backend(ExactBackend.PYTHON),
            patch.object(native, "_arg2b_readmit", observe),
        ):
            self.assertTrue(owner.expand(self.request).committed)
        self.assertTrue(seen)
        self.assertEqual(set(seen), {captured})

    def test_every_inverse_level_and_both_state_blocks_are_certified(self):
        inputs = self.owner.state.inputs
        backend = self.owner.state.differential_reference
        cert = RG2bCertificate(inputs, backend)
        query = tuple(inputs.current.C) + tuple(
            512 * math.log(w) for w in inputs.current.W_A
        )
        x, h = signed.propose(cert, query)
        for depth in range(1, 5):
            for coord in (0, len(inputs.current.C), len(query) - 1):
                xx = deepcopy(x)
                xx[depth][coord] += 2**-12
                with (
                    self.subTest(depth=depth, coordinate=coord),
                    patch.object(signed, "propose", return_value=(xx, h)),
                    self.assertRaisesRegex(RG2bStageError, "tolerance"),
                ):
                    CandidateRG2bSection(inputs, backend)
        mutations = [(x[:-1], h[:-1]), (x + [x[-1]], h + [h[-1]])]
        xx = deepcopy(x)
        xx[0][0] += 1
        mutations.append((xx, h))
        hh = deepcopy(h)
        hh[-1][0, 0] += 2**-20
        mutations.append((x, hh))
        hh = deepcopy(h)
        hh[2][0, 1] += 2**-20
        mutations.append((x, hh))
        hh = deepcopy(h)
        mask = np.array(cert.graph_data.mask, dtype=float)
        hh[2] = np.eye(len(mask)) + 2**-13 * (mask != 0)
        mutations.append((x, hh))
        for value in (math.nan, math.inf):
            xx = deepcopy(x)
            xx[3][-1] = value
            mutations.append((xx, h))
        xx = deepcopy(x)
        xx[2] = xx[2].astype(np.float32)
        mutations.append((xx, h))
        hh = deepcopy(h)
        hh[1] = hh[1][:-1]
        mutations.append((x, hh))
        for xx, hh in mutations:
            with (
                patch.object(signed, "propose", return_value=(xx, hh)),
                self.assertRaises(RG2bStageError),
            ):
                CandidateRG2bSection(inputs, backend)
        # Caller-owned exact logarithm must survive mutation of producer scratch.
        real = signed.propose

        def change_query(cert, query):
            altered = (*query[:-1], query[-1] + 2**-12)
            return real(cert, altered)

        with (
            patch.object(signed, "propose", side_effect=change_query),
            self.assertRaisesRegex(RG2bStageError, "query"),
        ):
            CandidateRG2bSection(inputs, backend)

    def test_signed_predecessor_tail_and_complete_clamped_equations(self):
        import test_p980_rg2b_completion as proof
        import test_p980_rg2b_numerical as numerical
        from test_p980_os_effect_witness import IV, endpoint, number, vector

        for role in ("current", "reset"):
            inputs = replace(
                self.owner.state.inputs, current=getattr(self.owner.state.inputs, role)
            )
            backend = self.owner.state.differential_reference
            cert = RG2bCertificate(inputs, backend)
            query = tuple(inputs.current.C) + tuple(
                512 * math.log(w) for w in inputs.current.W_A
            )
            x, h = signed.propose(cert, query)
            high = proof.auxiliary(oracle.model_for(backend.port_graph.to_payload()))
            exact = proof.state(
                "A", vector(inputs.current.C), vector(inputs.current.W_A)
            )
            _, budgets = numerical.certify_chain(
                high, "A", numerical.Chain(x, h), exact
            )
            error, nb = signed.certify_chain(
                cert, query, x, h, signed.coordinates(inputs.current)
            )
            self.assertLess(Q(str(error)), oracle.SECTION_ERROR)
            self.assertGreater(Q(str(nb["input_error"])), 0)
            b = proof.global_bounds("A")
            sb = proof.section_budgets(b)
            tail = (
                sb["inverse_lip"] * b["A_H"] * sb["q_section"] ** 3 * sb["value_radius"]
            )
            k = list(inputs.current.C).index(0)
            input_tail = sb["inverse_lip"] * b["A_H"] * Q(str(nb["input_error"]))
            self.assertLess(
                Q(float(x[1][k])) + budgets["state_error"] + tail + input_tail, 0
            )
            xx = deepcopy(x)
            xx[1][k] = 0
            with (
                patch.object(signed, "propose", return_value=(xx, h)),
                self.assertRaisesRegex(RG2bStageError, "tolerance"),
            ):
                CandidateRG2bSection(inputs, backend)
        m = len(h[0])
        n = len(inputs.current.C)
        hd = np.eye(m) + np.diag([(-1) ** i * 2**-12 for i in range(m)])
        self.assertGreater(
            np.max(
                np.abs(
                    hd @ np.array(cert.graph_data.gram, dtype=float)
                    - np.array(cert.graph_data.gram, dtype=float) @ hd
                )
            ),
            0,
        )
        for cface, yface in (
            (-1.0, -1.0),
            (5.0, 1.0),
            (math.nextafter(-1.0, -math.inf), math.nextafter(1.0, math.inf)),
            (math.nextafter(5.0, math.inf), math.nextafter(-1.0, -math.inf)),
            (math.nextafter(-1.0, math.inf), math.nextafter(1.0, 0)),
            (-1e100, 1e100),
            (1e100, -1e100),
        ):
            xx = tuple(cface if i % 2 else 2.0 for i in range(n)) + tuple(
                yface if i % 2 else -yface for i in range(m)
            )
            f, g, _ = signed.literal(cert, xx, hd.tolist())
            ef, es = high.increment("A", vector(xx), IV.matrix(hd.tolist()))
            eg = high.I + number(Q(1, 2)) * es
            for actual, expected in list(zip(f, ef, strict=True)) + list(
                zip((v for row in g for v in row), eg, strict=True)
            ):
                self.assertLessEqual(Q(str(actual.lo)), endpoint(expected, 0))
                self.assertGreaterEqual(Q(str(actual.hi)), endpoint(expected, 1))

    def test_C_Y_chart_boundaries_and_dt_zero_admission(self):
        for c in (0.0, 4.25, math.nextafter(4.25, math.inf), 4.5):
            state = replace(self.seed.inputs.current, C=(c,) * 10, W_A=(1.0,) * 9)
            inputs = replace(
                self.seed.inputs, current=state, reset=state, Q_target=10 * c, dt=0
            )
            section, _ = read(inputs)
            self.assertEqual(section.geometry, inputs.geometry.reference.geometry())
            if c <= 4.25:
                self.assertEqual(
                    ProvisionalCandidateRG2bStep(
                        inputs, self.seed.differential_reference
                    ).next_inputs,
                    inputs,
                )
            else:
                with self.assertRaisesRegex(ResourceBoundaryError, "K_minus"):
                    ProvisionalCandidateRG2bStep(
                        inputs, self.seed.differential_reference
                    )
        for radius in (5 / 8, 3 / 4):
            for sign in (-1, 1):
                boundary = math.exp(sign * radius / 512)
                for w in (
                    math.nextafter(boundary, 0),
                    boundary,
                    math.nextafter(boundary, math.inf),
                ):
                    state = replace(
                        self.seed.inputs.current, C=(2.0,) * 10, W_A=(w,) * 9
                    )
                    inputs = replace(
                        self.seed.inputs,
                        current=state,
                        reset=state,
                        Q_target=20.0,
                        dt=0,
                    )
                    y = 512 * oracle.IV.ln(oracle.number(Q(w)))
                    lo, hi = oracle.endpoint(y, 0), oracle.endpoint(y, 1)
                    k_good = max(abs(lo), abs(hi)) <= Q(3, 4)
                    ordinary_good = max(abs(lo), abs(hi)) <= Q(5, 8)
                    if k_good:
                        read(inputs)
                    else:
                        with self.assertRaisesRegex(RG2bStageError, "outside K"):
                            read(inputs)
                    if ordinary_good:
                        ProvisionalCandidateRG2bStep(
                            inputs, self.seed.differential_reference
                        )
                    else:
                        with self.assertRaisesRegex(ResourceBoundaryError, "K_minus"):
                            ProvisionalCandidateRG2bStep(
                                inputs, self.seed.differential_reference
                            )
        state = replace(state, C=(math.nextafter(4.5, math.inf),) * 10, W_A=(1.0,) * 9)
        with self.assertRaisesRegex(RG2bStageError, "outside K"):
            read(replace(inputs, current=state))

    def test_frozen_recipe_graph_hypotheses_and_explicit_descriptor(self):
        from tests.models.test_grc_9_v4_topology import edge

        for changes in (
            {"realization": {"iteration_limit": 147}},
            {"realization": {"error_tolerance": 2**-70}},
            {"realization": {"extension_evaluator_id": "unknown"}},
            {"realization": {"approximation_policy_id": "unknown"}},
            {"realization": {"error_norm_id": "unknown"}},
            {"realization": {"containment_certificate_id": "unknown"}},
            {"candidate": {"alpha": 2**-23}},
            {"candidate": {"chi_A": 1 / 32}},
            {"candidate": {"tau_A": 2}},
            {"geometry": {"kappa_H": 0.25}},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                read(configure(self.seed.inputs, changes))
        for dt in (math.nextafter(DT, 0), 2 * DT):
            with self.assertRaisesRegex(RG2bStageError, "beat"):
                read(replace(self.seed.inputs, dt=dt))
        section, _ = read(self.seed.inputs)
        with self.assertRaisesRegex(RG2bStageError, "Lipschitz-only"):
            section.classical_jacobian()
        with self.assertRaisesRegex(TypeError, "differential"):
            CandidateRG2bSection(self.seed.inputs)
        for n in (2, 17, 18):
            graph = GRC9V4PortGraph(
                tuple(range(n)),
                tuple(edge(f"e{i}", (i, 2), (i + 1, 1)) for i in range(n - 1)),
            )
            ref = oracle.reference(graph.to_payload())
            c = tuple(4.25 if i % 2 else 0.0 for i in range(n))
            w = tuple(math.exp((0.6 if i % 2 else -0.6) / 512) for i in range(n - 1))
            state = GRCV4AuthoritativeState(c, w, None)
            inputs = replace(
                self.seed.inputs,
                geometry=ref.geometry(),
                current=state,
                reset=state,
                Q_target=sum(c),
                dt=0,
            )
            if n > 17:
                with self.assertRaisesRegex(RG2bStageError, "at most 17"):
                    read(inputs)
            else:
                import test_p980_rg2b_numerical as numerical

                ss, _ = read(inputs)
                _, hi, _, _ = numerical.section(
                    oracle.model_for(graph.to_payload()), "A", np.array(c), np.array(w)
                )
                self.assertLess(
                    oracle.full_error(
                        np.array(ss.geometry.one_form_hodge.matrix).ravel(),
                        oracle.IV.matrix(list(hi)),
                    ),
                    oracle.SECTION_ERROR,
                )
        graph = GRC9V4PortGraph(
            (0, 1, 2),
            (
                edge("a", (0, 1), (1, 1)),
                edge("b", (1, 2), (2, 1)),
                edge("c", (2, 2), (0, 2)),
            ),
        )
        ref = oracle.reference(graph.to_payload())
        state = GRCV4AuthoritativeState((2.0,) * 3, (1.0,) * 3, None)
        with self.assertRaisesRegex(RG2bStageError, "connected tree"):
            read(
                replace(
                    self.seed.inputs,
                    geometry=ref.geometry(),
                    current=state,
                    reset=state,
                    Q_target=6.0,
                    dt=0,
                )
            )

    def test_actual_operator_norm_limit_rejects_high_degree_tree(self):
        from tests.models.test_grc_9_v4_topology import edge

        # Seventeen valid vertices and port occupancy do not imply ||B^T B||inf<=10.
        edges = (
            (edge("bridge", (0, 1), (1, 1)),)
            + tuple(edge(f"left{i}", (0, i), (i, 1)) for i in range(2, 10))
            + tuple(edge(f"right{i}", (1, i - 8), (i, 1)) for i in range(10, 17))
        )
        graph = GRC9V4PortGraph(tuple(range(17)), edges)
        ref = oracle.reference(graph.to_payload())
        state = GRCV4AuthoritativeState((2.0,) * 17, (1.0,) * 16, None)
        inputs = replace(
            self.seed.inputs,
            geometry=ref.geometry(),
            current=state,
            reset=state,
            Q_target=34.0,
            dt=0,
        )
        with self.assertRaisesRegex(RG2bStageError, "graph norm hypotheses"):
            read(inputs)

    def test_native_bridge_requires_scaled_log_history_error(self):
        from pygrc.models import grc_v4_rg2b as owner

        real = owner.CandidateAWriter

        def corrupt(point, resource):
            out = real(point, resource)
            old = out.authority.state
            object.__setattr__(
                out.authority,
                "state",
                replace(old, W_A=(old.W_A[0] + 2**-44, *old.W_A[1:])),
            )
            return out

        inputs = replace(self.seed.inputs, dt=DT)
        with patch.object(owner, "CandidateAWriter", side_effect=corrupt):
            with self.assertRaisesRegex(ResourceBoundaryError, "arithmetic bridge"):
                ProvisionalCandidateRG2bStep(inputs, self.seed.differential_reference)
            bridge = signed.native_bridge

            def wrong_units(section, point, following, generated):
                je, xe, he, jn = bridge(section, point, following, generated)
                return je, xe / 512, he, jn

            with patch.object(signed, "native_bridge", side_effect=wrong_units):
                wrong = ProvisionalCandidateRG2bStep(
                    inputs, self.seed.differential_reference
                )
                self.assertGreater(Q(wrong.diagnostics["native_state_error"]), 0)

    def test_current_error_uses_L2_not_coordinate_maximum(self):
        from pygrc.models import grc_v4_rg2b as owner
        from pygrc.models.grc_v4_geometry import PhysicalFlux

        real = owner.CandidateACurrent.__post_init__
        inputs = replace(self.seed.inputs, dt=DT)

        def corrupt(point):
            real(point)
            stage = point.inputs
            if stage.stage == "rg2b_section" and stage.current == inputs.current:
                object.__setattr__(
                    point,
                    "current",
                    PhysicalFlux(
                        stage.geometry.reference.graph,
                        tuple(j + 8e-12 for j in point.current.values),
                    ),
                )

        with patch.object(owner.CandidateACurrent, "__post_init__", corrupt):
            with self.assertRaisesRegex(ResourceBoundaryError, "arithmetic bridge"):
                ProvisionalCandidateRG2bStep(inputs, self.seed.differential_reference)
            with patch.object(signed, "_norm", side_effect=lambda values: max(values)):
                wrong = ProvisionalCandidateRG2bStep(
                    inputs, self.seed.differential_reference
                )
        self.assertNotEqual(
            wrong.point.current,
            owner.CandidateACurrent(
                wrong.point.inputs, self.seed.differential_reference
            ).current,
        )

    def test_real_target_seed_failure_and_two_role_simplex_negativity(self):
        params = self.seed.specialization.resolved.to_dict()
        params["expansion"]["bond_seed"] = 2
        identity = self.seed.specialization.identity_payload.to_dict()
        identity["specialization_params_hash"] = payload_identity(
            "resolved_specialization", params
        )
        spec = GRC9V4Specialization(FrozenJSONMap(params), FrozenJSONMap(identity))
        seed = replace(self.seed, specialization=spec)
        request = replace(
            request_for(seed, self.request),
            target_specialization_id=spec.specialization_id,
        )
        result = self.assertRollback(
            GRC9V4ARG2bOperation(seed), request, stage="target_readmission"
        )
        self.assertIn("parameter/reference", result.failure.message)
        for weights in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            owner = GRC9V4ARG2bOperation(self.seed)
            result = owner.expand(
                replace(
                    self.request,
                    resource_distribution=weights,
                    expected_event_id=None,
                    expected_target_graph_digest=None,
                )
            )
            self.assertTrue(result.committed, result.failure)
            before = owner.checkpoint()
            for role in ("current", "reset"):
                inputs = replace(
                    owner.state.inputs, current=getattr(owner.state.inputs, role), dt=DT
                )
                graph = owner.state.differential_reference.port_graph.to_payload()
                c, w = inputs.current.C, inputs.current.W_A
                observed = oracle.PaperARG(graph).step(c, w)
                checked = oracle.check_step(
                    graph, c, w, observed, require_positive=False
                )
                self.assertLess(
                    min(oracle.endpoint(v, 1) for v in checked["truth"]["C"]), -0.012
                )
                with self.assertRaises(ResourceBoundaryError):
                    ProvisionalCandidateRG2bStep(
                        inputs, owner.state.differential_reference
                    )
                self.assertEqual(owner.checkpoint(), before)

    def test_signed_edge_permutations_covary_current_history_and_section(self):
        for state in (self.seed, self.owner.state):
            inputs = replace(state.inputs, dt=DT)
            section, point = read(inputs)
            baseline = values(section, point)
            graph = state.differential_reference.port_graph
            order = list(reversed(range(len(graph.edges))))
            signs = np.array([-1 if i % 2 else 1 for i in order])
            edges = tuple(
                replace(
                    graph.edges[i], tail=graph.edges[i].head, head=graph.edges[i].tail
                )
                if sign < 0
                else graph.edges[i]
                for i, sign in zip(order, signs, strict=True)
            )
            ref = oracle.reference(
                GRC9V4PortGraph(graph.live_node_ids, edges).to_payload()
            )
            moved = replace(
                inputs.current, W_A=tuple(inputs.current.W_A[i] for i in order)
            )
            other = replace(inputs, geometry=ref.geometry(), current=moved, reset=moved)
            ss, pp = read(other)
            check(other, ss, pp)
            self.assertLess(
                np.max(
                    np.abs(
                        np.array(pp.current.values)
                        - np.array(baseline["current"])[order] * signs
                    )
                ),
                float(oracle.CURRENT_ERROR),
            )
            self.assertLess(
                np.max(
                    np.abs(
                        np.array(ss.geometry.one_form_hodge.matrix)
                        - np.array(baseline["H"])[np.ix_(order, order)]
                        * np.outer(signs, signs)
                    )
                ),
                float(oracle.SECTION_ERROR),
            )

    def test_duplicate_concurrent_events_publish_once(self):
        owner = GRC9V4ARG2bOperation(self.seed)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(owner.checkpoint(), self.checkpoint)

    def test_immutable_oracle_continuations_and_thirty_effect_controls(self):
        from verify_p983arg2b_native import observations

        report = observations()
        self.assertEqual(len(report["comparisons"]), 25)
        self.assertEqual(len(report["effects"]), 30)
        self.assertGreater(report["minimum_effect_margin"], 1)
        type(self).observations = report

    def test_real_current_only_and_reset_only_target_tolerance_failures(self):
        from pygrc.models.grc_9_v4_expansion import (
            GRC9ExpansionPolicy,
            GRC9V4ExpansionPlan,
        )

        for reset_failure in (False, True):
            inputs = configure(
                self.seed.inputs,
                {
                    "realization": {
                        "error_tolerance": 1.07e-16 if reset_failure else 1.059e-16
                    }
                },
            )
            if reset_failure:
                old = inputs.reset
                inputs = replace(
                    inputs, reset=replace(old, W_A=(old.W_A[0] - 2**-20, *old.W_A[1:]))
                )
            seed = replace(self.seed, inputs=inputs)
            request = request_for(seed, self.request)
            for role in ("current", "reset"):
                read(replace(inputs, current=getattr(inputs, role)))
            plan = GRC9V4ExpansionPlan(
                seed.differential_reference.port_graph,
                seed.scientific_digest,
                request,
                GRC9ExpansionPolicy.from_payload(
                    seed.specialization.resolved["expansion"]
                ),
            )
            target = GRC9V4ARG2bExpansion(
                plan, inputs.geometry.reference, inputs.current, inputs.reset
            )
            for role in ("current", "reset"):
                mapped = replace(
                    inputs,
                    geometry=target.target.geometry(),
                    current=target.transfer(getattr(inputs, role)),
                    reset=target.transfer(inputs.reset),
                )
                if (role == "reset") == reset_failure:
                    with self.assertRaisesRegex(RG2bStageError, "tolerance"):
                        read(mapped)
                else:
                    read(mapped)
            result = self.assertRollback(
                GRC9V4ARG2bOperation(seed), request, stage="target_readmission"
            )
            self.assertIn("tolerance", result.failure.message)

    def test_scoped_authorization_and_side_tool_claims(self):
        import phase9_specialization_acceptance as entry

        from pygrc.models.grc_v4_profile import list_supported_profiles

        self.assertEqual(entry.arg2b_authorization(ROOT), "P9-8.3A.2")
        for path in entry.ARG2B_PATHS:
            self.assertTrue(entry.arg2b_permitted(path, "P9-8.3A.2"))
        self.assertFalse(entry.arg2b_permitted("specs/grc-v4-spec.md", "P9-8.3A.2"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.arg2b_authorization(ROOT)
        self.assertNotIn(
            self.owner.state.inputs.geometry.reference.profile.complete_profile_id,
            list_supported_profiles(),
        )
        result = oracle.provenance()
        self.assertTrue(
            all(row["row_count"] == 1 for row in result["contracts"].values())
        )


def native_effects(seed, target):
    from pygrc.models.grc_v4_candidate_a import (
        _conductance,
        candidate_a_log_interpolation,
    )
    from pygrc.models.grc_v4_geometry import VertexScalar
    from pygrc.models.grc_v4_realizations import CandidateAOSPass

    rows = []

    def compare(label, enabled, disabled, ei, di):
        try:
            item = oracle.separation(
                np.array(enabled).ravel(),
                np.array(disabled).ravel(),
                oracle.IV.matrix(list(ei)),
                oracle.IV.matrix(list(di)),
            )
        except AssertionError as exc:
            raise AssertionError(label + ": " + str(exc)) from exc
        rows.append({"effect": label, **item})

    for place, state in (("source", seed), ("target", target)):
        backend = state.differential_reference
        graph = backend.port_graph.to_payload()
        for role in ("current", "reset"):
            inputs = replace(state.inputs, current=getattr(state.inputs, role), dt=DT)
            step = ProvisionalCandidateRG2bStep(inputs, backend)
            t, _ = check(inputs, step.section, step.point, step.next_inputs)
            high, truth = t["high"], t["truth"]
            c, w = inputs.current.C, inputs.current.W_A
            prefix = place + "_" + role + "_"
            for name, changes, flags in (
                ("geometry", {"kappa_Ah": 0}, {"geometry": False}),
                ("readback", {"chi_A": 0}, {"feedback": False}),
            ):
                changed = configure(inputs, {"candidate": changes})
                point = CandidateACurrent(
                    replace(
                        step.point.inputs,
                        geometry=replace(
                            step.section.geometry, reference=changed.geometry.reference
                        ),
                    ),
                    backend,
                )
                exact = high.read("A", t["c"], t["w"], truth["H"], **flags)
                compare(
                    prefix + name,
                    step.point.current.values,
                    point.current.values,
                    truth["current"],
                    exact["J"],
                )
            compare(
                prefix + "not_instantaneous_CI",
                step.section.geometry.one_form_hodge.matrix,
                step.generated.one_form_hodge.matrix,
                truth["H"],
                high.I + oracle.number(Q(1, 2)) * truth["source"],
            )
            if place == "source":
                continue
            osref = oracle.common.reference(graph)
            os = CandidateAOSPass(replace(inputs, geometry=osref.geometry()), backend)
            osi = high.ordinary_os("A", t["c"], t["w"])[2]
            compare(
                prefix + "not_OS_current",
                step.point.current.values,
                os.corrector.current.values,
                truth["current"],
                osi["read"]["J"],
            )
            next_inputs = step.next_inputs
            ns, npnt = read(next_inputs)
            nt, _ = check(next_inputs, ns, npnt, ci=truth["C"], wi=truth["W_A"])
            for name in ("stale_C_writer", "baseline_J_writer", "no_W_writer"):
                if name == "no_W_writer":
                    wc, wci = w, t["w"]
                else:
                    cv = c if name == "stale_C_writer" else next_inputs.current.C
                    j = (
                        step.point.baseline
                        if name == "baseline_J_writer"
                        else step.point.current
                    )
                    field = VertexScalar(backend.graph, cv)
                    drive = _conductance(
                        backend.graph,
                        inputs.geometry.reference.profile.params_resolved.candidate,
                        field,
                        backend.rebuild(field, w),
                        j,
                    )
                    wc = candidate_a_log_interpolation(w, drive, DT, 1)
                    wci = high.write(
                        t["c"] if name == "stale_C_writer" else truth["C"],
                        t["w"],
                        truth["baseline"]
                        if name == "baseline_J_writer"
                        else truth["current"],
                    )
                compare(
                    prefix + name + "_W", next_inputs.current.W_A, wc, truth["W_A"], wci
                )
                changed = replace(
                    next_inputs, current=replace(next_inputs.current, W_A=tuple(wc))
                )
                cs, cp = read(changed)
                ct, _ = check(changed, cs, cp, ci=truth["C"], wi=wci)
                compare(
                    prefix + name + "_next_current",
                    npnt.current.values,
                    cp.current.values,
                    nt["truth"]["current"],
                    ct["truth"]["current"],
                )
            changed = replace(
                inputs, current=replace(inputs.current, W_A=(1.0,) * len(w))
            )
            cs, cp = read(changed)
            ct, _ = check(changed, cs, cp)
            compare(
                prefix + "retained_W_current",
                step.point.current.values,
                cp.current.values,
                truth["current"],
                ct["truth"]["current"],
            )
            compare(
                prefix + "retained_W_section",
                step.section.geometry.one_form_hodge.matrix,
                cs.geometry.one_form_hodge.matrix,
                truth["H"],
                ct["truth"]["H"],
            )
    return rows


if __name__ == "__main__":
    unittest.main()
