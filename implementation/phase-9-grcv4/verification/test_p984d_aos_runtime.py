"""Native A_OS saved-consumer pressure; no repeated deep campaign."""

from copy import deepcopy
import unittest

import p984d_aos_runtime as p


class DeepAOSRuntimeTests(unittest.TestCase):
    def test_retained_native_population_and_rollback_of_false_credit(self):
        m, r = p.oracle.read(p.INPUTS), p.oracle.read(p.RESULTS)
        status = p.check(m, r)
        self.assertEqual(status["successful_history_cells"], 40)
        for kind in ("missing", "history", "receipt", "acceptance"):
            bad = deepcopy(r)
            execution = p.storage.expand(bad["execution"])
            if kind == "missing":
                execution["cases"].pop()
            elif kind == "history":
                execution["cases"][0]["continuation"][0]["role"] = "reset"
            elif kind == "receipt":
                execution["cases"][0]["event"]["receipts"] = []
            else:
                bad["user_accepted"] = True
            bad["execution"] = p.storage.compact(p.b.seal(execution))
            with self.subTest(kind=kind), self.assertRaises((ValueError, TypeError, IndexError)):
                p.check(m, p.b.seal(bad))

    def test_largest_native_saved_equations(self):
        m, r = p.oracle.read(p.INPUTS), p.oracle.read(p.RESULTS)
        execution = p.storage.expand(r["execution"])
        declared, expected = p.oracle_data()
        i = next(i for i, c in enumerate(m["cases"]) if c["fixture_id"] == "P984D-D94-E1-P1")
        value, nominal = execution["cases"][i], expected["cases"][i]
        target = p.runtime.seed_from_payload(value["event"]["actual_target"])
        from dataclasses import replace
        for role, offset in (("current", 0), ("reset", 11)):
            before = replace(target.inputs, current=getattr(target.inputs, role), dt=p.runtime.aos.DT)
            step = next(x["step"] for x in value["continuation"] if x["role"] == role and x["index"] == 1)
            p.runtime.check_step_record(before, step, target.differential_reference,
                                        nominal["expectations"][offset]["output"], numerics=True)


if __name__ == "__main__":
    unittest.main()
