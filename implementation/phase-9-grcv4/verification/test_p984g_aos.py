"""Large A_OS exclusion, deterministic companion and scope pressure."""

from copy import deepcopy
import unittest
import p984g_aos as p


class LargeAOSOracleTests(unittest.TestCase):
    def test_companion_exact_charge_and_unchanged_history(self):
        m=p.make_manifest()
        for role in p.ROLES:
            before=m["original"]["source"]["roles"][role]
            after=m["adjusted"]["source"]["roles"][role]
            self.assertEqual(before["W_A"],after["W_A"])
            self.assertEqual(sum(map(p.q,before["C"]),p.q(0)),sum(map(p.q,after["C"]),p.q(0)))
            target=m["adjusted"]["target"]["roles"][role]
            self.assertEqual(sum(map(p.q,after["C"]),p.q(0)),sum(map(p.q,target["C"]),p.q(0)))
        self.assertGreater(m["companion"]["compensation_distance"],2)
        self.assertEqual(m["companion"]["source_deficit"],"1/1024")

    def test_preserved_exclusion_and_no_native_credit(self):
        m,r=p.storage.read(p.INPUTS),p.storage.read(p.RESULTS)
        self.assertTrue(p.check(m,r)["original_reset_excluded"])
        for kind in ("missing_role","native","readiness","negative_companion"):
            bad=deepcopy(r)
            if kind=="missing_role":bad["cases"].pop()
            elif kind=="native":bad["native_steps"]=1
            elif kind=="readiness":bad["ready_for_8_4h"]=True
            else:bad["cases"][-1]["result"]["certificate"]["minimum_resource_lower"]="-1"
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.check(m,p.b.seal(bad))


if __name__=="__main__":unittest.main()
