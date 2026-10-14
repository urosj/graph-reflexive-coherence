"""Focused retained-data pressure; no large native trajectory reruns."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import p984g_cos_native as p


class NativeAdmissionBridge(unittest.TestCase):
    def test_retained_four_cases_do_not_execute_native_steps(self):
        with patch.object(p, "execute", side_effect=AssertionError("native rerun")):
            summary = p.check()
        self.assertEqual(summary["numerical_steps"], 4)
        self.assertEqual(summary["native_events"], 0)
        self.assertEqual(summary["committed_steps"], 0)
        self.assertTrue(summary["native_admission"])
        self.assertTrue(summary["scientifically_ready_for_8_4h"])
        self.assertFalse(summary["ready_for_8_4h"])
        self.assertFalse(summary["user_accepted"])
        self.assertFalse(summary["aggregate_closed"])

    def test_resealed_scope_role_process_and_stage_mutations_fail(self):
        m = p.read(p.INPUTS)
        baseline = p.read(p.case_path("source", "current"))
        mutations = [
            lambda r: r.update(role="reset"),
            lambda r: r.update(graph="target"),
            lambda r: r.update(worker_exitcode=-15),
            lambda r: r.update(cleanup_terminated=True),
            lambda r: r.update(fallback_attempted=True),
            lambda r: r.update(native_events=1),
            lambda r: r.update(committed_steps=1),
            lambda r: r["result"].update(continuity_evaluations=2),
            lambda r: r["result"].update(after_time=1),
            lambda r: r["result"].update(initial_reset_readmitted=False),
            lambda r: r["result"]["final"].update(input_hodge_digest="0" * 64),
            lambda r: r["result"]["split_certificate"].update(weighted_row_bound="1"),
            lambda r: r["result"]["split_certificate"].update(margin_lower="0"),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                row = deepcopy(baseline)
                mutation(row)
                with self.assertRaises((ValueError, KeyError)):
                    p.check_case(p.seal(row), m)

    def test_resealed_physical_and_charge_outliers_fail(self):
        m = p.read(p.INPUTS)
        baseline = p.read(p.case_path("target", "current"))
        mutations = [
            lambda r: r["result"]["after_C"].__setitem__(0, -1e-300),
            lambda r: r["result"]["after_C"].pop(),
            lambda r: r["result"]["corrector"]["current"].__setitem__(0, 1.0),
            lambda r: r["result"]["final"]["current"].__setitem__(0, 1.0),
            lambda r: r["result"]["charge"].update(admitted_charge=201.0),
            lambda r: r["result"].update(Q_target=201.0),
            lambda r: r["result"].update(exact_resource_sum_delta="1/2"),
            lambda r: r["result"].update(charge_remainder=0),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                row = deepcopy(baseline)
                mutation(row)
                with self.assertRaises((ValueError, KeyError)):
                    p.check_case(p.seal(row), m)
        # Nonfinite JSON cannot even be sealed as a valid record.
        row = deepcopy(baseline)
        row["result"]["final"]["current"][0] = float("nan")
        with self.assertRaises(ValueError):
            p.seal(row)

    def test_manifest_and_summary_cannot_promote_or_drop_cases(self):
        m, r = p.read(p.INPUTS), p.read(p.RESULTS)
        changed = deepcopy(m)
        changed["numerical_policy"] = "legacy_exact_v1"
        with self.assertRaisesRegex(ValueError, "source drift"):
            p.check(p.seal(changed), r)
        for key, value in (
            ("user_accepted", True),
            ("ready_for_8_4h", True),
            ("native_events", 1),
            ("numerical_steps", 3),
            ("aggregate_closed", True),
        ):
            changed = deepcopy(r)
            changed[key] = value
            with self.assertRaisesRegex(ValueError, "summary drift"):
                p.check(m, p.seal(changed))

    def test_literal_continuity_uses_host_builtin_sum(self):
        subject = dict(
            graph=dict(
                live_node_ids=["s", "a", "b", "c"],
                edges=[
                    dict(
                        edge_id=str(i), tail=dict(node_id="s"), head=dict(node_id=node)
                    )
                    for i, node in enumerate(("a", "b", "c"))
                ],
            ),
            profile=dict(
                params_resolved=dict(candidate=dict(W_C_tr={"0": 1, "1": 1, "2": 1}))
            ),
            roles=dict(current=dict(C=[2.0, 2.0, 2.0, 2.0])),
        )
        # CPython 3.12 improves sum; do not impose the older naive fold result.
        # Check the actual builtin call, not a hand-written fold or fused BLAS dot.
        currents = [float(2**53), 1.0, -float(2**53)]
        expected = 2.0 - sum(currents)
        with patch("builtins.sum", wraps=sum) as native_sum:
            out = p.independent_continuity(subject, "current", currents, 1.0)
        self.assertEqual(out[0], expected)
        self.assertEqual(native_sum.call_count, 4)

    def test_corrector_cannot_be_relabelled_as_final_C_reconstruction(self):
        m = p.read(p.INPUTS)
        record = deepcopy(p.read(p.case_path('source', 'current')))
        record['result']['final']['current'] = list(record['result']['corrector']['current'])
        with self.assertRaisesRegex(ValueError, 'final-C mismatch'):
            p.check_case(p.seal(record), m)

    def test_worker_preserves_explicit_failure_not_success(self):
        from pygrc.models.grc_v4_certification import CertificationInconclusive
        from unittest.mock import Mock

        pipe = Mock()
        with patch.object(
            p, "execute", side_effect=CertificationInconclusive("bounded pressure")
        ):
            p.worker(pipe, "source", "current")
        kind, result = pipe.send.call_args.args[0]
        self.assertEqual(kind, "error")
        self.assertEqual(result["type"], "CertificationInconclusive")
        self.assertEqual(result["message"], "bounded pressure")
        pipe.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
