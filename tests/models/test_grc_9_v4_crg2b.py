"""Native C_RG2b: signed completion, independent sections and atomic events."""

from __future__ import annotations

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

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_9_v4_rg2b as signed
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4CRG2bExpansion,
    GRC9V4ExpansionPlan,
    crg2b_profile_template,
)
from pygrc.models.grc_9_v4_lifecycle import GRC9V4CRG2bOperation, GRC9V4CRG2bState
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_profile import list_supported_profiles, resolve_profile
from pygrc.models.grc_v4_rg2b import (
    CandidateRG2bSection,
    ProvisionalCandidateRG2bStep,
    RG2bCertificate,
    RG2bStageError,
)
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_9_v4_lifecycle import native_cos_fixture
from tests.models.test_grc_v4_profile import reidentify

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "implementation/phase-9-grcv4/verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))

DT, TOLERANCE = 2**-12, 2**-48


def configure(inputs, *, changes=None):
    ref = inputs.geometry.reference
    params, identity = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    params["realization"] = {
        "schema_version": "grcv4-rg2b-params-v1",
        "extension_evaluator_id": signed.EXTENSION,
        "approximation_policy_id": signed.APPROXIMATION,
        "error_norm_id": signed.ERROR_NORM,
        "containment_certificate_id": signed.CONTAINMENT,
        "error_tolerance": TOLERANCE,
        "iteration_limit": 222,
        "failure_policy_id": "fail_closed_on_uncertified_section_v1",
    }
    params["solver"]["solver_kind"] = "direct"
    identity.update(
        realization="RG2b",
        profile_family_id="C_RG2b",
        solver_id="direct_unique_root_v1",
    )
    for group, values in (changes or {}).items():
        params[group].update(values)
    reidentify(params, identity)
    return replace(
        inputs,
        geometry=replace(ref, profile=resolve_profile(params, identity)).geometry(),
    )


def fixture():
    declaration, request = native_cos_fixture()
    initial = configure(
        replace(
            declaration.inputs,
            current=GRCV4AuthoritativeState((3.0, *((193 / 64,) * 9)), None, None),
            step_index=0,
            time=0,
            dt=DT,
        )
    )
    step = ProvisionalCandidateRG2bStep(initial)
    seed = GRC9V4CRG2bState(replace(step.next_inputs, dt=0), declaration.specialization)
    request = replace(
        request,
        source_state_digest=seed.scientific_digest,
        target_profile_template_id=crg2b_profile_template(
            seed.inputs.geometry.reference
        ).profile_template_id,
        operation_id="native-crg2b-expand-1",
    )
    return seed, request, initial


