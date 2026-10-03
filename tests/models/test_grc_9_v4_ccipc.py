"""Native C_CI+PC event pressure against independent paper equations."""

from __future__ import annotations

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
from pygrc.models import grc_v4_ci as ci
from pygrc.models import grc_v4_pc as pc
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4CCIPCExpansion,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
    ccipc_profile_template,
    cpc_history_policy,
)
from pygrc.models.grc_9_v4_lifecycle import GRC9V4CCIPCOperation, GRC9V4CCIPCState
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import ExactBackend, current_exact_backend, exact_backend
from pygrc.models.grc_v4_geometry import (
    GRCV4Geometry,
    GRCV4Graph,
    PhysicalFlux,
)
from pygrc.models.grc_v4_profile import list_supported_profiles, resolve_profile
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_9_v4_lifecycle import native_cpc_fixture
from tests.models.test_grc_v4_cipc import configure

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "implementation/phase-9-grcv4/verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))
if importlib.util.find_spec("mpmath") is None:
    raise unittest.SkipTest("C_CI+PC pressure requires research mpmath==1.3.0")
import verify_p983ccipc_native as oracle
from test_p980_os_effect_witness import separation


def request_for(state, request):
    return replace(
        request,
        operation_id="native-ccipc-expand-1",
        source_state_digest=state.scientific_digest,
        source_graph_digest=state.inputs.geometry.reference.graph.graph_digest,
        target_profile_template_id=ccipc_profile_template(
            state.inputs.geometry.reference
        ).profile_template_id,
        history_policy=cpc_history_policy(state.inputs.current, state.inputs.reset),
        expected_event_id=None,
        expected_target_graph_digest=None,
    )


def fixture():
    # C_PC supplies only the accepted declared compact chart/resource/Z recipe.
    # Discard its physical output; C_CI+PC executes its own source beat.
    declaration, request, initial = native_cpc_fixture()
    initial = configure(
        initial, domain_radius=oracle.ROOT_RADIUS, tolerance=oracle.TOLERANCE, limit=60
    )
    step = ci.ProvisionalCandidateCIStep(initial)
    seed = GRC9V4CCIPCState(replace(step.next_inputs, dt=0), declaration.specialization)
    return seed, request_for(seed, request), initial


def construction(seed, request):
    ref = seed.inputs.geometry.reference
    plan = GRC9V4ExpansionPlan(
        ref.graph.port_graph,
        seed.scientific_digest,
        request,
        GRC9ExpansionPolicy.from_payload(seed.specialization.resolved["expansion"]),
    )
    return GRC9V4CCIPCExpansion(plan, ref, seed.inputs.current, seed.inputs.reset)


def outputs(root):
    return {
        "H": np.array(root.selected.inputs.geometry.one_form_hodge.matrix),
        "J": np.array(root.current.values),
        "baseline": np.array(root.selected.point.algebra.baseline.values),
        "source": np.array(root.selected.structural_source.increment),
    }


def certify(inputs, root):
    graph = inputs.geometry.reference.graph.port_graph.to_payload()
    return oracle.certify(graph, inputs.current.C, inputs.current.Z_4, outputs(root))


def reconfigure(inputs, *, candidate=None, realization=None, geometry=None):
    ref = inputs.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    ident = ref.profile.identity_payload.to_payload()
    for key, changes in [
        ("candidate", candidate),
        ("realization", realization),
        ("geometry", geometry),
    ]:
        if changes:
            params[key].update(changes)
    ident["params_hash"] = payload_identity("resolved_params", params)
    ref = replace(ref, profile=resolve_profile(params, ident))
    return replace(inputs, geometry=ref.geometry())


