"""Baseline gates and bounded P9-8.3C-OS native event/continuation evidence.

No completed-spark, full public lifecycle or broad profile conformance claim.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import sys
import unittest
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import numpy as np

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4COSExpansion,
    GRC9V4CPCExpansion,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
    cos_profile_template,
    cpc_history_policy,
    cpc_profile_template,
)
from pygrc.models.grc_9_v4_lifecycle import (
    GRC9SparkPolicy,
    GRC9V4CandidateDetection,
    GRC9V4COSOperation,
    GRC9V4COSState,
    GRC9V4CPCOperation,
    GRC9V4CPCState,
    GRC9V4Specialization,
    UnsupportedGRC9SparkLane,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortGraph,
    GRC9V4PostbeatRows,
)
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import ExactBackend, current_exact_backend, exact_backend
from pygrc.models.grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4Graph,
    NonfiniteGeometryError,
    OrientedEdge,
)
from pygrc.models.grc_v4_lifecycle import GRCV4Operation
from pygrc.models.grc_v4_pc import (
    CandidatePCRead,
    PCBaseChart,
    ProvisionalCandidatePCStep,
    carrier_geometry,
)
from pygrc.models.grc_v4_profile import (
    CandidateCParams,
    PCParams,
    get_supported_profile,
    list_supported_profiles,
    resolve_profile,
)
from pygrc.models.grc_v4_realizations import CandidateCOSPass, OSStageError
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep, ResourceBoundaryError
from tests.models.test_grc_9_v4_topology import edge, row_profile
from tests.models.test_grc_v4_candidate_c import current_fixture, dense_current_oracle
from tests.models.test_grc_v4_geometry import (
    stage_inputs_fixture,
    stage_reference_fixture,
)


def native_cos_fixture(
    *, cutoff: float = 1 / 512
) -> tuple[GRC9V4COSState, GRC9V4ExpansionRequestInput]:
    """Separate P9-8.3 native companion: dyadic shares and one shared Q.

    It does not relabel the P980 equal-third, separate-Q research experiment
    or the frozen cutoff=1 allocation vector as a native numerical success.
    """
    vectors = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "specs/grc-v4-conformance-vectors.json"
        ).read_text()
    )
    declarations = {v["vector_id"]: v["payload"] for v in vectors["identity_vectors"]}
    params = deepcopy(declarations["IDENTITY-GRC9V4-PARAMS"])
    params["expansion"]["bond_seed"] = 1
    identity = deepcopy(declarations["IDENTITY-GRC9V4-SPECIALIZATION"])
    identity.update(
        hessian_sign=-1,
        specialization_params_hash=payload_identity("resolved_specialization", params),
    )
    specialization = GRC9V4Specialization(
        FrozenJSONMap(params), FrozenJSONMap(identity)
    )
    port_graph = GRC9V4PortGraph(
        ("s", *range(1, 10)),
        tuple(edge(f"e{p}", ("s", p), (p, p)) for p in range(1, 10)),
    )
    reference = stage_reference_fixture(
        graph=GRCV4Graph.from_port_graph(port_graph),
        weights={f"e{i}": 1.0 for i in range(1, 10)},
        base=[[0.0] * 9 for _ in range(9)],
        changes={
            "candidate": {
                "Lambda_C": cutoff,
                "kappa_M_C": 2**-24,
                "kappa_Phi_C": 1,
                "eta_C": 1,
                "tau_C": 1,
                "chi_C": 16,
                "zeta_C": 2**-37,
            },
            "geometry": {"kappa_H": 0.5},
            "realization": {"tolerance": 1e-8},
            "solver": {
                "conditioning_limit": 1e8,
                "absolute_tolerance": 1e-11,
                "relative_tolerance": 1e-11,
            },
            "charge": {"absolute_tolerance": 1e-11},
        },
    )
    current = GRCV4AuthoritativeState((3.0, *((3 + 1 / 64,) * 9)), None, None)
    reset = GRCV4AuthoritativeState(
        (2.0, *((3 + 1 / 64 + 1 / 8,) * 8), 3 + 1 / 64), None, None
    )
    inputs = replace(
        stage_inputs_fixture(reference),
        current=current,
        reset=reset,
        Q_target=sum(current.C),
        dt=1 / 4096,
    )
    inputs = ProvisionalCandidateCOSStep(inputs).next_inputs
    state = GRC9V4COSState(replace(inputs, dt=0), specialization)
    request = deepcopy(vectors["grc9_expansion_vectors"][0]["request"])
    request.update(
        schema_version="grc9v4-expansion-event-request-input-v1",
        operation_id="native-cos-expand-1",
        source_state_digest=state.scientific_digest,
        source_graph_digest=port_graph.graph_digest,
        source_node_id="s",
        target_profile_template_id=cos_profile_template(reference).profile_template_id,
        target_specialization_id=specialization.specialization_id,
        target_effective_degree=52,
        module_chirality=1,
        growth_phase=3,
        resource_distribution=[0.5, 0.25, 0.25],
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    return state, GRC9V4ExpansionRequestInput.from_payload(request)


def native_cpc_fixture() -> tuple[
    GRC9V4CPCState, GRC9V4ExpansionRequestInput, GeometryStageInputs
]:
    """Separate native PC recipe; current takes one beat, reset none.

    The inherited C_OS helper supplies only graph, policy and resource recipe.
    PC uses its own identified R=1, kappa_H=2^-16, zeta=2^-30, M=16 chart;
    these are not the P9-8.0 R=2^-22 research parameters or a new G2 declaration.
    """
    seed, request = native_cos_fixture()
    reference = seed.inputs.geometry.reference
    params: Any = reference.profile.params_resolved.to_payload()
    identity = reference.profile.identity_payload.to_payload()
    params["realization"] = {
        "schema_version": "grcv4-pc-params-v1",
        "tau_PC": 1,
        "radius": 1,
        "carrier_norm_id": "symmetric_star_frobenius_v1",
        "source_envelope_id": PCBaseChart(16).identity,
        "writer_id": "zero_order_hold_exponential_v1",
    }
    params["geometry"]["kappa_H"] = 2**-16
    params["candidate"]["zeta_C"] = 2**-30
    identity.update(
        realization="PC",
        profile_family_id="C_PC",
        solver_id="direct_unique_root_v1",
        params_hash=payload_identity("resolved_params", params),
    )
    reference = replace(reference, profile=resolve_profile(params, identity))
    z = tuple(
        (1 if i == j else 0.5) * (-1) ** (i + j) / 16
        for i in range(9)
        for j in range(9)
    )
    initial = replace(
        seed.inputs,
        geometry=reference.geometry(),
        current=GRCV4AuthoritativeState((3.0, *((193 / 64,) * 9)), None, z),
        reset=GRCV4AuthoritativeState(seed.inputs.reset.C, None, tuple(-x for x in z)),
        step_index=0,
        time=0,
        dt=1 / 4096,
    )
    initial = replace(initial, geometry=carrier_geometry(initial, initial.current))
    stepped = ProvisionalCandidatePCStep(initial).next_inputs
    state = GRC9V4CPCState(replace(stepped, dt=0), seed.specialization)
    request = replace(
        request,
        operation_id="native-cpc-expand-1",
        source_state_digest=state.scientific_digest,
        target_profile_template_id=cpc_profile_template(reference).profile_template_id,
        history_policy=cpc_history_policy(state.inputs.current, state.inputs.reset),
    )
    return state, request, initial


def independent_pc_beat(
    inputs: GeometryStageInputs,
) -> tuple[np.ndarray, tuple[float, ...], np.ndarray]:
    """Paper D.7: old-Z read, continuity, held-source scalar ODE solution.

    No production carrier, source, continuity or scalar-ZOH routine is called.
    The dense C evaluator independently implements the fixed-h paper equations.
    This nonloop fixture has overlap 1 on diagonal and 1/2 per common endpoint.
    """
    ref = inputs.geometry.reference
    assert isinstance(ref.profile.params_resolved.candidate, CandidateCParams)
    assert isinstance(ref.profile.params_resolved.realization, PCParams)
    point = dense_current_oracle(inputs)
    b = np.array(ref.graph.incidence)
    lowered = np.linalg.solve(
        np.array(inputs.geometry.one_form_hodge.matrix), point["read"]
    )
    overlap = abs(b).T @ abs(b) / 2
    zeta = ref.profile.params_resolved.candidate.zeta_C
    source = np.array(
        [
            [
                float(
                    Fraction(zeta)
                    * Fraction(float(a))
                    * Fraction(float(x))
                    * Fraction(float(y))
                )
                for a, y in zip(row, lowered, strict=True)
            ]
            for row, x in zip(overlap, lowered, strict=True)
        ]
    )
    resource = np.array(
        [
            float(
                Fraction(c)
                - Fraction(inputs.dt)
                * sum(
                    (
                        Fraction(float(a)) * Fraction(float(j))
                        for a, j in zip(row, point["current"], strict=True)
                    ),
                    Fraction(),
                )
            )
            for c, row in zip(inputs.current.C, b, strict=True)
        ]
    )
    assert inputs.current.Z_4 is not None
    with localcontext() as context:
        context.prec = 150
        a = (
            -Decimal.from_float(inputs.dt)
            / Decimal.from_float(ref.profile.params_resolved.realization.tau_PC)
        ).exp()
        z = tuple(
            float(a * Decimal.from_float(old) + (1 - a) * Decimal.from_float(float(s)))
            for old, s in zip(inputs.current.Z_4, source.flat, strict=True)
        )
    return resource, z, source


def policy(**changes: Any) -> GRC9SparkPolicy:
    return GRC9SparkPolicy.from_payload(
        {
            "schema_version": "grc9v4-spark-policy-v1",
            "lane": "current_hybrid_signed_hessian",
            "gradient_tolerance": 0.5,
            "basin_hessian_tolerance": 0.5,
            "spark_hessian_tolerance": 0,
            "child_stabilization": None,
            **changes,
        }
    )


def star_inputs(
    *,
    gradients: tuple[float, ...] = (0.125, 0.125, 0.125),
    ports: tuple[int, ...] = tuple(range(1, 10)),
    sign: int = -1,
    center: float = 0.0,
) -> GRC9V4PostbeatRows:
    graph = GRC9V4PortGraph(
        ("s", *range(1, 10)), tuple(edge(f"e{p}", ("s", p), (p, 1)) for p in ports)
    )
    resources = (center, *(center + gradients[(p - 1) // 3] for p in range(1, 10)))
    return GRC9V4PostbeatRows(
        graph,
        row_profile("A", {}),
        GRCV4AuthoritativeState(resources, (1.0,) * len(ports), None),
        (0.0,) * len(ports),
        1,
        sign,
    )


def admitted_c_fixture() -> tuple[GRCV4Operation, GRC9V4PortGraph, Any]:
    """Concrete C_OS source: strict cutoff 1/2, star spectrum {0,1,10}.

    Current and reset resources are independently owned by the real generic
    lifecycle; one ordinary beat supplies the fresh handoff. This is a local
    admitted numerical fixture, not a new accepted G2 declaration.
    """
    graph = GRCV4Graph(
        ("s", *range(1, 10)), tuple(OrientedEdge(f"e{i}", "s", i) for i in range(1, 10))
    )
    port_graph = GRC9V4PortGraph(
        graph.live_node_ids,
        tuple(edge(f"e{i}", ("s", i), (i, 1)) for i in range(1, 10)),
    )
    inputs = replace(
        current_fixture(
            graph=graph,
            weights={f"e{i}": 1.0 for i in range(1, 10)},
            resource=(3.0, *((3 + 1 / 64,) * 9)),
            changes={
                "candidate": {
                    "Lambda_C": 0.5,
                    "kappa_M_C": 0,
                    "kappa_Phi_C": 1 / 64,
                    "eta_C": 1 / 8,
                    "tau_C": 1 / 8,
                    "chi_C": 1 / 4,
                    "zeta_C": 1 / 4,
                },
                "geometry": {"kappa_H": 1 / 1024},
                "realization": {"tolerance": 1e-8},
                "solver": {"conditioning_limit": 1e8},
                "charge": {"absolute_tolerance": 1e-11},
            },
        ),
        dt=1 / 4096,
    )
    return GRCV4Operation(inputs), port_graph, inputs


class SparkPolicyTests(unittest.TestCase):
    def test_matches_frozen_policy_and_rejects_closed_schema_defects(self) -> None:
        root = Path(__file__).resolve().parents[2]
        vectors = json.loads(
            (root / "specs/grc-v4-conformance-vectors.json").read_text()
        )
        expected = next(
            v["payload"]["spark"]
            for v in vectors["identity_vectors"]
            if isinstance(v.get("payload"), dict) and "spark" in v["payload"]
        )
        self.assertEqual(policy().to_payload(), expected)
        for field in expected:
            missing = {k: v for k, v in expected.items() if k != field}
            with self.subTest(field=field), self.assertRaises(ValueError):
                GRC9SparkPolicy.from_payload(missing)
        for values in (
            {"unknown": 1},
            {"lane": "almost_baseline"},
            {"schema_version": "old"},
            {"gradient_tolerance": -1},
            {"basin_hessian_tolerance": 0},
        ):
            with self.assertRaises(ValueError):
                policy(**values)

    def test_numeric_admission_on_both_constructor_routes(self) -> None:
        for field in (
            "gradient_tolerance",
            "basin_hessian_tolerance",
            "spark_hessian_tolerance",
        ):
            for value in (True, -0.0, math.nan, math.inf, 2**53, "1", Decimal(1)):
                for route in ("payload", "direct"):
                    with (
                        self.subTest(field=field, value=value, route=route),
                        self.assertRaises((TypeError, ValueError)),
                    ):
                        if route == "payload":
                            policy(**{field: value})
                        else:
                            changes: dict[str, Any] = {field: value}
                            replace(policy(), **changes)

    def test_optional_lane_is_recognized_but_never_silently_executed(self) -> None:
        optional = policy(lane="grc9v3_column_h_assisted")
        self.assertEqual(optional.lane, "grc9v3_column_h_assisted")
        with self.assertRaises(UnsupportedGRC9SparkLane):
            GRC9V4CandidateDetection(star_inputs(), optional)
        baseline = GRC9V4CandidateDetection(star_inputs(), policy()).assess()[0]
        with self.assertRaises(UnsupportedGRC9SparkLane):
            replace(baseline, policy=optional)

    def test_child_policy_is_detached_content_and_grants_no_completion(self) -> None:
        child = {
            "schema_version": "grc9v4-child-stabilization-policy-v1",
            "policy_id": "example",
            "basin_classifier_id": "example",
            "sample_stage": "post_ordinary_step_commit",
            "reference_parent_organization_digest": "example-parent-sha256:" + "a" * 64,
            "required_consecutive_beats": 3,
            "residual_norm_id": "example",
            "residual_tolerance": 0.01,
            "minimum_child_separation": 1,
            "transient_disposition": "mechanical_refinement_only",
            "reset_behavior": "clear_candidate_window",
            "hierarchy_update": "append_stable_child_ids_in_canonical_order",
        }
        detector = GRC9V4CandidateDetection(
            star_inputs(), policy(child_stabilization=child)
        )
        identity = detector.identity
        child["required_consecutive_beats"] = 99
        self.assertEqual(detector.identity, identity)
        self.assertEqual(detector.candidate_node_ids(), ("s",))
        for name in ("events", "completed_spark", "expand", "hierarchy", "step"):
            self.assertFalse(hasattr(detector, name))
        changed = replace(detector, policy=policy())
        self.assertNotEqual(changed.identity, identity)
        self.assertEqual(changed.candidate_node_ids(), detector.candidate_node_ids())


class CandidateGateTests(unittest.TestCase):
    def test_all_eight_conjunction_cases(self) -> None:
        for saturated, small, degenerate in product((False, True), repeat=3):
            inputs = star_inputs(
                center=2,
                gradients=(-1 if degenerate else 1, 0, 0),
                ports=tuple(range(1, 10 if saturated else 9)),
                sign=1,
            )
            result = GRC9V4CandidateDetection(
                inputs, policy(gradient_tolerance=2 if small else 0.5)
            ).assess()[0]
            self.assertEqual(
                (result.saturated, result.small_gradient, result.hessian_degenerate),
                (saturated, small, degenerate),
            )
            self.assertEqual(result.is_candidate, saturated and small and degenerate)

    def test_all_512_occupancy_masks_require_exactly_nine_ports(self) -> None:
        p = policy(spark_hessian_tolerance=1)
        for mask in range(512):
            ports = tuple(i + 1 for i in range(9) if mask & (1 << i))
            inputs = star_inputs(gradients=(0, 0, 0), ports=ports)
            result = GRC9V4CandidateDetection(inputs, p).assess()[0]
            self.assertEqual(result.occupied_ports, ports)
            self.assertTrue(result.small_gradient and result.hessian_degenerate)
            self.assertEqual(result.is_candidate, mask == 511)

    def test_loops_count_two_ports_and_do_not_admit_an_expansion(self) -> None:
        original = star_inputs(gradients=(0, 0, 0))
        graph = GRC9V4PortGraph(
            ("s", 1),
            (
                *(edge(f"loop{i}", ("s", i), ("s", i + 1)) for i in (1, 3, 5, 7)),
                edge("spoke", ("s", 9), (1, 1)),
            ),
        )
        inputs = replace(
            original,
            port_graph=graph,
            committed=GRCV4AuthoritativeState((1, 1), (1,) * 5, None),
            physical_current=(0,) * 5,
        )
        detector = GRC9V4CandidateDetection(inputs, policy(spark_hessian_tolerance=1))
        result = detector.assess()[0]
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(result.occupied_ports, tuple(range(1, 10)))
        self.assertTrue(result.is_candidate)
        self.assertFalse(hasattr(result, "expansion_admitted"))

    def test_gradient_equality_adjacent_thresholds_and_zero_tolerance(self) -> None:
        inputs = star_inputs(gradients=(3, 4, 0))
        for tolerance, expected in (
            (math.nextafter(5, 0), False),
            (5, False),
            (math.nextafter(5, math.inf), True),
        ):
            actual = GRC9V4CandidateDetection(
                inputs, policy(gradient_tolerance=tolerance)
            ).assess()[0]
            self.assertEqual(actual.small_gradient, expected)
            self.assertEqual(actual.is_candidate, expected)
        zero = GRC9V4CandidateDetection(
            star_inputs(gradients=(0, 0, 0)),
            policy(gradient_tolerance=0, spark_hessian_tolerance=1),
        )
        self.assertFalse(zero.assess()[0].small_gradient)
        self.assertEqual(zero.candidate_node_ids(), ())

    def test_norm_comparison_resolves_rounding_underflow_and_overflow(self) -> None:
        g = (math.nextafter(1, 0), math.nextafter(2**-26, 0), 0)
        self.assertEqual(math.hypot(*g), 1)
        self.assertLess(sum(Fraction(x) ** 2 for x in g), 1)
        inputs = star_inputs(gradients=g)
        self.assertTrue(
            GRC9V4CandidateDetection(inputs, policy(gradient_tolerance=1))
            .assess()[0]
            .is_candidate
        )
        tiny, huge = math.ulp(0.0), sys.float_info.max
        for gradients, tolerance, expected in (
            ((tiny, tiny, 0), tiny, False),
            ((tiny, tiny, 0), 2 * tiny, True),
            ((tiny, 0, 0), tiny, False),
            ((huge / 2, huge / 2, 0), huge, True),
            ((huge, huge, 0), huge, False),
        ):
            with self.subTest(gradients=gradients, tolerance=tolerance):
                actual = GRC9V4CandidateDetection(
                    star_inputs(gradients=gradients),
                    policy(gradient_tolerance=tolerance),
                ).assess()[0]
                self.assertEqual(actual.small_gradient, expected)

    def test_signed_hessian_equality_neighbors_and_separate_basin_seed(self) -> None:
        for sign in (-1, 1):
            inputs = star_inputs(gradients=(1, 1, 1), sign=sign)
            for cutoff, expected in (
                (math.nextafter(sign, -math.inf), False),
                (sign, False),
                (math.nextafter(sign, math.inf), True),
            ):
                row = GRC9V4CandidateDetection(
                    inputs, policy(gradient_tolerance=4, spark_hessian_tolerance=cutoff)
                ).assess()[0]
                self.assertEqual(row.hessian_degenerate, expected)
                self.assertEqual(row.is_candidate, expected)
                self.assertEqual(row.basin_seed, sign == 1)
        for tolerance, expected in (
            (math.nextafter(1, 0), True),
            (1, False),
            (math.nextafter(1, math.inf), False),
        ):
            row = GRC9V4CandidateDetection(
                star_inputs(gradients=(1, 1, 1), sign=1, ports=tuple(range(1, 9))),
                policy(gradient_tolerance=4, basin_hessian_tolerance=tolerance),
            ).assess()[0]
            self.assertEqual(row.basin_seed, expected)
            self.assertFalse(row.is_candidate)

    def test_column_cancellation_is_not_a_baseline_gate(self) -> None:
        inputs = star_inputs(sign=1)
        values = (0, 0, 1, 2, 0, 2, 1, 0, 1, 2)
        inputs = replace(inputs, committed=replace(inputs.committed, C=values))
        self.assertEqual(sum(values[p] for p in (1, 4, 7)), 0)
        row = GRC9V4CandidateDetection(inputs, policy(gradient_tolerance=2)).assess()[0]
        self.assertEqual(row.row.gradient, (1, 1, 1))
        self.assertTrue(row.small_gradient and row.saturated)
        self.assertFalse(row.hessian_degenerate or row.is_candidate)

    def test_independent_decimal_decisions_for_180_inputs(self) -> None:
        rng = random.Random(9813)
        with localcontext() as ctx:
            ctx.prec = 100
            for _ in range(180):
                sign = rng.choice((-1, 1))
                inputs = star_inputs(
                    sign=sign, center=4, ports=tuple(range(1, rng.choice((8, 9, 10))))
                )
                resources = (4.0, *(rng.randrange(16, 48) / 8 for _ in range(9)))
                weights = tuple(
                    rng.randrange(1, 9) / 4 for _ in inputs.port_graph.edges
                )
                inputs = replace(
                    inputs,
                    committed=replace(inputs.committed, C=resources, W_A=weights),
                )
                p = policy(
                    gradient_tolerance=rng.randrange(1, 9) / 4,
                    spark_hessian_tolerance=rng.randrange(-4, 5) / 4,
                )
                # Literal per-port weighted means, independently accumulated in
                # Decimal, then rounded to the .b output coordinate contract.
                gradients = []
                for ports in ((1, 2, 3), (4, 5, 6), (7, 8, 9)):
                    terms = [
                        (
                            Decimal(w),
                            Decimal(resources[int(e.head.node_id)]) - Decimal(4),
                        )
                        for e, w in zip(inputs.port_graph.edges, weights, strict=True)
                        if e.tail.port in ports
                    ]
                    den = sum((w for w, _ in terms), Decimal(0))
                    gradients.append(
                        float(sum((w * d for w, d in terms), Decimal(0)) / den)
                        if den
                        else 0.0
                    )
                small = (
                    sum((Decimal(g) ** 2 for g in gradients), Decimal(0))
                    < Decimal(p.gradient_tolerance) ** 2
                )
                degenerate = (
                    min(sign * g for g in gradients) < p.spark_hessian_tolerance
                )
                row = GRC9V4CandidateDetection(inputs, p).assess()[0]
                self.assertEqual(row.row.gradient, tuple(gradients))
                self.assertEqual(
                    row.is_candidate, len(weights) == 9 and small and degenerate
                )


class CandidateBoundaryTests(unittest.TestCase):
    def test_native_admitted_saturated_c_source_after_actual_commit(self) -> None:
        owner, port_graph, inputs = admitted_c_fixture()
        self.assertEqual(
            owner.reference.profile.complete_profile_id,
            "grcv4-profile-sha256:63f96db281496bebd732b69339cbe8f3a195be46cfc1b6b1769f517783d80fa0",
        )
        before = owner.state
        result = owner.step_v4(
            GRCV4StepRequestInput(
                "grcv4-step-request-input-v1",
                "p981c-source-beat",
                inputs.dt,
                FrozenJSONMap({}),
            )
        )
        self.assertTrue(result.committed)
        committed = owner.state
        self.assertIsNone(result.failure)
        self.assertEqual(committed.step_index, 1)
        self.assertNotEqual(committed.current.C, before.current.C)
        self.assertEqual(committed.reset, before.reset)
        current: Any = result.observables.to_dict()["authoritative_current"]
        self.assertEqual(current["stage"], "os_corrector")
        self.assertTrue(current["consumed_by_continuity"])
        rows = GRC9V4PostbeatRows(
            port_graph,
            owner.reference.profile,
            committed.current,
            tuple(current["values"]),
            committed.step_index,
            -1,
        )
        detector = GRC9V4CandidateDetection(rows, policy())
        assessment = detector.assess()[0]
        # Independent fresh-poststate arithmetic: each equal-weight row is the
        # mean of its three literal neighbor differences. All are in (1/64,1/32).
        differences = tuple(
            Fraction(c) - Fraction(committed.current.C[0])
            for c in committed.current.C[1:]
        )
        self.assertTrue(all(Fraction(1, 64) < d < Fraction(1, 32) for d in differences))
        expected = tuple(
            float(sum(differences[start : start + 3]) / 3) for start in (0, 3, 6)
        )
        self.assertEqual(assessment.row.gradient, expected)
        self.assertLess(sum(Fraction(x) ** 2 for x in expected), Fraction(1, 4))
        self.assertLess(assessment.minimum_signed_hessian, 0)
        self.assertEqual(detector.candidate_node_ids(), ("s",))
        self.assertIs(detector.postbeat.port_graph, port_graph)
        self.assertIs(owner.state, committed)
        self.assertEqual(len(committed.receipt_ledger), len(owner.state.receipt_ledger))
        self.assertFalse(hasattr(detector, "completed_spark"))

    def test_fresh_replacement_changes_verdict_without_stale_cache(self) -> None:
        old = GRC9V4CandidateDetection(star_inputs(), policy())
        identity = old.identity
        self.assertEqual(old.candidate_node_ids(), ("s",))
        uniform = replace(
            old.postbeat,
            committed=replace(old.postbeat.committed, C=(1,) * 10),
            step_index=2,
        )
        new = replace(old, postbeat=uniform)
        self.assertEqual(new.candidate_node_ids(), ())
        self.assertNotEqual(new.identity, identity)
        self.assertEqual(old.identity, identity)
        self.assertEqual(old.candidate_node_ids(), ("s",))
        self.assertIsNot(old.assess(), old.assess())

    def test_input_type_stage_and_typed_defects_reject(self) -> None:
        rows = star_inputs()
        for stage in (
            "os_predictor",
            "ci_trial",
            "pre_continuity",
            "reset",
            "pc_old_history",
        ):
            bad = deepcopy(rows)
            object.__setattr__(bad, "stage", stage)
            with self.subTest(stage=stage), self.assertRaises(ValueError):
                GRC9V4CandidateDetection(bad, policy())
        for wrong_input in (
            rows.evaluate(),
            rows.committed,
            rows.port_graph,
            {},
            object(),
        ):
            with self.assertRaises(TypeError):
                GRC9V4CandidateDetection(wrong_input, policy())  # type: ignore[arg-type]
        for wrong_policy in (policy().to_payload(), {}, object()):
            with self.assertRaises(TypeError):
                GRC9V4CandidateDetection(rows, wrong_policy)  # type: ignore[arg-type]
        malformed = deepcopy(policy())
        object.__setattr__(malformed, "gradient_tolerance", True)
        with self.assertRaises(ValueError):
            GRC9V4CandidateDetection(rows, malformed)
        row = GRC9V4CandidateDetection(rows, policy()).assess()[0]
        for ports in ((1, 1), (0,), (10,), (True,)):
            with self.assertRaises((TypeError, ValueError)):
                replace(row, occupied_ports=ports)
        with self.assertRaises(TypeError):
            replace(row, row=object())  # type: ignore[arg-type]

    def test_owned_policy_and_inputs_bind_identity_without_mutation(self) -> None:
        original = star_inputs()
        detector = GRC9V4CandidateDetection(original, policy())
        self.assertIsNot(detector.postbeat, original)
        identity = detector.identity
        for modified in (
            replace(detector, policy=policy(gradient_tolerance=1)),
            replace(detector, policy=policy(basin_hessian_tolerance=0.25)),
            replace(detector, policy=policy(spark_hessian_tolerance=0.25)),
            replace(detector, postbeat=replace(original, step_index=2)),
            replace(detector, postbeat=replace(original, hessian_sign=1)),
            replace(detector, postbeat=replace(original, physical_current=(1,) * 9)),
        ):
            self.assertNotEqual(modified.identity, identity)
        exported = detector.policy.to_payload()
        exported["gradient_tolerance"] = 99
        self.assertEqual(detector.identity, identity)
        with self.assertRaises(FrozenInstanceError):
            detector.postbeat = original  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            detector.assess()[0].occupied_ports = ()  # type: ignore[misc]

    def test_relabel_permute_and_reorient_preserve_results_and_node_order(self) -> None:
        rows = star_inputs()
        expected = GRC9V4CandidateDetection(rows, policy()).candidate_node_ids()
        for mask in range(0, 512, 17):
            edges = tuple(
                replace(e, tail=e.head, head=e.tail) if mask & (1 << i) else e
                for i, e in enumerate(rows.port_graph.edges)
            )
            changed = replace(
                rows, port_graph=replace(rows.port_graph, edges=edges[::-1])
            )
            detector = GRC9V4CandidateDetection(changed, policy())
            self.assertEqual(detector.candidate_node_ids(), expected)
        graph = GRC9V4PortGraph(
            ("1", 1), tuple(edge(f"p{i}", (1, i), ("1", i)) for i in range(1, 10))
        )
        inputs = replace(
            rows,
            port_graph=graph,
            committed=GRCV4AuthoritativeState((1, 1), (1,) * 9, None),
        )
        detector = GRC9V4CandidateDetection(inputs, policy(spark_hessian_tolerance=1))
        self.assertEqual(detector.candidate_node_ids(), ("1", 1))
        reverse = replace(
            detector,
            postbeat=replace(inputs, port_graph=replace(graph, live_node_ids=(1, "1"))),
        )
        self.assertEqual(reverse.candidate_node_ids(), (1, "1"))
        self.assertNotEqual(reverse.identity, detector.identity)

    def test_all_ten_declaration_shapes_use_the_same_baseline_predicate(self) -> None:
        families = set()
        for key in sorted(list_supported_profiles()):
            p = get_supported_profile(key)
            families.add(p.identity_payload.profile_family_id)
            candidate: Any = p.params_resolved.candidate
            is_a = p.identity_payload.candidate == "A"
            ids = ("e0",) if is_a else tuple(candidate.W_C_tr)
            graph = GRC9V4PortGraph(
                ("s", *range(len(ids))),
                tuple(edge(name, ("s", i + 1), (i, 1)) for i, name in enumerate(ids)),
            )
            carrier = p.identity_payload.realization in ("PC", "CI+PC")
            state = GRCV4AuthoritativeState(
                (1,) * (len(ids) + 1),
                (1,) * len(ids) if is_a else None,
                (0,) * len(ids) ** 2 if carrier else None,
            )
            rows = GRC9V4PostbeatRows(graph, p, state, (0,) * len(ids), 1, -1)
            detector = GRC9V4CandidateDetection(rows, policy(spark_hessian_tolerance=1))
            self.assertTrue(detector.assess()[0].small_gradient)
            self.assertEqual(detector.candidate_node_ids(), ())  # Not saturated.
        self.assertEqual(len(families), 10)

    def test_empty_isolated_and_atomic_numerical_failure(self) -> None:
        rows = star_inputs()
        for graph in (GRC9V4PortGraph((), ()), GRC9V4PortGraph(("",), ())):
            inputs = replace(
                rows,
                port_graph=graph,
                committed=GRCV4AuthoritativeState(
                    (0,) * len(graph.live_node_ids), (), None
                ),
                physical_current=(),
            )
            detector = GRC9V4CandidateDetection(
                inputs, policy(spark_hessian_tolerance=1)
            )
            self.assertEqual(detector.candidate_node_ids(), ())
        bad = replace(rows, physical_current=(sys.float_info.max,) * 9)
        detector = GRC9V4CandidateDetection(bad, policy())
        before = canonical_json_bytes(bad.port_graph.to_payload())
        with self.assertRaises(NonfiniteGeometryError):
            detector.assess()
        self.assertEqual(canonical_json_bytes(bad.port_graph.to_payload()), before)


def independent_cos_beat(inputs: Any) -> np.ndarray:
    """Literal dense OS equations and independent exact binary64 continuity."""
    from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge

    ref = inputs.geometry.reference
    predictor = dense_current_oracle(inputs)
    b = np.array(ref.graph.incidence)
    # Each nonloop edge is covered by its two endpoint stars. Diagonal=1;
    # off-diagonal=1/2 exactly when the two edges share an endpoint.
    cover = abs(b).T @ abs(b) / 2
    lowered = np.linalg.solve(
        np.array(inputs.geometry.one_form_hodge.matrix), predictor["read"]
    )
    assembly = np.array(
        [
            [
                float(Fraction(float(w)) * Fraction(float(x)) * Fraction(float(y)))
                for w, y in zip(row, lowered, strict=True)
            ]
            for row, x in zip(cover, lowered, strict=True)
        ]
    )
    h = np.array(
        ref.pairings.one_form.matrix
    ) + ref.profile.params_resolved.geometry.kappa_H * (
        ref.profile.params_resolved.candidate.zeta_C * assembly
    )
    corrector = dense_current_oracle(
        replace(
            inputs,
            geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, tuple(map(tuple, h)))),
        )
    )
    # Numerical flux is binary64 authority for this continuity boundary;
    # compare the independent equation within solver error, not bitwise NumPy.
    return np.array(
        [
            float(
                Fraction(c)
                - Fraction(inputs.dt)
                * sum(
                    (
                        Fraction(float(a)) * Fraction(float(j))
                        for a, j in zip(row, corrector["current"], strict=True)
                    ),
                    Fraction(),
                )
            )
            for c, row in zip(inputs.current.C, b, strict=True)
        ]
    )


class NativeCOSEventTests(unittest.TestCase):
    backend: ExactBackend
    seed: GRC9V4COSState
    request: GRC9V4ExpansionRequestInput

    @classmethod
    def setUpClass(cls) -> None:
        cls.backend = (
            ExactBackend.FLINT
            if importlib.util.find_spec("flint")
            else ExactBackend.PYTHON
        )
        with exact_backend(cls.backend):
            cls.seed, cls.request = native_cos_fixture()

    def setUp(self) -> None:
        scope = exact_backend(self.backend)
        scope.__enter__()
        self.addCleanup(scope.__exit__, None, None, None)
        self.owner = GRC9V4COSOperation(self.seed)

    def committed(self) -> Any:
        result = self.owner.expand(self.request)
        self.assertTrue(
            result.committed, None if result.failure is None else result.failure.message
        )
        return result

    def test_native_identities_and_independent_target_resources_references(
        self,
    ) -> None:
        before = self.seed
        result = self.committed()
        after = self.owner.state
        self.assertEqual(len(after.inputs.current.C), 17)
        self.assertNotEqual(before.inputs.current, before.inputs.reset)
        self.assertEqual(before.inputs.Q_target, after.inputs.Q_target)
        self.assertEqual(
            (after.inputs.step_index, after.inputs.time),
            (before.inputs.step_index, before.inputs.time),
        )
        self.assertNotEqual(after.model_identity, before.model_identity)
        self.assertNotEqual(after.reset_digest, before.reset_digest)
        self.assertNotEqual(after.scientific_digest, after.inputs.scientific_state_id)
        primary = result.emitted_receipts[0].identity_payload.to_dict()
        event = primary["event_id"]
        graph = after.inputs.geometry.reference.graph
        assert graph.port_graph is not None
        self.assertEqual(graph.port_graph.graph_digest, graph.graph_digest)
        self.assertEqual(primary["core"]["target_model_identity"], after.model_identity)
        self.assertEqual(primary["core"]["target_reset_digest"], after.reset_digest)
        self.assertEqual(primary["core"]["actual_charge_delta"], 0)
        self.assertEqual(primary["core"]["information_losses"], [])
        for subject, disposition in (
            ("candidate", "rederived"),
            ("carrier", "not_applicable"),
        ):
            self.assertEqual(
                primary["history"][subject],
                {
                    "subject": subject,
                    "disposition": disposition,
                    "source_history_digest": None,
                    "target_history_digest": None,
                    "information_loss": "none",
                },
            )
        for role in ("current", "reset"):
            source = dict(
                zip(
                    before.inputs.geometry.reference.graph.live_node_ids,
                    getattr(before.inputs, role).C,
                    strict=True,
                )
            )
            expected = {node: source.get(node, 0.0) for node in graph.live_node_ids}
            expected.update(
                {
                    event + f"/satellite/{b}": float(Fraction(source["s"]) * share)
                    for b, share in enumerate(
                        (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)), 1
                    )
                }
            )
            authority = getattr(after.inputs, role)
            self.assertEqual(
                authority.C, tuple(expected[n] for n in graph.live_node_ids)
            )
            self.assertEqual(sum(x == 0 for x in authority.C), 5)
            self.assertIsNone(authority.W_A)
            self.assertIsNone(authority.Z_4)
            self.assertEqual(
                sum(map(Fraction, authority.C)),
                sum(map(Fraction, getattr(before.inputs, role).C)),
            )
        weights = after.inputs.geometry.reference.edge_weights.to_dict()
        self.assertEqual(weights, {e: 1 for e in graph.live_edge_ids})
        model_payload = {
            "schema_version": "grc9v4-complete-identity-v1",
            "grcv4_complete_profile_id": after.inputs.geometry.reference.profile.complete_profile_id,
            "specialization_id": after.specialization.specialization_id,
        }
        self.assertEqual(
            after.model_identity,
            "grc9v4-model-sha256:"
            + hashlib.sha256(canonical_json_bytes(model_payload)).hexdigest(),
        )
        # Exact IDs are independently hashed from the authoritative D11 fields.
        payload: dict[str, Any] = {
            k: self.request.to_payload()[k]
            for k in (
                "source_state_digest",
                "source_graph_digest",
                "source_node_id",
                "target_profile_template_id",
                "target_specialization_id",
                "target_effective_degree",
                "module_chirality",
                "growth_phase",
                "expansion_policy_id",
                "resource_distribution",
            )
        }
        ep = before.specialization.resolved["expansion"]
        payload.update(
            schema_version="grc9v4-expansion-event-identity-v1",
            canonical_module_node_count=8,
            expansion_policy_digest=payload_identity(
                "expansion_policy_identity_payload",
                {"schema_version": "grc9v4-expansion-policy-identity-v1", "policy": ep},
            ),
            bond_seed=1,
            **{
                k: self.request.history_policy[k]
                for k in (
                    "candidate_history_policy_digest",
                    "carrier_history_policy_digest",
                )
            },
        )
        self.assertEqual(
            event,
            "grc-event-sha256:"
            + hashlib.sha256(canonical_json_bytes(payload)).hexdigest(),
        )

    def test_independent_numerics_and_ten_beat_continuation_for_both_roles(
        self,
    ) -> None:
        source = replace(
            self.seed.inputs,
            current=GRCV4AuthoritativeState((3.0, *((3 + 1 / 64,) * 9)), None, None),
            step_index=0,
            time=0,
            dt=1 / 4096,
        )
        np.testing.assert_allclose(
            self.seed.inputs.current.C,
            independent_cos_beat(source),
            atol=2e-13,
            rtol=2e-13,
        )
        self.committed()
        for role in ("current", "reset"):
            inputs = replace(
                self.owner.state.inputs,
                current=getattr(self.owner.state.inputs, role),
                dt=1 / 4096,
            )
            for beat in range(10):
                with self.subTest(role=role, beat=beat):
                    expected = independent_cos_beat(inputs)
                    step = ProvisionalCandidateCOSStep(inputs)
                    np.testing.assert_allclose(
                        step.next_inputs.current.C, expected, atol=2e-13, rtol=2e-13
                    )
                    self.assertGreaterEqual(min(step.next_inputs.current.C), 0)
                    self.assertEqual(
                        step.next_inputs.reset, self.owner.state.inputs.reset
                    )
                    inputs = step.next_inputs
            native._cos_readmit(
                GRC9V4COSState(replace(inputs, dt=0), self.seed.specialization)
            )

    def test_checkpoint_replay_and_detached_payload_tampering(self) -> None:
        self.assertIsNot(
            self.owner.state.inputs.geometry.reference,
            self.seed.inputs.geometry.reference,
        )
        self.assertIsNot(
            self.owner.state.inputs.geometry.reference.graph.port_graph,
            self.seed.inputs.geometry.reference.graph.port_graph,
        )
        self.committed()
        checkpoint = self.owner.checkpoint()
        # Recorded by executing the accepted eeb82e9 owner against this exact
        # fixture; the C_PC sharing refactor must preserve all C_OS wire bytes.
        self.assertEqual(
            hashlib.sha256(checkpoint).hexdigest(),
            "b87595b68e6a344b17062de0df5b44fd498780ed3121233e33c27cfbed8b78f4",
        )
        self.assertEqual(GRC9V4COSOperation.replay(checkpoint).checkpoint(), checkpoint)
        mutations: tuple[Any, ...] = (
            lambda d: d["state"]["inputs"]["current"]["C"].__setitem__(0, 123),
            lambda d: d["state"]["inputs"]["reset"]["C"].__setitem__(0, 123),
            lambda d: d["state"]["inputs"]["reference"]["graph"]["edges"][0][
                "tail"
            ].__setitem__("port", 9),
            lambda d: d["receipts"].pop(),
            lambda d: d["requests"][0].__setitem__("module_chirality", -1),
            lambda d: d["initial"].__setitem__(
                "model_identity", d["state"]["model_identity"]
            ),
        )
        for mutate in mutations:
            data = json.loads(checkpoint)
            mutate(data)
            with self.assertRaises(ValueError):
                GRC9V4COSOperation.replay(canonical_json_bytes(data))
        self.assertEqual(self.owner.checkpoint(), checkpoint)

    def test_stale_input_predicate_and_semantic_failures_leave_everything_intact(
        self,
    ) -> None:
        for changes in (
            {"source_state_digest": "grcv4-state-sha256:" + "0" * 64},
            {"target_specialization_id": "grc9v4-specialization-sha256:" + "0" * 64},
            {"module_chirality": None},
            {"growth_phase": None},
            {"resource_distribution": (1 / 3, 1 / 3, 1 / 3)},
            {"expected_target_graph_digest": "grc-graph-sha256:" + "0" * 64},
            {"source_node_id": 1},
        ):
            with self.subTest(changes=changes):
                checkpoint = self.owner.checkpoint()
                result = self.owner.expand(replace(self.request, **changes))
                self.assertFalse(result.committed)
                assert result.failure is not None
                self.assertEqual(
                    result.failure.prestate_digest, result.failure.poststate_digest
                )
                self.assertEqual(self.owner.checkpoint(), checkpoint)
                self.assertEqual(self.owner.receipts, ())
        self.committed()
        checkpoint = self.owner.checkpoint()
        self.assertFalse(self.owner.expand(self.request).committed)
        self.assertEqual(self.owner.checkpoint(), checkpoint)

    def test_current_and_reset_charge_failures_and_late_receipt_failure_are_atomic(
        self,
    ) -> None:
        transfer = GRC9V4COSExpansion.transfer
        for failing_role in (0, 1):
            calls: list[Any] = []

            def changed(
                target: Any,
                state: Any,
                calls: list[Any] = calls,
                failing_role: int = failing_role,
            ) -> Any:
                result = transfer(target, state)
                calls.append(state)
                return (
                    replace(result, C=(result.C[0] + 1.0, *result.C[1:]))
                    if len(calls) - 1 == failing_role
                    else result
                )

            before = self.owner.checkpoint()
            with patch.object(GRC9V4COSExpansion, "transfer", changed):
                result = self.owner.expand(self.request)
            self.assertFalse(result.committed)
            assert result.failure is not None
            self.assertEqual(result.failure.code, "target_readmission_failure")
            self.assertEqual(self.owner.checkpoint(), before)
        with patch.object(
            native, "make_commit_receipts", side_effect=ValueError("receipt failure")
        ):
            result = self.owner.expand(self.request)
        self.assertFalse(result.committed)
        self.assertEqual(self.owner.checkpoint(), before)

    def test_concurrent_requests_publish_exactly_one_event(self) -> None:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(len(self.owner.receipts), 4)

    def test_history_channels_cannot_claim_carrier_reset_or_drop_c_rederivation(
        self,
    ) -> None:
        for subject in ("candidate", "carrier"):
            history: Any = self.request.to_payload()["history_policy"]
            history[subject]["source_history_digest"] = (
                "grcv4-history-content-sha256:" + "0" * 64
            )
            if subject == "carrier":
                history[subject].update(
                    policy_id="carrier_archive_and_reset_whole_v1",
                    disposition="whole_carrier_reset",
                    information_loss="carrier_history_loss",
                )
            # Rehash the altered declaration: policy consistency, not stale
            # digest detection, must reject the claimed nonexistent history.
            history[subject + "_history_policy_digest"] = payload_identity(
                "history_channel_policy_identity_payload",
                {
                    "schema_version": "grcv4-history-channel-policy-identity-v1",
                    "policy": history[subject],
                },
            )
            checkpoint = self.owner.checkpoint()
            result = self.owner.expand(replace(self.request, history_policy=history))
            self.assertFalse(result.committed)
            assert result.failure is not None
            self.assertIn("absent carrier history", result.failure.message)
            self.assertEqual(self.owner.checkpoint(), checkpoint)

    def test_source_reset_charge_and_exact_cutoff_regressions(self) -> None:
        bad = replace(self.seed.inputs.reset, C=(0.0,) * 10)
        with self.assertRaises(ValueError):
            GRC9V4COSOperation(
                replace(self.seed, inputs=replace(self.seed.inputs, reset=bad))
            )
        with self.assertRaisesRegex(ValueError, "cutoff|gap|singular"):
            native_cos_fixture(cutoff=1)

    def with_os_tolerance(
        self, tolerance: float, *, equal_roles: bool = False
    ) -> tuple[GRC9V4COSState, GRC9V4ExpansionRequestInput]:
        reference = self.seed.inputs.geometry.reference
        params: Any = reference.profile.params_resolved.to_payload()
        identity = reference.profile.identity_payload.to_payload()
        params["realization"]["tolerance"] = tolerance
        identity["params_hash"] = payload_identity("resolved_params", params)
        reference = replace(reference, profile=resolve_profile(params, identity))
        inputs = replace(self.seed.inputs, geometry=reference.geometry())
        if equal_roles:
            inputs = replace(inputs, reset=inputs.current)
        seed = replace(self.seed, inputs=inputs)
        return seed, replace(
            self.request,
            source_state_digest=seed.scientific_digest,
            target_profile_template_id=cos_profile_template(
                reference
            ).profile_template_id,
        )

    def test_actual_target_os_split_failures_reject_current_and_reset_atomically(
        self,
    ) -> None:
        # These are genuine domain failures, with no injected kernel exception.
        # Both source roles and the old zero-duration target gate pass. The
        # strict complete OS read rejects target reset alone at 2^-54, and
        # target current (and the equal reset) at 2^-56.
        for tolerance, equal_roles in ((2**-54, False), (2**-56, True)):
            with self.subTest(tolerance=tolerance):
                seed, request = self.with_os_tolerance(
                    tolerance, equal_roles=equal_roles
                )
                for role in (seed.inputs.current, seed.inputs.reset):
                    CandidateCOSPass(replace(seed.inputs, current=role, dt=1))
                owner = GRC9V4COSOperation(seed)
                graph = seed.inputs.geometry.reference.graph.port_graph
                assert graph is not None
                plan = GRC9V4ExpansionPlan(
                    graph,
                    seed.scientific_digest,
                    request,
                    GRC9ExpansionPolicy.from_payload(
                        seed.specialization.resolved["expansion"]
                    ),
                )
                target = GRC9V4COSExpansion(plan, seed.inputs.geometry.reference)
                inputs = replace(
                    seed.inputs,
                    geometry=target.target.geometry(),
                    current=target.transfer(seed.inputs.current),
                    reset=target.transfer(seed.inputs.reset),
                )
                ProvisionalCandidateCOSStep(replace(inputs, dt=0))
                if not equal_roles:
                    CandidateCOSPass(replace(inputs, dt=1))
                failing = inputs.current if equal_roles else inputs.reset
                with self.assertRaisesRegex(OSStageError, "split tolerance"):
                    CandidateCOSPass(replace(inputs, current=failing, dt=1))
                checkpoint = owner.checkpoint()
                result = owner.expand(request)
                self.assertFalse(result.committed)
                assert result.failure is not None
                self.assertEqual(result.failure.code, "target_readmission_failure")
                self.assertEqual(result.failure.stage, "target_readmission")
                self.assertIn("split tolerance", result.failure.message)
                self.assertEqual(
                    result.failure.prestate_digest, result.failure.poststate_digest
                )
                self.assertEqual(owner.checkpoint(), checkpoint)
                self.assertEqual(owner.receipts, ())

    def test_seed_admission_checks_reset_os_even_when_zero_step_passes(self) -> None:
        seed, _ = self.with_os_tolerance(2**-58)
        ProvisionalCandidateCOSStep(replace(seed.inputs, dt=0))
        CandidateCOSPass(replace(seed.inputs, dt=1))
        with self.assertRaisesRegex(OSStageError, "split tolerance"):
            GRC9V4COSOperation(seed)

    def test_os_read_duration_is_irrelevant_and_event_never_advances_clock(
        self,
    ) -> None:
        surfaces = [
            CandidateCOSPass(replace(self.seed.inputs, dt=dt))
            for dt in (2**-1074, 1.0, 2**52)
        ]
        for surface in surfaces[1:]:
            self.assertEqual(
                surface.corrector.current.values, surfaces[0].corrector.current.values
            )
            self.assertEqual(
                surface.residual.exact_values, surfaces[0].residual.exact_values
            )
        # No headroom for an ordinary step-index increment; event reads must
        # still succeed and retain the exact clock/index/current/reset role.
        seed = replace(
            self.seed,
            inputs=replace(self.seed.inputs, time=2**52, step_index=2**53 - 1),
        )
        owner = GRC9V4COSOperation(seed)
        result = owner.expand(
            replace(self.request, source_state_digest=seed.scientific_digest)
        )
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.state.inputs.time, seed.inputs.time)
        self.assertEqual(owner.state.inputs.step_index, seed.inputs.step_index)
        self.assertEqual(owner.state.inputs.dt, 0)
        self.assertNotEqual(owner.state.inputs.current, owner.state.inputs.reset)

    def weighted_seed(self) -> GRC9V4COSState:
        reference = self.seed.inputs.geometry.reference
        weights = {f"e{i}": i / 4 for i in range(1, 10)}
        params: Any = reference.profile.params_resolved.to_payload()
        identity = reference.profile.identity_payload.to_payload()
        params["candidate"].update(
            W_C_tr=weights,
            W_C_tr_content_digest=payload_identity(
                "wctr_identity_payload",
                {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
            ),
            eta_C=1.5,
            kappa_M_C=0.25,
        )
        params["geometry"]["reference_hodge_digest"] = payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": weights,
            },
        )
        identity["params_hash"] = payload_identity("resolved_params", params)
        reference = replace(
            reference,
            profile=resolve_profile(params, identity),
            edge_weights=FrozenJSONMap(weights),
        )
        data = self.seed.specialization.to_payload()
        data["resolved"]["expansion"]["bond_seed"] = 0.5
        data["identity_payload"]["specialization_params_hash"] = payload_identity(
            "resolved_specialization", data["resolved"]
        )
        return replace(
            self.seed,
            inputs=replace(self.seed.inputs, geometry=reference.geometry()),
            specialization=GRC9V4Specialization(
                FrozenJSONMap(data["resolved"]), FrozenJSONMap(data["identity_payload"])
            ),
        )

    def request_for(
        self, seed: GRC9V4COSState, **changes: Any
    ) -> GRC9V4ExpansionRequestInput:
        reference = seed.inputs.geometry.reference
        return replace(
            self.request,
            source_state_digest=seed.scientific_digest,
            source_graph_digest=reference.graph.graph_digest,
            target_profile_template_id=cos_profile_template(
                reference
            ).profile_template_id,
            target_specialization_id=seed.specialization.specialization_id,
            **changes,
        )

    def test_weighted_native_targets_match_paper_equations_and_simplex_extremes(
        self,
    ) -> None:
        # Paper D.3.2--D.3.5, D.5.3 and A.6. Nonidentity H, nonunit eta,
        # retained conditioning and a distinct new-edge seed prevent accidental
        # equality of H_M, mobility and the two identification maps.
        seed = self.weighted_seed()
        for degree, chirality, phase, shares in (
            (9, -1, None, (1.0, 0.0, 0.0)),
            (31, 1, 1, (0.0, 1.0, 0.0)),
            (52, -1, 2, (0.0, 0.0, 1.0)),
            (52, 1, 3, (0.5, 0.25, 0.25)),
        ):
            with self.subTest(degree=degree, chirality=chirality, phase=phase):
                owner = GRC9V4COSOperation(seed)
                result = owner.expand(
                    self.request_for(
                        seed,
                        target_effective_degree=degree,
                        module_chirality=chirality,
                        growth_phase=phase,
                        resource_distribution=shares,
                    )
                )
                self.assertTrue(result.committed, result.failure)
                for source, target in (
                    (seed.inputs.current, owner.state.inputs.current),
                    (seed.inputs.reset, owner.state.inputs.reset),
                ):
                    graph = owner.state.inputs.geometry.reference.graph
                    primary: Any = result.emitted_receipts[0].identity_payload
                    prefix = cast(str, primary["event_id"]) + "/"
                    for node, value in zip(graph.live_node_ids, target.C, strict=True):
                        if isinstance(node, int):
                            expected = source.C[node]
                        elif "/satellite/" in node:
                            expected = float(
                                Fraction(source.C[0])
                                * Fraction(shares[int(node[-1]) - 1])
                            )
                        else:
                            self.assertTrue(node.startswith(prefix))
                            expected = 0.0
                        self.assertEqual(value, expected)
                    inputs = replace(owner.state.inputs, current=target, dt=1 / 4096)
                    surface = CandidateCOSPass(inputs)
                    for point in (surface.predictor, surface.corrector):
                        oracle = dense_current_oracle(point.inputs)
                        for field, actual in (
                            ("hm", point.algebra.retained_hodge.matrix),
                            ("phi", point.algebra.potential.values),
                            ("j0", point.algebra.baseline.values),
                            ("q", point.algebra.physical_identification),
                            ("current", point.current.values),
                            ("read", point.read.flux.values),
                        ):
                            np.testing.assert_allclose(
                                actual,
                                oracle[field],
                                rtol=3e-12,
                                atol=3e-12,
                                err_msg=field,
                            )
                        weights = point.algebra.transport.params.W_C_tr
                        np.testing.assert_array_equal(
                            point.algebra.transport.mobility.matrix,
                            np.diag(
                                np.array(
                                    [
                                        1.5 * cast(float, weights[e])
                                        for e in graph.live_edge_ids
                                    ]
                                )
                            ),
                        )
                        self.assertNotEqual(
                            point.algebra.retained_hodge.matrix,
                            point.algebra.transport.mobility.matrix,
                        )
                    expected_next = independent_cos_beat(inputs)
                    if max(shares) == 1:
                        # A valid event is not a positive-cone invariance proof.
                        # The paper's fourth-order transport can point outward
                        # at a newly zero coordinate; shrinking dt cannot admit
                        # that outward derivative. Never floor or clip it.
                        self.assertLess(float(min(expected_next)), 0)
                        divergence = (
                            np.array(graph.incidence) @ surface.corrector.current.values
                        )
                        self.assertTrue(
                            any(
                                c == 0 and d > 1e-10
                                for c, d in zip(target.C, divergence, strict=True)
                            )
                        )
                        checkpoint = owner.checkpoint()
                        for dt in (1 / 4096, 2**-20):
                            with self.assertRaisesRegex(
                                ResourceBoundaryError, "nonnegative"
                            ):
                                ProvisionalCandidateCOSStep(replace(inputs, dt=dt))
                        self.assertEqual(owner.checkpoint(), checkpoint)
                    else:
                        step = ProvisionalCandidateCOSStep(inputs)
                        np.testing.assert_allclose(
                            step.next_inputs.current.C,
                            expected_next,
                            rtol=3e-12,
                            atol=3e-12,
                        )

    def test_weighted_event_covaries_under_order_and_orientation_changes(self) -> None:
        seed = self.weighted_seed()
        base_owner = GRC9V4COSOperation(seed)
        first = base_owner.expand(self.request_for(seed))
        self.assertTrue(first.committed, first.failure)
        original = seed.inputs.geometry.reference.graph.port_graph
        assert original is not None
        for mask in (0b101010101, 0b111111111):
            graph = GRC9V4PortGraph(
                original.live_node_ids[::-1],
                tuple(
                    replace(e, tail=e.head, head=e.tail) if mask & (1 << i) else e
                    for i, e in reversed(list(enumerate(original.edges)))
                ),
            )
            reference = replace(
                seed.inputs.geometry.reference, graph=GRCV4Graph.from_port_graph(graph)
            )
            transformed = replace(
                seed,
                inputs=replace(
                    seed.inputs,
                    geometry=reference.geometry(),
                    current=replace(seed.inputs.current, C=seed.inputs.current.C[::-1]),
                    reset=replace(seed.inputs.reset, C=seed.inputs.reset.C[::-1]),
                ),
            )
            owner = GRC9V4COSOperation(transformed)
            second = owner.expand(self.request_for(transformed))
            self.assertTrue(second.committed, second.failure)
            states = (base_owner.state, owner.state)
            events = [
                cast(Any, r.emitted_receipts[0].identity_payload)["event_id"]
                for r in (first, second)
            ]
            self.assertNotEqual(events[0], events[1])
            for role in ("current", "reset"):
                resources, divergences = [], []
                for state, event in zip(states, events, strict=True):
                    inputs = state.inputs
                    authority = getattr(inputs, role)
                    target_graph = inputs.geometry.reference.graph
                    labels = [
                        n.replace(event, "event") if type(n) is str else n
                        for n in target_graph.live_node_ids
                    ]
                    resources.append(dict(zip(labels, authority.C, strict=True)))
                    current = CandidateCOSPass(
                        replace(inputs, current=authority, dt=1)
                    ).corrector.current.values
                    divergences.append(
                        dict(
                            zip(
                                labels,
                                np.array(target_graph.incidence) @ current,
                                strict=True,
                            )
                        )
                    )
                self.assertEqual(resources[0], resources[1])
                for node in resources[0]:
                    self.assertAlmostEqual(
                        divergences[0][node], divergences[1][node], delta=3e-12
                    )

    def test_specialization_binding_and_candidate_gate(self) -> None:
        data = self.seed.specialization.to_payload()
        data["resolved"]["spark"]["gradient_tolerance"] = 0
        with self.assertRaises(ValueError):
            GRC9V4Specialization(
                FrozenJSONMap(data["resolved"]), FrozenJSONMap(data["identity_payload"])
            )
        data["identity_payload"]["specialization_params_hash"] = payload_identity(
            "resolved_specialization", data["resolved"]
        )
        spec = GRC9V4Specialization(
            FrozenJSONMap(data["resolved"]), FrozenJSONMap(data["identity_payload"])
        )
        owner = GRC9V4COSOperation(replace(self.seed, specialization=spec))
        request = replace(
            self.request,
            target_specialization_id=spec.specialization_id,
            source_state_digest=owner.state.scientific_digest,
        )
        result = owner.expand(request)
        self.assertFalse(result.committed)
        assert result.failure is not None
        self.assertIn("candidate", result.failure.message)
        self.assertEqual(owner.receipts, ())

    def test_extreme_positive_bonds_fail_real_target_admission_atomically(self) -> None:
        for bond, message in ((2**-1074, "conditioning"), (1e308, "finite")):
            with self.subTest(bond=bond):
                data = self.seed.specialization.to_payload()
                data["resolved"]["expansion"]["bond_seed"] = bond
                data["identity_payload"]["specialization_params_hash"] = (
                    payload_identity("resolved_specialization", data["resolved"])
                )
                seed = replace(
                    self.seed,
                    specialization=GRC9V4Specialization(
                        FrozenJSONMap(data["resolved"]),
                        FrozenJSONMap(data["identity_payload"]),
                    ),
                )
                owner = GRC9V4COSOperation(seed)
                checkpoint = owner.checkpoint()
                result = owner.expand(self.request_for(seed))
                self.assertFalse(result.committed)
                assert result.failure is not None
                self.assertEqual(result.failure.code, "target_readmission_failure")
                self.assertIn(message, result.failure.message)
                self.assertEqual(owner.checkpoint(), checkpoint)

    def test_rounded_charge_delta_is_receipted_and_zero_tolerance_rejects(self) -> None:
        # Exact dyadic simplex, but satellite products/reduction can round.
        # Use a literal independent implementation of the specified adjacent
        # binary64 charge tree, not a mathematical/f-sum substitute.
        shares = (5421 / 32768, 29653 / 65536, 25041 / 65536)
        self.assertEqual(sum(map(Fraction, shares)), 1)

        def charge(values: tuple[float, ...]) -> float:
            while len(values) > 1:
                values = tuple(
                    values[i] + values[i + 1] if i + 1 < len(values) else values[i]
                    for i in range(0, len(values), 2)
                )
            return values[0]

        source_charge = charge(self.seed.inputs.current.C)
        self.assertEqual(source_charge, self.seed.inputs.Q_target)
        self.assertEqual(charge(self.seed.inputs.reset.C), source_charge)
        result = self.owner.expand(replace(self.request, resource_distribution=shares))
        self.assertTrue(result.committed, result.failure)
        target_charge = charge(self.owner.state.inputs.current.C)
        self.assertEqual(target_charge, math.nextafter(source_charge, -math.inf))
        core = cast(Any, result.emitted_receipts[0].identity_payload)["core"]
        self.assertEqual(core["actual_charge_delta"], target_charge - source_charge)
        # The conservative map has zero declared injection. Retain Q_target;
        # charge tolerance admits only the measured binary64 reduction error.
        self.assertEqual(self.owner.state.inputs.Q_target, self.seed.inputs.Q_target)
        reference = self.seed.inputs.geometry.reference
        params: Any = reference.profile.params_resolved.to_payload()
        identity = reference.profile.identity_payload.to_payload()
        params["charge"].update(absolute_tolerance=0, relative_tolerance=0)
        identity["params_hash"] = payload_identity("resolved_params", params)
        reference = replace(reference, profile=resolve_profile(params, identity))
        seed = replace(
            self.seed, inputs=replace(self.seed.inputs, geometry=reference.geometry())
        )
        owner = GRC9V4COSOperation(seed)
        checkpoint = owner.checkpoint()
        rejected = owner.expand(self.request_for(seed, resource_distribution=shares))
        self.assertFalse(rejected.committed)
        assert rejected.failure is not None
        self.assertEqual(rejected.failure.code, "target_readmission_failure")
        self.assertIn("charge", rejected.failure.message)
        self.assertEqual(owner.checkpoint(), checkpoint)

    @unittest.skipUnless(importlib.util.find_spec("flint"), "optional FLINT backend")
    def test_backend_capture_and_python_flint_event_parity(self) -> None:
        checkpoints = []
        for backend in (ExactBackend.PYTHON, ExactBackend.FLINT):
            with exact_backend(backend):
                owner = GRC9V4COSOperation(self.seed)
            observations: list[ExactBackend] = []
            readmit = native._cos_readmit

            def observed(
                state: Any,
                observations: list[ExactBackend] = observations,
                readmit: Any = readmit,
            ) -> None:
                observations.append(current_exact_backend())
                readmit(state)

            with (
                exact_backend(
                    ExactBackend.FLINT
                    if backend is ExactBackend.PYTHON
                    else ExactBackend.PYTHON
                ),
                patch.object(native, "_cos_readmit", observed),
            ):
                self.assertTrue(owner.expand(self.request).committed)
            self.assertEqual(observations, [backend, backend])
            checkpoints.append(owner.checkpoint())
        self.assertEqual(checkpoints[0], checkpoints[1])


class NativeCPCEventTests(unittest.TestCase):
    backend: ExactBackend
    seed: GRC9V4CPCState
    request: GRC9V4ExpansionRequestInput
    initial: GeometryStageInputs

    @classmethod
    def setUpClass(cls) -> None:
        cls.backend = (
            ExactBackend.FLINT
            if importlib.util.find_spec("flint")
            else ExactBackend.PYTHON
        )
        with exact_backend(cls.backend):
            cls.seed, cls.request, cls.initial = native_cpc_fixture()

    def setUp(self) -> None:
        scope = exact_backend(self.backend)
        scope.__enter__()
        self.addCleanup(scope.__exit__, None, None, None)
        self.owner = GRC9V4CPCOperation(self.seed)

    def committed(self) -> Any:
        result = self.owner.expand(self.request)
        self.assertTrue(result.committed, result.failure)
        return result

    def test_actual_whole_role_archives_zero_target_and_separate_loss_receipts(
        self,
    ) -> None:
        result = self.committed()
        before, after = self.seed, self.owner.state
        self.assertNotEqual(before.inputs.current.Z_4, self.initial.current.Z_4)
        self.assertEqual(before.inputs.reset, self.initial.reset)
        self.assertNotEqual(before.inputs.current.Z_4, before.inputs.reset.Z_4)
        self.assertTrue(any(cast(tuple[float, ...], before.inputs.current.Z_4)))
        self.assertTrue(any(cast(tuple[float, ...], before.inputs.reset.Z_4)))
        archive = self.owner.carrier_archives[0].to_dict()
        source = before.inputs.geometry.reference.graph
        target = after.inputs.geometry.reference.graph
        self.assertEqual(archive["source_edge_ids"], list(source.live_edge_ids))
        self.assertEqual(archive["source_state_digest"], before.scientific_digest)
        self.assertEqual(archive["source_graph_digest"], source.graph_digest)
        content = {
            "schema_version": "grcv4-history-content-identity-v1",
            "subject": "carrier",
            "content": list(
                cast(tuple[float, ...], before.inputs.current.Z_4)
                + cast(tuple[float, ...], before.inputs.reset.Z_4)
            ),
        }
        self.assertEqual(archive["history_content"], content)
        self.assertEqual(
            archive["history_digest"],
            payload_identity("history_content_identity_payload", content),
        )
        primary = result.emitted_receipts[0].identity_payload.to_dict()
        self.assertEqual(
            primary["history"]["carrier"]["source_history_digest"],
            archive["history_digest"],
        )
        expected_zero = {
            **content,
            "content": [0.0] * (2 * len(target.live_edge_ids) ** 2),
        }
        self.assertEqual(
            primary["history"]["carrier"]["target_history_digest"],
            payload_identity("history_content_identity_payload", expected_zero),
        )
        self.assertEqual(
            primary["history"]["carrier"]["disposition"], "whole_carrier_reset"
        )
        for receipt in result.emitted_receipts:
            self.assertEqual(
                receipt.identity_payload["core"]["information_losses"],
                ("carrier_history_loss",),
            )
        self.assertEqual(
            result.emitted_receipts[2].identity_payload["information_loss"], "none"
        )
        self.assertEqual(
            result.emitted_receipts[3].identity_payload["information_loss"],
            "carrier_history_loss",
        )
        self.assertEqual(primary["history"]["candidate"]["disposition"], "rederived")
        self.assertIsNone(primary["history"]["candidate"]["source_history_digest"])
        self.assertIsNone(primary["history"]["candidate"]["target_history_digest"])
        self.assertEqual(primary["core"]["target_model_identity"], after.model_identity)
        self.assertEqual(primary["core"]["target_reset_digest"], after.reset_digest)
        self.assertEqual(primary["core"]["actual_charge_delta"], 0)
        self.assertNotEqual(after.model_identity, before.model_identity)
        self.assertNotEqual(after.reset_digest, before.reset_digest)
        for state in (before, after):
            self.assertNotIn(
                state.inputs.geometry.reference.profile.complete_profile_id,
                list_supported_profiles(),
            )
        self.assertEqual(
            (after.inputs.time, after.inputs.step_index, after.inputs.Q_target),
            (before.inputs.time, before.inputs.step_index, before.inputs.Q_target),
        )
        self.assertEqual(
            after.inputs.geometry, after.inputs.geometry.reference.geometry()
        )
        self.assertEqual(
            after.inputs.geometry.reference.profile.params_resolved.realization,
            before.inputs.geometry.reference.profile.params_resolved.realization,
        )
        for old, new in (
            (before.inputs.current, after.inputs.current),
            (before.inputs.reset, after.inputs.reset),
        ):
            self.assertEqual(new.Z_4, (0.0,) * len(target.live_edge_ids) ** 2)
            self.assertIsNone(new.W_A)
            for node, value in zip(target.live_node_ids, new.C, strict=True):
                if isinstance(node, int):
                    expected = old.C[node]
                elif "/satellite/" in node:
                    expected = float(
                        Fraction(old.C[0])
                        * (Fraction(1, 2) if node.endswith("/1") else Fraction(1, 4))
                    )
                else:
                    expected = 0.0
                self.assertEqual(value, expected)
        for e in source.live_edge_ids:
            self.assertEqual(
                after.inputs.geometry.reference.edge_weights[e],
                before.inputs.geometry.reference.edge_weights[e],
            )
        for e in set(target.live_edge_ids) - set(source.live_edge_ids):
            self.assertEqual(after.inputs.geometry.reference.edge_weights[e], 1)

    def assert_independent_step(
        self, inputs: GeometryStageInputs
    ) -> GeometryStageInputs:
        ref = inputs.geometry.reference
        size = len(ref.graph.live_edge_ids)
        assert inputs.current.Z_4 is not None
        weights = ref.edge_weights
        # Exact represented affine Hodge, including off-diagonal old carrier.
        expected_h = [
            [
                float(
                    Fraction(cast(float, weights[e])) * int(i == j)
                    + Fraction(ref.profile.params_resolved.geometry.kappa_H)
                    * Fraction(inputs.current.Z_4[i * size + j])
                )
                for j in range(size)
            ]
            for i, e in enumerate(ref.graph.live_edge_ids)
        ]
        np.testing.assert_array_equal(inputs.geometry.one_form_hodge.matrix, expected_h)
        resource, carrier, source = independent_pc_beat(inputs)
        step = ProvisionalCandidatePCStep(inputs)
        np.testing.assert_allclose(
            step.read.point.current.values,
            dense_current_oracle(inputs)["current"],
            rtol=3e-12,
            atol=3e-12,
        )
        np.testing.assert_allclose(
            step.read.structural_source.increment, source, rtol=3e-12, atol=3e-20
        )
        np.testing.assert_allclose(
            step.next_inputs.current.C, resource, rtol=3e-12, atol=3e-12
        )
        assert step.next_inputs.current.Z_4 is not None
        np.testing.assert_allclose(
            np.array(step.next_inputs.current.Z_4),
            np.array(carrier),
            rtol=3e-12,
            atol=3e-20,
        )
        self.assertEqual(step.carrier_writes, 1)
        self.assertEqual(step.next_inputs.reset, inputs.reset)
        return step.next_inputs

    def test_independent_source_schedule_both_role_continuation_and_delayed_geometry(
        self,
    ) -> None:
        source = self.assert_independent_step(self.initial)
        self.assertEqual(source.current, self.seed.inputs.current)
        self.assertEqual(source.reset, self.seed.inputs.reset)
        self.committed()
        base = self.owner.state.inputs
        for role in (base.current, base.reset):
            with self.subTest(reset=role == base.reset):
                inputs = replace(base, current=role, dt=1 / 4096)
                self.assertEqual(inputs.geometry, inputs.geometry.reference.geometry())
                for i in range(10):
                    inputs = self.assert_independent_step(inputs)
                    self.assertTrue(any(cast(tuple[float, ...], inputs.current.Z_4)))
                    self.assertNotEqual(
                        inputs.geometry, inputs.geometry.reference.geometry()
                    )
                native._cpc_readmit(
                    replace(self.owner.state, inputs=replace(inputs, dt=0))
                )
                # The zero old-carrier entry has no geometry/history effect.
                # After formation and ten writes, old Z changes the next read.
                zero = replace(
                    inputs.current,
                    Z_4=(0.0,) * len(cast(tuple[float, ...], inputs.current.Z_4)),
                )
                control = replace(
                    inputs, current=zero, geometry=inputs.geometry.reference.geometry()
                )
                actual = np.array(CandidatePCRead(inputs).point.current.values)
                other = np.array(CandidatePCRead(control).point.current.values)
                truth, control_truth = (
                    dense_current_oracle(inputs)["current"],
                    dense_current_oracle(control)["current"],
                )
                error = max(abs(actual - truth)) + max(abs(other - control_truth))
                ulp = max(math.ulp(float(x)) for x in (*actual, *other))
                self.assertGreater(float(max(abs(actual - other))), 4 * error + 8 * ulp)

    def test_zero_duration_admission_never_writes_or_advances(self) -> None:
        before = self.seed.to_payload()
        with patch.object(
            native, "ProvisionalCandidatePCStep", wraps=ProvisionalCandidatePCStep
        ) as probe:
            native._cpc_readmit(self.seed)
        self.assertEqual(probe.call_args.args[0].dt, 0)
        self.assertEqual(self.seed.to_payload(), before)
        zero_step = ProvisionalCandidatePCStep(replace(self.seed.inputs, dt=0))
        self.assertEqual(zero_step.carrier_writes, 0)
        self.assertEqual(zero_step.next_inputs.current, self.seed.inputs.current)
        self.assertEqual(zero_step.next_inputs.reset, self.seed.inputs.reset)
        at_limit = replace(
            self.seed,
            inputs=replace(self.seed.inputs, step_index=2**53 - 1, time=2**52),
        )
        owner = GRC9V4CPCOperation(at_limit)
        result = owner.expand(
            replace(self.request, source_state_digest=at_limit.scientific_digest)
        )
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.state.inputs.time, at_limit.inputs.time)
        self.assertEqual(owner.state.inputs.step_index, at_limit.inputs.step_index)

    def test_checkpoint_replays_complete_archives_and_rejects_tampering(self) -> None:
        self.committed()
        checkpoint = self.owner.checkpoint()
        restored = GRC9V4CPCOperation.replay(checkpoint)
        self.assertEqual(restored.checkpoint(), checkpoint)
        exported = self.owner.carrier_archives[0].to_dict()
        cast(Any, exported["history_content"])["content"][0] += 1
        self.assertEqual(self.owner.checkpoint(), checkpoint)
        for mutation in (
            "missing",
            "content",
            "order",
            "digest",
            "reset",
            "policy",
            "target",
            "loss",
        ):
            data = json.loads(checkpoint)
            archive = data["carrier_archives"][0]
            if mutation == "missing":
                data["carrier_archives"] = []
            elif mutation == "content":
                archive["history_content"]["content"][0] += 1 / 256
                archive["history_digest"] = payload_identity(
                    "history_content_identity_payload", archive["history_content"]
                )
            elif mutation == "order":
                archive["source_edge_ids"].reverse()
            elif mutation == "digest":
                archive["source_state_digest"] = "grcv4-state-sha256:" + "0" * 64
            elif mutation == "reset":
                archive["history_content"]["content"][-1] *= -1
            elif mutation == "policy":
                data["requests"][0]["history_policy"]["carrier"]["information_loss"] = (
                    "none"
                )
            elif mutation == "target":
                data["state"]["inputs"]["current"]["Z_4"][0] = 1 / 256
            else:
                data["receipts"][0]["identity_payload"]["core"][
                    "information_losses"
                ] = []
            with (
                self.subTest(mutation=mutation),
                self.assertRaises((ValueError, TypeError)),
            ):
                GRC9V4CPCOperation.replay(canonical_json_bytes(data))
        with self.assertRaises(ValueError):
            GRC9V4COSOperation.replay(checkpoint)
        with self.assertRaises(TypeError):
            GRC9V4COSOperation(self.seed)
        cos, _ = native_cos_fixture()
        with self.assertRaises(TypeError):
            GRC9V4CPCOperation(cos)

    def test_history_policy_binds_actual_current_and_reset_before_transfer(
        self,
    ) -> None:
        for role in ("current", "reset"):
            authority = getattr(self.seed.inputs, role)
            z = list(authority.Z_4)
            z[-1] += 1 / 256
            inputs = replace(
                self.seed.inputs, **{role: replace(authority, Z_4=tuple(z))}
            )
            inputs = replace(inputs, geometry=carrier_geometry(inputs, inputs.current))
            seed = replace(self.seed, inputs=inputs)
            owner = GRC9V4CPCOperation(seed)
            checkpoint = owner.checkpoint()
            # A fresh scientific digest is insufficient: the independently bound
            # request carrier digest must also describe this actual role pair.
            request = replace(self.request, source_state_digest=seed.scientific_digest)
            with patch.object(
                native,
                "GRC9V4ExpansionPlan",
                side_effect=AssertionError("must not allocate"),
            ):
                result = owner.expand(request)
            self.assertFalse(result.committed)
            assert result.failure is not None
            self.assertIn("actual whole carrier pair", result.failure.message)
            self.assertEqual(owner.checkpoint(), checkpoint)
        for field, value in (
            ("policy_id", "identity_carrier_history_v1"),
            ("target_initializer_id", None),
            ("information_loss", "none"),
            ("disposition", "not_applicable"),
        ):
            policy: Any = self.request.to_payload()["history_policy"]
            policy["carrier"][field] = value
            if field == "disposition":
                policy["carrier"].update(
                    source_history_digest=None,
                    target_initializer_id=None,
                    information_loss="none",
                )
            policy["carrier_history_policy_digest"] = payload_identity(
                "history_channel_policy_identity_payload",
                {
                    "schema_version": "grcv4-history-channel-policy-identity-v1",
                    "policy": policy["carrier"],
                },
            )
            checkpoint = self.owner.checkpoint()
            result = self.owner.expand(replace(self.request, history_policy=policy))
            self.assertFalse(result.committed)
            self.assertEqual(self.owner.checkpoint(), checkpoint)

    def test_target_whole_chart_failure_rejects_even_with_regular_zero_carrier_point(
        self,
    ) -> None:
        data = self.seed.specialization.to_payload()
        data["resolved"]["expansion"]["bond_seed"] = 2
        data["identity_payload"]["specialization_params_hash"] = payload_identity(
            "resolved_specialization", data["resolved"]
        )
        spec = GRC9V4Specialization(
            FrozenJSONMap(data["resolved"]), FrozenJSONMap(data["identity_payload"])
        )
        seed = replace(self.seed, specialization=spec)
        request = replace(
            self.request,
            source_state_digest=seed.scientific_digest,
            target_specialization_id=spec.specialization_id,
        )
        owner = GRC9V4CPCOperation(seed)
        graph = seed.inputs.geometry.reference.graph.port_graph
        assert graph is not None
        plan = GRC9V4ExpansionPlan(
            graph,
            seed.scientific_digest,
            request,
            GRC9ExpansionPolicy.from_payload(spec.resolved["expansion"]),
        )
        target = GRC9V4CPCExpansion(
            plan, seed.inputs.geometry.reference, seed.inputs.current, seed.inputs.reset
        )
        inputs = replace(
            seed.inputs,
            geometry=target.target.geometry(),
            current=target.transfer(seed.inputs.current),
            reset=target.transfer(seed.inputs.reset),
        )
        for role in (inputs.current, inputs.reset):
            # A point solve and zero carrier radius check alone would pass.
            CandidateCCurrent(replace(inputs, current=role))
            self.assertFalse(any(cast(tuple[float, ...], role.Z_4)))
        checkpoint = owner.checkpoint()
        result = owner.expand(request)
        self.assertFalse(result.committed)
        assert result.failure is not None
        self.assertEqual(result.failure.code, "target_readmission_failure")
        self.assertIn("uniform source envelope", result.failure.message)
        self.assertEqual(
            result.failure.prestate_digest, result.failure.poststate_digest
        )
        self.assertEqual(
            result.failure.pre_lifecycle_digest, result.failure.post_lifecycle_digest
        )
        self.assertEqual(owner.checkpoint(), checkpoint)
        self.assertEqual(owner.carrier_archives, ())
        self.assertEqual(owner.receipts, ())

    def test_source_current_and_reset_carrier_domains_are_independent(self) -> None:
        for role in ("current", "reset"):
            for failure in ("radius", "symmetry", "absent"):
                authority = getattr(self.seed.inputs, role)
                z = list(authority.Z_4)
                if failure == "radius":
                    z[0] = 2
                elif failure == "symmetry":
                    z[1] += 1 / 256
                with (
                    self.subTest(role=role, failure=failure),
                    self.assertRaises(ValueError),
                ):
                    inputs = replace(
                        self.seed.inputs,
                        **{
                            role: replace(
                                authority, Z_4=None if failure == "absent" else tuple(z)
                            )
                        },
                    )
                    inputs = replace(
                        inputs, geometry=carrier_geometry(inputs, inputs.current)
                    )
                    GRC9V4CPCOperation(replace(self.seed, inputs=inputs))
        with self.assertRaisesRegex(ValueError, "realization geometry"):
            replace(
                self.seed,
                inputs=replace(
                    self.seed.inputs,
                    geometry=self.seed.inputs.geometry.reference.geometry(),
                ),
            )

    def test_both_resource_failures_and_late_archive_receipt_failures_publish_nothing(
        self,
    ) -> None:
        checkpoint = self.owner.checkpoint()
        transfer = GRC9V4CPCExpansion.transfer
        for failing in (self.seed.inputs.current, self.seed.inputs.reset):

            def corrupted(target: Any, state: Any, failing: Any = failing) -> Any:
                mapped = transfer(target, state)
                return (
                    replace(mapped, C=(mapped.C[0] + 1, *mapped.C[1:]))
                    if state == failing
                    else mapped
                )

            with patch.object(GRC9V4CPCExpansion, "transfer", corrupted):
                result = self.owner.expand(self.request)
            self.assertFalse(result.committed)
            self.assertEqual(self.owner.checkpoint(), checkpoint)
        for target, attr in (
            (GRC9V4CPCExpansion, "carrier_archive_payload"),
            (native, "make_commit_receipts"),
        ):
            with patch.object(
                target, attr, side_effect=ValueError("late publication failure")
            ):
                result = self.owner.expand(self.request)
            self.assertFalse(result.committed)
            self.assertEqual(self.owner.checkpoint(), checkpoint)
            self.assertEqual(self.owner.carrier_archives, ())
            self.assertEqual(self.owner.receipts, ())
        self.committed()
        self.assertEqual(len(self.owner.carrier_archives), 1)
        self.assertEqual(len(self.owner.receipts), 4)

    def test_concurrent_requests_archive_and_publish_exactly_once(self) -> None:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.owner.expand, (self.request, self.request)))
        self.assertEqual(sum(r.committed for r in results), 1)
        self.assertEqual(len(self.owner.carrier_archives), 1)
        self.assertEqual(len(self.owner.receipts), 4)

    def test_present_zero_source_carriers_still_use_explicit_reset_policy(self) -> None:
        zeros = (0.0,) * 81
        inputs = replace(
            self.seed.inputs,
            geometry=self.seed.inputs.geometry.reference.geometry(),
            current=replace(self.seed.inputs.current, Z_4=zeros),
            reset=replace(self.seed.inputs.reset, Z_4=zeros),
        )
        seed = replace(self.seed, inputs=inputs)
        owner = GRC9V4CPCOperation(seed)
        result = owner.expand(
            replace(
                self.request,
                source_state_digest=seed.scientific_digest,
                history_policy=cpc_history_policy(inputs.current, inputs.reset),
            )
        )
        self.assertTrue(result.committed, result.failure)
        history = cast(Any, result.emitted_receipts[0].identity_payload)["history"][
            "carrier"
        ]
        self.assertEqual(history["disposition"], "whole_carrier_reset")
        self.assertEqual(history["information_loss"], "carrier_history_loss")
        self.assertIsNotNone(history["source_history_digest"])
        self.assertNotEqual(
            history["source_history_digest"], history["target_history_digest"]
        )
        self.assertEqual(
            cast(Any, owner.carrier_archives[0])["history_content"]["content"],
            zeros + zeros,
        )

    @unittest.skipUnless(importlib.util.find_spec("flint"), "optional FLINT backend")
    def test_python_flint_checkpoint_parity_and_captured_backend(self) -> None:
        checkpoints = []
        for backend in (ExactBackend.PYTHON, ExactBackend.FLINT):
            with exact_backend(backend):
                owner = GRC9V4CPCOperation(self.seed)
            observations: list[ExactBackend] = []
            readmit = native._cpc_readmit

            def observed(
                state: GRC9V4CPCState,
                observations: list[ExactBackend] = observations,
                readmit: Callable[[GRC9V4CPCState], None] = readmit,
            ) -> None:
                observations.append(current_exact_backend())
                readmit(state)

            other = (
                ExactBackend.FLINT
                if backend is ExactBackend.PYTHON
                else ExactBackend.PYTHON
            )
            with exact_backend(other), patch.object(native, "_cpc_readmit", observed):
                result = owner.expand(self.request)
            self.assertTrue(result.committed, result.failure)
            self.assertEqual(observations, [backend, backend])
            checkpoints.append(owner.checkpoint())
        self.assertEqual(*checkpoints)


if __name__ == "__main__":
    unittest.main()
