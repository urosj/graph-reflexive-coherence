"""Large A_OS saved-input and numerical-consumer mutation pressure."""

from copy import deepcopy
import unittest
import p984gh_aos_native as p


class LargeAOSNativeTests(unittest.TestCase):
    def test_source_consumption_and_scope(self):
        r=p.read("source")
        p.b.check_digest(r)
        with p.policy():
            p.check_step(r["execution"])
            for kind in ("current","history","clock","reset"):
                bad=deepcopy(r["execution"])
                if kind=="current":bad["corrector"]["current"][0]+=1e-4
                elif kind=="history":bad["writer"]["W_A"][0]+=1e-4
                elif kind=="clock":bad["after"]["step_index"]+=1
                else:bad["after"]["reset"]["C"][0]+=1e-4
                with self.subTest(kind=kind),self.assertRaises(ValueError):p.check_step(bad)


if __name__=="__main__":unittest.main()
