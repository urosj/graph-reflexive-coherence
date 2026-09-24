#!/usr/bin/env python3
"""ATC-1 research pressure; stdout only, no production ATC or accepted writes.

The dictionary protocol model below tests conditional K0 propositions, not
native lifecycle rollback. Two small numerical controls use existing owners.
Run from any directory with the repository .venv interpreter.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / "implementation/investigations/grc9v4-constitutive-design"
REFS = INV / "evidence/autonomous-topology-change"
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
PHYSICAL = ("graph", "profile", "reference", "context", "current")
BINDING = PHYSICAL + ("reset", "charge_target", "ledger", "time", "step_index")
EVIDENCE: dict = {}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def physical(publication):
    """A finite protocol model, not an adapter for GRCV4LifecycleState."""
    return canonical({key: publication[key] for key in PHYSICAL})


def token(publication):
    return sha(canonical({key: publication[key] for key in BINDING}))


def bound_publish(publication, expected, target):
    if token(publication) != expected:
        raise ValueError("stale whole-publication binding")
    return deepcopy(target)


def after(before, ordinary, target, *, admitted=True, success=True,
          duration=1.0, phase="committed"):
    """Pure two-transaction model; no numerical solver, lock or native event."""
    if not admitted or not success or duration < 0:
        return before, 0, "not_attempted"
    if duration == 0:
        return ordinary, 0, "not_eligible"
    if not math.isfinite(duration):
        raise ValueError("duration outside admitted model domain")
    if phase == "committed":
        return target, 1, phase
    if phase not in ("no_event", "unresolved", "uncertified", "construction_rejected",
                     "target_rejected", "internal_error", "interrupted"):
        raise ValueError("unknown protocol outcome")
    return ordinary, 1, phase


def publication():
    return dict(graph=["u", "v", "w"], profile="fixed-law-domain",
                reference={"weights": [1.0, 2.0], "backend": "declared"},
                context={"kind": "constant_zero"},
                current={"C": [3.0, 1.0, 2.0], "W": [2.0, 1.0], "Z": [0.0, 0.0]},
                reset={"C": [2.0, 2.0, 2.0], "W": [1.0, 1.0], "Z": [0.0, 0.0]},
                charge_target=6.0, ledger=["earlier-primary"], time=1.0,
                step_index=1, operation_id="example", telemetry={})


class CausalBoundaryPressure(unittest.TestCase):
    def test_projection_excludes_administration_but_not_physical_inputs(self):
        source = publication()
        excluded = dict(reset={"C": [1.0, 3.0, 2.0]}, charge_target=6.25,
                        ledger=["different-primary"], time=42.0, step_index=90,
                        operation_id="another", telemetry={"failed_attempts": 100},
                        duration=0.5)
        for key, value in excluded.items():
            with self.subTest(excluded=key):
                other = deepcopy(source); other[key] = value
                self.assertEqual(physical(source), physical(other))
        for key in PHYSICAL:
            with self.subTest(included=key):
                other = deepcopy(source); other[key] = {"changed": other[key]}
                self.assertNotEqual(physical(source), physical(other))
        for coordinate in ("C", "W", "Z"):
            other = deepcopy(source); other["current"][coordinate][0] += 0.125
            self.assertNotEqual(physical(source), physical(other))
        EVIDENCE["projection"] = dict(excluded_fields=sorted(excluded),
            retained_fields=list(PHYSICAL), separately_varied_state=["C", "W", "Z"],
            scope="synthetic protocol publications, not native admissibility")

    def test_full_binding_detects_same_physics_different_parent_or_reset(self):
        source = publication(); expected = token(source)
        for key, value in (("ledger", ["zero-duration-primary"]),
                           ("reset", {"C": [1.0, 3.0, 2.0]}),
                           ("charge_target", 6.25), ("time", 2.0), ("step_index", 2)):
            with self.subTest(field=key):
                live = deepcopy(source); live[key] = value
                snapshot = deepcopy(live)
                self.assertEqual(physical(source), physical(live))
                self.assertNotEqual(expected, token(live))
                with self.assertRaisesRegex(ValueError, "stale"):
                    bound_publish(live, expected, {"would_overwrite": True})
                self.assertEqual(live, snapshot)
        EVIDENCE["binding"] = dict(stale_same_physics_cases=5,
            scope="protocol freshness, not production CAS/concurrency evidence")

    def test_reset_changes_admission_without_changing_selected_action(self):
        # Independently chosen exact column-conservative map sends C to (u+v,w).
        # Both source roles have charge 6, but only one reset passes target C0<=4.
        source = publication(); other = deepcopy(source)
        source["reset"]["C"] = [1.0, 2.0, 3.0]
        other["reset"]["C"] = [3.0, 2.0, 1.0]
        mapping = ((1, 1, 0), (0, 0, 1))
        def mapped(values):
            return tuple(sum(Fraction(a)*Fraction(x) for a, x in zip(row, values))
                         for row in mapping)
        self.assertEqual(physical(source), physical(other))
        self.assertEqual(mapped(source["current"]["C"]), (4, 2))
        self.assertEqual(mapped(source["reset"]["C"]), (3, 3))
        self.assertEqual(mapped(other["reset"]["C"]), (5, 1))
        self.assertLessEqual(mapped(source["reset"]["C"])[0], 4)
        self.assertGreater(mapped(other["reset"]["C"])[0], 4)
        EVIDENCE["reset_control"] = dict(map=mapping, current_target=[4, 2],
            passing_reset_target=[3, 3], failing_reset_target=[5, 1],
            scope="exact affine countermodel; target bound is synthetic, not a GRCV4 chart")

    def test_positive_duration_need_not_advance_rounded_clock(self):
        time, duration = 1.0, 2.0**-54
        rounded = float(Fraction(time) + Fraction(duration))
        self.assertEqual(rounded, time)
        self.assertGreater(duration, 0)
        self.assertFalse(rounded > time)  # discriminates a clock-difference guard
        self.assertEqual(after("s0", "s1", "s2", duration=duration)[1], 1)
        self.assertEqual(after("s0", "s1", "s2", duration=0)[1], 0)
        EVIDENCE["clock_counterexample"] = dict(time=time.hex(),
            duration=duration.hex(), rounded_time=rounded.hex(), eligible=True)

    def test_postbeat_truth_table_and_no_joint_rollback(self):
        s0 = ("graph0", "current0", "reset0", ("old",))
        s1 = ("graph0", "current1", "reset0", ("old", "ordinary"))
        s2 = ("graph1", "current2", "reset2", ("old", "ordinary", "event"))
        cases = [({"admitted": False}, s0, 0), ({"success": False}, s0, 0),
                 ({"duration": -1}, s0, 0), ({"duration": 0}, s1, 0),
                 ({"phase": "committed"}, s2, 1)]
        cases += [({"phase": phase}, s1, 1) for phase in (
            "no_event", "unresolved", "uncertified", "construction_rejected",
            "target_rejected", "internal_error", "interrupted")]
        for arguments, expected, attempts in cases:
            with self.subTest(arguments=arguments):
                actual = after(s0, s1, s2, **arguments)
                self.assertEqual(actual[:2], (expected, attempts))
        self.assertNotEqual(after(s0, s1, s2, phase="target_rejected")[0], s0)
        EVIDENCE["transactions"] = dict(cases=len(cases),
            event_failure_retains="s1", ordinary_failure_retains="s0",
            scope="symbolic transaction model, not native rollback or lock testing")

    def test_no_memory_no_event_chain_and_no_event_count_overclaim(self):
        source = publication(); before = deepcopy(source)
        for _ in range(8):
            self.assertEqual(after(source, source, "unused", phase="unresolved"),
                             (source, 1, "unresolved"))
            self.assertEqual(source, before)
        # Finitely many positive beats can be bounded; a positive lower duration
        # does not follow from positivity. This finite geometric sum is <1.
        durations = [Fraction(1, 2**n) for n in range(1, 21)]
        self.assertTrue(all(x > 0 for x in durations))
        self.assertLess(sum(durations), 1)
        EVIDENCE["memory_and_rate"] = dict(repeated_unchanged_calls=8,
            geometric_duration_sum=str(sum(durations)), non_zeno_proved=False)

    def test_native_reference_geometry_nonedge_control(self):
        from pygrc.models.grc_v4_geometry import (
            GRCV4Graph, OrientedEdge, reference_pairings)
        graph = GRCV4Graph(("a", "b", "c"),
                          (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c")))
        h = reference_pairings(graph, vertex_measure=(1., 1., 1.),
                               reference_edge_weights=(1., 2.)).one_form.matrix
        b = ((1, 0), (-1, 1), (0, -1))  # independent incidence convention
        def entry(matrix, u, v):
            return sum(Fraction(b[u][i])*Fraction(matrix[i][j])*Fraction(b[v][j])
                       for i in range(2) for j in range(2))
        self.assertEqual(h, ((1., 0.), (0., 2.)))
        self.assertEqual(entry(h, 0, 2), 0)
        self.assertEqual(entry(((1., .25), (.25, 1.)), 0, 2), Fraction(-1, 4))
        EVIDENCE["reference_hodge"] = dict(graph_vertices=3, graph_edges=2,
            native_reference_hodge=h, nonedge_entry="0", off_diagonal_control="-1/4",
            scope="native reference-pairing constructor plus independent exact algebra; no native ATC event")

    def test_native_os_consumed_and_present_currents_are_different(self):
        from tests.models.test_grc_v4_realizations import a_os_fixture, a_scalar_pass
        from pygrc.models.grc_v4_candidate_a import CandidateACurrent
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
        from pygrc.models.grc_v4_step import ProvisionalCandidateAOSStep
        before, backend = a_os_fixture()
        saved = before.to_payload() if hasattr(before, "to_payload") else before
        expected = a_scalar_pass(before)["corrector"][1]
        self.assertEqual(expected, Fraction(-2360, 1029))
        step = ProvisionalCandidateAOSStep(before, backend)
        consumed = step.os_pass.corrector.current.values
        present_inputs = replace(step.next_inputs, dt=0)
        present = CandidateACurrent(present_inputs, backend).current.values
        self.assertAlmostEqual(consumed[0], float(expected), delta=2e-14)
        self.assertEqual(present, step.restart.current.values)
        self.assertNotEqual(consumed, present)
        variant = replace(present_inputs, operation_id="atc-metadata-control",
                          step_index=91, time=1234.,
                          reset=GRCV4AuthoritativeState((2., 2.), (1.,), None))
        self.assertEqual(CandidateACurrent(variant, backend).current.values, present)
        self.assertEqual(before.to_payload() if hasattr(before, "to_payload") else before, saved)
        EVIDENCE["native_os_stage"] = dict(fixture="a_os_fixture default unchanged",
            dt=before.dt.hex(), C_before=before.current.C, W_before=before.current.W_A,
            C_after=step.next_inputs.current.C, W_after=step.next_inputs.current.W_A,
            independent_consumed_current=str(expected), consumed_current=consumed,
            present_reference_current=present, metadata_variant_same_current=True,
            scope="existing A_OS numerical owners only; no public lifecycle commit or ATC event")

    def test_tight_os_pass_failure_is_not_a_present_read_failure(self):
        from tests.models.test_grc_v4_candidate_a import current_fixture
        from pygrc.models.grc_v4_candidate_a import CandidateACurrent
        from pygrc.models.grc_v4_realizations import CandidateAOSPass, OSStageError
        before, backend = current_fixture(dt=6.1e-5, kappa_Ah=.25, gamma=.1)
        point = CandidateACurrent(before, backend)
        self.assertTrue(all(math.isfinite(x) for x in point.current.values))
        with self.assertRaises(OSStageError) as caught:
            CandidateAOSPass(before, backend)
        self.assertEqual(caught.exception.substage, "split_residual")
        EVIDENCE["unselected_os_pass"] = dict(present_read_valid=True,
            os_pass_rejection_stage="split_residual", tolerance_repaired=False,
            scope="different read recipes have different admission obligations")

    def test_pinned_proposal_sources_and_inherited_context(self):
        row = json.loads((REFS / "ATC1CausalBoundaryProposal.json").read_text())
        declared = row.pop("record_digest")
        self.assertEqual(sha(canonical(row)), declared)
        for binding in row["source_bindings"]:
            self.assertEqual(sha((ROOT / binding["path"]).read_bytes()), binding["sha256"])
        self.assertEqual(row["status"], "proposed_not_admitted")
        self.assertFalse(row["scientific_acceptance"])
        self.assertFalse(row["executable_profile"])
        sys.path.insert(0, str(INV / "tools/exploratory-side-tool/tool/src"))
        from grcv4_explorer.a_initializer import load_current_forensic_context
        from grcv4_explorer.forensic import contract_provenance, debt_lifecycle
        context = load_current_forensic_context(ROOT, INV / "tools/exploratory-side-tool")
        intake = json.loads((REFS / "ATCSourceIntake.json").read_text())
        self.assertEqual(sha(canonical(context.nodes)), intake["forensic_context"]["current_nodes_digest"])
        self.assertEqual(sha(canonical(context.propagation_edges)),
                         intake["forensic_context"]["propagation_edges_digest"])
        self.assertFalse(any(key.split(":", 1)[-1].startswith("ATC")
                             for key in context.nodes))
        queries = intake["forensic_queries"] + row["additional_forensic_queries"]
        for query in queries:
            fn = {"contract_provenance": contract_provenance,
                  "debt_lifecycle": debt_lifecycle}[query["operation"]]
            actual = fn(context, **query["query"])
            self.assertEqual(actual["trace_digest"], query["trace_digest"])
        EVIDENCE["bindings"] = dict(source_files=len(row["source_bindings"]),
            inherited_queries_reproduced=len(queries), proposal_record_digest=declared,
            accepted_graph_unchanged=True, ATC_nodes_admitted=False)


def run():
    EVIDENCE.clear()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CausalBoundaryPressure)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    if not result.wasSuccessful():
        sys.stderr.write(stream.getvalue())
        raise SystemExit(1)
    record = dict(schema="grcv4_atc1_research_pressure_v1", status="passed",
                  tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
                  script_path=Path(__file__).resolve().relative_to(ROOT).as_posix(),
                  script_sha256=sha(Path(__file__).read_bytes()),
                  environment=dict(python=platform.python_version(), implementation=platform.python_implementation()),
                  evidence=EVIDENCE, native_ATC_executed=False, scientific_acceptance=False,
                  scope="finite protocol and exact-arithmetic pressure; existing reference geometry and bounded A_OS numerical controls; not production ATC or all-profile conformance")
    record["record_digest"] = sha(canonical(record))
    return record


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
