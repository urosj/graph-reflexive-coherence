"""All-ten larger-graph examples must contain actual contracts and histories."""

import json
import unittest
from copy import deepcopy
from fractions import Fraction

import prepare_p983_all_realizations as examples

from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_profile import GRCV4Profile


class AllRealizationPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {
            family: json.loads(
                (examples.ROOT / examples.OUTPUT / (family + ".json")).read_text()
            )
            for family in examples.FAMILIES
        }

    def test_every_family_has_resolved_source_and_target_profiles(self):
        self.assertEqual(set(self.records), set(examples.settings()["families"]))
        source_ids, target_ids = set(), set()
        for family, record in self.records.items():
            with self.subTest(family=family):
                self.assertEqual(
                    record["record_digest"], examples.common.record_digest(record)
                )
                for side, n, m in [("source", 100, 400), ("target", 107, 407)]:
                    data = record[side]
                    graph = GRC9V4PortGraph.from_envelope(data["graph"])
                    profile = GRCV4Profile.from_canonical_bytes(
                        canonical_json_bytes(data["profile"])
                    )
                    self.assertEqual(profile.identity_payload.profile_family_id, family)
                    self.assertEqual(
                        (len(graph.live_node_ids), len(graph.edges)), (n, m)
                    )
                    self.assertEqual(
                        examples.common.graph_facts(graph), record["graph_facts"][side]
                    )
                source_ids.add(record["source"]["profile"]["complete_profile_id"])
                target_ids.add(record["target"]["profile"]["complete_profile_id"])
                self.assertNotEqual(
                    record["source"]["profile"]["complete_profile_id"],
                    record["target"]["profile"]["complete_profile_id"],
                )
                GRC9V4ExpansionRequestInput.from_payload(record["event_request"])
        self.assertEqual(len(source_ids), 10)
        self.assertEqual(len(target_ids), 10)

    def test_all_actual_history_shapes_lineage_and_carrier_reset(self):
        for family, record in self.records.items():
            with self.subTest(family=family):
                source = {
                    role: examples.authority(value, 400)
                    for role, value in record["source"]["roles"].items()
                }
                target = {
                    role: examples.authority(value, 407)
                    for role, value in record["target"]["roles"].items()
                }
                old_edges = [e["edge_id"] for e in record["source"]["graph"]["edges"]]
                new_edges = [e["edge_id"] for e in record["target"]["graph"]["edges"]]
                for role in ("current", "reset"):
                    self.assertEqual(sum(map(Fraction, source[role].C)), 200)
                    self.assertEqual(sum(map(Fraction, target[role].C)), 200)
                    if family.startswith("A_"):
                        old = dict(zip(old_edges, source[role].W_A, strict=True))
                        self.assertEqual(
                            target[role].W_A, tuple(old.get(e, 1) for e in new_edges)
                        )
                        self.assertNotEqual(source["current"].W_A, source["reset"].W_A)
                    else:
                        self.assertIsNone(source[role].W_A)
                        self.assertIsNone(target[role].W_A)
                    if family.endswith("PC"):
                        self.assertTrue(any(source[role].Z_4))
                        self.assertEqual(len(source[role].Z_4), 400**2)
                        self.assertEqual(target[role].Z_4, (0.0,) * 407**2)
                    else:
                        self.assertIsNone(source[role].Z_4)
                        self.assertIsNone(target[role].Z_4)
                if family.endswith("PC"):
                    self.assertEqual(
                        source["current"].Z_4, tuple(-x for x in source["reset"].Z_4)
                    )

    def test_explicit_new_domains_and_unchanged_rg_completion_identity(self):
        for family, record in self.records.items():
            selected = record["selected_configuration"]
            for side in ("source", "target"):
                params = record[side]["profile"]["params_resolved"]
                self.assertEqual(params["geometry"]["kappa_H"], selected["kappa_H"])
                if family.endswith("PC"):
                    self.assertEqual(selected["resource_radius"], 32)
                    self.assertEqual(
                        params["realization"]["radius"], selected["carrier_radius"]
                    )
                    self.assertTrue(
                        params["realization"]["source_envelope_id"].startswith(
                            "pc_compact_base_chart_v1:0x1.0000000000000p+5:"
                        )
                    )
                if family.endswith("RG2b"):
                    self.assertIn(
                        "tree17", params["realization"]["containment_certificate_id"]
                    )
                    self.assertEqual(record["graph_facts"][side]["cycle_rank"], 301)
            self.assertEqual(record["execution"]["numerical_admission"], "not_run")
            self.assertEqual(record["execution"]["events_committed"], 0)

    def test_profile_tampering_cannot_reuse_accepted_identity(self):
        for family, record in self.records.items():
            bad = deepcopy(record["source"]["profile"])
            bad["params_resolved"]["geometry"]["kappa_H"] *= 2
            with self.assertRaises(ValueError, msg=family):
                GRCV4Profile.from_canonical_bytes(canonical_json_bytes(bad))

    def test_rehashed_promotion_and_omitted_or_extra_family_reject(self):
        for family, record in self.records.items():
            examples.validate_claims(record)
            bad = deepcopy(record)
            bad["execution"]["events_committed"] = 1
            bad["record_digest"] = examples.common.record_digest(bad)
            with self.assertRaisesRegex(ValueError, "cannot claim execution"):
                examples.validate_claims(bad)
            request = examples.settings()
            del request["families"][family]
            with self.assertRaisesRegex(ValueError, "all ten"):
                examples.settings(request)
        request = examples.settings()
        request["families"]["A_UNKNOWN"] = {}
        with self.assertRaisesRegex(ValueError, "all ten"):
            examples.settings(request)

    def test_whole_carrier_norm_and_composite_double_image(self):
        for family, record in self.records.items():
            if not family.endswith("PC"):
                continue
            selected = record["selected_configuration"]
            for role in ("current", "reset"):
                state = examples.authority(record["source"]["roles"][role], 400)
                norm2 = sum(Fraction(v) ** 2 for v in state.Z_4 if v)
                self.assertEqual(norm2, Fraction(400, 4096**2))
                self.assertLess(norm2, Fraction(selected["carrier_radius"]) ** 2)
                self.assertGreater(sum(Fraction(v) ** 2 for v in state.C), 16**2)
                self.assertLess(sum(Fraction(v) ** 2 for v in state.C), 32**2)
            if "CI" in family:
                self.assertGreaterEqual(
                    Fraction(selected["geometry_radius"]),
                    2
                    * Fraction(selected["kappa_H"])
                    * Fraction(selected["carrier_radius"]),
                )
                self.assertEqual(
                    record["source"]["profile"]["identity_payload"]["composition_gain"],
                    2,
                )

    def test_carrier_recipe_cannot_hide_unknown_fields(self):
        for z in (
            {"recipe": "zero_v1", "scale": 1},
            {"recipe": "unknown_v1"},
            {"recipe": "alternating_diagonal_v1", "scale": 1, "ignore": 1},
        ):
            with self.assertRaises(ValueError):
                examples.authority({"C": [1], "W_A": None, "Z_4": z}, 1)

    def test_all_forty_numerical_outcomes_are_explicit_and_scope_bound(self):
        for family, record in self.records.items():
            report = json.loads(
                (
                    examples.ROOT / examples.OUTPUT / (family + "-Admission.json")
                ).read_text()
            )
            self.assertEqual(
                report["record_digest"], examples.common.record_digest(report)
            )
            self.assertEqual(report["prepared_digest"], record["record_digest"])
            self.assertEqual(report["family"], family)
            self.assertEqual(report["physical_steps"], 0)
            self.assertEqual(report["events_committed"], 0)
            self.assertEqual(report["supported_profiles_added"], [])
            for side in ("source", "target"):
                self.assertEqual(set(report[side]), {"current", "reset"})
                for result in report[side].values():
                    self.assertEqual(result["owner"], examples.numerical_owner(family))
                    self.assertIn(
                        result["status"], {"passed", "rejected", "incomplete"}
                    )
                    if result["status"] == "incomplete":
                        self.assertGreater(result["numerical_budget_seconds"], 0)
                        self.assertIn("no admission conclusion", result["reason"])
                        self.assertNotIn("bounds", result)
                    if family.endswith("RG2b"):
                        self.assertEqual(result["status"], "rejected")
                        self.assertIn("tree with at most 17 vertices", result["reason"])


if __name__ == "__main__":
    unittest.main()
