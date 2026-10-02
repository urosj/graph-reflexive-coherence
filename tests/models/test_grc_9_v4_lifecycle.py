"""P9-8.1c independent baseline gates and admitted post-commit handoff.

No expansion, completed-spark or native nine-port lifecycle claim.
"""

from __future__ import annotations

import json
import math
import random
import sys
import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

from pygrc.models.grc_9_v4_lifecycle import (
    GRC9SparkPolicy,
    GRC9V4CandidateDetection,
    UnsupportedGRC9SparkLane,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortGraph,
    GRC9V4PostbeatRows,
)
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    NonfiniteGeometryError,
    OrientedEdge,
)
from pygrc.models.grc_v4_lifecycle import GRCV4Operation
from pygrc.models.grc_v4_profile import get_supported_profile, list_supported_profiles
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from tests.models.test_grc_9_v4_topology import edge, row_profile
from tests.models.test_grc_v4_candidate_c import current_fixture


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


if __name__ == "__main__":
    unittest.main()
