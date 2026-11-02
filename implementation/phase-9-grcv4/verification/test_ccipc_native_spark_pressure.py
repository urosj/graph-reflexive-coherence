"""Bounded composite root/history pressure; synthetic windows never claim an endpoint."""

import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import test_cos_native_spark_pressure as common
from ccipc_native_spark_audit import (
    Equations,
    audit_event,
    audit_root,
    audit_step,
    contains_ball,
    matrix,
    norm2,
    vector,
)
from ccipc_native_spark_oracle import CCIPCReference
from cos_native_spark_oracle import nullspace
from cpc_native_spark_pressure_oracle import decode, intervals, pack, upper
from p991a6_ccipc_preflight import seal, transition
from p991a6_ccipc_subjects import profile, request

from pygrc.models import grc_9_v4_spark_carrier_event as event_owner
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_ccipc as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import (
    _ARB_CONTEXT_LOCK,
    CertificationInconclusive,
)
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_carrier import (
    ExactCarrierState,
    exact_state,
)
from pygrc.models.grc_v4_spark_state import ExactResources, flint_operation
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_ccipc as fixtures


def with_Z(state, Z):
    return replace(state, Z_4=tuple(tuple(row) for row in pack(Z)))


def mixed(state, scale=None):
    scale = Q(1, 2**16) if scale is None else scale
    eq = Equations(state.graph.to_payload())
    Z = M(eq.I.nrows(), eq.I.ncols())
    for k, (i, j) in enumerate(eq.pairs):
        Z[i, j] = Z[j, i] = (-1 if k % 3 else 1) * scale
    return with_Z(state, Z)


def observed(model):
    """Observe scientific ownership; internal solver work is not a beat count."""
    initial = model.configuration
    publication = model._operation._spark_scope.published
    stages = []
    steps = []
    active = []
    K = native.SparkCCIPCKernel
    root, geometry, read, writer, advance, step = (
        K._root,
        K._geometry_ball,
        K._admitted_read,
        K._writer,
        ExactCarrierState.advance_carrier,
        K.step,
    )

    def frozen():
        if (
            model.configuration != initial
            or model._operation._spark_scope.published is not publication
        ):
            raise AssertionError("solver work published physical progress")

    def root_spy(k, C, Z):
        frozen()
        record = {
            "C": intervals(C),
            "Z": intervals(Z),
            "proposal_C": intervals(arb_mat([[x.mid()] for x in C.entries()])),
            "proposal_Z": intervals(
                arb_mat(
                    [
                        [Z[i, j].mid() for j in range(Z.ncols())]
                        for i in range(Z.nrows())
                    ]
                )
            ),
            "trials": 0,
        }
        active.append(record)
        try:
            result = root(k, C, Z)
            if record["last_C"] != record["C"] or record["last_Z"] != record["Z"]:
                raise AssertionError("selected root dropped whole-input uncertainty")
            return result
        finally:
            active.pop()
            stages.append(dict(stage="root_work", **record))

    def geometry_spy(k, f, Z):
        frozen()
        if active:
            record = active[-1]
            if intervals(Z) not in (record["Z"], record["proposal_Z"]):
                raise AssertionError("trial source aged incoming history")
            record["last_Z"] = intervals(Z)
            record["trials"] += 1
        return geometry(k, f, Z)

    fixed_read = K._read_ball

    def fixed_spy(k, C, H):
        frozen()
        if active:
            record = active[-1]
            if intervals(C) not in (record["C"], record["proposal_C"]):
                raise AssertionError("root iteration changed incoming resources")
            record["last_C"] = intervals(C)
        return fixed_read(k, C, H)

    def read_spy(k, state):
        frozen()
        result = read(k, state)
        stages.append(
            {
                "stage": "read",
                "input": state.to_payload(),
                "read": k.read_payload(result).to_dict(),
            }
        )
        return result

    def writer_spy(k, state, value):
        frozen()
        held = k.read_payload(value).to_dict()
        result = writer(k, state, value)
        stages.append(
            {
                "stage": "writer",
                "input": state.to_payload(),
                "held": held,
                "writer": result[1].to_dict(),
            }
        )
        return result

    def advance_spy(state, *args):
        frozen()
        value = advance(state, *args)
        stages.append(
            {
                "stage": "write",
                "input": state.to_payload(),
                "output": value.to_payload(),
            }
        )
        return value

    def step_spy(k, *args):
        result = step(k, *args)
        steps.append(result)
        return result

    with (
        patch.object(K, "_root", root_spy),
        patch.object(K, "_geometry_ball", geometry_spy),
        patch.object(K, "_read_ball", fixed_spy),
        patch.object(K, "_admitted_read", read_spy),
        patch.object(K, "_writer", writer_spy),
        patch.object(ExactCarrierState, "advance_carrier", advance_spy),
        patch.object(K, "step", step_spy),
    ):
        result = model.step()
    if not result.committed:
        raise AssertionError(result.reason)
    if (
        len(steps) != 1
        or sum(r["stage"] == "write" for r in stages) != 1
        or sum(r["stage"] == "writer" for r in stages) != 1
    ):
        raise AssertionError("one coherent physical C/Z publication")
    return steps[0], stages


class CCIPCNativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeCCIPCTests.setUpClass()
        cls.fixture = fixtures.NativeCCIPCTests()
        cls.event = cls.fixture.event_model
        cls.config = cls.event.configuration
        cls.cert = cls.fixture.certificates[0]
        cls.good = owner.kernel(cls.config).step(cls.config.current)
        cls.measurements = {}
        cls.evidence = {}

    assert_classification = common.COSNativePressureTests.assert_classification
    test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries = common.COSNativePressureTests.test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries
    test_atomic_failures_at_preparation_window_and_publication = common.COSNativePressureTests.test_atomic_failures_at_preparation_window_and_publication
    test_checkpoints_at_each_window_boundary_and_observer_noninterference = common.COSNativePressureTests.test_checkpoints_at_each_window_boundary_and_observer_noninterference
    test_inside_domain_without_event_cannot_earn_gain = (
        common.COSNativePressureTests.test_inside_domain_without_event_cannot_earn_gain
    )
    test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds = common.COSNativePressureTests.test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds

    def test_actual_source_beat_preserves_distinct_reset_history(self):
        config = self.fixture.config
        m = len(config.current.Z_4)
        for role, q in (("current", Q(1, 2**16)), ("reset", -Q(1, 2**17))):
            expected = M([[q if i == j else 0 for j in range(m)] for i in range(m)])
            self.assertEqual(matrix(getattr(config, role).Z_4), expected)
        model = GRC9V4(config)
        step, stages = observed(model)
        self.assertEqual(model.configuration.reset, config.reset)
        self.assertEqual(
            model.configuration.current, self.fixture.source_model.configuration.current
        )
        audit = audit_step(config, config.current, step)
        self.evidence["source_step"] = {
            "subject": config.to_payload(),
            "step": transition(step),
            "stages": stages,
            "role": "current",
            "audit": audit,
        }
        self.measurements["actual_source_steps"] = 1

    def test_native_step_without_research_import_or_trajectory_read(self):
        import json
        import os
        import subprocess

        code = r"""
import builtins,json,sys
original=builtins.__import__
def admitted(name,*args,**kwargs):
    if any(x in name for x in ('spark_completion_', 'oracle', 'research')) or any(x.startswith('test_') for x in name.split('.')):
        raise AssertionError('forbidden verification dependency: '+name)
    return original(name,*args,**kwargs)
builtins.__import__=admitted
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
model=GRC9V4(GRC9V4SparkConfiguration.from_payload(json.loads(sys.stdin.read())))
assert model.step().committed
assert any(x!='0' for row in model.configuration.current.Z_4 for x in row)
print('native C/Z advance without verifier imports')
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            input=json.dumps(self.config.to_payload()),
            text=True,
            capture_output=True,
            cwd=ROOT,
            env=dict(os.environ, PYTHONPATH=str(ROOT / "src")),
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_equal_C_equal_norm_trace_different_patterns_and_roles(self):
        k = owner.kernel(self.config)
        base = self.good.after
        eq = Equations(base.graph.to_payload())
        pairs = [p for p in eq.pairs if p[0] != p[1]]
        states = []
        for p in pairs[:2]:
            Z = M(eq.I.nrows(), eq.I.ncols())
            i, j = p
            Z[i, j] = Z[j, i] = Q(1, 2**16)
            states.append(with_Z(base, Z))
        a, b = states
        self.assertEqual(norm2(matrix(a.Z_4)), norm2(matrix(b.Z_4)))
        self.assertEqual(sum(matrix(a.Z_4)[i, i] for i in range(eq.I.nrows())), 0)
        sa, sb = k.step(a), k.step(b)
        self.assertNotEqual(sa.consumed_read, sb.consumed_read)
        self.assertEqual(
            classify(a, self.config.policy), classify(b, self.config.policy)
        )
        self.assertNotEqual(a.to_canonical_bytes(), b.to_canonical_bytes())
        for s in (sa, sb):
            audit_step(
                replace(self.config, current=s.before, reset=s.before), s.before, s
            )
        wrong = replace(sa, consumed_read=sb.consumed_read)
        self.detect(
            "swap_equal_C_carriers",
            "full root subject binding",
            lambda: audit_step(replace(self.config, current=a, reset=b), a, wrong),
        )
        model = GRC9V4(replace(self.config, current=a, reset=b))
        snapshot = model.snapshot()
        self.assertTrue(model.reset().committed)
        self.assertEqual(model.configuration.current, b)
        restored = GRC9V4.from_state(snapshot)
        self.assertEqual(restored.configuration.current, a)
        self.assertEqual(restored.configuration.reset, b)
        self.measurements["equal_C_roles"] = {
            "equal_C": True,
            "different_Z": True,
            "equal_norm": True,
            "equal_trace": True,
            "distinct_reads": True,
        }

    def detect(self, label, assertion, operation):
        with self.assertRaisesRegex(AssertionError, assertion):
            operation()
        self.measurements.setdefault("mutations", []).append(
            {"mutation": label, "assertion": assertion}
        )

    @flint_operation
    def test_writer_primitive_held_source_semigroup_and_cancellation(self):
        state = mixed(self.good.after)
        k = owner.kernel(self.config)
        Z = matrix(state.Z_4)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            a = (-arb(1)).exp()
            cases = [
                ("zero_source", arb_mat(M(Z.nrows(), Z.ncols()))),
                ("stationary_held", arb_mat(Z)),
                ("mixed", arb_mat(-Z / 2)),
                ("cancelling", -a / (1 - a) * arb_mat(Z)),
            ]
            bounds = []
            for name, S in cases:
                with ctx.workprec(256):
                    result, writer = k._writer(
                        state,
                        {
                            "subject_digest": sha256(
                                state.to_canonical_bytes()
                            ).hexdigest(),
                            "S": S,
                        },
                    )
                expected = a * arb_mat(Z) + (1 - a) * S
                actual = arb_mat(matrix(result))
                self.assertLessEqual(
                    max(abs(x).upper().fmpq() for x in (actual - expected).entries()),
                    Q(1, 2**193) + Q(1, 2**224),
                )
                self.assertTrue(contains_ball(writer["ideal"], expected))
                bounds.append(name)
            # Same held source in two fixed-duration primitive calls; not two full beats.
            S = arb_mat(-Z / 2)
            current = state
            for _ in range(2):
                with ctx.workprec(256):
                    result, _ = k._writer(
                        current,
                        {
                            "subject_digest": sha256(
                                current.to_canonical_bytes()
                            ).hexdigest(),
                            "S": S,
                        },
                    )
                current = replace(current, Z_4=result)
            expected = (-arb(2)).exp() * arb_mat(Z) + (1 - (-arb(2)).exp()) * S
            self.assertLessEqual(
                max(
                    abs(x).upper().fmpq()
                    for x in (arb_mat(matrix(current.Z_4)) - expected).entries()
                ),
                2 * (Q(1, 2**193) + Q(1, 2**224)),
            )
        for duration in ("0", "-1", "1/1000000000", "64"):
            with self.assertRaises(ValueError):
                k.step(state, duration)
        for tau in (1, 0, -1, 64):
            with self.assertRaises((ValueError, RuntimeError)):
                native.SparkCCIPCKernel(
                    state.graph, profile(state.graph, realization={"tau_PC": tau})
                )
        self.measurements["writer_primitive"] = {
            "cases": bounds,
            "held_source_two_beat_semigroup": True,
            "variable_duration_support": False,
        }

    def test_invalid_carrier_payloads_and_wrong_graph_binding(self):
        good = mixed(self.good.after)
        eq = Equations(good.graph.to_payload())
        payload = good.to_payload()
        i, j = next(
            (i, j)
            for i in range(eq.I.nrows())
            for j in range(i + 1, eq.I.nrows())
            if not eq.O[i, j]
        )
        changes = [
            lambda x: x.pop("Z_4"),
            lambda x: x["Z_4"].pop(),
            lambda x: x["Z_4"][0].pop(),
            lambda x: x["Z_4"][0].__setitem__(1, "1/64"),
            lambda x: x["Z_4"][i].__setitem__(j, "1/1024"),
            lambda x: x["Z_4"][0].__setitem__(0, "nan"),
            lambda x: x["Z_4"][0].__setitem__(0, "inf"),
            lambda x: x.update(Z_4=[{"i": 0, "j": 0, "value": "0"}] * eq.I.nrows()),
        ]
        for change in changes:
            bad = deepcopy(payload)
            change(bad)
            with self.assertRaises((ValueError, TypeError, KeyError)):
                exact_state(bad)
        graph = good.graph.to_payload()
        graph["edges"][0]["tail"], graph["edges"][0]["head"] = (
            graph["edges"][0]["head"],
            graph["edges"][0]["tail"],
        )
        other = GRCV4Graph.from_payload(graph)
        with self.assertRaisesRegex(ValueError, "subject"):
            owner.kernel(self.config).step(replace(good, graph=other))
        with self.assertRaises(ValueError):
            self.cert.membership(ExactResources(good.graph, good.C, good.charge))

    def test_joint_trap_boundary_all_coordinates_and_relabelled_proofs(self):
        center = self.fixture.center
        eq = Equations(center.graph.to_payload())
        r = Q(self.cert.operands["carrier_radius"])
        for i, j in eq.pairs:
            for sign in (-1, 1):
                Z = M(eq.I.nrows(), eq.I.ncols())
                Z[i, j] = Z[j, i] = sign * r * (1 if i == j else Q(1, 2))
                state = with_Z(center, Z)
                expected = norm2(Z) / r**2
                self.assertEqual(self.cert.membership(state), (True, str(expected)))
        Z = M(eq.I.nrows(), eq.I.ncols())
        Z[0, 0] = r
        self.assertEqual(self.cert.membership(with_Z(center, Z)), (True, "1"))
        Z[0, 0] = r * (1 + Q(1, 2**32))
        outside = with_Z(center, Z)
        owner.kernel(self.config).readmission(outside)
        self.assertFalse(self.cert.membership(outside)[0])
        i, j = next(p for p in eq.pairs if p[0] != p[1])
        Z = M(eq.I.nrows(), eq.I.ncols())
        Z[i, j] = Z[j, i] = 3 * r / 4
        self.assertFalse(self.cert.membership(with_Z(center, Z))[0])
        simultaneous = mixed(center, r / 16)
        self.assertEqual(
            self.cert.membership(simultaneous),
            (True, str(norm2(matrix(simultaneous.Z_4)) / r**2)),
        )
        for mutation in (
            lambda x: x["operands"]["carrier_pairs"].pop(),
            lambda x: x["operands"].pop("carrier_center"),
            lambda x: x["operands"]["binding"].update(state_channels=["C"]),
            lambda x: x["operands"].update(
                schema_version="grc9v4-native-trap-operands-v1"
            ),
            lambda x: x["operands"]["binding"]["profile"]["identity_payload"].update(
                profile_family_id="C_PC"
            ),
        ):
            data = deepcopy(self.cert.to_payload())
            mutation(data)
            with self.assertRaises((ValueError, TypeError, KeyError, RuntimeError)):
                CompletionCertificate.from_payload(data)
        from tests.models import test_grc_v4_spark_cci as ci

        ci.NativeCCITests.setUpClass()
        wrong = ci.NativeCCITests.certificates[0].to_payload()
        wrong["operands"]["binding"] = self.cert.operands["binding"].to_dict()
        with self.assertRaises((ValueError, RuntimeError)):
            CompletionCertificate.from_payload(wrong)
        self.measurements["joint_membership"] = {
            "directions": 46,
            "both_signs": True,
            "ordinary_admitted_outside_trap": True,
            "off_diagonal_factor_two": True,
        }

    def test_event_whole_actual_archive_changed_support_and_regeneration(self):
        records = []
        for chirality in (-1, 1):
            source = self.fixture.source_model.duplicate()
            before = source.configuration
            self.assertNotEqual(before.current.Z_4, self.fixture.config.current.Z_4)
            self.assertEqual(before.reset, self.fixture.config.reset)
            self.assertTrue(source.expand(request(source, chirality)).committed)
            event = source._operation._published.completion.event.to_dict()
            audit = audit_event(before, source.configuration, event)
            sg = before.reference.graph
            tg = source.configuration.reference.graph
            old = Equations(sg.to_payload())
            new = Equations(tg.to_payload())
            ids = sg.live_edge_ids
            newids = tg.live_edge_ids
            lost = [
                (i, j)
                for i, j in old.pairs
                if i != j
                and ids[i] in newids
                and ids[j] in newids
                and not new.O[newids.index(ids[i]), newids.index(ids[j])]
            ]
            self.assertTrue(lost)
            active = [(i, j) for i, j in lost if Q(before.current.Z_4[i][j])]
            self.assertTrue(
                active, "actual source history must occupy a lost support pair"
            )
            pair = tuple(
                next(
                    i
                    for i, e in enumerate(sg.oriented_edges)
                    if {e.tail_node_id, e.head_node_id} == {"v", n}
                )
                for n in ("n1", "n2")
            )
            self.assertIn(tuple(sorted(pair)), lost)
            self.assertNotEqual(Q(before.current.Z_4[pair[0]][pair[1]]), 0)
            self.assertEqual(
                new.O[newids.index(ids[pair[0]]), newids.index(ids[pair[1]])], 0
            )
            records.append(
                {
                    "source": before.to_payload(),
                    "target": source.configuration.to_payload(),
                    "event": event,
                    "audit": audit,
                    "lost_pairs": [list(x) for x in lost],
                }
            )
            formed = owner.kernel(source.configuration).step(
                source.configuration.current
            )
            self.assertTrue(any(Q(x) for row in formed.after.Z_4 for x in row))
            audit_step(source.configuration, formed.before, formed)
        self.evidence["events"] = records
        self.measurements["event_history"] = {
            "chiralities": 2,
            "source_coordinates": 58,
            "target_coordinates": 46,
            "changed_support_pairs": len(records[0]["lost_pairs"]),
            "whole_target_reset": True,
        }

    def test_archive_and_whole_target_mutations(self):
        before = self.fixture.source_model.configuration
        after = self.event.configuration
        event = self.event._operation._published.completion.event.to_dict()
        for label, role, payload in [
            ("prebeat_current", "current", self.fixture.config.current.to_payload()),
            ("role_swap", "current", before.reset.to_payload()),
            (
                "diagonal_only",
                "current",
                replace(
                    before.current,
                    Z_4=tuple(
                        tuple(x if i == j else "0" for j, x in enumerate(row))
                        for i, row in enumerate(before.current.Z_4)
                    ),
                ).to_payload(),
            ),
        ]:
            changed = deepcopy(event)
            changed["carrier_history"]["source_archive"][role] = payload
            self.detect(
                label,
                "whole actual source archive",
                lambda changed=changed: audit_event(before, after, changed),
            )
        changed = replace(after, current=mixed(after.current))
        self.detect(
            "copy_old_history_or_zero_only_new_rows",
            "whole target carrier zero",
            lambda: audit_event(before, changed, event),
        )

    def test_all_composite_transaction_faults_preserve_whole_publication(self):
        cases = [
            ("_admitted_read", 1),
            ("read_payload", 1),
            ("_writer", 1),
            ("_admitted_read", 2),
        ]
        for method, index in cases:
            model = self.fixture.synthetic_window_fixture()
            model.step()
            model.step()
            snapshot = model.snapshot()
            root = model._operation._spark_scope.published
            original = getattr(native.SparkCCIPCKernel, method)
            calls = []

            def fail(k, *args, original=original, calls=calls, index=index):
                calls.append(True)
                value = original(k, *args)
                if len(calls) == index:
                    raise CertificationInconclusive("injected PC stage")
                return value

            with patch.object(native.SparkCCIPCKernel, method, fail):
                self.assertFalse(model.step().committed)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertIs(model._operation._spark_scope.published, root)
            self.assertEqual(model.step().local_gain, 1)
        for method in ("archive", "capture"):
            model = self.fixture.source_model.duplicate()
            req = request(model)
            snapshot = model.snapshot()
            root = model._operation._spark_scope.published
            with patch.object(
                event_owner, method, side_effect=ValueError("archive preparation")
            ):
                self.assertFalse(model.expand(req).committed)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertIs(model._operation._spark_scope.published, root)
            self.assertTrue(model.expand(req).committed)
        self.measurements["PC_faults"] = {
            "read": True,
            "writer": True,
            "poststate": True,
            "archive": True,
            "complete_snapshot_and_root": True,
            "retry_once": True,
        }

    def test_observer_snapshot_aliasing_zero_duration_and_migration(self):
        state = mixed(self.good.after)
        config = replace(
            self.config, current=state, reset=with_Z(state, -matrix(state.Z_4))
        )
        a, b = GRC9V4(config), GRC9V4(config)
        for i in range(2):
            before = a.snapshot()
            Z = deepcopy(state.to_payload())
            for _ in range(3):
                with patch.object(
                    native.SparkCCIPCKernel,
                    "_writer",
                    side_effect=AssertionError("observation aged history"),
                ):
                    a.compute_observables()
                    snap = a.snapshot()
                GRC9V4.from_state(snap)
            self.assertEqual(a.snapshot(), before)
            Z["Z_4"][0][0] = "0"
            self.assertEqual(a.configuration.current, b.configuration.current)
            self.assertTrue(a.step().committed and b.step().committed)
            self.assertEqual(a.configuration, b.configuration)
        from pygrc.models.grc_v4 import GRCV4StepRequestInput

        for duration in (0, -1, 1):
            snap = a.snapshot()
            result = a.step_v4_input(
                GRCV4StepRequestInput(
                    "grcv4-step-request-input-v1",
                    "wrong-duration",
                    duration,
                    FrozenJSONMap({}),
                )
            )
            self.assertFalse(result.committed)
            self.assertEqual(a.snapshot(), snap)
        migrated = GRC9V4(config)
        self.assertTrue(migrated.migrate_spark_configuration(config).committed)
        self.assertEqual(migrated.configuration.current.Z_4, state.Z_4)
        self.assertEqual(migrated.configuration.reset.Z_4, config.reset.Z_4)

    def test_actual_stages_frozen_inputs_and_complete_joint_error(self):
        records = []
        for index, role in enumerate(("current", "reset")):
            model = self.event.duplicate()
            self.assertTrue(
                model.install_completion_certificates(
                    *self.fixture.certificates
                ).committed
            )
            if role == "reset":
                self.assertTrue(model.reset().committed)
            for beat in range(2):
                config = model.configuration
                step, stages = observed(model)
                reads = [r for r in stages if r["stage"] == "read"]
                held = next(r for r in stages if r["stage"] == "writer")
                self.assertEqual(reads[0]["input"], config.current.to_payload())
                self.assertEqual(held["held"], reads[0]["read"])
                self.assertEqual(reads[-1]["input"], step.after.to_payload())
                self.assertEqual(model.configuration.reset, config.reset)
                self.assertEqual(Q(model.configuration.time) - Q(config.time), 32)
                checked = audit_step(
                    config, config.current, step, self.fixture.certificates[index], role
                )
                records.append(
                    {
                        "subject": config.to_payload(),
                        "step": transition(step),
                        "stages": stages,
                        "role": role,
                        "beat": beat + 1,
                        "certificate": self.fixture.certificates[index].to_payload(),
                        "audit": checked,
                    }
                )
        self.evidence["actual_steps"] = records
        self.measurements["actual_target_steps"] = len(records)

    def test_uniform_signed_history_releases_without_resource_motion(self):
        state = self.fixture.config.current
        state = mixed(replace(state, C=("1",) * len(state.C), charge=str(len(state.C))))
        k = owner.kernel(self.fixture.config)
        start = matrix(state.Z_4)
        rows = []
        for n in range(1, 4):
            before = state
            step = k.step(state)
            state = step.after
            self.assertEqual(state.C, before.C)
            self.assertNotEqual(state.Z_4, before.Z_4)
            with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                eq = Equations(state.graph.to_payload())
                exact = eq.fixed(vector(before.C), eq.I + matrix(before.Z_4) / 2)
                self.assertEqual(exact["J"], M(eq.I.nrows(), 1))
                self.assertEqual(exact["S"], M(eq.I.nrows(), eq.I.nrows()))
                for key in ("H", "J", "flat", "S"):
                    self.assertTrue(
                        contains_ball(step.consumed_read[key], arb_mat(exact[key])), key
                    )
                error = arb_mat(matrix(state.Z_4)) - (-arb(n)).exp() * arb_mat(start)
                self.assertLessEqual(
                    max(abs(x).upper().fmpq() for x in error.entries()),
                    n * (Q(1, 2**193) + Q(1, 2**224)),
                )
            rows.append(
                audit_step(
                    replace(self.fixture.config, current=before, reset=before),
                    before,
                    step,
                )
            )
        self.measurements["uniform_release"] = {
            "charge": state.charge,
            "steps": 3,
            "nonzero_signed_history": True,
            "audits": rows,
        }

    def test_zero_Z_CI_read_then_history_is_consumed(self):
        from p991a6_cci_subjects import profile as ci_profile

        from pygrc.models.grc_v4_spark_cci import SparkCCIKernel

        k = owner.kernel(self.config)
        first = self.good
        ci = SparkCCIKernel(first.before.graph, ci_profile(first.before.graph)).step(
            ExactResources(first.before.graph, first.before.C, first.before.charge)
        )
        self.assertEqual(first.flux, ci.flux)
        self.assertEqual(first.after.C, ci.after.C)
        self.assertTrue(any(Q(x) for row in first.after.Z_4 for x in row))
        neutral = ExactCarrierState.zero(first.after)
        second = k.step(first.after)
        control = k.step(neutral)
        self.assertNotEqual(second.flux, control.flux)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(first.before.graph.to_payload())
            source = eq.audit_read(first.before, first.consumed_read)
            self.assertTrue(any(source["S"][i, j] < 0 for i, j in eq.pairs))
            a = eq.audit_read(first.after, second.consumed_read)
            b = eq.read(vector(neutral.C), matrix(neutral.Z_4))
            effect = max(abs(x).lower().fmpq() for x in (a["J"] - b["J"]).entries())
            self.assertGreater(effect, Q(1, 2**192))
            self.assertFalse(
                all(x.contains(0) for x in (source["H"] - arb_mat(eq.I)).entries())
            )
        self.measurements["formation_consumer"] = {
            "first_read_equals_CI": True,
            "nonzero_target_instantaneous_geometry": True,
            "next_history_effect_lower": str(effect),
        }

    def test_exact_geometry_cancellation_retains_nonzero_writer(self):
        base = self.fixture.config.current
        eq = Equations(base.graph.to_payload())
        fixed = eq.fixed(vector(base.C), eq.I)
        S = fixed["S"]
        self.assertGreater(norm2(S), 0)
        self.assertLess(norm2(S), Q(1, 128) ** 2)
        self.assertLess(max(map(abs, fixed["flat"].entries())), Q(1, 32))
        state = with_Z(base, -S)
        k = owner.kernel(self.fixture.config)
        step = k.step(state)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            for key in ("H", "J", "flat", "S"):
                self.assertTrue(
                    contains_ball(step.consumed_read[key], arb_mat(fixed[key])), key
                )
            expected = (1 - 2 * (-arb(1)).exp()) * arb_mat(S)
            error = arb_mat(matrix(step.after.Z_4)) - expected
            self.assertLessEqual(
                max(abs(x).upper().fmpq() for x in error.entries()),
                Q(1, 2**193) + Q(1, 2**224),
            )
            self.assertTrue(any(Q(x) for row in step.after.Z_4 for x in row))
            checked = audit_step(
                replace(self.fixture.config, current=state), state, step
            )
            for label, wrong in (
                ("net_increment_zero", M(S.nrows(), S.ncols())),
                ("effective_H_minus_I_zero", M(S.nrows(), S.ncols())),
            ):
                writer = step.writer.to_dict()
                writer["source"] = intervals(arb_mat(wrong))
                self.detect(
                    label,
                    "same incoming held source",
                    lambda writer=writer: audit_step(
                        replace(self.fixture.config, current=state),
                        state,
                        replace(step, writer=FrozenJSONMap(writer)),
                    ),
                )
        self.evidence["cancellation"] = {
            "subject": state.to_payload(),
            "reference_flat": pack(fixed["flat"]),
            "source": pack(S),
            "step": transition(step),
            "audit": checked,
        }
        self.measurements["geometry_cancellation"] = {
            "exact_rational_fixture": True,
            "carrier": -1,
            "geometry": "I",
            "writer_coefficient": "1-2*exp(-1)",
            "nonzero_writer": True,
        }

    def test_same_source_two_uses_and_gain_placement(self):
        state = mixed(self.good.after)
        config = replace(self.config, current=state)
        k = owner.kernel(config)
        step = k.step(state)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(state.graph.to_payload())
            old = eq.audit_read(state, step.consumed_read)
            Z = arb_mat(matrix(state.Z_4))
            S = old["S"]
            self.assertFalse(
                all(
                    x.contains(0) for x in (old["H"] * eq.L - eq.L * old["H"]).entries()
                )
            )
            for label, source in (
                ("write_Z_plus_S", Z + S),
                ("write_H_minus_I", old["H"] - arb_mat(eq.I)),
                ("reapply_chi", S / 2),
                ("reapply_zeta", S / 2),
                ("average_channels", S / 2),
                (
                    "poststate_source",
                    eq.read(vector(step.after.C), matrix(step.after.Z_4))["S"],
                ),
            ):
                writer = step.writer.to_dict()
                writer["source"] = intervals(source)
                self.detect(
                    label,
                    "same incoming held source",
                    lambda writer=writer: audit_step(
                        config, state, replace(step, writer=FrozenJSONMap(writer))
                    ),
                )
            report = audit_step(config, state, step)
            # Algebraic source/composition control; no nonzero physical equilibrium claim.
            f = M([[Q((-1) ** i, 1024)] for i in range(eq.I.nrows())])
            source = eq.fixed(vector(state.C), eq.I)["S"]
            source = M(
                [
                    [eq.O[i, j] * f[i, 0] * f[j, 0] / 4 for j in range(f.nrows())]
                    for i in range(f.nrows())
                ]
            )
            H = eq.I + (source + source) / 2
            self.assertEqual(H, eq.I + source)
            self.assertNotEqual(H, eq.I + source / 2)
            synthetic = with_Z(state, source)
            with ctx.workprec(256):
                from pygrc.models.grc_v4_spark_state import flint_operation

                Z1, _ = flint_operation(k._writer)(
                    synthetic,
                    {
                        "subject_digest": sha256(
                            synthetic.to_canonical_bytes()
                        ).hexdigest(),
                        "S": arb_mat(source),
                    },
                )
            self.assertEqual(matrix(Z1), source)
        self.measurements["same_source"] = {
            "cross_identity": report["geometry_writer_cross_identity"],
            "stationary_composition_gain": 2,
            "synthetic_writer_only": True,
        }

    def test_rehashed_tuple_proposal_domain_and_noncommuting_mutations(self):
        state = mixed(self.good.after)
        config = replace(self.config, current=state)
        step = owner.kernel(config).step(state)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(state.graph.to_payload())
            true = eq.audit_read(state, step.consumed_read)
            C = arb_mat(vector(state.C))
            H = true["H"]
            fixed = eq.fixed_ball(C, H)
            j0 = fixed["j0"]
            cycle = nullspace(eq.B)[0]
            no_H_site = (
                -arb_mat(eq.B).transpose()
                * (
                    arb_mat(eq.B) * arb_mat(eq.B).transpose() * C / 64
                    - arb_mat([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
                )
                / 1024
            )
            bads = [
                (
                    "CI_ignores_history",
                    "H",
                    eq.read(vector(state.C), M(H.nrows(), H.ncols()))["H"],
                    "fresh selected-root containment: H",
                ),
                (
                    "PC_omits_instantaneous",
                    "H",
                    arb_mat(eq.I) + arb_mat(matrix(state.Z_4)) / 2,
                    "fresh selected-root containment: H",
                ),
                (
                    "reverse_HL_to_LH",
                    "J",
                    j0 + (3 * arb_mat(eq.I) / 4 + arb_mat(eq.L) * H).solve(j0) / 4,
                    "fresh selected-root containment: J",
                ),
                (
                    "omit_H_from_potential",
                    "J",
                    no_H_site
                    + (3 * arb_mat(eq.I) / 4 + H * arb_mat(eq.L)).solve(no_H_site) / 4,
                    "fresh selected-root containment: J",
                ),
                (
                    "omit_H_inverse_flat",
                    "flat",
                    fixed["y"] / 2,
                    "proposal enclosure identity",
                ),
                (
                    "cycle_current_same_continuity",
                    "J",
                    true["J"] + arb_mat(cycle) / 2**20,
                    "fresh selected-root containment: J",
                ),
                (
                    "negate_flat_preserve_quadratic_source",
                    "flat",
                    -true["flat"],
                    "proposal enclosure identity",
                ),
                (
                    "corrupt_last_source_coordinate",
                    "S",
                    true["S"]
                    + arb_mat(
                        [
                            [
                                Q(1, 2**20) if i == j == H.nrows() - 1 else 0
                                for j in range(H.ncols())
                            ]
                            for i in range(H.nrows())
                        ]
                    ),
                    "fresh selected-root containment: S",
                ),
            ]
            for label, key, A, assertion in bads:
                data = step.consumed_read.to_dict()
                data[key] = intervals(A)
                wrapped = seal({"payload": data})
                self.assertEqual(wrapped, seal(wrapped))
                self.detect(label, assertion, lambda data=data: audit_root(state, data))
            for label, mutate, assertion in [
                (
                    "radius_widened_to_PC",
                    lambda p: p["root_domain"].update(carrier_radius="1/64"),
                    "complete composite domain binding",
                ),
                (
                    "CI_contraction_borrowed",
                    lambda p: p["root_domain"].update(carrier_hodge_deviation="0"),
                    "complete composite domain binding",
                ),
                (
                    "wrong_proposal",
                    lambda p: p["proposal"][0].__setitem__(0, ["0", "0"]),
                    "independent proposal residual",
                ),
                (
                    "zero_residual",
                    lambda p: p.update(proposal_residual=["0", "0"]),
                    "independent proposal residual",
                ),
                (
                    "zero_root_error",
                    lambda p: p.update(root_error=["0", "0"]),
                    "residual-to-root error bound",
                ),
                (
                    "midpoint_outside_enclosure",
                    lambda p: p["current_midpoint"].__setitem__(0, "0"),
                    "whole current midpoint budget",
                ),
            ]:
                data = step.consumed_read.to_dict()
                mutate(data)
                data = seal({"payload": data})["payload"]
                self.detect(label, assertion, lambda data=data: audit_root(state, data))
            source_domain = owner.kernel(self.fixture.config).domain.to_dict()
            data = step.consumed_read.to_dict()
            data["root_domain"] = source_domain
            self.detect(
                "wrong_graph_domain",
                "complete composite domain binding",
                lambda: audit_root(state, data),
            )
            for label, other in (
                ("old_root", state),
                ("new_C_old_Z", replace(state, C=step.after.C)),
                ("old_C_new_Z", replace(state, Z_4=step.after.Z_4)),
            ):
                data = owner.kernel(config).readmission(other).to_dict()
                data["subject_digest"] = step.restart_read["subject_digest"]
                self.detect(
                    label,
                    "independent proposal residual",
                    lambda data=data: audit_root(step.after, data),
                )

    def test_actual_C_and_Z_input_uncertainty_in_root_certificate(self):
        state = mixed(self.good.after)
        k = owner.kernel(self.config)
        eq = Equations(state.graph.to_payload())
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            C = arb_mat(vector(state.C))
            Z = arb_mat(matrix(state.Z_4))
            eps = Q(1, 2**48)
            C[0, 0] = arb(Q(state.C[0]), eps)
            Z[0, 0] = arb(Q(state.Z_4[0][0]), eps)
            with ctx.workprec(256):
                root = k.read_ball(C, Z)
            p = arb_mat([[x.mid().fmpq()] for x in root["proposal"].entries()])
            # Independent solve/inverse interval extensions need not order their
            # upper bounds. Cover the entire input box with smaller boxes, then
            # certify this independent sup bound against the native certificate.
            residuals = []
            for ci in range(4):
                for zi in range(4):
                    cbox = arb_mat(vector(state.C))
                    zbox = arb_mat(matrix(state.Z_4))
                    cbox[0, 0] = arb(
                        Q(state.C[0]) + eps * (Q(2 * ci + 1, 4) - 1), eps / 4
                    )
                    zbox[0, 0] = arb(
                        Q(state.Z_4[0][0]) + eps * (Q(2 * zi + 1, 4) - 1), eps / 4
                    )
                    read = eq.fixed_ball(
                        cbox, arb_mat(eq.I) + (zbox + eq.source(p)) / 2
                    )
                    residuals.append(upper(read["flat"] - p))
            residual = max(residuals)
            error = root["error"].upper().fmpq()
            self.assertGreaterEqual(root["proposal_residual"].upper().fmpq(), residual)
            self.assertGreaterEqual(error, residual / (1 - Q(k.domain["contraction"])))
            for cs in (-1, 1):
                for zs in (-1, 1):
                    pointC = arb_mat(vector(state.C))
                    pointZ = arb_mat(matrix(state.Z_4))
                    pointC[0, 0] += cs * eps
                    pointZ[0, 0] += zs * eps
                    fresh = eq.read(pointC, pointZ)
                    self.assertTrue(
                        contains_ball(intervals(root["flat"]), fresh["flat"])
                    )
            narrow = k.readmission(state)
            self.assertGreater(error, Q(narrow["root_error"][1]))
        self.measurements["uncertain_inputs"] = {
            "C_and_Z": True,
            "corners": 4,
            "whole_box_cover": 16,
            "root_error": str(error),
            "whole_box_residual": str(residual),
        }

    def test_solver_work_variants_failures_and_workspace_isolation(self):
        K = native.SparkCCIPCKernel
        k = owner.kernel(self.config)
        state = mixed(self.good.after)
        ordinary = k.step(state)
        # Different successful proposal tolerances change work, not physical duration.
        with patch.object(native, "PROPOSAL_BITS", 232):
            tighter = k.step(state)
        self.assertEqual(ordinary.after, tighter.after)
        self.assertEqual(ordinary.duration, tighter.duration)
        audit_step(replace(self.config, current=state), state, tighter)
        calls = []
        model = GRC9V4(replace(self.config, current=state))
        snapshot = model.snapshot()
        original = K._geometry_ball

        def fail_after_trials(k, f, Z):
            calls.append(True)
            if len(calls) == 4:
                raise CertificationInconclusive("trial source failure")
            return original(k, f, Z)

        with patch.object(K, "_geometry_ball", fail_after_trials):
            self.assertFalse(model.step().committed)
        self.assertEqual(model.snapshot(), snapshot)
        self.assertTrue(model.step().committed)
        self.assertEqual(model.configuration.current, ordinary.after)
        one = profile(
            state.graph,
            realization={"iteration_limit": 1},
            solver={"iteration_limit": 1},
        )
        limited = K(state.graph, one)
        with self.assertRaisesRegex(CertificationInconclusive, "limit reached"):
            limited.step(state)
        # Inject only proposal work. The actual residual evaluation and every
        # physical numerical admission remain intact in both controls.
        read = K._read_ball
        warm_proposal = decode(ordinary.consumed_read["proposal"])
        proposal_calls = []

        def seed(k, C, H):
            result = read(k, C, H)
            proposal_calls.append(True)
            if len(proposal_calls) == 1:
                result["F"] = warm_proposal
            return result

        with patch.object(K, "_read_ball", seed):
            warm = k.step(state)
        self.assertEqual(warm.after, ordinary.after)
        audit_step(replace(self.config, current=state), state, warm)
        stalled = []

        def stagnate(k, C, H):
            result = read(k, C, H)
            stalled.append(True)
            if len(stalled) == 1:
                result["F"] = arb_mat(H.nrows(), 1)
            return result

        with (
            patch.object(K, "_read_ball", stagnate),
            self.assertRaises(CertificationInconclusive),
        ):
            k.step(state)
        original_bytes = state.to_canonical_bytes()
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            r = k._admitted_read(state)
            r["S"][0, 0] = 999
            r["H"][0, 0] = -99
        self.assertEqual(state.to_canonical_bytes(), original_bytes)
        self.assertEqual(k.step(state).after, ordinary.after)
        self.measurements["solver_work"] = {
            "ordinary_iterations": ordinary.consumed_read["iterations"],
            "tighter_iterations": tighter.consumed_read["iterations"],
            "warm_iterations": warm.consumed_read["iterations"],
            "same_represented_state": True,
            "failed_trials": len(calls),
            "no_trial_history": True,
        }

    def test_composite_norm_boundary_and_offdiagonal_factor(self):
        state = self.good.after
        eq = Equations(state.graph.to_payload())
        k = owner.kernel(self.config)
        R = Q(1, 128)
        for q in (R, -R, R * (1 - Q(1, 2**32))):
            Z = M(eq.I.nrows(), eq.I.ncols())
            Z[0, 0] = q
            k.readmission(with_Z(state, Z))
        Z[0, 0] = R * (1 + Q(1, 2**32))
        with self.assertRaisesRegex(RuntimeError, "carrier ball"):
            k.readmission(with_Z(state, Z))
        i, j = next(p for p in eq.pairs if p[0] != p[1])
        Z = M(eq.I.nrows(), eq.I.ncols())
        Z[i, j] = Z[j, i] = 3 * R / 4
        self.assertLess((3 * R / 4) ** 2, R**2)
        self.assertGreater(norm2(Z), R**2)
        with self.assertRaisesRegex(RuntimeError, "carrier ball"):
            k.readmission(with_Z(state, Z))
        self.measurements["packed_norm"] = {
            "radius": str(R),
            "offdiagonal_factor_two": True,
            "no_projection": True,
        }

    def test_signed_edge_permutation_covariance_and_untransported_binding(self):
        state = mixed(self.good.after)
        graph = state.graph.to_payload()
        m = len(graph["edges"])
        perm = list(reversed(range(m)))
        sign = [-1 if i % 3 == 0 else 1 for i in range(m)]
        graph["edges"] = [deepcopy(graph["edges"][i]) for i in perm]
        for i, e in enumerate(graph["edges"]):
            if sign[i] < 0:
                e["tail"], e["head"] = e["head"], e["tail"]
        target = GRCV4Graph.from_payload(graph)
        Qm = M([[sign[i] if j == perm[i] else 0 for j in range(m)] for i in range(m)])
        transformed = replace(
            state, graph=target, Z_4=pack(Qm * matrix(state.Z_4) * Qm.transpose())
        )
        first = owner.kernel(self.config).step(state)
        second = native.SparkCCIPCKernel(target, profile(target)).step(transformed)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            a = Equations(state.graph.to_payload()).audit_read(
                state, first.consumed_read
            )
            Equations(target.to_payload()).audit_read(transformed, second.consumed_read)
            for key in ("J", "flat"):
                self.assertTrue(
                    contains_ball(second.consumed_read[key], arb_mat(Qm) * a[key])
                )
            for key in ("H", "S"):
                self.assertTrue(
                    contains_ball(
                        second.consumed_read[key],
                        arb_mat(Qm) * a[key] * arb_mat(Qm.transpose()),
                    )
                )
        self.assertEqual(first.after.C, second.after.C)
        self.assertEqual(
            matrix(second.after.Z_4), Qm * matrix(first.after.Z_4) * Qm.transpose()
        )
        with self.assertRaises(ValueError):
            owner.kernel(self.config).step(transformed)
        self.measurements["covariance"] = {
            "permutation": perm,
            "signs": sign,
            "offdiagonal_history": True,
            "exact_represented_transport": True,
        }

    def test_semantic_reset_target_and_poststate_failures(self):
        K = native.SparkCCIPCKernel
        for phase in ("source_reset", "target_current", "target_reset"):
            model = self.fixture.source_model.duplicate()
            before = model.configuration
            snapshot = model.snapshot()
            req = request(model)
            original = K.readmission

            def fail(k, state, phase=phase, before=before, original=original):
                source = state.graph == before.reference.graph
                reset = source and state == before.reset
                # Target current/reset are identified by their independently
                # allocated C vectors, not by ordinal calls.
                if phase == "source_reset" and source and reset:
                    raise CertificationInconclusive("source reset")
                if (
                    phase == "target_current"
                    and not source
                    and state.C == self.config.current.C
                ):
                    raise CertificationInconclusive("target root")
                if (
                    phase == "target_reset"
                    and not source
                    and state.C == self.config.reset.C
                ):
                    raise CertificationInconclusive("target reset")
                return original(k, state)

            with patch.object(K, "readmission", fail):
                self.assertFalse(model.expand(req).committed, phase)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertTrue(model.expand(req).committed)
        for key in ("J", "S"):
            model = self.event.duplicate()
            snapshot = model.snapshot()
            original = K.read_ball

            def broken(k, *args, key=key, original=original):
                r = original(k, *args)
                r[key][r[key].nrows() - 1, r[key].ncols() - 1] = arb("nan")
                return r

            with patch.object(K, "read_ball", broken):
                self.assertFalse(model.step().committed)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertTrue(model.step().committed)
        self.measurements["semantic_faults"] = [
            "source_reset",
            "target_current",
            "target_reset",
            "nonfinite_current",
            "nonfinite_source",
        ]

    def test_mixed_derivatives_and_rehashed_borrowed_certificates(self):
        # The original preflight already checks all 60 individual directions;
        # exercise simultaneous resource and signed history perturbations here.
        k = owner.kernel(self.config)
        state = mixed(self.good.after, Q(1, 2**24))
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            C = arb_mat(vector(state.C))
            Z = arb_mat(matrix(state.Z_4))
            ref = CCIPCReference(state.graph.to_payload())
            eps = Q(1, 2**36)
            chart = matrix(self.cert.operands["S"])
            dC = arb_mat(chart * vector([str((-1) ** i) for i in range(14)]))
            dZ = arb_mat(matrix(mixed(state, Q(1, 1024)).Z_4))
            box = lambda A, D: arb_mat(
                [
                    [
                        arb(A[i, j].mid().fmpq(), (eps * abs(D[i, j])).upper().fmpq())
                        for j in range(A.ncols())
                    ]
                    for i in range(A.nrows())
                ]
            )
            with ctx.workprec(256):
                p = k.partials(box(C, dC), box(Z, dZ))
            a = ref.pc_step(C - eps * dC, Z - eps * dZ)
            b = ref.pc_step(C + eps * dC, Z + eps * dZ)
            packed = arb_mat(
                [[(1 if i == j else arb(2).sqrt()) * dZ[i, j]] for i, j in ref.pairs]
            )
            predictedC = p["CC"] * dC + p["CZ"] * packed
            predictedZ = (1 - ref.decay) * (
                p["SC"] * dC + p["SZ"] * packed
            ) + ref.decay * packed
            for actual, expected in (
                (predictedC, (b["after"] - a["after"]) / (2 * eps)),
                (
                    predictedZ,
                    arb_mat(
                        [
                            [
                                (1 if i == j else arb(2).sqrt())
                                * (b["carrier_after"][i, j] - a["carrier_after"][i, j])
                                / (2 * eps)
                            ]
                            for i, j in ref.pairs
                        ]
                    ),
                ),
            ):
                self.assertTrue(contains_ball(intervals(actual), expected))
        from tests.models import test_grc_v4_spark_cpc as pc

        pc.NativeCPCTests.setUpClass()
        wrong = deepcopy(self.cert.to_payload())
        wrong["proof"] = pc.NativeCPCTests.certificates[0].proof.to_dict()
        wrong["proof"]["operands_digest"] = self.cert.proof["operands_digest"]
        with self.assertRaisesRegex(ValueError, "recomputed mathematics"):
            CompletionCertificate.from_payload(wrong)
        self.measurements["mixed_derivative"] = {
            "all_60_coordinates": True,
            "nonstationary": True,
            "borrowed_PC_proof_rejected": True,
            "root_decay_and_full_map_bounds_distinct": True,
        }