def native_effects(seed, target):
    effects = []
    for label, state in (("source", seed), ("target", target)):
        graph = state.inputs.geometry.reference.graph.port_graph.to_payload()
        for role in ("current", "reset"):
            inputs = replace(
                state.inputs, current=getattr(state.inputs, role), dt=oracle.DT
            )
            root = ci.CandidateCIRoot(inputs)
            out = outputs(root)
            truth = certify(inputs, root)

            def compare(name, a, b, ai, bi, label=label, role=role):
                effects.append(
                    {
                        "graph": label,
                        "role": role,
                        "effect": name,
                        **separation(
                            np.asarray(a).reshape(-1),
                            np.asarray(b).reshape(-1),
                            oracle.IV.matrix(list(ai)),
                            oracle.IV.matrix(list(bi)),
                        ),
                    }
                )

            # This control changes the named modulation path at the same H.
            mod = reconfigure(inputs, candidate={"kappa_M_C": 0})
            mod = replace(
                mod,
                geometry=GRCV4Geometry(
                    mod.geometry.reference, root.selected.inputs.geometry.one_form_hodge
                ),
            )
            point = CandidateCCurrent(mod)
            mod_truth = truth["high"].read(
                "C", truth["c"], None, truth["H"], modulation=False
            )
            compare(
                "modulation_at_selected_H",
                out["J"],
                point.current.values,
                truth["read"]["J"],
                mod_truth["J"],
            )
            feedback = reconfigure(inputs, candidate={"chi_C": 0})
            other = ci.CandidateCIRoot(feedback)
            other_out = outputs(other)
            other_truth = oracle.certify(
                graph, inputs.current.C, inputs.current.Z_4, other_out, feedback=False
            )
            compare(
                "feedback_complete_root",
                out["J"],
                other_out["J"],
                truth["read"]["J"],
                other_truth["read"]["J"],
            )
            if label == "source":
                zero = replace(
                    inputs,
                    current=replace(
                        inputs.current, Z_4=(0.0,) * len(inputs.current.Z_4)
                    ),
                )
                other = ci.CandidateCIRoot(zero)
                other_out = outputs(other)
                # Removing old Z can select the reference on evaluation one.
                # Certify this distinct control against the declared tolerance;
                # separation below still subtracts its actual full error.
                other_truth = oracle.certify(
                    graph,
                    zero.current.C,
                    zero.current.Z_4,
                    other_out,
                    root_error_limit=Q(oracle.TOLERANCE),
                )
                compare(
                    "old_Z_complete_root_current",
                    out["J"],
                    other_out["J"],
                    truth["read"]["J"],
                    other_truth["read"]["J"],
                )
                compare(
                    "old_Z_complete_root_geometry",
                    out["H"],
                    other_out["H"],
                    truth["H"],
                    other_truth["H"],
                )
                continue
            from tests.models.test_grc_v4_pc import configure as pc_configure

            off = pc_configure(
                inputs,
                radius=oracle.RADIUS,
                resource_radius=oracle.RESOURCE_RADIUS,
                tau=1,
                gain=oracle.KAPPA,
                z=inputs.current.Z_4,
                reset_z=inputs.reset.Z_4,
                changes={"identity": {"composition_gain": None}},
            )
            other = pc.CandidatePCRead(off)
            other_out = {
                "H": np.array(other.point.inputs.geometry.one_form_hodge.matrix),
                "J": np.array(other.point.current.values),
                "baseline": np.array(other.point.algebra.baseline.values),
                "source": np.array(other.structural_source.increment),
            }
            other_truth = oracle.certify(
                graph, inputs.current.C, inputs.current.Z_4, other_out, instant=False
            )
            compare(
                "instantaneous_source_complete_root_current",
                out["J"],
                other_out["J"],
                truth["read"]["J"],
                other_truth["read"]["J"],
            )
            step = ci.ProvisionalCandidateCIStep(inputs)
            cn, zn = oracle.step_truth(truth)
            # Deliberately forbidden second source: new C, original selected H.
            wrong_inputs = replace(
                root.selected.inputs,
                current=replace(inputs.current, C=step.next_inputs.current.C),
                stage="post_continuity",
                evaluation_index=0,
                trial_current=None,
            )
            wrong_point = CandidateCCurrent(wrong_inputs)
            wrong_source = ci._source_from_flat(
                wrong_point, wrong_point.read.causal_flat
            )
            wrong_z = pc.scalar_zoh(
                inputs.current.Z_4,
                tuple(x for row in wrong_source.increment for x in row),
                oracle.DT,
                1,
            )
            wrong_read = truth["high"].read("C", cn, None, truth["H"])
            decay = oracle.IV.exp(-oracle.number(oracle.DT))
            wrong_zn = decay * truth["z"] + (1 - decay) * wrong_read["source"]
            compare(
                "same_root_vs_postcontinuity_source_Z_write",
                step.next_inputs.current.Z_4,
                wrong_z,
                zn,
                wrong_zn,
            )
            later = step.next_inputs
            for _ in range(9):
                later = ci.ProvisionalCandidateCIStep(later).next_inputs
            actual = ci.CandidateCIRoot(later)
            later_truth = certify(later, actual)
            held = replace(
                later,
                current=replace(later.current, Z_4=(0.0,) * len(later.current.Z_4)),
            )
            held_root = ci.CandidateCIRoot(held)
            held_truth = certify(held, held_root)
            compare(
                "ten_writes_Z_next_root_current",
                actual.current.values,
                held_root.current.values,
                later_truth["read"]["J"],
                held_truth["read"]["J"],
            )
            compare(
                "ten_writes_Z_next_root_geometry",
                outputs(actual)["H"],
                outputs(held_root)["H"],
                later_truth["H"],
                held_truth["H"],
            )
    return effects


