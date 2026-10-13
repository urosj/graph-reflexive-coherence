"""Independent full-formula pressure on the D94 simplex exclusion."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import p984d_apc_feasibility as f


def overlap(left,right):
    return f.endpoint(left,0)<=f.endpoint(right,1) and f.endpoint(right,0)<=f.endpoint(left,1)


def literal(ctx,x,y):
    """Full interval matrix equations without the affine/correction decomposition."""
    high=ctx["high"];dt=f.number(f.Q(f.b.DT))
    c=f.affine(ctx["initial"],f.number(x),f.number(y))
    w=f.IV.matrix([f.number(v) for v in ctx["w"]])
    first=high.read("A",c,w,high.I)
    c1=c-dt*high.B*first["J"]
    if min(f.endpoint(v,0) for v in c1)<0:
        return c1,None
    w1=high.write(c1,w,first["J"])
    z1=(1-f.IV.exp(-dt))*first["source"]
    second=high.read("A",c1,w1,high.I+f.number(f.Q(f.o.KAPPA_H))*z1)
    return c1,c1-dt*high.B*second["J"]


class AllocationFeasibilityTests(unittest.TestCase):
    def test_literal_equations_and_nontrivial_w_writer(self):
        m=f.b.read(f.prior.INPUTS);ctx=f.context(m)
        for x,y in ((f.Q(1,3),f.Q(1,3)),(f.Q(21,64),f.Q(21,64)),(f.Q(0),f.Q(0)),(f.Q(1),f.Q(0))):
            with self.subTest(x=x,y=y):
                first,second=literal(ctx,x,y)
                result=f.enclose(ctx,(x,x,y,y))
                a=f.affine(ctx["first"],f.number(x),f.number(y))+result["first_error"]
                self.assertTrue(all(overlap(v,w) for v,w in zip(first,a)))
                if second is not None:
                    z=f.affine(ctx["second"],f.number(x),f.number(y))+result["second_error"]
                    self.assertTrue(all(overlap(v,w) for v,w in zip(second,z)))
        x=y=f.Q(21,64)
        _,truth=literal(ctx,x,y)
        with patch.object(ctx["high"],"write",side_effect=lambda c,w,j:w):
            wrong=f.enclose(ctx,(x,x,y,y))
        wrong=f.affine(ctx["second"],f.number(x),f.number(y))+wrong["second_error"]
        self.assertTrue(any(not overlap(a,z) for a,z in zip(truth,wrong)),"frozen-W alternative must be distinguished")

    def test_simplex_boundary_and_history_scope(self):
        m=f.b.read(f.prior.INPUTS)
        current=f.context(m)
        for represented in (False,True):
            result=f.inspect_box(current,represented=represented)
            f.check_certificate(current,result)
            self.assertLess(f.Q(result["terminal_resource_upper"]),-f.Q(1,100_000_000))
        # Do not promote a current-history obstruction into a reset/all-source one.
        reset=f.context(m,role="reset")
        self.assertFalse(f.inspect_box(reset)["excluded"])
        for box in ((-1,1,0,1),(0,2,0,1),(1,1,1,1)):
            with self.assertRaises(ValueError):f.enclose(current,box)
        with self.assertRaises(ValueError):f.enclose(current,represented=1)
        with patch.dict(f.r.LIMITS,{"resource_error":f.Q(1,100)}):
            self.assertFalse(f.inspect_box(current,represented=True)["excluded"],"large uncertainty cannot retain exclusion")

    def test_writer_reference_is_not_clipped_to_represented_resources(self):
        ctx=f.context(f.b.read(f.prior.INPUTS));h=ctx["high"]
        tiny=-f.Q(1,2**41)
        c=f.IV.matrix([f.number(tiny) for _ in ctx["initial"]])
        w=f.IV.matrix([f.number(1) for _ in ctx["w"]]);j=f.IV.matrix(len(w),1)
        out=f.writer_extension(h,c,w,j,f.number(f.Q(f.b.DT)))
        # Exact writer reference at this numerical-boundary enclosure exceeds
        # one; clipping C to zero would falsely erase that effect.
        self.assertTrue(all(f.endpoint(v,0)>1 for v in out))

    def test_retained_certificates_and_rehashed_mutations(self):
        value=f.b.read(f.RESULTS)
        with patch.object(f.r,"CandidatePCRead",side_effect=AssertionError("native read")), \
                patch.object(f.r,"ProvisionalCandidatePCStep",side_effect=AssertionError("native step")), \
                patch.object(f.r.native,"GRC9V4APCOperation",side_effect=AssertionError("native event")):
            summary=f.check(value,numerics=True)
        self.assertEqual(summary["D94_cases"],6)
        self.assertEqual(summary["runtime_cells_closed"],0)
        for kind in ("source", "domain", "cases", "role", "coefficient", "polygon", "margin", "scope"):
            wrong=deepcopy(value)
            cert=wrong["cases"][0]["represented"]
            if kind=="source":wrong["source_bindings"].pop()
            elif kind=="domain":wrong["domain"]["max_updates"]=10
            elif kind=="cases":wrong["cases"].pop()
            elif kind=="role":wrong["cases"][0]["role"]="reset"
            elif kind=="coefficient":cert["constraints"][0]["affine"][0]="1"
            elif kind=="polygon":cert["first_step_polygon"][0][0]="0"
            elif kind=="margin":cert["terminal_resource_upper"]="0"
            else:wrong["all_sources_infeasible"]=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):f.check(f.b.seal(wrong))
        wrong=deepcopy(value)
        # A slightly widened lower endpoint preserves the halfplane proof, but
        # numerical rechecking must still detect alteration of the enclosure.
        bound=wrong["cases"][0]["exact"]["constraints"][0]["correction"]
        bound[0]=str(f.Q(bound[0])-f.Q(1,10**30))
        with self.assertRaisesRegex(ValueError,"enclosure drift"):
            f.check(f.b.seal(wrong),numerics=True)


if __name__=="__main__":
    unittest.main()
