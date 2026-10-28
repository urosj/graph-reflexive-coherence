"""A_OS deep transfer, numerical-consumer and false-credit pressure."""

from copy import deepcopy
from fractions import Fraction
import unittest

import p984d_aos_oracle as p


class DeepAOSOracleTests(unittest.TestCase):
    def test_population_transfer_and_unsigned_history(self):
        m = p.make_manifest()
        self.assertEqual(len(m["cases"]), 20)
        self.assertEqual(len({x for c in m["cases"] for x in c["coverage_binding"]["cell_ids"]}), 40)
        self.assertEqual({len(c["target"]["port_graph"]["live_node_ids"]) for c in m["cases"]}, {18, 19, 20, 23})
        for c in m["cases"]:
            graph = c["target"]["port_graph"]
            for role in p.ROLES:
                before = m["shared"]["source"][role]
                after = c["target"]["roles"][role]["authoritative"]
                self.assertEqual(sum(map(Fraction, before["C"])), sum(map(Fraction, after["C"])))
                old = dict(zip((e["edge_id"] for e in m["shared"]["source"]["port_graph"]["edges"]), before["W_A"]))
                self.assertEqual(after["W_A"], [old.get(e["edge_id"], 1.0) for e in graph["edges"]])
                self.assertIsNone(after["Z_4"])
        for field in ("scope", "case", "source"):
            bad = deepcopy(m)
            if field == "scope":
                bad["scope"]["uniform_trajectory_enclosure"] = True
            elif field == "case":
                bad["cases"].pop()
            else:
                bad["shared"]["source"]["current"]["W_A"][0] += 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                p.check_manifest(p.b.seal(bad))

    def test_saved_domain_and_writer_mutations(self):
        m, r = p.read(p.INPUTS), p.read(p.RESULTS)
        case = next(c for c in m["cases"] if c["fixture_id"] == "P984D-D94-E1-P1")
        row = next(v for v in r["cases"] if v["case_id"] == case["case_id"])
        for role in p.ROLES:
            observation = next(v for v in row["expectations"] if v["role"] == role and v["index"] == 1)
            graph, entry = case["target"]["port_graph"], observation["entry"]
            p.equations.check_observation(graph, entry, observation, recheck_numerics=True)
            for field in ("W_A", "current", "H", "predictor_readback"):
                output = deepcopy(observation["output"])
                if field == "W_A":
                    output[field] = entry[field]
                elif field == "H":
                    output[field][0][0] += 1e-5
                else:
                    output[field][0] += 1e-5
                with self.subTest(role=role, field=field), self.assertRaises(ValueError):
                    p.equations.interval_certificate(graph, entry["C"], entry["W_A"], output)

    def test_retained_scope_and_schedule(self):
        m, r = p.read(p.INPUTS), p.read(p.RESULTS)
        self.assertEqual(p.check(m, r)["independent_observations"], 440)
        for kind in ("native", "missing", "role", "history"):
            bad = deepcopy(r)
            if kind == "native":
                bad["native_runtime_executed"] = True
            elif kind == "missing":
                bad["cases"].pop()
            elif kind == "role":
                bad["cases"][0]["expectations"][0]["role"] = "reset"
            else:
                bad["cases"][0]["expectations"][1]["entry"] = bad["cases"][0]["expectations"][0]["entry"]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                p.check(m, p.b.seal(bad))


if __name__ == "__main__":
    unittest.main()