def construction(state, request):
    ref = state.inputs.geometry.reference
    return GRC9V4CRG2bExpansion(
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


class NativeCRG2bPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = exact_backend(ExactBackend.FLINT)
        cls.backend.__enter__()
        cls.addClassCleanup(cls.backend.__exit__, None, None, None)
        cls.seed, cls.request, cls.initial = fixture()
        cls.owner = GRC9V4CRG2bOperation(cls.seed)
        result = cls.owner.expand(cls.request)
        assert result.committed, result.failure
        cls.committed = cls.owner.checkpoint()

    def test_event_and_section_smoke(self):
        target = self.owner.state.inputs
        self.assertEqual(len(target.current.C), 17)
        self.assertEqual(min(target.current.C), 0)
        section = CandidateRG2bSection(target)
        self.assertEqual(section.levels, 6)
        self.assertLessEqual(Q(section.error_upper), TOLERANCE)
        self.assertIsNone(target.current.W_A)
        self.assertIsNone(target.current.Z_4)

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

    def test_actual_graph_hypotheses_and_section_corner_queries(self):
        import test_p980_rg2b_numerical as numerical
        from test_p980_os_effect_witness import IV, full_error
        from verify_p983crg2b_native import actual, model, read

        from tests.models.test_grc_9_v4_topology import edge
        from tests.models.test_grc_v4_geometry import (
            stage_inputs_fixture,
            stage_reference_fixture,
        )

        for n in (2, 17, 18):
            graph = GRCV4Graph.from_port_graph(
                GRC9V4PortGraph(
                    tuple(range(n)),
                    tuple(edge(f"e{i}", (i, 2), (i + 1, 1)) for i in range(n - 1)),
                )
            )
            ref = stage_reference_fixture(
                graph=graph,
                weights={f"e{i}": 1.0 for i in range(n - 1)},
                base=[[0.0] * (n - 1) for _ in range(n - 1)],
                changes={
                    "candidate": {
                        "Lambda_C": 2**-9,
                        "kappa_M_C": 2**-24,
                        "kappa_Phi_C": 1,
                        "eta_C": 1,
                        "tau_C": 1,
                        "chi_C": 16,
                        "zeta_C": 2**-37,
                    },
                    "geometry": {"kappa_H": 0.5},
                    "solver": {
                        "conditioning_limit": 1e8,
                        "absolute_tolerance": 1e-11,
                        "relative_tolerance": 1e-11,
                    },
                },
            )
            raw = stage_inputs_fixture(ref)
            c = tuple(4.25 if i % 2 else 0.0 for i in range(n))
            state = GRCV4AuthoritativeState(c, None, None)
            inputs = configure(
                replace(raw, current=state, reset=state, Q_target=sum(c), dt=0)
            )
            if n > 17:
                with self.assertRaisesRegex(RG2bStageError, "at most 17"):
                    CandidateRG2bSection(inputs)
                continue
            ss, pp = read(inputs)
            _, hi, _, _ = numerical.section(model(inputs), "C", np.array(c))
            self.assertLess(
                full_error(actual(ss, pp)["H"].ravel(), IV.matrix(list(hi))),
                Q(1, 2**48),
            )
        # A cycle has perfectly valid ports but is outside this tree certificate.
        graph = GRCV4Graph.from_port_graph(
            GRC9V4PortGraph(
                (0, 1, 2),
                (
                    edge("e0", (0, 1), (1, 1)),
                    edge("e1", (1, 2), (2, 1)),
                    edge("e2", (2, 2), (0, 2)),
                ),
            )
        )
        ref = stage_reference_fixture(
            graph=graph,
            weights={f"e{i}": 1.0 for i in range(3)},
            base=[[0.0] * 3 for _ in range(3)],
        )
        with self.assertRaisesRegex(RG2bStageError, "connected tree"):
            CandidateRG2bSection(configure(replace(stage_inputs_fixture(ref), dt=0)))

    def test_global_bounds_match_independent_exact_proof(self):
        import test_p980_rg2b_completion as proof

        cert = RG2bCertificate(self.owner.state.inputs)
        b, sb = (
            proof.global_bounds("C"),
            proof.section_budgets(proof.global_bounds("C")),
        )
        for key, field in (
            ("base_X_lipschitz", "A_X"),
            ("base_h_lipschitz", "A_H"),
            ("source_X_lipschitz", "B_X"),
            ("source_h_lipschitz", "B_H"),
            ("base_displacement_upper", "M_f"),
            ("source_upper", "M_S"),
        ):
            self.assertEqual(Q(cert.bounds[key]), b[field])
        self.assertEqual(Q(cert.bounds["contraction_upper"]), sb["q_section"])
        self.assertEqual(Q(cert.bounds["section_value_radius"]), sb["value_radius"])
        self.assertLess(sb["q_section"], Q(1, 400))

    def test_current_bridge_enforces_euclidean_not_coordinatewise_budget(self):
        """Distributed producer error may fit each coordinate but fail edge_l2."""
        from pygrc.models import grc_v4_rg2b as owner
        from pygrc.models.grc_v4_geometry import PhysicalFlux

        real = owner.CandidateCCurrent

        def corrupt(inputs):
            point = real(inputs)
            if (
                inputs.stage == "rg2b_section"
                and inputs.current == self.initial.current
            ):
                object.__setattr__(
                    point,
                    "current",
                    PhysicalFlux(
                        inputs.geometry.reference.graph,
                        tuple(j + 8e-12 for j in point.current.values),
                    ),
                )
            return point

        with patch.object(owner, "CandidateCCurrent", side_effect=corrupt):
            with self.assertRaisesRegex(ResourceBoundaryError, "arithmetic bridge"):
                ProvisionalCandidateRG2bStep(self.initial)
            # Reproduce the original norm mismatch without changing the fixture,
            # solver tolerance, physical update or other bridge checks.
            with patch.object(signed, "_norm", side_effect=lambda values: max(values)):
                unchecked = ProvisionalCandidateRG2bStep(self.initial)
                self.assertNotEqual(
                    unchecked.point.current.values,
                    real(unchecked.point.inputs).current.values,
                )

    def test_independent_finite_continuations_and_mechanism_consumers(self):
        from verify_p983crg2b_native import observations

        report = observations(self.seed, self.request, self.initial)
        self.assertEqual(len(report["comparisons"]), 24)
        self.assertEqual(sum(len(v) for v in report["effects"].values()), 24)
        type(self).observations = report

    def test_every_chain_depth_query_terminal_and_norm_are_checked(self):
        inputs = self.owner.state.inputs
        cert = RG2bCertificate(inputs)
        x, h = signed.propose(cert, inputs.current.C)
        for depth in range(1, 7):
            bad_x = deepcopy(x)
            bad_x[depth][0] += 2**-12
            with (
                self.subTest(depth=depth),
                patch.object(signed, "propose", return_value=(bad_x, h)),
                self.assertRaisesRegex(RG2bStageError, "tolerance"),
            ):
                CandidateRG2bSection(inputs)
        mutations = []
        mutations.append((x[:-1], h[:-1]))
        mutations.append((x + [x[-1]], h + [h[-1]]))
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
        # Each coordinate is below rho, but the actual row-sum norm exceeds it.
        mask = np.array(cert.graph_data.mask, dtype=float)
        hh[2] = np.eye(len(mask)) + 2**-13 * (mask != 0)
        mutations.append((x, hh))
        for value in (float("nan"), float("inf")):
            xx = deepcopy(x)
            xx[3][0] = value
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
                CandidateRG2bSection(inputs)

    def test_signed_predecessors_completion_faces_and_noncommuting_equations(self):
        import test_p980_rg2b_completion as proof
        import test_p980_rg2b_numerical as numerical
        from test_p980_os_effect_witness import IV, endpoint, number, vector
        from verify_p983crg2b_native import model

        inputs = self.owner.state.inputs
        cert, high = RG2bCertificate(inputs), proof.auxiliary(model(inputs))
        x, h = signed.propose(cert, inputs.current.C)
        _enclosure, bounds = numerical.certify_chain(
            high, "C", numerical.Chain(x, h), vector(inputs.current.C)
        )
        native_error, native_bounds = signed.certify_chain(cert, inputs.current.C, x, h)
        self.assertLessEqual(Q(str(native_error)), Q(1, 2**48))
        self.assertGreater(Q(str(native_bounds["truncation_error"])), 0)
        k = list(inputs.current.C).index(0)
        b, sb = (
            proof.global_bounds("C"),
            proof.section_budgets(proof.global_bounds("C")),
        )
        inverse_tail = (
            sb["inverse_lip"] * b["A_H"] * sb["q_section"] ** 5 * sb["value_radius"]
        )
        self.assertLess(Q(float(x[1][k])) + bounds["state_error"] + inverse_tail, 0)
        xx = deepcopy(x)
        xx[1][k] = 0
        with (
            patch.object(signed, "propose", return_value=(xx, h)),
            self.assertRaisesRegex(RG2bStageError, "tolerance"),
        ):
            CandidateRG2bSection(inputs)
        # Stress exact faces, adjacent floats, mixed saturation and a noncommuting H.
        m = len(h[0])
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
        faces = (
            -1.0,
            math.nextafter(-1.0, -math.inf),
            math.nextafter(-1.0, math.inf),
            5.0,
            math.nextafter(5.0, math.inf),
            math.nextafter(5.0, -math.inf),
            -1e100,
            1e100,
        )
        for value in faces:
            query = tuple(value if i % 2 else 2.0 for i in range(len(x[0])))
            f, g, _ = signed.literal(cert, query, hd.tolist())
            expected_f, expected_s = high.increment(
                "C", vector(query), IV.matrix(hd.tolist())
            )
            expected_g = high.I + number(Q(1, 2)) * expected_s
            for native_v, reference_v in list(zip(f, expected_f, strict=True)) + list(
                zip((v for row in g for v in row), expected_g, strict=True)
            ):
                self.assertLessEqual(Q(str(native_v.lo)), endpoint(reference_v, 1))
                self.assertGreaterEqual(Q(str(native_v.hi)), endpoint(reference_v, 0))

    def test_equilibrium_and_K_vs_K_minus_boundaries(self):
        for value in (0.0, 17 / 4, math.nextafter(17 / 4, math.inf), 9 / 2):
            authority = replace(
                self.initial.current, C=(value,) * len(self.initial.current.C)
            )
            inputs = replace(
                self.initial,
                current=authority,
                reset=authority,
                Q_target=value * len(authority.C),
                dt=0,
            )
            section = CandidateRG2bSection(inputs)
            self.assertEqual(section.geometry, inputs.geometry.reference.geometry())
            state = GRC9V4CRG2bState(inputs, self.seed.specialization)
            self.assertTrue(
                all(v == 0 for j in native._crg2b_readmit(state) for v in j.values)
            )
            if value <= 17 / 4:
                self.assertEqual(
                    ProvisionalCandidateRG2bStep(inputs).next_inputs, inputs
                )
            else:
                with self.assertRaisesRegex(ResourceBoundaryError, "K_minus"):
                    ProvisionalCandidateRG2bStep(inputs)
        outside = replace(
            inputs,
            current=replace(
                authority, C=(math.nextafter(9 / 2, math.inf),) * len(authority.C)
            ),
        )
        with self.assertRaisesRegex(RG2bStageError, "outside K"):
            CandidateRG2bSection(outside)

    def test_declared_recipe_budget_parameters_and_beat_fail_closed(self):
        changes = (
            {"realization": {"iteration_limit": 221}},
            {"realization": {"error_tolerance": 2**-70}},
            {"realization": {"extension_evaluator_id": "unknown"}},
            {"realization": {"approximation_policy_id": "unknown"}},
            {"realization": {"error_norm_id": "unknown"}},
            {"realization": {"containment_certificate_id": "unknown"}},
            {"candidate": {"Lambda_C": 1 / 256}},
            {"candidate": {"kappa_M_C": 2**-23}},
            {"candidate": {"chi_C": 8}},
            {"geometry": {"kappa_H": 0.25}},
        )
        for change in changes:
            with (
                self.subTest(change=change),
                self.assertRaises((RG2bStageError, ValueError)),
            ):
                CandidateRG2bSection(configure(self.seed.inputs, changes=change))
        for dt in (math.nextafter(DT, 0), 2 * DT):
            with self.assertRaisesRegex(RG2bStageError, "beat"):
                CandidateRG2bSection(replace(self.initial, dt=dt))
        section = CandidateRG2bSection(self.seed.inputs)
        with self.assertRaisesRegex(RG2bStageError, "Lipschitz-only"):
            section.classical_jacobian()
        self.assertEqual(
            CandidateRG2bSection.from_payload(section.to_payload()).identity,
            section.identity,
        )

    def test_exact_map_references_history_absence_and_fresh_read_replay(self):
        from verify_p983crg2b_native import read

        target = construction(self.seed, self.request)
        current, reset = self.seed.inputs.current, self.seed.inputs.reset
        for before, after in (
            (current, self.owner.state.inputs.current),
            (reset, self.owner.state.inputs.reset),
        ):
            old = dict(zip(target.source.graph.live_node_ids, before.C, strict=True))
            satellites = {
                target.plan.event_id + f"/satellite/{i}": float(
                    Q(old[self.request.source_node_id]) * Q(share)
                )
                for i, share in enumerate(self.request.resource_distribution, 1)
            }
            del old[self.request.source_node_id]
            self.assertEqual(
                after.C,
                tuple(
                    old.get(node, satellites.get(node, 0.0))
                    for node in target.target.graph.live_node_ids
                ),
            )
            self.assertIsNone(after.W_A)
            self.assertIsNone(after.Z_4)
            self.assertEqual(sum(map(Q, after.C)), sum(map(Q, before.C)))
        self.assertEqual(
            self.owner.state.inputs.step_index, self.seed.inputs.step_index
        )
        self.assertEqual(self.owner.state.inputs.time, self.seed.inputs.time)
        self.assertEqual(set(target.target.edge_weights.values()), {1.0})
        self.assertNotEqual(
            target.target.profile.complete_profile_id,
            target.source.profile.complete_profile_id,
        )
        self.assertNotIn(
            target.target.profile.complete_profile_id, list_supported_profiles()
        )
        data = json.loads(self.committed)
        self.assertNotIn("carrier_archives", data)
        for role in ("current", "reset"):
            _, point = read(
                replace(self.seed.inputs, current=getattr(self.seed.inputs, role))
            )
            recorded = data["reference_currents"][0]["roles"][role]
            self.assertEqual(recorded["source"], list(point.current.values))
            old = dict(
                zip(
                    target.source.graph.live_edge_ids, point.current.values, strict=True
                )
            )
            self.assertEqual(
                recorded["target"],
                [old.get(e, 0.0) for e in target.target.graph.live_edge_ids],
            )
        self.assertEqual(
            GRC9V4CRG2bOperation.replay(self.committed).checkpoint(), self.committed
        )

    def test_event_runs_no_step_CI_OS_writer_or_inherited_section(self):
        with (
            patch.object(
                native, "ProvisionalCandidateCIStep", side_effect=AssertionError("CI")
            ),
            patch.object(native, "CandidateCOSPass", side_effect=AssertionError("OS")),
            patch(
                "pygrc.models.grc_v4_rg2b.ProvisionalCandidateRG2bStep",
                side_effect=AssertionError("ordinary beat"),
            ),
        ):
            owner = GRC9V4CRG2bOperation(self.seed)
            self.assertTrue(owner.expand(self.request).committed)

    def test_real_target_parameter_failure_and_late_failure_are_atomic(self):
        # Source completion admits, target seed=2 violates unit-reference hypotheses.
        params = self.seed.specialization.resolved.to_dict()
        params["expansion"]["bond_seed"] = 2
        from pygrc.models.grc_v4_codec import payload_identity
        from pygrc.models.grc_v4_state import FrozenJSONMap

        identity = self.seed.specialization.identity_payload.to_dict()
        identity["specialization_params_hash"] = payload_identity(
            "resolved_specialization", params
        )
        spec = type(self.seed.specialization)(
            FrozenJSONMap(params), FrozenJSONMap(identity)
        )
        seed = replace(self.seed, specialization=spec)
        request = replace(
            self.request,
            source_state_digest=seed.scientific_digest,
            target_specialization_id=spec.specialization_id,
        )
        result = self.assertRollback(
            GRC9V4CRG2bOperation(seed), request, "target_readmission"
        )
        self.assertIn("parameter/reference", result.failure.message)
        owner = GRC9V4CRG2bOperation(self.seed)
        with patch.object(
            native, "make_commit_receipts", side_effect=ValueError("late receipt")
        ):
            self.assertRollback(owner, self.request, "commit")
        with patch.object(
            GRC9V4CRG2bExpansion,
            "transfer_reference_current",
            side_effect=ValueError("late reference"),
        ):
            self.assertRollback(owner, self.request, "commit")

    def test_current_and_reset_charge_corruption_roll_back(self):
        real = GRC9V4CRG2bExpansion.transfer
        for role in ("current", "reset"):
            owner = GRC9V4CRG2bOperation(self.seed)
            chosen = getattr(owner.state.inputs, role)

            def corrupt(target, state, chosen=chosen):
                out = real(target, state)
                return (
                    replace(out, C=(out.C[0] + 1, *out.C[1:]))
                    if state == chosen
                    else out
                )

            with patch.object(GRC9V4CRG2bExpansion, "transfer", corrupt):
                self.assertRollback(owner, self.request, "target_readmission")

    def test_rehashed_authority_reference_and_receipt_forgery_rejects(self):
        for path in (
            ("state", "scientific_digest"),
            ("receipts", 0, "receipt_id"),
            ("reference_currents", 0, "roles", "reset", "target", 0),
        ):
            data = json.loads(self.committed)
            cursor = data
            for key in path[:-1]:
                cursor = cursor[key]
            value = cursor[path[-1]]
            cursor[path[-1]] = value + "x" if isinstance(value, str) else value + 1
            with self.assertRaises(ValueError):
                GRC9V4CRG2bOperation.replay(canonical_json_bytes(data))
        for role in ("current", "reset"):
            data = json.loads(self.committed)
            old = getattr(self.owner.state.inputs, role)
            forged = replace(
                self.owner.state,
                inputs=replace(
                    self.owner.state.inputs,
                    **{
                        role: replace(
                            old, C=(*old.C[:-2], old.C[-2] + 2**-20, old.C[-1] - 2**-20)
                        )
                    },
                ),
            )
            data["state"] = forged.to_payload()
            data["lifecycle_digest"] = forged.lifecycle_digest(self.owner.receipts)
            with self.assertRaises(ValueError):
                GRC9V4CRG2bOperation.replay(canonical_json_bytes(data))

    def test_duplicate_concurrent_events_and_backend_ownership(self):
        owner = GRC9V4CRG2bOperation(self.seed)
        with (
            exact_backend(ExactBackend.PYTHON),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            results = list(pool.map(owner.expand, [self.request] * 2))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(owner.checkpoint(), self.committed)

    def test_covariance_signed_edge_permutations(self):
        from verify_p983crg2b_native import actual, check, expected, read

        for inputs in (self.seed.inputs, self.owner.state.inputs):
            section, point = read(inputs)
            baseline = actual(section, point)
            ref, graph = (
                inputs.geometry.reference,
                inputs.geometry.reference.graph.port_graph,
            )
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
            new_ref = replace(
                ref,
                graph=GRCV4Graph.from_port_graph(
                    GRC9V4PortGraph(graph.live_node_ids, edges)
                ),
            )
            other = replace(inputs, geometry=new_ref.geometry())
            ss, pp = read(other)
            _, truth = expected(other)
            check(ss, pp, truth)
            out = actual(ss, pp)
            self.assertLess(
                np.max(np.abs(out["J"] - baseline["J"][order] * signs)), 2**-39
            )
            self.assertLess(
                np.max(
                    np.abs(
                        out["H"]
                        - baseline["H"][np.ix_(order, order)] * np.outer(signs, signs)
                    )
                ),
                2**-48,
            )

    def test_simplex_vertex_event_does_not_guarantee_positive_next_beat(self):
        from test_p980_os_effect_witness import endpoint
        from verify_p983crg2b_native import expected

        for weights in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            owner = GRC9V4CRG2bOperation(self.seed)
            result = owner.expand(replace(self.request, resource_distribution=weights))
            self.assertTrue(result.committed, result.failure)
            checkpoint = owner.checkpoint()
            for role in ("current", "reset"):
                inputs = replace(
                    owner.state.inputs, current=getattr(owner.state.inputs, role), dt=DT
                )
                _, truth = expected(inputs)
                self.assertLess(min(endpoint(v, 1) for v in truth["exact_after"]), 0)
                with self.assertRaises(ResourceBoundaryError):
                    ProvisionalCandidateRG2bStep(inputs)
                self.assertEqual(owner.checkpoint(), checkpoint)

    def test_authorization_and_claim_scope_remain_closed(self):
        import phase9_specialization_acceptance as entry
        from verify_p983crg2b_native import provenance

        self.assertEqual(entry.crg2b_authorization(ROOT), "P9-8.3C-RG2b")
        for path in entry.CRG2B_PATHS:
            self.assertTrue(entry.crg2b_permitted(path, "P9-8.3C-RG2b"))
        self.assertFalse(entry.crg2b_permitted("specs/grc-v4-spec.md", "P9-8.3C-RG2b"))
        with (
            patch.object(
                entry, "accepted", return_value={"accepted_generic_runtime_support": []}
            ),
            self.assertRaises(ValueError),
        ):
            entry.crg2b_authorization(ROOT)
        result = provenance()
        self.assertTrue(all(r["row_count"] == 1 for r in result["contracts"].values()))


if __name__ == "__main__":
    unittest.main()
