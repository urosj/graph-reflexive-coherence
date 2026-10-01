"""Research-only feasibility discriminators; no new runtime profile admission.

Run directly with the repository .venv. Exact rational calculations below are
independent of production current/step code. Native domain parsing only checks
the scope of the already accepted RG2b completion declarations.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from pygrc.models.grc_v4_profile import get_supported_profile
from pygrc.models.grc_v4_rg2b import RG2bStageError
from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain


def laplacian(edges, weights, values):
    """Literal weighted difference sums, without production matrix helpers."""
    result = dict.fromkeys(values, Q(0))
    for edge in edges:
        u, v = edge["tail"]["node_id"], edge["head"]["node_id"]
        flux = Q(weights[edge["edge_id"]]) * (values[u] - values[v])
        result[u] += flux
        result[v] -= flux
    return result


class AllProfileFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads(
            (ROOT / "specs/grc-v4-conformance-vectors.json").read_text()
        )
        registry = json.loads(
            (ROOT / "implementation/phase-9-grcv4/tranche-7/ProfileG2Registry.json").read_text()
        )
        cls.profiles = {row["profile_family_id"]: get_supported_profile(row["complete_profile_id"])
                        for row in registry["records"]}

    def target(self):
        row = next(r for r in self.vectors["grc9_expansion_vectors"]
                   if r["fixture_id"] == "G9-EXPAND-D30-CHIRALITY-POSITIVE")
        target = row["expected"]
        return (target["target_edges"], dict(target["target_W_C_tr"]),
                {n: Q(c) for n, c in target["target_resource_by_node"].items()})

    def test_all_ten_generic_declarations_remain_in_scope(self):
        self.assertEqual(set(self.profiles),
                         {c + "_" + r for c in ("A", "C")
                          for r in ("OS", "CI", "PC", "CI_PC", "RG2b")})

    def test_both_rg2b_completion_domains_exclude_the_required_zero_core(self):
        _, _, resources = self.target()
        zero = next(c for n, c in resources.items() if n.endswith("/core"))
        self.assertEqual(zero, 0)
        for family in ("A_RG2b", "C_RG2b"):
            with self.subTest(family=family):
                d = RG2bGraphDomain.from_identity(
                    self.profiles[family].params_resolved.realization.extension_evaluator_id
                )
                self.assertTrue(0 < Q(d.inner) < Q(d.core) < Q(d.outer) < Q(d.center_C))
                self.assertGreater(abs(zero - Q(d.center_C)), Q(d.core))
                self.assertGreater(Q(d.center_C) - Q(d.outer), 0)
                # Enlarging the current outer chart through zero is rejected;
                # a new completion cannot be hidden behind the same contract.
                with self.assertRaisesRegex(RG2bStageError, "invalid nested RG2b charts"):
                    RG2bGraphDomain(d.center_C, d.center_W, d.inner, d.core,
                                    d.center_C, d.h_radius, d.section_lipschitz, d.beat_dt)

    def test_reference_baseline_has_an_outward_core_rate(self):
        edges, weights, resource = self.target()
        core = next(n for n in resource if n.endswith("/core"))
        # At reference geometry, zero site derivative, kappa_M,C=0 and causal
        # feedback disabled, both candidate baselines give Cdot=eta*kappa*Lw^2 C.
        # This is a declared reduction, NOT evaluation of the frozen enabled
        # C_OS profile or any CI/PC/RG2b realization.
        for role_scale in (Q(1), Q(2, 3)):
            values = {n: role_scale * c for n, c in resource.items()}
            rate = laplacian(edges, weights, laplacian(edges, weights, values))
            self.assertEqual(rate[core], -66 * role_scale)
            self.assertEqual(sum(rate.values()), 0)
            for candidate, eta, stiffness in (("A", Q(1, 4), Q(1, 2)),
                                               ("C", Q(1, 2), Q(1))):
                with self.subTest(candidate=candidate, role_scale=role_scale):
                    self.assertLess(eta * stiffness * rate[core], 0)
                    # Exact sign proves failure for every positive duration,
                    # not just the three displayed duration controls.
                    for dt in (Q(1, 128), Q(1, 2**40), Q(1, 2**100)):
                        self.assertLess(values[core] + dt * eta * stiffness * rate[core], 0)

    def test_distinct_reference_control_has_positive_duration_continuation(self):
        edges, weights, resource = self.target()
        # Different outside data AND a different bond seed: not a repair of
        # the frozen vector. This refutes a universal no-continuation reading
        # of the bounded counterexample, not an all-profile feasibility pass.
        weights = {edge: Q(1) for edge in weights}
        resource.update({n: Q(3) for n in resource if n.startswith("outside-")})
        core = next(n for n in resource if n.endswith("/core"))
        rate = laplacian(edges, weights, laplacian(edges, weights, resource))
        self.assertEqual(rate[core], 6)
        after = {n: c + Q(1, 128) * rate[n] for n, c in resource.items()}
        self.assertTrue(all(c > 0 for c in after.values()))
        self.assertEqual(sum(after.values()), sum(resource.values()))


if __name__ == "__main__":
    unittest.main()
