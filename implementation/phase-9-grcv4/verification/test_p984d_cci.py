"""Focused deep C_CI pressure; retained tests do not rerun native campaigns."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import p984d_cci as d

r, b = d.r, d.b


class DeepCCITests(unittest.TestCase):
    def test_tree23_proof_boundary_and_rejected_recipes(self):
        manifest = d.make_manifest()
        case = next(c for c in manifest['cases'] if c['request']['target_effective_degree'] == 94)
        target = d.previous.preparation.target_for(manifest, case)
        model = r.independent_model(target)
        self.assertEqual(len(model.nodes), 23)
        self.assertGreater(d.certificate.graph_bound(model), 0)
        for kind in ('oversize', 'duplicate', 'disconnected'):
            bad = deepcopy(model)
            if kind == 'oversize': bad.nodes = (*bad.nodes, 'extra')
            elif kind == 'duplicate': bad.nodes = (*bad.nodes[:-1], bad.nodes[0])
            else:
                bad.edges = list(bad.edges)
                bad.edges[-1] = deepcopy(bad.edges[0]); bad.edges[-1]['edge_id'] = 'distinct'
            with self.subTest(kind=kind), self.assertRaises(ValueError): d.certificate.graph_bound(bad)
        for shares in ([0.25, 0.5, 0.25], [22/64, 21/64, 21/64]):
            changed = deepcopy(case); changed['request']['resource_distribution'] = shares
            target = b.independent_target(manifest, changed)
            with self.subTest(shares=shares), self.assertRaisesRegex(ValueError, 'negative/nonfinite'):
                r.preflight(target)

    def test_ci_only_interval_lift_and_geometry_enclosure_pressure(self):
        c = d.certificate
        old, _ = d.predecessor()
        source = b.GeometryStageInputs.from_payload(old['expected_source']['inputs'])
        high = c.n.IntervalRows(r.independent_model(source))
        resources = c.n.vector(source.current.C)
        _, legacy = c.e.read_bounds(high, 'C', resources, None)
        lifted = c.read_bounds(high, resources)
        self.assertEqual(lifted, {k:legacy[k] for k in ('contraction', 'regularity')})
        m = d.make_manifest()
        case = next(v for v in m['cases'] if v['request']['target_effective_degree'] == 94)
        target = d.previous.preparation.target_for(m, case)
        high = c.n.IntervalRows(r.independent_model(target))
        resources = c.n.vector(target.current.C)
        budget = c.read_bounds(high, resources)
        self.assertLess(budget['contraction'], 1)
        self.assertGreater(budget['regularity'], 0)
        with patch.object(c.e, 'geometry_box', side_effect=lambda model, radius:model.I.copy()):
            with self.assertRaisesRegex(AssertionError, 'geometry ball not covered'):
                c.read_bounds(high, resources)
        original = c.e.assert_current_frobenius_aggregation
        with patch.object(c.e, 'assert_current_frobenius_aggregation', side_effect=lambda source,squared:original(source,0)):
            with self.assertRaisesRegex(AssertionError, 'complete interval-entry'):
                c.read_bounds(high, resources)

    def test_population_target_and_scientific_freeze(self):
        manifest = d.make_manifest()
        self.assertEqual(len(manifest["cases"]), 20)
        self.assertEqual(len({s for c in manifest["cases"] for s in c["coverage_binding"]["cell_ids"]}), 40)
        old, _ = d.predecessor()
        for case in manifest["cases"]:
            target = d.previous.preparation.target_for(manifest, case)
            self.assertEqual(target.geometry.reference.profile.identity_payload.profile_family_id, "C_CI")
            self.assertEqual(case["comparison"], old["cases"][0]["comparison"])
            self.assertEqual(case["schedule"], old["cases"][0]["schedule"])
        for kind in ("roster", "shares", "budget", "source"):
            changed = deepcopy(manifest)
            if kind == "roster": changed["cases"].pop()
            elif kind == "shares": changed["cases"][0]["request"]["resource_distribution"] = [0.5, 0.5]
            elif kind == "budget": changed["cases"][0]["execution_budget_seconds"] += 1
            else: changed["expected_source"]["inputs"]["current"]["C"][0] += 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                d.check_manifest(b.seal(changed))

    def test_retained_roster_scope_and_compaction(self):
        manifest, record = b.read(d.INPUTS), b.read(d.RESULTS)
        execution = d.previous.expand(record["execution"])
        self.assertEqual(d.previous.expand(d.previous.compact(execution)), execution)
        for kind in ("roster", "scope", "event_vs_case", "schedule", "shared"):
            changed, raw = deepcopy(record), deepcopy(execution)
            if kind == "roster": raw["cases"].pop()
            elif kind == "scope": raw["cases"][0]["user_accepted"] = True
            elif kind == "event_vs_case": raw["cases"][0]["case_passed"] = False
            elif kind == "schedule": raw["cases"][0]["continuation"].pop()
            else: raw["shared"]["actual_source"]["inputs"]["current"]["C"][0] += 1
            changed["execution"] = d.previous.compact(b.seal(raw))
            with self.subTest(kind=kind), self.assertRaises(ValueError): d.status(manifest, b.seal(changed))
        changed = deepcopy(record["execution"])
        changed["contexts"][next(iter(changed["contexts"]))] = []
        with self.assertRaisesRegex(ValueError, "context digest"): d.previous.expand(changed)

    def test_deepest_joint_root_and_event_pressure(self):
        manifest, record = b.read(d.INPUTS), b.read(d.RESULTS)
        execution = d.previous.expand(record["execution"])
        i = next(i for i,c in enumerate(manifest["cases"]) if c["request"]["target_effective_degree"] == 94)
        case, row = manifest["cases"][i], execution["cases"][i]
        seed = r.state(execution["shared"]["actual_source"])
        target = r.check_event(seed, case, row["event"])
        for role in r.ROLES:
            before = replace(target.inputs, current=getattr(target.inputs, role), dt=b.DT)
            step = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 1)
            r.check_step(before, step)
            for kind in ("geometry", "current", "domain", "source", "restart", "continuity"):
                changed = deepcopy(step)
                if kind == "geometry": changed["root"]["H"][0][0] += 2**-20
                elif kind == "current": changed["root"]["read_current"][0] += 1
                elif kind == "domain": changed["root"]["bounds"]["contraction_upper"] = "1"
                elif kind == "source": changed["root"]["source"][0][0] += 2**-50
                elif kind == "restart": changed["restart"] = changed["root"]
                else: changed["poststate"]["current"]["C"][0] += 1
                if kind in ("geometry", "current", "domain", "source"):
                    raw = {k:v for k,v in changed["root"].items() if k != "independent_certificate"}
                    changed["root"]["record_digest"] = b.seal(raw)["record_digest"]
                    changed["root"]["independent_certificate"]["selected_root_digest"] = changed["root"]["record_digest"]
                with self.subTest(role=role,kind=kind), self.assertRaises(ValueError): r.check_step(before, changed)
        for kind in ("reset", "reference", "publication", "missing_read", "replay"):
            changed = deepcopy(row["event"])
            if kind == "reset": changed["actual_target"]["inputs"]["reset"]["C"][0] += 1
            elif kind == "reference": changed["checkpoint"]["reference_currents"][0]["roles"]["reset"]["target"][0] += 1
            elif kind == "publication": changed["publication"][0]["admission_pairs"] = 1
            elif kind == "missing_read": changed["admission_reads"].pop()
            else: changed["replay_identical"] = False
            with self.subTest(kind=kind), self.assertRaises(ValueError): r.check_event(seed, case, changed)


if __name__ == "__main__":
    unittest.main()
