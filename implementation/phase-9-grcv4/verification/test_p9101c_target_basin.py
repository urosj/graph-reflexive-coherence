"""Focused retained-subject and complete-root pressure; no repeat native campaign."""

from copy import deepcopy
import unittest
import p9101c_target_basin as c


class ExactTargetBasinTests(unittest.TestCase):
    def test_all_exact_subjects_and_both_boundaries(self):
        for family in c.FAMILIES:
            with self.subTest(family=family):
                value, _ = c.check(family=family, equations=True)
                self.assertEqual(len(value["observations"]), 2)
                self.assertEqual(value["native_role_captures"], 4)

    def test_resealed_subject_boundary_role_and_full_geometry_mutations(self):
        mutations = (
            "subject",
            "boundary",
            "role",
            "geometry",
            "certificate",
            "rows",
            "scope",
        )
        for family in c.FAMILIES:
            original, _ = c.load(c.ROOT, family)
            old = c.predecessor.load(c.ROOT, family)[0]["evidence"]["v2"]
            for kind in mutations:
                with self.subTest(family=family, mutation=kind):
                    bad = deepcopy(original)
                    case = bad["observations"][1]
                    root = case["selected_roots"]["current"]
                    if kind == "subject":
                        bad["subject"]["model_identity"] = "unrelated"
                    elif kind == "boundary":
                        bad["observations"][1] = deepcopy(bad["observations"][0])
                        bad["observations"][1]["label"] = c.LABELS[1]
                    elif kind == "role":
                        case["selected_roots"]["current"] = deepcopy(
                            case["selected_roots"]["reset"]
                        )
                    elif kind == "geometry":
                        root["H1_form"][0][0] = float(2).hex()
                    elif kind == "certificate":
                        case["observations"]["current_observation"]["binding"][
                            "root_certificate_binding"
                        ] = "forged"
                    elif kind == "rows":
                        case["observations"]["current_observation"]["witness"]["rows"][
                            0
                        ]["gradient"][0] = float(7).hex()
                    else:
                        case["role_equations"]["current"][
                            "exact_root_signs_claimed"
                        ] = True
                    with self.assertRaises((AssertionError, ValueError)):
                        c.validate(c.predecessor.seal(bad), old)

    def test_original_oracle_refuses_out_of_domain_input(self):
        # A positive base geometry is insufficient: the reused formula needs I.
        from dataclasses import replace

        value, _ = c.load(c.ROOT, "C_OS")
        saved = c.restore_state(value["observations"][0]["saved_native_state"], "C_OS")
        ref = saved.inputs.geometry.reference
        weights = dict(ref.edge_weights)
        weights[next(iter(weights))] = 2
        # Use an operand proxy to test the assumption gate itself, without
        # obtaining incidental rejection from a stale production profile hash.
        from types import SimpleNamespace as NS

        fake_ref = NS(
            **{k: getattr(ref, k) for k in ("profile", "graph", "context", "K4_base")},
            edge_weights=weights,
        )
        fake = NS(
            inputs=NS(
                geometry=NS(reference=fake_ref),
                context=saved.inputs.context,
                current=saved.inputs.current,
            )
        )
        with self.assertRaisesRegex(AssertionError, "oracle reference/base"):
            c.assumptions(fake, "current")


if __name__ == "__main__":
    unittest.main()
