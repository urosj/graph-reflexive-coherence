"""A_OS covariance transport and retained false-credit pressure."""

from copy import deepcopy
import unittest

import p984ef_aos as p


class AOSCovarianceTests(unittest.TestCase):
    def test_signed_history_and_chart_roundtrip(self):
        initial = p.o.read(p.deep.INPUTS)["initial_inputs"]
        graph = initial["reference"]["graph"]
        for checkpoint in ("e", "f"):
            for d in p.declarations(checkpoint):
                value = p.transform(initial, d)
                ni, ei, signs = p.mapping(graph, value.geometry.reference.graph.to_payload(), d)
                for role in p.ROLES:
                    state = getattr(value, role)
                    self.assertEqual(list(state.C), [initial[role]["C"][i] for i in ni])
                    self.assertEqual(list(state.W_A), [initial[role]["W_A"][i] for i in ei])
                    self.assertIsNone(state.Z_4)
                if d["kind"] == "signed":
                    self.assertTrue(any(s < 0 for s in signs))
        bad = deepcopy(p.chart.declarations()[1])
        bad["ports"]["1"] = bad["ports"]["2"]
        with self.assertRaises(ValueError):
            p.transform(initial, bad)

    def test_complete_retained_covariance_and_mutations(self):
        for checkpoint, cells in (("e", 20), ("f", 24)):
            inputs, result = p.paths(checkpoint)
            m, r = p.o.read(inputs), p.o.read(result)
            self.assertEqual(p.check(m, r)["successful_history_cells"], cells)
            for kind in ("missing", "signed_W", "phase", "acceptance"):
                bad = deepcopy(r)
                data = p.deep.storage.expand(bad["execution"])
                row = data["cases"][-1]
                if kind == "missing":
                    row["roles"].pop("reset")
                elif kind == "signed_W":
                    row["roles"]["current"]["steps"][0]["native"]["poststate"]["W_A"][0] *= -1
                elif kind == "phase":
                    row["request"]["growth_phase"] = 2
                else:
                    bad["user_accepted"] = True
                bad["execution"] = p.deep.storage.compact(data)
                with self.subTest(checkpoint=checkpoint, kind=kind), self.assertRaises((ValueError, KeyError)):
                    p.check(m, p.b.seal(bad))


if __name__ == "__main__":
    unittest.main()
