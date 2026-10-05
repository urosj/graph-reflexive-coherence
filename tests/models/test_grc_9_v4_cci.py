"""Bounded native C_CI event: independent joint equations and atomic pressure.

The native Frobenius domain is separately identified from the P9-8.0 infinity
ball. No production result supplies the independent oracle's entry operands.
"""

from __future__ import annotations

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
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4CCIExpansion,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
    cci_profile_template,
)
from pygrc.models.grc_9_v4_lifecycle import GRC9V4CCIOperation, GRC9V4CCIState
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_ci import (
    CandidateCIRoot,
    CIStageError,
    ProvisionalCandidateCIStep,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import ExactBackend, current_exact_backend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph, PhysicalFlux
from pygrc.models.grc_v4_profile import list_supported_profiles
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from tests.models.test_grc_9_v4_lifecycle import native_cos_fixture
from tests.models.test_grc_v4_ci import configure

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "implementation/phase-9-grcv4/verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))
if importlib.util.find_spec("mpmath") is None:
    raise unittest.SkipTest("C_CI interval pressure requires research mpmath==1.3.0")
import test_p980_realization_numerical as oracle
from test_p980_os_effect_witness import PARAMS, full_error, number, separation

DT = 2**-12
RADIUS = 2**-18
TOLERANCE = 2**-44


def request_for(state, request):
    return replace(
        request,
        source_state_digest=state.scientific_digest,
        source_graph_digest=state.inputs.geometry.reference.graph.graph_digest,
        target_profile_template_id=cci_profile_template(
            state.inputs.geometry.reference
        ).profile_template_id,
        expected_event_id=None,
        expected_target_graph_digest=None,
    )


def fixture():
    # Inherit only declarations/graph/reset recipe; discard the OS physical output.
    declaration, request = native_cos_fixture()
    initial = configure(
        replace(
            declaration.inputs,
            current=GRCV4AuthoritativeState((3.0, *((193 / 64,) * 9)), None, None),
            step_index=0,
            time=0,
            dt=DT,
        ),
        radius=RADIUS,
        gain=0.5,
        tolerance=TOLERANCE,
    )
    step = ProvisionalCandidateCIStep(initial)
    seed = GRC9V4CCIState(replace(step.next_inputs, dt=0), declaration.specialization)
    return (
        seed,
        request_for(seed, replace(request, operation_id="native-cci-expand-1")),
        initial,
    )


def construction(state, request):
    ref = state.inputs.geometry.reference
    return GRC9V4CCIExpansion(
        GRC9V4ExpansionPlan(
            ref.graph.port_graph,
            state.scientific_digest,
            request,
            GRC9ExpansionPolicy.from_payload(
                state.specialization.resolved["expansion"]
            ),
        ),
        ref,
    )


def independent_model(inputs):
    graph = inputs.geometry.reference.graph.port_graph
    return oracle.RepresentedRows(
        graph.live_node_ids, [edge.to_payload() for edge in graph.edges], PARAMS
    )


def root_outputs(root):
    return {
        "H": np.array(root.selected.inputs.geometry.one_form_hodge.matrix),
        "J": np.array(root.current.values),
        "baseline": np.array(root.selected.point.algebra.baseline.values),
        "source": np.array(root.selected.structural_source.increment),
    }


def certify(inputs, root):
    """Independent interval full-formula/root error, not a solve-residual proxy."""
    model = independent_model(inputs)
    values = root_outputs(root)
    truth = oracle.certify_read(
        model, "C", "CI", np.array(inputs.current.C), None, None, values["H"], values
    )
    return model, values, truth


class NativeCCIPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = exact_backend(
            ExactBackend.FLINT
            if importlib.util.find_spec("flint")
            else ExactBackend.PYTHON
        )
        cls.backend.__enter__()
        cls.addClassCleanup(cls.backend.__exit__, None, None, None)
        cls.seed, cls.request, cls.initial = fixture()
        cls.owner = GRC9V4CCIOperation(cls.seed)
        result = cls.owner.expand(cls.request)
        assert result.committed, result.failure
        cls.committed = cls.owner.checkpoint()

    def assertRollback(self, owner, request, stage):
        before, state = owner.checkpoint(), owner.state
        result = owner.expand(request)
        self.assertFalse(result.committed)
        self.assertIs(owner.state, state)
        self.assertEqual(owner.checkpoint(), before)
        self.assertEqual(result.failure.stage, stage)
        self.assertEqual(
            result.failure.prestate_digest, result.failure.poststate_digest
        )
        self.assertEqual(
            result.failure.pre_lifecycle_digest, result.failure.post_lifecycle_digest
        )
        return result

    def test_source_beat_and_twenty_target_beats_against_independent_intervals(self):
        sequences = [self.initial]
        sequences.extend(
            replace(
                self.owner.state.inputs,
                current=getattr(self.owner.state.inputs, role),
                dt=DT,
            )
            for role in ("current", "reset")
        )
        for start, count in zip(sequences, (1, 10, 10), strict=True):
            inputs = start
            for _ in range(count):
                saved = np.array(inputs.current.C)  # before any native evaluation
                model = independent_model(inputs)
                expected, _ = oracle.evaluate(model, "C", "CI", saved)
                step = ProvisionalCandidateCIStep(inputs)
                _, values, truth = certify(inputs, step.root)
                after = truth["c"] - number(DT) * truth["high"].B * truth["read"]["J"]
                self.assertLess(
                    full_error(step.next_inputs.current.C, after),
                    oracle.RESOURCE_ERROR_LIMIT,
                )
                self.assertLess(
                    np.max(np.abs(values["J"] - expected["read"]["J"])), 2**-39
                )
                self.assertGreaterEqual(step.root.evaluations, 2)
                self.assertIsNone(step.writer)
                self.assertEqual(step.carrier_writes, 0)
                self.assertEqual(step.next_inputs.reset, inputs.reset)
                self.assertIsNone(step.next_inputs.current.W_A)
                self.assertIsNone(step.next_inputs.current.Z_4)
                self.assertGreater(min(step.next_inputs.current.C), 0)
                inputs = step.next_inputs
            certify(inputs, CandidateCIRoot(inputs))
        step = ProvisionalCandidateCIStep(self.initial)
        self.assertEqual(step.next_inputs.current, self.seed.inputs.current)
        self.assertEqual(self.initial.reset, self.seed.inputs.reset)

    def test_exact_map_complete_references_and_no_event_physical_step(self):
        before, after = self.seed.inputs, self.owner.state.inputs
        self.assertEqual(
            (after.time, after.step_index), (before.time, before.step_index)
        )
        self.assertEqual(after.dt, 0)
        ref = after.geometry.reference
        self.assertEqual(set(ref.edge_weights), set(ref.graph.live_edge_ids))
        self.assertEqual(set(ref.edge_weights.values()), {1.0})
        self.assertNotEqual(
            ref.profile.complete_profile_id,
            before.geometry.reference.profile.complete_profile_id,
        )
        self.assertNotIn(ref.profile.complete_profile_id, list_supported_profiles())
        target = construction(self.seed, self.request)
        transform = target.resource_transform_payload()
        width = len(before.current.C)
        for role in ("current", "reset"):
            old, new = getattr(before, role), getattr(after, role)
            exact = tuple(
                float(
                    sum(
                        (
                            Fraction(a) * Fraction(c)
                            for a, c in zip(
                                transform["row_major_coefficients"][i : i + width],
                                old.C,
                                strict=True,
                            )
                        ),
                        Fraction(),
                    )
                )
                for i in range(0, len(transform["row_major_coefficients"]), width)
            )
            self.assertEqual(new.C, exact)
            self.assertIsNone(new.W_A)
            self.assertIsNone(new.Z_4)
            self.assertLess(
                abs(sum(map(Fraction, new.C)) - Fraction(after.Q_target)),
                Fraction(1, 10**11),
            )
        self.assertEqual(len(self.owner.receipts), 4)
        topology = self.owner.receipts[0].to_payload()["identity_payload"]
        self.assertEqual(topology["schema_version"], "grcv4-topology-event-receipt-v1")
        self.assertEqual(topology["core"]["information_losses"], [])
        self.assertEqual(topology["core"]["actual_charge_delta"], 0.0)
        for subject, disposition in (
            ("candidate", "rederived"),
            ("carrier", "not_applicable"),
        ):
            self.assertEqual(
                topology["history"][subject],
                {
                    "subject": subject,
                    "disposition": disposition,
                    "source_history_digest": None,
                    "target_history_digest": None,
                    "information_loss": "none",
                },
            )

    def test_fresh_joint_reference_reads_stable_ids_zero_new_and_replay(self):
        checkpoint = json.loads(self.committed)
        reference = checkpoint["reference_currents"][0]
        old_ids = self.seed.inputs.geometry.reference.graph.live_edge_ids
        new_ids = self.owner.state.inputs.geometry.reference.graph.live_edge_ids
        previous = ProvisionalCandidateCIStep(self.initial).root.current.values
        for role in ("current", "reset"):
            inputs = replace(self.seed.inputs, current=getattr(self.seed.inputs, role))
            root = CandidateCIRoot(inputs)
            certify(inputs, root)
            observed = reference["roles"][role]
            self.assertEqual(observed["source"], list(root.current.values))
            old = dict(zip(old_ids, root.current.values, strict=True))
            self.assertEqual(observed["target"], [old.get(e, 0.0) for e in new_ids])
            if role == "current":
                self.assertNotEqual(observed["source"], list(previous))
        self.assertNotEqual(reference["roles"]["current"], reference["roles"]["reset"])
        self.assertNotIn("carrier_archives", checkpoint)
        self.assertEqual(
            GRC9V4CCIOperation.replay(self.committed).checkpoint(), self.committed
        )

    def test_event_zero_step_runs_both_roots_without_os_continuity_or_writer(self):
        with (
            patch.object(
                native, "ProvisionalCandidateCIStep", wraps=ProvisionalCandidateCIStep
            ) as calls,
            patch.object(
                native,
                "CandidateCOSPass",
                side_effect=AssertionError("OS substitution"),
            ),
            patch(
                "pygrc.models.grc_v4_step.CurrentSelection",
                side_effect=AssertionError("continuity"),
            ),
            patch(
                "pygrc.models.grc_v4_ci.CandidateAWriter",
                side_effect=AssertionError("writer"),
            ),
        ):
            owner = GRC9V4CCIOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)
            self.assertEqual(len(calls.call_args_list), 3)  # constructor/source/target
            self.assertTrue(all(c.args[0].dt == 0 for c in calls.call_args_list))

    def test_real_target_domain_failure_both_roles_and_reset_only(self):
        # These certify failure of the declared sufficient domain, not nonexistence of a root.
        for radius, current_passes in ((2**-19, False), (3e-6, True)):
            seed = replace(
                self.seed,
                inputs=configure(
                    self.seed.inputs, radius=radius, gain=0.5, tolerance=TOLERANCE
                ),
            )
            owner = GRC9V4CCIOperation(seed)  # both source roots really pass
            request = request_for(seed, self.request)
            target = construction(seed, request)
            for role in ("current", "reset"):
                inputs = replace(
                    seed.inputs,
                    geometry=target.target.geometry(),
                    current=target.transfer(getattr(seed.inputs, role)),
                    reset=target.transfer(seed.inputs.reset),
                )
                if role == "current" and current_passes:
                    CandidateCIRoot(inputs)
                else:
                    with self.assertRaisesRegex(CIStageError, "self-map"):
                        CandidateCIRoot(inputs)
            result = self.assertRollback(owner, request, "target_readmission")
            self.assertIn("self-map", result.failure.message)

    def test_authority_absence_is_strict_for_both_roles_even_zero_carrier(self):
        for role in ("current", "reset"):
            for field, values in (("W_A", (1.0,) * 9), ("Z_4", (0.0,) * 81)):
                with (
                    self.subTest(role=role, field=field),
                    self.assertRaises(ValueError),
                ):
                    inputs = replace(
                        self.seed.inputs,
                        **{
                            role: replace(
                                getattr(self.seed.inputs, role), **{field: values}
                            )
                        },
                    )
                    GRC9V4CCIOperation(replace(self.seed, inputs=inputs))
        with self.assertRaises(TypeError):
            native.GRC9V4COSOperation(self.seed)
        root = CandidateCIRoot(self.seed.inputs)
        with self.assertRaisesRegex(ValueError, "restart"):
            replace(
                self.seed,
                inputs=replace(
                    self.seed.inputs, geometry=root.selected.inputs.geometry
                ),
            )

    def test_rehashed_history_policy_cannot_add_candidate_or_carrier_history(self):
        owner = GRC9V4CCIOperation(self.seed)
        for subject, changes in (
            ("candidate", {"policy_id": "candidate_a_history_free_v1"}),
            (
                "carrier",
                {
                    "policy_id": "whole_carrier_reset_with_loss_receipt_v1",
                    "disposition": "whole_carrier_reset",
                    "source_history_digest": "grcv4-history-content-sha256:" + "0" * 64,
                    "target_initializer_id": "zero_carrier_v1",
                    "information_loss": "carrier_history_loss",
                },
            ),
        ):
            payload = self.request.to_payload()
            payload["history_policy"][subject].update(changes)
            payload["history_policy"][subject + "_history_policy_digest"] = (
                payload_identity(
                    "history_channel_policy_identity_payload",
                    {
                        "schema_version": "grcv4-history-channel-policy-identity-v1",
                        "policy": payload["history_policy"][subject],
                    },
                )
            )
            request = GRC9V4ExpansionRequestInput.from_payload(payload)
            self.assertRollback(owner, request, "target_construction")

    def test_both_charge_failures_and_late_publication_errors_roll_back(self):
        real = GRC9V4CCIExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4CCIOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                out = real(target, state)
                return (
                    replace(out, C=(out.C[0] + 1, *out.C[1:]))
                    if state == chosen
                    else out
                )

            with patch.object(GRC9V4CCIExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, "target_readmission")
        owner = GRC9V4CCIOperation(self.seed)
        with patch.object(
            native, "make_commit_receipts", side_effect=ValueError("late receipt")
        ):
            self.assertRollback(owner, self.request, "commit")
        with patch.object(
            GRC9V4CCIExpansion,
            "transfer_reference_current",
            side_effect=ValueError("late reference"),
        ):
            self.assertRollback(owner, self.request, "commit")
        self.assertTrue(owner.expand(self.request).committed)

    def test_replay_rejects_receipts_identities_roots_and_role_forgery(self):
        for path in (
            ("state", "scientific_digest"),
            ("receipts", 0, "receipt_id"),
            ("state", "inputs", "current", "C", 0),
            ("state", "inputs", "reset", "C", 0),
            ("reference_currents", 0, "roles", "current", "target", 0),
            ("reference_currents", 0, "roles", "reset", "source", 0),
        ):
            data = json.loads(self.committed)
            cursor = data
            for key in path[:-1]:
                cursor = cursor[key]
            old = cursor[path[-1]]
            cursor[path[-1]] = old + "x" if isinstance(old, str) else old + 2**-20
            with self.subTest(path=path), self.assertRaises((ValueError, TypeError)):
                GRC9V4CCIOperation.replay(canonical_json_bytes(data))
        data = json.loads(self.committed)
        refs = data["reference_currents"][0]["roles"]
        refs["current"] = deepcopy(refs["reset"])
        with self.assertRaises(ValueError):
            GRC9V4CCIOperation.replay(canonical_json_bytes(data))
        for role in ("current", "reset"):
            data = json.loads(self.committed)
            old = getattr(self.owner.state.inputs, role)
            c = (old.C[0] + 2**-20, old.C[1] - 2**-20, *old.C[2:])
            forged = replace(
                self.owner.state,
                inputs=replace(self.owner.state.inputs, **{role: replace(old, C=c)}),
            )
            data["state"] = forged.to_payload()
            data["lifecycle_digest"] = forged.lifecycle_digest(self.owner.receipts)
            with self.assertRaises(ValueError):
                GRC9V4CCIOperation.replay(canonical_json_bytes(data))

    def test_duplicate_concurrent_event_commits_once_and_owns_backend(self):
        owner = GRC9V4CCIOperation(self.seed)
        captured = current_exact_backend()
        seen = []
        real = native._cci_readmit

        def observe(state):
            seen.append(current_exact_backend())
            return real(state)

        with (
            exact_backend(ExactBackend.PYTHON),
            patch.object(native, "_cci_readmit", observe),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            results = list(pool.map(owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(owner.checkpoint(), self.committed)
        self.assertTrue(seen)
        self.assertEqual(set(seen), {captured})

    def test_real_iteration_exhaustion_current_and_reset_target_roots(self):
        for tolerance, current_passes in ((6e-9, False), (9e-9, True)):
            seed = replace(
                self.seed,
                inputs=configure(
                    self.seed.inputs,
                    radius=RADIUS,
                    gain=0.5,
                    tolerance=tolerance,
                    limit=1,
                ),
            )
            owner = GRC9V4CCIOperation(seed)
            request = request_for(seed, self.request)
            target = construction(seed, request)
            for role in ("current", "reset"):
                inputs = replace(
                    seed.inputs,
                    geometry=target.target.geometry(),
                    current=target.transfer(getattr(seed.inputs, role)),
                    reset=target.transfer(seed.inputs.reset),
                )
                if role == "current" and current_passes:
                    self.assertEqual(CandidateCIRoot(inputs).evaluations, 1)
                else:
                    with self.assertRaisesRegex(CIStageError, "iteration limit"):
                        CandidateCIRoot(inputs)
            result = self.assertRollback(owner, request, "target_readmission")
            self.assertIn("iteration limit", result.failure.message)

    def test_fixed_selected_geometry_path_effects_exceed_full_errors(self):
        # Named path ablations at the selected geometry, not alternate CI roots.
        for role in ("current", "reset"):
            inputs = replace(
                self.owner.state.inputs, current=getattr(self.owner.state.inputs, role)
            )
            root = CandidateCIRoot(inputs)
            model, values, truth = certify(inputs, root)
            for channel in ("modulation", "feedback", "geometry"):
                control = model.read(
                    "C",
                    np.array(inputs.current.C),
                    None,
                    values["H"],
                    **{channel: False},
                )
                exact_control = truth["high"].read(
                    "C", truth["c"], None, truth["H"], **{channel: False}
                )
                margin = separation(
                    values["J"], control["J"], truth["read"]["J"], exact_control["J"]
                )
                self.assertGreater(margin["minimum_margin_ratio"], 1)
            altered = dict(values, source=values["source"] * 2)
            with self.assertRaisesRegex(ValueError, "source binding"):
                oracle.certify_read(
                    model,
                    "C",
                    "CI",
                    np.array(inputs.current.C),
                    None,
                    None,
                    values["H"],
                    altered,
                )

    def test_joint_root_covariance_under_edge_reorder_and_orientation(self):
        for original in (self.seed.inputs, self.owner.state.inputs):
            baseline = CandidateCIRoot(original)
            base = root_outputs(baseline)
            ref = original.geometry.reference
            graph = ref.graph.port_graph
            n = len(graph.edges)
            for reverse, reorder in ((True, False), (False, True), (True, True)):
                permutation = list(reversed(range(n))) if reorder else list(range(n))
                signs = [-1 if reverse and i % 2 == 0 else 1 for i in permutation]
                edges = tuple(
                    replace(
                        graph.edges[i],
                        tail=graph.edges[i].head,
                        head=graph.edges[i].tail,
                    )
                    if sign < 0
                    else graph.edges[i]
                    for i, sign in zip(permutation, signs, strict=True)
                )
                new_graph = GRC9V4PortGraph(graph.live_node_ids, edges)
                new_ref = replace(ref, graph=GRCV4Graph.from_port_graph(new_graph))
                inputs = replace(original, geometry=new_ref.geometry())
                root = CandidateCIRoot(inputs)
                certify(inputs, root)
                out = root_outputs(root)
                expected = base["J"][permutation] * np.array(signs)
                self.assertLess(np.max(np.abs(out["J"] - expected)), 2**-39)
                expected_h = base["H"][np.ix_(permutation, permutation)] * np.outer(
                    signs, signs
                )
                self.assertLess(np.max(np.abs(out["H"] - expected_h)), 2**-47)
                self.assertLess(
                    np.max(
                        np.abs(
                            np.array(new_ref.graph.incidence) @ out["J"]
                            - np.array(ref.graph.incidence) @ base["J"]
                        )
                    ),
                    2**-38,
                )

    def test_simplex_vertices_fail_narrow_domain_and_admit_explicit_wider_domain(self):
        # No adaptive radius widening: each radius is declared in the source profile.
        for shares in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            owner = GRC9V4CCIOperation(self.seed)
            request = replace(self.request, resource_distribution=shares)
            result = self.assertRollback(owner, request, "target_readmission")
            self.assertIn("self-map", result.failure.message)
            seed = replace(
                self.seed,
                inputs=configure(
                    self.seed.inputs, radius=2**-17, gain=0.5, tolerance=TOLERANCE
                ),
            )
            owner = GRC9V4CCIOperation(seed)
            result = owner.expand(request_for(seed, request))
            self.assertTrue(result.committed, result.failure)
            for role in ("current", "reset"):
                inputs = replace(
                    owner.state.inputs, current=getattr(owner.state.inputs, role)
                )
                self.assertGreaterEqual(inputs.current.C.count(0.0), 7)
                certify(inputs, CandidateCIRoot(inputs))

    def test_source_cutoff_postbeat_and_reference_graph_fail_closed(self):
        for cutoff in (1.0, 10.0):
            inputs = configure(
                self.seed.inputs,
                radius=RADIUS,
                gain=0.5,
                tolerance=TOLERANCE,
                changes={"candidate": {"Lambda_C": cutoff}},
            )
            with self.assertRaises(ValueError):
                GRC9V4CCIOperation(replace(self.seed, inputs=inputs))
        seed = replace(self.seed, inputs=replace(self.seed.inputs, step_index=0))
        owner = GRC9V4CCIOperation(seed)
        self.assertRollback(owner, request_for(seed, self.request), "admission")
        target = construction(self.seed, self.request)
        foreign = PhysicalFlux(
            target.target.graph, (0.0,) * len(target.target.graph.live_edge_ids)
        )
        with self.assertRaisesRegex(ValueError, "source graph"):
            target.transfer_reference_current(foreign)

    def test_authorization_binds_exact_G2_predecessor_and_immutable_research(self):
        import phase9_specialization_acceptance as entry

        self.assertEqual(entry.cci_authorization(ROOT), "P9-8.3C-CI")
        for path in entry.CCI_PATHS:
            self.assertTrue(entry.cci_permitted(path, "P9-8.3C-CI"))
            self.assertFalse(entry.cci_permitted(path, "P9-8.3A.2"))
        for path in ("src/pygrc/models/grc_v4_ci.py", "specs/grc-9-v4-spec.md"):
            self.assertFalse(entry.cci_permitted(path, "P9-8.3C-CI"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.cci_authorization(ROOT)
        bad = dict(entry.CCI_PREDECESSOR_HASHES)
        bad[entry.CCI_RESEARCH_PATHS[0]] = "0" * 64
        with (
            patch.object(entry, "CCI_PREDECESSOR_HASHES", bad),
            self.assertRaises(ValueError),
        ):
            entry.cci_authorization(ROOT)


if __name__ == "__main__":
    unittest.main()
