"""Native A_CI+PC pressure against the accepted immutable A.1 oracle."""

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
from pygrc.models import grc_v4_ci as ci
from pygrc.models import grc_v4_pc as pc
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4ACIPCExpansion,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
    acipc_profile_template,
)
from pygrc.models.grc_9_v4_lifecycle import (
    GRC9V4ACIPCOperation,
    GRC9V4ACIPCState,
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
        "A_CI+PC interval pressure requires research dependency mpmath==1.3.0"
    )
import verify_p983a_acipc_oracle as oracle

RECORD = ROOT / oracle.RECORD
ORACLE_SHA = "e34243fd149d4f4cccc720232a3d7d2ac92b04a7e16059e8adf04f839c2a7238"


def authority(value):
    return GRCV4AuthoritativeState(
        tuple(value["C"]), tuple(value["W_A"]), tuple(value["Z_4"])
    )


def authority_payload(value):
    return {"C": list(value.C), "W_A": list(value.W_A), "Z_4": list(value.Z_4)}


def role_inputs(inputs, state, *, dt=oracle.DT):
    return replace(
        inputs, current=state, geometry=inputs.geometry.reference.geometry(), dt=dt
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
        "acipc-seed",
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
    return GRC9V4ACIPCState(inputs, spec), GRC9V4ExpansionRequestInput.from_payload(
        record["request"]
    )


def request_for(state, request):
    data = request.to_payload()
    data.update(
        source_state_digest=state.scientific_digest,
        target_profile_template_id=acipc_profile_template(
            state.inputs.geometry.reference
        ).profile_template_id,
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
    inputs,
    *,
    candidate_changes=None,
    pc_changes=None,
    geometry_changes=None,
    solver_changes=None,
):
    ref = inputs.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    ident = ref.profile.identity_payload.to_payload()
    for key, changes in (
        ("candidate", candidate_changes),
        ("realization", pc_changes),
        ("geometry", geometry_changes),
        ("solver", solver_changes),
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
        "current": step.root.selected.point.current.values,
        "baseline": step.root.selected.point.baseline.values,
        "H": step.root.selected.point.inputs.geometry.one_form_hodge.matrix,
        "source": step.root.selected.structural_source.increment,
    }


def checked(inputs, backend):
    step = ci.ProvisionalCandidateCIStep(inputs, backend)
    graph = backend.port_graph.to_payload()
    s = inputs.current
    proof = oracle.check_step(graph, s.C, s.W_A, s.Z_4, outputs(step))
    return step, proof


def root_proof(inputs, backend, root):
    """Independent literal joint equations at the represented selected pair."""
    high = oracle.IntervalRows(oracle.model_for(backend.port_graph.to_payload()))
    s = inputs.current
    c, w = oracle.vector(s.C), oracle.vector(s.W_A)
    z = oracle.IV.matrix(np.asarray(s.Z_4).reshape(len(s.W_A), -1).tolist())
    h = oracle.IV.matrix(root.selected.inputs.geometry.one_form_hodge.matrix)
    point = high.read("A", c, w, h)
    drive = high.conductance(c, w, point["baseline"])
    contrast = [(x - g) / (x + g) for x, g in zip(w, drive, strict=True)]
    j = oracle.vector(root.current.values)
    causal = oracle.IV.matrix([q * x / 16 for q, x in zip(contrast, j, strict=True)])
    fj = j - point["baseline"] - causal / 2
    flat = oracle.inverse(h) * causal
    source = oracle.IV.matrix(
        [
            [
                oracle.number(high.mask[i, k]) * flat[i] * flat[k] / 2
                for k in range(j.rows)
            ]
            for i in range(j.rows)
        ]
    )
    fh = h - high.I - oracle.number(oracle.KAPPA_H) * (z + source)
    joint = oracle.sqrt_upper(oracle.norm(fj) ** 2 + oracle.norm(fh) ** 2)
    if joint > Q(
        inputs.geometry.reference.profile.params_resolved.realization.tolerance
    ):
        raise ValueError("independent joint residual exceeds tolerance")
    truth = oracle.enclosed_root(high, c, w, z, h)
    return {
        "joint_residual": str(joint),
        "root_error": str(truth["root_error"]),
        "current_error": str(
            oracle.full_error(root.current.values, truth["read"]["J"])
        ),
        "contraction_upper": str(truth["certificate"]["contraction_upper"]),
    }


def corner_roots(seed, target):
    results = []
    for label, state in (("source", seed), ("target", target)):
        n, m = len(state.inputs.current.C), len(state.inputs.current.W_A)
        for vertex in (0, n - 1):
            c = tuple(16.0 if i == vertex else 0.0 for i in range(n))
            for weights in ("low", "high", "alternating"):
                w = tuple(
                    oracle.W_MIN
                    if weights == "low" or (weights == "alternating" and i % 2 == 0)
                    else oracle.W_MAX
                    for i in range(m)
                )
                for sign in (-1, 1):
                    z = (sign * float(oracle.RADIUS),) + (0.0,) * (m * m - 1)
                    inputs = role_inputs(
                        state.inputs, GRCV4AuthoritativeState(c, w, z), dt=0
                    )
                    row = {
                        "graph": label,
                        "vertex": vertex,
                        "weights": weights,
                        "carrier_sign": sign,
                    }
                    try:
                        root = ci.CandidateCIRoot(inputs, state.differential_reference)
                    except ci.CIStageError as error:
                        # Whole-chart existence is not a promise that binary64
                        # can attain every requested residual tolerance.
                        if "iteration limit" not in str(error):
                            raise
                        row.update(result="iteration_limit", reason=str(error))
                    else:
                        row.update(
                            result="root",
                            evaluations=root.evaluations,
                            proof=root_proof(
                                inputs, state.differential_reference, root
                            ),
                        )
                    results.append(row)
    return results


def native_effects(seed, target):
    """Native ablations; independent intervals include root and composed errors."""
    effects = []
    for label, state in (("source", seed), ("target", target)):
        backend = state.differential_reference
        for role in ("current", "reset"):
            inputs = role_inputs(state.inputs, getattr(state.inputs, role))
            step, truth = checked(inputs, backend)
            point, high = step.root.selected.point, truth["high"]

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
                ("geometry", {"kappa_Ah": 0}),
                ("feedback", {"chi_A": 0}),
            ):
                alt = configure(inputs, candidate_changes=changes)
                geometry = replace(
                    point.inputs.geometry, reference=alt.geometry.reference
                )
                off = candidate.CandidateACurrent(
                    replace(alt, geometry=geometry), backend
                )
                exact = high.read(
                    "A", truth["c"], truth["w"], truth["H"], **{flag: False}
                )
                compare(
                    flag + "_at_selected_H",
                    point.current.values,
                    off.current.values,
                    truth["read"]["J"],
                    exact["J"],
                )

            def enclosure(root, c, w, z, high=high):
                return oracle.enclosed_root(
                    high,
                    c,
                    w,
                    z,
                    oracle.IV.matrix(
                        root.selected.inputs.geometry.one_form_hodge.matrix
                    ),
                )

            zero = (0.0,) * len(inputs.current.Z_4)
            zi = oracle.IV.zeros(len(inputs.current.W_A))
            if label == "source":
                off = ci.CandidateCIRoot(
                    role_inputs(inputs, replace(inputs.current, Z_4=zero)), backend
                )
                exact = enclosure(off, truth["c"], truth["w"], zi)
                compare(
                    "old_Z_complete_root_current",
                    point.current.values,
                    off.current.values,
                    truth["read"]["J"],
                    exact["read"]["J"],
                )
                compare(
                    "old_Z_complete_root_geometry",
                    point.inputs.geometry.one_form_hodge.matrix,
                    off.selected.inputs.geometry.one_form_hodge.matrix,
                    truth["H"],
                    exact["H"],
                )
                continue

            # PC timing ablation: solve at old-Z geometry with the same A law.
            old_h = pc.carrier_geometry(inputs, inputs.current)
            off = candidate.CandidateACurrent(replace(inputs, geometry=old_h), backend)
            exact = oracle.enclosed_root(
                high,
                truth["c"],
                truth["w"],
                truth["z"],
                oracle.IV.matrix(old_h.one_form_hodge.matrix),
                instant=False,
            )
            compare(
                "instantaneous_source_vs_PC_current",
                point.current.values,
                off.current.values,
                truth["read"]["J"],
                exact["read"]["J"],
            )

            after = step.next_inputs.current

            def next_pair(
                w,
                z,
                wi,
                zi,
                after=after,
                step=step,
                backend=backend,
                truth=truth,
                enclosure=enclosure,
            ):
                changed = replace(after, W_A=tuple(w), Z_4=tuple(z))
                root = ci.CandidateCIRoot(
                    role_inputs(step.next_inputs, changed, dt=0), backend
                )
                return root, enclosure(root, truth["C"], wi, zi)

            nxt, ni = next_pair(after.W_A, after.Z_4, truth["W_A"], truth["Z_4"])
            off, oi = next_pair(after.W_A, zero, truth["W_A"], zi)
            compare(
                "written_carrier_next_current",
                nxt.current.values,
                off.current.values,
                ni["read"]["J"],
                oi["read"]["J"],
            )
            compare(
                "written_carrier_next_geometry",
                nxt.selected.inputs.geometry.one_form_hodge.matrix,
                off.selected.inputs.geometry.one_form_hodge.matrix,
                ni["H"],
                oi["H"],
            )

            # Forbidden source recomputation at post-continuity C/W, selected H.
            wrong_point = candidate.CandidateACurrent(
                replace(inputs, current=after, geometry=point.inputs.geometry), backend
            )
            source = ci._source_from_flat(wrong_point, wrong_point.read.causal_flat)
            wrong_z = pc.scalar_zoh(
                inputs.current.Z_4,
                tuple(x for row in source.increment for x in row),
                oracle.DT,
                1,
            )
            wrong_si = high.read("A", truth["C"], truth["W_A"], truth["H"])["source"]
            decay = oracle.IV.exp(-oracle.number(oracle.DT))
            wrong_zi = decay * truth["z"] + (1 - decay) * wrong_si
            compare(
                "same_root_source_Z_writer", after.Z_4, wrong_z, truth["Z_4"], wrong_zi
            )
            off, oi = next_pair(after.W_A, wrong_z, truth["W_A"], wrong_zi)
            compare(
                "same_root_source_next_current",
                nxt.current.values,
                off.current.values,
                ni["read"]["J"],
                oi["read"]["J"],
            )

            params = inputs.geometry.reference.profile.params_resolved.candidate
            for name, c, j, ci_values, ji in (
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
                wi = high.write(ci_values, truth["w"], ji)
                compare(name + "_W", after.W_A, wrong_w, truth["W_A"], wi)
                off, oi = next_pair(wrong_w, after.Z_4, wi, truth["Z_4"])
                compare(
                    name + "_next_current",
                    nxt.current.values,
                    off.current.values,
                    ni["read"]["J"],
                    oi["read"]["J"],
                )
            off, oi = next_pair(inputs.current.W_A, after.Z_4, truth["w"], truth["Z_4"])
            compare(
                "next_current_consumes_written_W",
                nxt.current.values,
                off.current.values,
                ni["read"]["J"],
                oi["read"]["J"],
            )
    return effects


class NativeACIPCPressure(unittest.TestCase):
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
        cls.owner = GRC9V4ACIPCOperation(cls.seed)
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
            GRC9V4ACIPCOperation.replay(owner.checkpoint()).checkpoint(),
            owner.checkpoint(),
        )

    def test_policy_rehashed_role_substitutions_fail_at_admission(self):
        owner = GRC9V4ACIPCOperation(self.seed)
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
        original = GRC9V4ACIPCExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4ACIPCOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                value = original(target, state)
                return (
                    replace(value, C=(value.C[0] + 1, *value.C[1:]))
                    if state == chosen
                    else value
                )

            with patch.object(GRC9V4ACIPCExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, stage="target_readmission")
        owner = GRC9V4ACIPCOperation(self.seed)
        with patch.object(
            native,
            "make_commit_receipts",
            side_effect=ValueError("late receipt failure"),
        ):
            self.assertRollback(owner, self.request, stage="commit")
        with patch.object(
            GRC9V4ACIPCExpansion,
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
                GRC9V4ACIPCOperation.replay(canonical_json_bytes(data))
        data = json.loads(self.committed)
        data["reference_currents"][0]["roles"]["current"] = data["reference_currents"][
            0
        ]["roles"]["reset"]
        with self.assertRaises(ValueError):
            GRC9V4ACIPCOperation.replay(canonical_json_bytes(data))

    def test_duplicate_concurrent_event_publishes_only_once(self):
        owner = GRC9V4ACIPCOperation(self.seed)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(len(owner.receipts), 4)
        self.assertEqual(owner.checkpoint(), self.committed)

    def test_receiver_owns_exact_backend_across_context_changes(self):
        if importlib.util.find_spec("flint") is None:
            self.skipTest("cross-backend ownership requires optional v4-flint")
        owner = GRC9V4ACIPCOperation(self.seed)
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
                GRC9V4ACIPCOperation.replay(canonical_json_bytes(data))
        seed = replace(self.seed, inputs=replace(self.seed.inputs, step_index=0))
        owner = GRC9V4ACIPCOperation(seed)
        result = self.assertRollback(
            owner, request_for(seed, self.request), stage="admission"
        )
        self.assertIn("postbeat", result.failure.message)
        # CI starts from reference geometry and reads the authoritative old Z.
        # Zero old Z is valid; it does not leave a stale PC geometry cache.
        inputs = replace(
            self.seed.inputs,
            current=replace(self.seed.inputs.current, Z_4=(0.0,) * 81),
        )
        GRC9V4ACIPCOperation(replace(self.seed, inputs=inputs))

    def test_A2_authorization_is_exact_and_cannot_replace_accepted_oracle(self):
        import phase9_specialization_acceptance as entry

        self.assertEqual(entry.acipc_authorization(ROOT), "P9-8.3A.2")
        for path in entry.ACIPC_PATHS:
            self.assertTrue(entry.acipc_permitted(path, "P9-8.3A.2"))
            self.assertFalse(entry.acipc_permitted(path, "P9-8.3A.1"))
        for path in (
            "specs/grc-9-v4-spec.md",
            "src/pygrc/models/grc_9_v3.py",
            "src/pygrc/models/grc_v4_rg2b.py",
        ):
            self.assertFalse(entry.acipc_permitted(path, "P9-8.3A.2"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.acipc_authorization(ROOT)

        bad = dict(entry.ACIPC_ORACLE_HASHES)
        bad[oracle.RECORD] = "0" * 64
        with (
            patch.object(entry, "ACIPC_ORACLE_HASHES", bad),
            self.assertRaises(ValueError),
        ):
            entry.acipc_authorization(ROOT)

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
                GRC9V4ACIPCOperation.replay(canonical_json_bytes(data))
        owner = GRC9V4ACIPCOperation(self.seed)
        with patch.object(
            GRC9V4ACIPCExpansion,
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
        actual = GRC9V4ACIPCState(
            replace(step.next_inputs, dt=0), self.seed.specialization
        )
        owner = GRC9V4ACIPCOperation(actual)
        self.assertTrue(owner.expand(request_for(actual, self.request)).committed)
        content = owner.carrier_archives[0]["history_content"]["content"]
        self.assertEqual(
            tuple(content), actual.inputs.current.Z_4 + actual.inputs.reset.Z_4
        )
        # The read-only probe has a distinct hypothetical writer output, never archived.
        hypothetical = ci.ProvisionalCandidateCIStep(
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
                "ProvisionalCandidateCIStep",
                wraps=ci.ProvisionalCandidateCIStep,
            ) as zero,
            patch.object(
                ci, "CandidateAWriter", side_effect=AssertionError("event W write")
            ),
            patch.object(pc, "scalar_zoh", side_effect=AssertionError("event Z write")),
        ):
            owner = GRC9V4ACIPCOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)
            self.assertTrue(all(call.args[0].dt == 0 for call in zero.call_args_list))
        self.assertEqual(owner.state.inputs.step_index, self.seed.inputs.step_index)
        self.assertEqual(owner.state.inputs.time, self.seed.inputs.time)
        for role in ("current", "reset"):
            self.assertEqual(getattr(owner.state.inputs, role).Z_4, (0.0,) * 256)

    def test_both_carrier_roles_are_bound_in_request_and_loss_is_separate(self):
        owner = GRC9V4ACIPCOperation(self.seed)
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
        original = GRC9V4ACIPCExpansion.__post_init__

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

        owner = GRC9V4ACIPCOperation(self.seed)
        with patch.object(GRC9V4ACIPCExpansion, "__post_init__", oversized):
            failure = self.assertRollback(
                owner, self.request, stage="target_readmission"
            )
        self.assertIn("source envelope", failure.failure.message)
        # Actual bad authority in current-only/reset-only targets rejects atomically.
        transfer = GRC9V4ACIPCExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4ACIPCOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                out = transfer(target, state)
                return (
                    replace(out, W_A=(0.49, *out.W_A[1:])) if state == chosen else out
                )

            with patch.object(GRC9V4ACIPCExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, stage="target_readmission")

    def test_admitted_negative_continuation_rejects_physical_step_both_roles(self):
        negative = authority(
            self.record["boundary_witnesses"]["admitted_event_negative_next_step"][
                "source_role"
            ]
        )
        for role in ("current", "reset"):
            seed = altered_role(self.seed, role, negative)
            owner = GRC9V4ACIPCOperation(seed)
            self.assertTrue(owner.expand(request_for(seed, self.request)).committed)
            before = owner.checkpoint()
            target = owner.state
            inputs = role_inputs(target.inputs, getattr(target.inputs, role))
            high = oracle.IntervalRows(
                oracle.model_for(target.differential_reference.port_graph.to_payload())
            )
            root = ci.CandidateCIRoot(inputs, target.differential_reference)
            truth = oracle.enclosed_root(
                high,
                oracle.vector(inputs.current.C),
                oracle.vector(inputs.current.W_A),
                oracle.IV.matrix(
                    np.asarray(inputs.current.Z_4).reshape(16, 16).tolist()
                ),
                oracle.IV.matrix(root.selected.inputs.geometry.one_form_hodge.matrix),
            )
            after = (
                oracle.vector(inputs.current.C)
                - oracle.number(oracle.DT) * high.B * truth["read"]["J"]
            )
            self.assertLess(min(oracle.endpoint(x, 1) for x in after), 0)
            with self.assertRaises(ResourceBoundaryError) as error:
                ci.ProvisionalCandidateCIStep(inputs, target.differential_reference)
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
                step = ci.ProvisionalCandidateCIStep(
                    replace(state.inputs, dt=oracle.DT), backend
                )
                replay = ci.ProvisionalCandidateCIStep.from_payload(step.to_payload())
                self.assertEqual(replay.to_payload(), step.to_payload())
                self.assertEqual(replay.next_inputs, step.next_inputs)
                point = step.root.selected.point
                self.assertEqual(
                    candidate.CandidateACurrent.from_payload(
                        point.to_payload()
                    ).to_payload(),
                    point.to_payload(),
                )
            proof = oracle.whole_chart(backend.port_graph.to_payload())
            bounds = step.root.certificate.bounds["composite_envelope"]
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
                ci.ProvisionalCandidateCIStep.from_payload(data)

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

    def test_carrier_sphere_support_boundary_and_stale_geometry(self):
        state = self.owner.state
        inputs = state.inputs
        m = len(inputs.current.W_A)
        z = [0.0] * (m * m)
        z[0] = oracle.RADIUS
        authority_good = replace(inputs.current, Z_4=tuple(z))
        ci.CandidateCIRoot(
            role_inputs(inputs, authority_good, dt=0), state.differential_reference
        )
        bad = list(z)
        bad[0] = np.nextafter(float(oracle.RADIUS), np.inf)
        with self.assertRaises(pc.PCStageError):
            ci.CandidateCIRoot(
                role_inputs(inputs, replace(authority_good, Z_4=tuple(bad)), dt=0),
                state.differential_reference,
            )
        with self.assertRaises(ValueError):
            GRC9V4ACIPCState(
                replace(
                    inputs,
                    current=authority_good,
                    geometry=pc.carrier_geometry(inputs, authority_good),
                ),
                state.specialization,
            )
        bad = list(z)
        bad[1] = 2**-20
        with self.assertRaises(ValueError):
            ci.CandidateCIRoot(
                role_inputs(inputs, replace(authority_good, Z_4=tuple(bad)), dt=0),
                state.differential_reference,
            )
        for role in ("current", "reset"):
            with self.assertRaises((ValueError, TypeError)):
                GRC9V4ACIPCOperation(
                    altered_role(
                        self.seed,
                        role,
                        replace(getattr(self.seed.inputs, role), Z_4=None),
                    )
                )

    def test_native_effects_clear_all_thirty_two_full_error_ULP_controls(self):
        effects = native_effects(self.seed, self.owner.state)
        self.assertEqual(len(effects), 32)
        self.assertGreater(min(x["minimum_margin_ratio"] for x in effects), 1)

    def test_all_twenty_four_chart_corners_satisfy_independent_joint_equations(self):
        rows = corner_roots(self.seed, self.owner.state)
        self.assertEqual(len(rows), 24)
        self.assertTrue(all(row["result"] == "root" for row in rows))
        for row in rows:
            self.assertLess(Q(row["proof"]["current_error"]), Q(2**-40))
            self.assertLess(Q(row["proof"]["root_error"]), Q(2**-48))

    def test_composite_domain_and_strict_source_slack_are_not_PC_shortcuts(self):
        inputs, backend = self.seed.inputs, self.seed.differential_reference
        too_small = ci.CIBoundedDomain(float(np.nextafter(oracle.ROOT_RADIUS, 0)))
        with self.assertRaisesRegex(ValueError, "B_2R"):
            ci.CandidateCIRoot(
                configure(
                    inputs,
                    pc_changes={
                        "contraction_domain_id": too_small.identity,
                    },
                ),
                backend,
            )
        # Reusing the accepted PC coupling with the required doubled chart
        # loses the composite uniform source slack, despite regular point reads.
        with self.assertRaisesRegex(ValueError, "source envelope"):
            ci.CandidateCIRoot(
                configure(
                    inputs,
                    pc_changes={
                        "contraction_domain_id": ci.CIBoundedDomain(0.25).identity,
                    },
                    geometry_changes={"kappa_H": 2**-14},
                ),
                backend,
            )
        for state in (self.seed, self.owner.state):
            root = ci.CandidateCIRoot(state.inputs, state.differential_reference)
            b = root.certificate.bounds.to_dict()
            self.assertLess(
                Q(b["composite_envelope"]["source_norm_upper"]), oracle.RADIUS
            )
            self.assertLess(Q(b["contraction_upper"]), 1)

    def test_same_root_source_and_incoming_W_feed_exactly_one_writer_each(self):
        state = self.owner.state
        inputs = replace(state.inputs, dt=oracle.DT)
        real = GRC9V4CandidateADifferentialReference.rebuild
        calls = []

        def observe(backend, c, w):
            calls.append((c.values, w))
            return real(backend, c, w)

        with (
            patch.object(GRC9V4CandidateADifferentialReference, "rebuild", observe),
            patch.object(pc, "scalar_zoh", wraps=pc.scalar_zoh) as write,
        ):
            step = ci.ProvisionalCandidateCIStep(inputs, state.differential_reference)
        write.assert_called_once_with(
            inputs.current.Z_4,
            tuple(
                x for row in step.root.selected.structural_source.increment for x in row
            ),
            oracle.DT,
            1.0,
        )
        self.assertEqual(step.carrier_writes, 1)
        self.assertIn((step.resource.provisional_state.C, inputs.current.W_A), calls)
        self.assertIn((step.next_inputs.current.C, step.next_inputs.current.W_A), calls)
        self.assertEqual(step.next_inputs.reset, inputs.reset)
        self.assertEqual(step.writer.point, step.root.selected.point)
        high = oracle.IntervalRows(
            oracle.model_for(state.differential_reference.port_graph.to_payload())
        )
        drive = high.conductance(
            oracle.vector(step.resource.provisional_state.C),
            oracle.vector(inputs.current.W_A),
            oracle.vector(step.root.current.values),
        )
        self.assertLess(oracle.full_error(step.writer.W_drv_A, drive), Q(2**-48))

    def test_confirming_composite_recipe_is_distinct_and_replay_bound(self):
        step = ci.ProvisionalCandidateCIStep(
            replace(self.seed.inputs, dt=oracle.DT), self.seed.differential_reference
        )
        for value in (step.root, step):
            data = value.to_payload()
            self.assertEqual(data["numerics"], ci.GRC9_ACIPC_NUMERICS)
            for other in (ci.GRC9_ACI_NUMERICS, ci.CIPC_NUMERICS, ci.NUMERICS):
                forged = {**data, "numerics": other}
                with self.assertRaisesRegex(ValueError, "recipe"):
                    type(value).from_payload(forged)
        inputs = configure(
            self.seed.inputs,
            pc_changes={"iteration_limit": 2},
            solver_changes={"iteration_limit": 2},
        )
        with self.assertRaisesRegex(ci.CIStageError, "iteration limit"):
            ci.CandidateCIRoot(inputs, self.seed.differential_reference)

    def test_frozen_reference_conductance_cannot_pass_native_analytic_residual(self):
        backend = self.seed.differential_reference
        inputs = role_inputs(self.seed.inputs, self.seed.inputs.reset, dt=0)
        # A realistic implementation defect: freeze the reference-H conductance
        # while letting the rest of the simultaneous solve continue to update.
        frozen = candidate.CandidateACurrent(inputs, backend).W_hat_A
        with (
            patch.object(candidate, "_conductance", return_value=frozen),
            self.assertRaisesRegex(ci.CIStageError, "iteration limit"),
        ):
            ci.CandidateCIRoot(inputs, backend)

    def test_real_current_and_reset_only_iteration_failures_roll_back(self):
        for tolerance, current_passes in ((5e-9, False), (1e-8, True)):
            inputs = configure(
                self.seed.inputs,
                pc_changes={"tolerance": tolerance, "iteration_limit": 2},
                solver_changes={"iteration_limit": 2},
            )
            current = replace(inputs.current, Z_4=(0.0,) * 81)
            reset = replace(current, W_A=(0.875,) * 9)
            inputs = replace(inputs, current=current, reset=reset)
            seed = replace(self.seed, inputs=inputs)
            owner = GRC9V4ACIPCOperation(seed)
            request = request_for(seed, self.request)
            plan = GRC9V4ExpansionPlan(
                inputs.geometry.reference.graph.port_graph,
                seed.scientific_digest,
                request,
                GRC9ExpansionPolicy.from_payload(
                    seed.specialization.resolved["expansion"]
                ),
            )
            construction = GRC9V4ACIPCExpansion(
                plan, inputs.geometry.reference, inputs.current, inputs.reset
            )
            ref = construction.target
            backend = GRC9V4CandidateADifferentialReference(plan.target_graph)
            for role in ("current", "reset"):
                mapped = replace(
                    inputs,
                    geometry=ref.geometry(),
                    current=construction.transfer(getattr(inputs, role)),
                    reset=construction.transfer(inputs.reset),
                )
                if role == "current" and current_passes:
                    self.assertEqual(ci.CandidateCIRoot(mapped, backend).evaluations, 2)
                else:
                    with self.assertRaisesRegex(ci.CIStageError, "iteration limit"):
                        ci.CandidateCIRoot(mapped, backend)
            result = self.assertRollback(owner, request, stage="target_readmission")
            self.assertIn("iteration limit", result.failure.message)

    def test_signed_permutations_covary_W_Z_geometry_and_source(self):
        for name, state in (("source", self.seed), ("target", self.owner.state)):
            g = state.differential_reference.port_graph.to_payload()
            values = state.inputs.current
            base = outputs(
                ci.ProvisionalCandidateCIStep(
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