class NativeCCIPCPressure(unittest.TestCase):
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
        cls.owner = GRC9V4CCIPCOperation(cls.seed)
        outcome = cls.owner.expand(cls.request)
        assert outcome.committed, outcome.failure
        cls.checkpoint = cls.owner.checkpoint()

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

    def test_independent_roots_and_uniform_compact_chart(self):
        for state in (self.seed, self.owner.state):
            for role in ("current", "reset"):
                inputs = replace(state.inputs, current=getattr(state.inputs, role))
                root = ci.CandidateCIRoot(inputs)
                truth = certify(inputs, root)
                independent = oracle.independent_root(
                    inputs.geometry.reference.graph.port_graph.to_payload(),
                    inputs.current.C,
                    inputs.current.Z_4,
                )
                oracle.certify(
                    inputs.geometry.reference.graph.port_graph.to_payload(),
                    inputs.current.C,
                    inputs.current.Z_4,
                    independent,
                )
                self.assertLess(
                    np.max(np.abs(outputs(root)["J"] - independent["J"])),
                    float(oracle.CURRENT_ERROR),
                )
                self.assertLess(truth["certificate"]["source_upper"], oracle.RADIUS)
                self.assertLess(truth["certificate"]["contraction_upper"], 1)
                self.assertEqual(root.selected.point.algebra.selector.rank, 1)
                self.assertEqual(root.to_payload()["numerics"], ci.CIPC_NUMERICS)
                self.assertNotIn(
                    inputs.geometry.reference.profile.complete_profile_id,
                    list_supported_profiles(),
                )

    def test_both_charge_failures_and_late_publication_errors_roll_back(self):
        real = GRC9V4CCIPCExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4CCIPCOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                out = real(target, state)
                return (
                    replace(out, C=(out.C[0] + 1, *out.C[1:]))
                    if state == chosen
                    else out
                )

            with patch.object(GRC9V4CCIPCExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, "target_readmission")
        owner = GRC9V4CCIPCOperation(self.seed)
        with patch.object(
            native, "make_commit_receipts", side_effect=ValueError("late receipt")
        ):
            self.assertRollback(owner, self.request, "commit")
        with patch.object(
            GRC9V4CCIPCExpansion,
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
            data = json.loads(self.checkpoint)
            cursor = data
            for key in path[:-1]:
                cursor = cursor[key]
            old = cursor[path[-1]]
            cursor[path[-1]] = old + "x" if isinstance(old, str) else old + 2**-20
            with self.subTest(path=path), self.assertRaises((ValueError, TypeError)):
                GRC9V4CCIPCOperation.replay(canonical_json_bytes(data))
        data = json.loads(self.checkpoint)
        refs = data["reference_currents"][0]["roles"]
        refs["current"] = deepcopy(refs["reset"])
        with self.assertRaises(ValueError):
            GRC9V4CCIPCOperation.replay(canonical_json_bytes(data))
        for role in ("current", "reset"):
            data = json.loads(self.checkpoint)
            old = getattr(self.owner.state.inputs, role)
            c = (old.C[0] + 2**-20, old.C[1] - 2**-20, *old.C[2:])
            forged = replace(
                self.owner.state,
                inputs=replace(self.owner.state.inputs, **{role: replace(old, C=c)}),
            )
            data["state"] = forged.to_payload()
            data["lifecycle_digest"] = forged.lifecycle_digest(self.owner.receipts)
            with self.assertRaises(ValueError):
                GRC9V4CCIPCOperation.replay(canonical_json_bytes(data))

    def test_duplicate_concurrent_event_commits_once_and_owns_backend(self):
        owner = GRC9V4CCIPCOperation(self.seed)
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
        self.assertEqual(owner.checkpoint(), self.checkpoint)
        self.assertTrue(seen)
        self.assertEqual(set(seen), {captured})

    def test_source_stage_twenty_target_beats_and_same_root_writing(self):
        starts = [self.initial] + [
            replace(
                self.owner.state.inputs,
                current=getattr(self.owner.state.inputs, r),
                dt=oracle.DT,
            )
            for r in ("current", "reset")
        ]
        for inputs, count in zip(starts, (1, 10, 10), strict=True):
            for _ in range(count):
                c, z = tuple(inputs.current.C), tuple(inputs.current.Z_4)
                with patch.object(pc, "scalar_zoh", wraps=pc.scalar_zoh) as writer:
                    step = ci.ProvisionalCandidateCIStep(inputs)
                truth = certify(inputs, step.root)
                cn, zn = oracle.step_truth(truth)
                self.assertLess(
                    oracle.full_error(step.next_inputs.current.C, cn),
                    oracle.RESOURCE_ERROR,
                )
                self.assertLess(
                    oracle.full_error(
                        step.next_inputs.current.Z_4, oracle.IV.matrix(list(zn))
                    ),
                    oracle.CARRIER_ERROR,
                )
                self.assertEqual(writer.call_count, 1)
                self.assertEqual(writer.call_args.args[0], z)
                self.assertEqual(
                    writer.call_args.args[1],
                    tuple(
                        x
                        for row in step.root.selected.structural_source.increment
                        for x in row
                    ),
                )
                self.assertEqual(step.carrier_writes, 1)
                self.assertIsNone(step.writer)
                self.assertEqual(step.next_inputs.reset, inputs.reset)
                self.assertEqual(inputs.current.C, c)
                self.assertIsNone(step.next_inputs.current.W_A)
                self.assertGreater(min(step.next_inputs.current.C), 0)
                inputs = step.next_inputs
            certify(inputs, ci.CandidateCIRoot(inputs))
        actual = ci.ProvisionalCandidateCIStep(self.initial).next_inputs
        self.assertEqual(actual.current, self.seed.inputs.current)
        content = self.owner.carrier_archives[0]["history_content"]["content"]
        self.assertEqual(tuple(content), actual.current.Z_4 + actual.reset.Z_4)
        probe = ci.ProvisionalCandidateCIStep(replace(self.seed.inputs, dt=oracle.DT))
        self.assertNotEqual(tuple(content[:81]), probe.next_inputs.current.Z_4)

    def test_exact_resources_complete_references_archives_and_loss_channels(self):
        before, after = self.seed.inputs, self.owner.state.inputs
        target = construction(self.seed, self.request)
        self.assertEqual(
            (after.time, after.step_index), (before.time, before.step_index)
        )
        self.assertEqual(after.geometry, after.geometry.reference.geometry())
        self.assertEqual(set(after.geometry.reference.edge_weights.values()), {1.0})
        source_nodes = before.geometry.reference.graph.live_node_ids
        target_nodes = after.geometry.reference.graph.live_node_ids
        satellites = [
            n for n in target_nodes if isinstance(n, str) and "/satellite/" in n
        ]
        self.assertEqual(len(satellites), 3)
        for role in ("current", "reset"):
            old, new = getattr(before, role), getattr(after, role)
            source = old.C[source_nodes.index(self.request.source_node_id)]
            for n, c in zip(target_nodes, new.C, strict=True):
                if n in source_nodes:
                    self.assertEqual(c, old.C[source_nodes.index(n)])
                elif n in satellites:
                    share = self.request.resource_distribution[
                        int(n.rsplit("/", 1)[1]) - 1
                    ]
                    self.assertEqual(c, float(Q(source) * Q(share)))
                else:
                    self.assertEqual(c, 0.0)
            self.assertIsNone(new.W_A)
            self.assertEqual(new.Z_4, (0.0,) * 256)
            self.assertLess(abs(sum(map(Q, new.C)) - Q(after.Q_target)), Q(1, 10**11))
        archive = self.owner.carrier_archives[0].to_dict()
        self.assertEqual(archive, target.carrier_archive_payload())
        self.assertEqual(
            archive["source_edge_ids"],
            list(before.geometry.reference.graph.live_edge_ids),
        )
        self.assertEqual(archive["source_state_digest"], self.seed.scientific_digest)
        self.assertEqual(
            archive["history_content"]["content"],
            list(before.current.Z_4 + before.reset.Z_4),
        )
        topology = self.owner.receipts[0].to_payload()["identity_payload"]
        self.assertEqual(
            topology["core"]["information_losses"], ["carrier_history_loss"]
        )
        self.assertEqual(
            topology["history"]["candidate"],
            {
                "subject": "candidate",
                "disposition": "rederived",
                "source_history_digest": None,
                "target_history_digest": None,
                "information_loss": "none",
            },
        )
        self.assertEqual(
            topology["history"]["carrier"]["disposition"], "whole_carrier_reset"
        )
        self.assertEqual(
            topology["history"]["carrier"]["information_loss"], "carrier_history_loss"
        )
        self.assertEqual(
            topology["history"]["carrier"]["source_history_digest"],
            archive["history_digest"],
        )
        self.assertEqual(len(self.owner.receipts), 4)

    def test_fresh_reference_root_evidence_and_full_replay(self):
        checkpoint = json.loads(self.checkpoint)
        refs = checkpoint["reference_currents"][0]
        old_ids = self.seed.inputs.geometry.reference.graph.live_edge_ids
        new_ids = self.owner.state.inputs.geometry.reference.graph.live_edge_ids
        for role in ("current", "reset"):
            root = ci.CandidateCIRoot(
                replace(self.seed.inputs, current=getattr(self.seed.inputs, role))
            )
            self.assertEqual(refs["roles"][role]["source"], list(root.current.values))
            lookup = dict(zip(old_ids, root.current.values, strict=True))
            self.assertEqual(
                refs["roles"][role]["target"], [lookup.get(e, 0.0) for e in new_ids]
            )
            real = ci.CandidateCIRoot(
                replace(
                    self.owner.state.inputs,
                    current=getattr(self.owner.state.inputs, role),
                )
            )
            self.assertNotEqual(
                refs["roles"][role]["target"], list(real.current.values)
            )
        self.assertNotEqual(refs["roles"]["current"], refs["roles"]["reset"])
        self.assertEqual(
            GRC9V4CCIPCOperation.replay(self.checkpoint).checkpoint(), self.checkpoint
        )
        step = ci.ProvisionalCandidateCIStep(self.initial)
        self.assertEqual(
            ci.ProvisionalCandidateCIStep.from_payload(step.to_payload()).next_inputs,
            step.next_inputs,
        )
        self.assertEqual(
            ci.CandidateCIRoot.from_payload(step.root.to_payload()).to_payload(),
            step.root.to_payload(),
        )

    def test_zero_duration_event_runs_roots_but_no_physical_writers(self):
        with (
            patch.object(
                native,
                "ProvisionalCandidateCIStep",
                wraps=ci.ProvisionalCandidateCIStep,
            ) as calls,
            patch.object(
                pc, "scalar_zoh", side_effect=AssertionError("event Z writer")
            ),
            patch.object(
                ci, "CandidateAWriter", side_effect=AssertionError("A writer")
            ),
            patch.object(
                native, "CandidateCOSPass", side_effect=AssertionError("OS substitute")
            ),
            patch.object(
                native, "CandidatePCRead", side_effect=AssertionError("PC substitute")
            ),
            patch(
                "pygrc.models.grc_v4_step.CurrentSelection",
                side_effect=AssertionError("continuity"),
            ),
        ):
            owner = GRC9V4CCIPCOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)
            self.assertEqual(len(calls.call_args_list), 3)
            self.assertTrue(all(c.args[0].dt == 0 for c in calls.call_args_list))
        self.assertEqual(owner.checkpoint(), self.checkpoint)

    def test_both_actual_Z_roles_bound_before_target_construction(self):
        owner = GRC9V4CCIPCOperation(self.seed)
        for role in ("current", "reset"):
            states = {r: getattr(self.seed.inputs, r) for r in ("current", "reset")}
            z = states[role].Z_4
            states[role] = replace(states[role], Z_4=(z[0] + 2**-20, *z[1:]))
            req = replace(self.request, history_policy=cpc_history_policy(**states))
            self.assertRollback(owner, req, "admission")
        for subject, changes in [
            ("candidate", {"policy_id": "candidate_a_history_free_v1"}),
            ("carrier", {"information_loss": "none"}),
            ("carrier", {"target_initializer_id": "partial_reset_v1"}),
        ]:
            data = self.request.to_payload()
            policy = data["history_policy"]
            policy[subject].update(changes)
            policy[subject + "_history_policy_digest"] = payload_identity(
                "history_channel_policy_identity_payload",
                {
                    "schema_version": "grcv4-history-channel-policy-identity-v1",
                    "policy": policy[subject],
                },
            )
            self.assertRollback(
                owner, GRC9V4ExpansionRequestInput.from_payload(data), "admission"
            )

    def test_rehashed_archives_cannot_change_stage_role_order_or_content(self):
        for action in ("content", "order", "source", "swap", "omit", "digest"):
            data = json.loads(self.checkpoint)
            a = data["carrier_archives"][0]
            if action == "content":
                a["history_content"]["content"][0] += 2**-40
                a["history_digest"] = payload_identity(
                    "history_content_identity_payload", a["history_content"]
                )
            elif action == "order":
                a["source_edge_ids"].reverse()
            elif action == "source":
                a["source_state_digest"] = self.owner.state.scientific_digest
            elif action == "swap":
                v = a["history_content"]["content"]
                a["history_content"]["content"] = v[81:] + v[:81]
                a["history_digest"] = payload_identity(
                    "history_content_identity_payload", a["history_content"]
                )
            elif action == "omit":
                data["carrier_archives"] = []
            else:
                a["history_digest"] = "grcv4-history-content-sha256:" + "0" * 64
            with (
                self.subTest(action=action),
                self.assertRaises((ValueError, TypeError)),
            ):
                GRC9V4CCIPCOperation.replay(canonical_json_bytes(data))
        owner = GRC9V4CCIPCOperation(self.seed)
        with patch.object(
            GRC9V4CCIPCExpansion,
            "carrier_archive_payload",
            side_effect=ValueError("late archive"),
        ):
            self.assertRollback(owner, self.request, "commit")
        self.assertEqual(owner.carrier_archives, ())

    def test_real_uniform_target_failure_despite_regular_zero_carrier_points(self):
        from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
        from pygrc.models.grc_v4_state import FrozenJSONMap

        data = self.seed.specialization.to_payload()
        data["resolved"]["expansion"]["bond_seed"] = 2
        data["identity_payload"]["specialization_params_hash"] = payload_identity(
            "resolved_specialization", data["resolved"]
        )
        spec = GRC9V4Specialization(
            FrozenJSONMap(data["resolved"]), FrozenJSONMap(data["identity_payload"])
        )
        seed = replace(self.seed, specialization=spec)
        request = request_for(
            seed, replace(self.request, target_specialization_id=spec.specialization_id)
        )
        owner = GRC9V4CCIPCOperation(seed)
        target = construction(seed, request)
        for role in ("current", "reset"):
            inputs = replace(
                seed.inputs,
                geometry=target.target.geometry(),
                current=target.transfer(getattr(seed.inputs, role)),
                reset=target.transfer(seed.inputs.reset),
            )
            CandidateCCurrent(inputs)
            self.assertEqual(set(inputs.current.Z_4), {0.0})
            with self.assertRaisesRegex(ValueError, "uniform source envelope"):
                ci.CandidateCIRoot(inputs)
        result = self.assertRollback(owner, request, "target_readmission")
        self.assertIn("uniform source envelope", result.failure.message)

    def test_real_iteration_exhaustion_for_current_and_reset_only_targets(self):
        for tolerance, current_passes in ((2.5e-11, False), (3.5e-11, True)):
            inputs = configure(
                self.seed.inputs,
                domain_radius=oracle.ROOT_RADIUS,
                tolerance=tolerance,
                limit=1,
            )
            inputs = replace(
                inputs,
                current=replace(inputs.current, Z_4=(0.0,) * 81),
                reset=replace(inputs.reset, Z_4=(0.0,) * 81),
            )
            seed = replace(self.seed, inputs=inputs)
            owner = GRC9V4CCIPCOperation(seed)
            request = request_for(seed, self.request)
            target = construction(seed, request)
            for role in ("current", "reset"):
                mapped = replace(
                    inputs,
                    geometry=target.target.geometry(),
                    current=target.transfer(getattr(inputs, role)),
                    reset=target.transfer(inputs.reset),
                )
                if role == "current" and current_passes:
                    self.assertEqual(ci.CandidateCIRoot(mapped).evaluations, 1)
                else:
                    with self.assertRaisesRegex(ci.CIStageError, "iteration limit"):
                        ci.CandidateCIRoot(mapped)
            result = self.assertRollback(owner, request, "target_readmission")
            self.assertIn("iteration limit", result.failure.message)

    def test_carrier_and_composite_domain_boundaries_are_independent(self):
        inputs = self.owner.state.inputs
        m = len(inputs.current.Z_4)
        z = [0.0] * m
        z[0] = oracle.RADIUS
        for sign in (-1, 1):
            z[0] = sign * oracle.RADIUS
            good = replace(inputs, current=replace(inputs.current, Z_4=tuple(z)))
            ci.CandidateCIRoot(good)
            z[0] = float(np.nextafter(z[0], sign * np.inf))
            with self.assertRaises(ValueError):
                ci.CandidateCIRoot(
                    replace(inputs, current=replace(inputs.current, Z_4=tuple(z)))
                )
        with self.assertRaisesRegex(ValueError, "B_2R"):
            ci.CandidateCIRoot(
                reconfigure(
                    inputs,
                    realization={
                        "contraction_domain_id": ci.CIBoundedDomain(
                            float(np.nextafter(oracle.ROOT_RADIUS, 0))
                        ).identity
                    },
                )
            )
        for cutoff in (1, 10):
            with self.assertRaises(ValueError):
                GRC9V4CCIPCOperation(
                    replace(
                        self.seed,
                        inputs=reconfigure(
                            self.seed.inputs, candidate={"Lambda_C": cutoff}
                        ),
                    )
                )
        for role in ("current", "reset"):
            for changes in ({"Z_4": None}, {"W_A": (1.0,) * 9}, {"Z_4": (0.0,) * 80}):
                with self.assertRaises((ValueError, TypeError)):
                    GRC9V4CCIPCOperation(
                        replace(
                            self.seed,
                            inputs=replace(
                                self.seed.inputs,
                                **{
                                    role: replace(
                                        getattr(self.seed.inputs, role), **changes
                                    )
                                },
                            ),
                        )
                    )
        root = ci.CandidateCIRoot(self.seed.inputs)
        for h in (
            root.selected.inputs.geometry,
            pc.carrier_geometry(self.seed.inputs, self.seed.inputs.current),
        ):
            with self.assertRaisesRegex(ValueError, "restart"):
                replace(self.seed, inputs=replace(self.seed.inputs, geometry=h))

    def test_signed_covariance_of_carrier_joint_root_and_same_source_writer(self):
        for state in (self.seed, self.owner.state):
            inputs = replace(state.inputs, dt=oracle.DT)
            original = ci.ProvisionalCandidateCIStep(inputs)
            base = outputs(original.root)
            ref = inputs.geometry.reference
            g = ref.graph.port_graph
            m = len(g.edges)
            for offset in (0, 1, 3):
                order = list(range(offset, m)) + list(range(offset))
                signs = np.array([-1 if i % 2 else 1 for i in order])
                edges = tuple(
                    replace(g.edges[i], tail=g.edges[i].head, head=g.edges[i].tail)
                    if sign < 0
                    else g.edges[i]
                    for i, sign in zip(order, signs, strict=True)
                )

                def tensor(x, m=m, order=order, signs=signs):
                    return np.asarray(x).reshape(m, m)[np.ix_(order, order)] * np.outer(
                        signs, signs
                    )

                ref2 = replace(
                    ref,
                    graph=GRCV4Graph.from_port_graph(
                        GRC9V4PortGraph(g.live_node_ids, edges)
                    ),
                )
                roles = {
                    r: replace(
                        getattr(inputs, r),
                        Z_4=tuple(
                            float(x) if x else 0.0
                            for x in tensor(getattr(inputs, r).Z_4).flat
                        ),
                    )
                    for r in ("current", "reset")
                }
                moved = replace(inputs, geometry=ref2.geometry(), **roles)
                step = ci.ProvisionalCandidateCIStep(moved)
                out = outputs(step.root)
                certify(moved, step.root)
                self.assertLess(
                    np.max(np.abs(out["J"] - base["J"][order] * signs)),
                    float(oracle.CURRENT_ERROR),
                )
                for key in ("H", "source"):
                    self.assertLess(
                        np.max(np.abs(out[key] - tensor(base[key]))),
                        float(
                            oracle.GEOMETRY_ERROR if key == "H" else oracle.SOURCE_ERROR
                        ),
                    )
                self.assertLess(
                    np.max(
                        np.abs(
                            np.array(step.next_inputs.current.Z_4).reshape(m, m)
                            - tensor(original.next_inputs.current.Z_4)
                        )
                    ),
                    float(oracle.CARRIER_ERROR),
                )
                self.assertLess(
                    np.max(
                        np.abs(
                            np.array(step.next_inputs.current.C)
                            - original.next_inputs.current.C
                        )
                    ),
                    float(oracle.RESOURCE_ERROR),
                )

    def test_simplex_events_admit_but_negative_physical_steps_fail_without_repair(self):
        for shares in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            owner = GRC9V4CCIPCOperation(self.seed)
            outcome = owner.expand(replace(self.request, resource_distribution=shares))
            self.assertTrue(outcome.committed, outcome.failure)
            before = owner.checkpoint()
            for role in ("current", "reset"):
                inputs = replace(
                    owner.state.inputs,
                    current=getattr(owner.state.inputs, role),
                    dt=oracle.DT,
                )
                root = ci.CandidateCIRoot(inputs)
                truth = certify(inputs, root)
                cn, _ = oracle.step_truth(truth)
                self.assertLess(min(oracle.endpoint(v, 1) for v in cn), 0)
                with self.assertRaises(ResourceBoundaryError) as error:
                    ci.ProvisionalCandidateCIStep(inputs)
                self.assertEqual(error.exception.stage, "charge_admission")
                self.assertEqual(owner.checkpoint(), before)

    def test_twenty_full_error_ULP_effect_controls(self):
        effects = native_effects(self.seed, self.owner.state)
        self.assertEqual(len(effects), 20)
        self.assertGreater(min(e["minimum_margin_ratio"] for e in effects), 1)

    def test_source_postbeat_and_closed_owner_and_foreign_reference_guards(self):
        seed = replace(self.seed, inputs=replace(self.seed.inputs, step_index=0))
        self.assertRollback(
            GRC9V4CCIPCOperation(seed), request_for(seed, self.request), "admission"
        )
        with self.assertRaises(TypeError):
            native.GRC9V4CPCOperation(self.seed)
        target = construction(self.seed, self.request)
        with self.assertRaisesRegex(ValueError, "source graph"):
            target.transfer_reference_current(
                PhysicalFlux(target.target.graph, (0.0,) * 16)
            )
        with self.assertRaisesRegex(ValueError, "coupled root"):
            pc.CandidatePCRead(self.seed.inputs)

    def test_whole_chart_outliers_and_independent_equation_mutations(self):
        for state in (self.seed, self.owner.state):
            inputs = state.inputs
            graph = inputs.geometry.reference.graph.port_graph.to_payload()
            proof = oracle.chart(graph)
            for index, sign in ((0, 1), (-1, -1)):
                c = [0.0] * len(inputs.current.C)
                c[index] = 16.0
                z = [0.0] * len(inputs.current.Z_4)
                z[0] = float(sign)
                changed = replace(
                    inputs, current=GRCV4AuthoritativeState(tuple(c), None, tuple(z))
                )
                root = ci.CandidateCIRoot(changed)
                # The concentrated-C outlier is judged against the declared
                # root tolerance. The nominal fixture's tighter 2^-48 geometry
                # comparison budget is not a whole-chart accuracy promise.
                truth = oracle.certify(
                    graph,
                    changed.current.C,
                    changed.current.Z_4,
                    outputs(root),
                    root_error_limit=Q(oracle.TOLERANCE),
                )
                self.assertLess(truth["root_error_upper"], Q(oracle.TOLERANCE))
                self.assertLess(
                    oracle.norm_upper(truth["read"]["source"]), proof["source_upper"]
                )
            root = ci.CandidateCIRoot(inputs)
            out = outputs(root)
            for key in ("J", "source", "H"):
                bad = {k: v.copy() for k, v in out.items()}
                bad[key].flat[0] += 2**-20
                with self.assertRaises(ValueError):
                    oracle.certify(graph, inputs.current.C, inputs.current.Z_4, bad)
        for role in ("current", "reset"):
            inputs = self.owner.state.inputs
            m = 16
            z = list(getattr(inputs, role).Z_4)
            z[1] = 2**-20
            with self.assertRaises(ValueError):
                GRC9V4CCIPCOperation(
                    replace(
                        self.owner.state,
                        inputs=replace(
                            inputs,
                            **{role: replace(getattr(inputs, role), Z_4=tuple(z))},
                        ),
                    )
                )
            graph = inputs.geometry.reference.graph.port_graph.to_payload()
            mask = oracle.model(graph).mask
            i, j = next((i, j) for i in range(m) for j in range(m) if mask[i, j] == 0)
            z = [0.0] * (m * m)
            z[i * m + j] = z[j * m + i] = 2**-20
            with self.assertRaises(ValueError):
                GRC9V4CCIPCOperation(
                    replace(
                        self.owner.state,
                        inputs=replace(
                            inputs,
                            **{role: replace(getattr(inputs, role), Z_4=tuple(z))},
                        ),
                    )
                )

    def test_zero_source_release_preserves_history_and_composition_is_gain_two(self):
        inputs = self.initial
        roles = {
            r: replace(getattr(inputs, r), C=(0.0,) * 10) for r in ("current", "reset")
        }
        inputs = replace(inputs, **roles, Q_target=0.0)
        step = ci.ProvisionalCandidateCIStep(inputs)
        self.assertEqual(step.root.current.values, (0.0,) * 9)
        self.assertTrue(
            all(
                x == 0
                for row in step.root.selected.structural_source.increment
                for x in row
            )
        )
        decay = oracle.IV.exp(-oracle.number(oracle.DT))
        expected = decay * oracle.vector(inputs.current.Z_4)
        self.assertLess(
            oracle.full_error(step.next_inputs.current.Z_4, expected),
            oracle.CARRIER_ERROR,
        )
        self.assertTrue(any(step.next_inputs.current.Z_4))
        self.assertEqual(step.next_inputs.reset, inputs.reset)
        # Algebraic held-source equilibrium identity only, not settled dynamics.
        root = ci.CandidateCIRoot(self.owner.state.inputs)
        source = root.selected.structural_source
        z = tuple(x for row in source.increment for x in row)
        held = replace(
            self.owner.state.inputs,
            current=replace(self.owner.state.inputs.current, Z_4=z),
        )
        combined = ci._effective_source(held, source)
        self.assertEqual(
            tuple(x for row in combined.increment for x in row), tuple(2 * x for x in z)
        )
        self.assertEqual(pc.scalar_zoh(z, z, oracle.DT, 1), z)

    def test_authorization_is_exact_and_preserves_accepted_research(self):
        import phase9_specialization_acceptance as entry

        self.assertEqual(entry.ccipc_authorization(ROOT), "P9-8.3C-CI-PC")
        for path in entry.CCIPC_PATHS:
            self.assertTrue(entry.ccipc_permitted(path, "P9-8.3C-CI-PC"))
            self.assertFalse(entry.ccipc_permitted(path, "P9-8.3A.2"))
        for path in (
            "src/pygrc/models/grc_v4_ci.py",
            "src/pygrc/models/grc_v4_pc.py",
            "specs/grc-9-v4-spec.md",
        ):
            self.assertFalse(entry.ccipc_permitted(path, "P9-8.3C-CI-PC"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.ccipc_authorization(ROOT)
        bad = {**entry.CCIPC_RESEARCH_HASHES}
        bad[next(iter(bad))] = "0" * 64
        with (
            patch.object(entry, "CCIPC_RESEARCH_HASHES", bad),
            self.assertRaises(ValueError),
        ):
            entry.ccipc_authorization(ROOT)


if __name__ == "__main__":
    unittest.main()
