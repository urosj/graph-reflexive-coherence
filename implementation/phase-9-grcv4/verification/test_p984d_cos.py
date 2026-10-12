"""Independent deep allocation, excluded share recipes and saved OS pressure."""

from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import unittest
from unittest.mock import patch

import p984d_cos as run

b = run.b


class DeepCOSTests(unittest.TestCase):
    def test_layouts_native_plan_reference_charge_and_preflight(self):
        manifest = run.make_manifest()
        self.assertEqual(len(manifest["cases"]), 20)
        self.assertEqual(
            {v["expected"]["module_nodes"] for v in manifest["layouts"]},
            {9, 10, 11, 14},
        )
        self.assertEqual(
            {v["expected"]["maximum_core_depth"] for v in manifest["layouts"]}, {3, 4}
        )
        source = b.GeometryStageInputs.from_payload(
            manifest["expected_source"]["inputs"]
        )
        graph = source.geometry.reference.graph.port_graph
        policy = b.GRC9ExpansionPolicy.from_payload(
            manifest["expected_source"]["specialization"]["resolved"]["expansion"]
        )
        for layout, case in zip(manifest["layouts"], manifest["cases"], strict=True):
            request = b.GRC9V4ExpansionRequestInput.from_payload(case["request"])
            plan = b.GRC9V4ExpansionPlan(
                graph, request.source_state_digest, request, policy
            )
            self.assertEqual(
                plan.event_identity_payload(), case["oracle"]["event_identity"]
            )
            self.assertEqual(
                plan.target_graph.to_payload(), case["oracle"]["target_graph"]
            )
            mechanics = run.mechanics(layout)
            self.assertEqual(mechanics, case["mechanics"])
            self.assertEqual(
                len(mechanics["tree"]), layout["expected"]["module_nodes"] - 1
            )
            if layout["degree"] == 94:
                self.assertTrue(any(v.endswith("/04") for v in mechanics["depths"]))
                self.assertEqual(max(mechanics["depths"].values()), 4)
            target = run.target(manifest, case)
            self.assertNotEqual(target.current.C, target.reset.C)
            self.assertEqual(
                set(target.geometry.reference.profile.params_resolved.candidate.W_C_tr),
                set(target.geometry.reference.graph.live_edge_ids),
            )
            for role in run.ROLES:
                self.assertEqual(
                    sum(map(Fraction, getattr(source, role).C)),
                    sum(map(Fraction, getattr(target, role).C)),
                )
                self.assertIsNone(getattr(target, role).W_A)
                self.assertIsNone(getattr(target, role).Z_4)
        with ExitStack() as stack:
            for module, name in (
                (b, "CandidateCOSPass"),
                (b, "ProvisionalCandidateCOSStep"),
                (b.native, "GRC9V4COSOperation"),
            ):
                stack.enter_context(
                    patch.object(
                        module, name, side_effect=AssertionError("native forbidden")
                    )
                )
            rows = run.preflight(manifest)
        self.assertEqual(len(rows), 20)
        for row in rows:
            self.assertGreater(Fraction(row["reference_selector_gap_lower"]), 0)
            for role in run.ROLES:
                self.assertGreater(
                    min(row["dense_screen"]["roles"][role]["minimum_C_by_beat"]), 0
                )

    def test_failed_recipes_are_not_erased_by_successor(self):
        manifest = run.make_manifest()
        case = next(
            c
            for c in manifest["cases"]
            if c["request"]["target_effective_degree"] == 94
            and c["request"]["module_chirality"] == 1
            and c["request"]["growth_phase"] == 1
        )
        # Old unequal shares already fail the first current-role step.
        old = run.target(manifest, case, [1 / 4, 1 / 2, 1 / 4])
        self.assertLess(min(b.dense_os(replace(old, dt=b.DT))["C"]), -7e-4)
        # Nearly equal shares pass beat one but fail beat two at depth four.
        balanced = run.target(manifest, case, [22 / 64, 21 / 64, 21 / 64])
        first = b.dense_os(replace(balanced, dt=b.DT))
        self.assertGreater(min(first["C"]), 0)
        second = b.dense_os(
            replace(
                balanced,
                dt=b.DT,
                current=b.GRCV4AuthoritativeState(
                    tuple(map(float, first["C"])), None, None
                ),
            )
        )
        self.assertLess(min(second["C"]), -1e-7)
        # Real-simplex conservation is insufficient for represented event charge.
        rounded = run.target(manifest, case, [1 / 4, 3 / 8, 3 / 8])
        source = b.GeometryStageInputs.from_payload(
            manifest["expected_source"]["inputs"]
        )
        self.assertEqual(
            sum(map(Fraction, rounded.current.C))
            - sum(map(Fraction, source.current.C)),
            Fraction(1, 2**53),
        )
        self.assertEqual(
            sum(map(Fraction, rounded.reset.C)), sum(map(Fraction, source.reset.C))
        )
        accepted = run.target(manifest, case)
        self.assertEqual(
            sum(map(Fraction, accepted.current.C)), sum(map(Fraction, source.current.C))
        )
        # The zero-coupling L^2 stencil is only a design diagnostic, not an OS theorem.
        lap = b.np.asarray(accepted.geometry.reference.graph.incidence, dtype=int)
        lap = lap @ lap.T
        c = list(map(Fraction, accepted.current.C))
        lc = [
            sum((int(a) * x for a, x in zip(row, c, strict=True)), Fraction())
            for row in lap
        ]
        rates = [
            sum((int(a) * x for a, x in zip(row, lc, strict=True)), Fraction())
            for row in lap
        ]
        self.assertTrue(
            all(rate >= 0 for x, rate in zip(c, rates, strict=True) if x == 0)
        )

    def test_deep_retained_consumers_and_mutations(self):
        manifest, record = b.read(run.INPUTS), b.read(run.RESULTS)
        run.status(manifest, record)
        execution = run.previous.expand(record["execution"])
        i = next(
            i
            for i, c in enumerate(manifest["cases"])
            if c["request"]["target_effective_degree"] == 94
            and c["request"]["module_chirality"] == 1
            and c["request"]["growth_phase"] == 1
        )
        row, case = execution["cases"][i], manifest["cases"][i]
        with ExitStack() as stack:
            for module, name in (
                (b, "CandidateCOSPass"),
                (b, "ProvisionalCandidateCOSStep"),
                (b.native, "GRC9V4COSOperation"),
            ):
                stack.enter_context(
                    patch.object(
                        module, name, side_effect=AssertionError("native forbidden")
                    )
                )
            run.consumer.check_consumption(row, manifest, case)
            for role in run.ROLES:
                index = next(
                    i
                    for i, o in enumerate(row["observations"])
                    if o["stage"] == "target_continuation"
                    and o["role"] == role
                    and o["beat"] == 2
                )
                captured = row["consumption_evidence"][index]["value"]
                self.assertGreater(min(captured["poststate"]["current"]["C"]), 0)
                for kind in ("predictor", "geometry", "reset", "final", "sign"):
                    bad = deepcopy(captured)
                    if kind == "predictor":
                        point = bad["pass"]["corrector"]
                        point["current"] = point["read_current"] = deepcopy(
                            bad["pass"]["predictor"]["current"]
                        )
                    elif kind == "geometry":
                        bad["pass"]["corrector"] = deepcopy(bad["pass"]["predictor"])
                        run.consumer.check_point(
                            bad["pass"]["corrector"], case["comparison"]
                        )
                    elif kind == "reset":
                        bad["poststate"]["reset"] = bad["poststate"]["current"]
                    elif kind == "final":
                        bad["final"] = deepcopy(bad["pass"]["corrector"])
                    else:
                        bad["pass"]["corrector"]["read_flux"] = [
                            -x for x in bad["pass"]["corrector"]["read_flux"]
                        ]
                    with (
                        self.subTest(role=role, kind=kind),
                        self.assertRaises(ValueError),
                    ):
                        run.consumer.check_step(bad, case["comparison"])
        for kind in ("drop", "event_only", "missing_reset", "acceptance"):
            bad = deepcopy(record)
            raw = run.previous.expand(bad["execution"])
            if kind == "drop":
                raw["cases"].pop()
            elif kind == "event_only":
                raw["cases"][0]["case_passed"] = False
            elif kind == "missing_reset":
                raw["cases"][0]["consumption_evidence"].pop()
            else:
                raw["cases"][0]["user_accepted"] = True
            bad["execution"] = run.previous.compact(b.seal(raw))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                run.status(manifest, b.seal(bad))

    def test_deep_wrong_stage_discrimination_and_manifest_outliers(self):
        manifest = run.make_manifest()
        for case in manifest["cases"]:
            target = run.target(manifest, case)
            for role in run.ROLES:
                expected = b.dense_os(
                    replace(target, current=getattr(target, role), dt=b.DT)
                )
                with (
                    self.subTest(case=case["case_id"], role=role),
                    self.assertRaises(ValueError),
                ):
                    b.comparison(
                        expected["predictor_J"],
                        expected["corrector_J"],
                        case["comparison"],
                        "wrong_stage_J",
                    )
        for kind in ("depth", "shares", "horizon", "budget", "population"):
            bad = deepcopy(manifest)
            if kind == "depth":
                bad["cases"][0]["mechanics"]["depths"]["core"] = 1
            elif kind == "shares":
                bad["cases"][0]["request"]["resource_distribution"] = [
                    1 / 4,
                    1 / 2,
                    1 / 4,
                ]
            elif kind == "horizon":
                bad["cases"][0]["schedule"]["target_beats_per_role"] = 1
            elif kind == "budget":
                bad["cases"][0]["comparison"]["atol"] = 1
            else:
                bad["cases"].pop()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                run.check_manifest(b.seal(bad))


if __name__ == "__main__":
    unittest.main()
