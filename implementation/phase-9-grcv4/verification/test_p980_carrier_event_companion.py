"""Bounded whole-source archive / whole-target zero-reset research companion.

Consumes actual per-role carriers. No native receipt, digest or event API.
"""

import copy
import json
import math
import unittest
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import numpy as np
import test_p980_a_event_companion as a_event
import test_p980_event_companion as common
import test_p980_realization_numerical as numerical
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    bounds,
    endpoint,
    full_error,
    number,
    upper_abs,
    vector,
)

INPUT_PATH = (
    Path(__file__).resolve().parents[1] / "tranche-8/P9-8.0-CarrierEventInputs.json"
)
PROFILES = (("A", "PC"), ("C", "PC"), ("A", "CI_PC"), ("C", "CI_PC"))
require = common.require


def validate_inputs(case, shared, a_case):
    common.validate_inputs(shared)
    a_event.validate_inputs(a_case, shared)
    require(
        case
        == {
            "research_case_id": "P9-8.0-PERSISTENT-SOURCE-D52-POSITIVE-PHASE-3",
            "shared_input_record": common.INPUT_PATH.name,
            "A_input_record": a_event.INPUT_PATH.name,
            "inherited_A_fields": [
                "parameters",
                "source_W",
                "event_history",
                "row_detection",
            ],
            "profiles": [c + "_" + r for c, r in PROFILES],
            "source_carrier": {
                "edge_order": "source_graph.edges",
                "formula": "sign(role)*(R/16)*star_mask[i,j]*(-1)^(i+j)",
                "role_signs": {"current": 1, "reset": -1},
                "radius": str(numerical.exact.CARRIER_RADIUS),
                "current_event_stage": "after_one_enabled_source_beat",
                "reset_event_stage": "independently_supplied_no_source_beat",
            },
            "carrier_policy": "whole_source_archive_whole_target_zero_reset",
            "archive": "all_source_entries_in_source_edge_order",
            "target_carrier": "exact_zero_all_target_edge_pairs",
            "carrier_information_loss": ["carrier_history_loss"],
            "candidate_information_loss": [],
            "tau_PC": "1",
            "rho_inst": "1",
            "geometry_radius": str(numerical.exact.GEOMETRY_RADIUS),
            "target_steps": bounds.HORIZON,
            "reference_current": "fresh_role_event_entry_selected_realization_read",
            "new_reference_current": "exact_zero",
            "identity_scope": "research_operands_only_no_native_receipt_or_registration",
        },
        "persistent input recipe mismatch",
    )


def produce_event(shared, candidate, c, w, z, reference):
    ids = [e["edge_id"] for e in shared["source_graph"]["edges"]]
    target_ids = [e["edge_id"] for e in shared["expected_target_roles"]["edges"]]
    c_map = dict(zip(shared["source_graph"]["nodes"], c, strict=True))
    resources = common.produce_target(shared, c_map)["resources"]
    old_w = dict(zip(ids, w, strict=True)) if w is not None else {}
    refs = dict(zip(ids, reference, strict=True))
    return {
        "c": np.array([resources[n] for n in shared["expected_target_roles"]["nodes"]]),
        "w": np.array([old_w.get(e, 1.0) for e in target_ids])
        if candidate == "A"
        else None,
        "z": np.zeros((len(target_ids), len(target_ids))),
        "archive_edges": ids.copy(),
        "archive": z.copy(),
        "reference": np.array([refs.get(e, 0.0) for e in target_ids]),
        "C_references": copy.deepcopy(shared["target_reference_weights"])
        if candidate == "C"
        else None,
        "candidate_history": "exact_old_edge_lineage_and_positive_bond_seed"
        if candidate == "A"
        else "rederived",
        "carrier_history": "whole_source_archive_whole_target_zero_reset",
        "candidate_information_loss": [],
        "carrier_information_loss": ["carrier_history_loss"],
    }


def checked_event(
    case, shared, a_case, source, target, candidate, realization, c, w, z, reference
):
    validate_inputs(case, shared, a_case)
    require((candidate, realization) in PROFILES, "unsupported persistent profile")
    c = numerical.finite_array(c, (len(source.nodes),)).copy()
    z = numerical.finite_array(z, (len(source.edges), len(source.edges))).copy()
    reference = numerical.finite_array(reference, (len(source.edges),)).copy()
    numerical.carrier_input(source, z)
    if candidate == "A":
        w = numerical.finite_array(w, (len(source.edges),)).copy()
    else:
        require(w is None, "C history must be absent")
    # Bind the supplied reference to an independently certified fresh read of
    # these saved inputs; hypothetical ordinary outputs are discarded.
    _, read_truth = numerical.evaluate(source, candidate, realization, c, w, z)
    require(
        full_error(reference, read_truth["read"]["J"]) < numerical.CURRENT_ERROR_LIMIT,
        "source reference-current recipe mismatch",
    )
    p = IV.matrix(
        [[number(v) for v in row] for row in common.transfer_matrix(source, target)]
    )
    ci = p * vector(c)
    embedding, seed = a_event.history_embedding(source, target)
    e = IV.matrix([[number(v) for v in row] for row in embedding])
    wi = e * vector(w) + vector(seed) if w is not None else None
    ji = e * vector(reference)
    out = produce_event(
        copy.deepcopy(shared),
        candidate,
        c.copy(),
        None if w is None else w.copy(),
        z.copy(),
        reference.copy(),
    )
    require(
        set(out)
        == {
            "c",
            "w",
            "z",
            "archive_edges",
            "archive",
            "reference",
            "C_references",
            "candidate_history",
            "carrier_history",
            "candidate_information_loss",
            "carrier_information_loss",
        },
        "event fields mismatch",
    )
    error = full_error(out["c"], ci)
    require(error < numerical.RESOURCE_ERROR_LIMIT, "event resource error unresolved")
    for i, n in enumerate(target.nodes):
        if n.startswith("outside-"):
            require(out["c"][i] == c[source.index[n]], "exterior resource changed")
        elif n == "core" or n.startswith("extra/"):
            require(out["c"][i] == 0, "zero resource face changed")
    if candidate == "A":
        require(full_error(out["w"], wi) == 0, "W lineage changed")
        require(
            out["candidate_history"] == "exact_old_edge_lineage_and_positive_bond_seed"
            and out["C_references"] is None,
            "A history channel mismatch",
        )
    else:
        require(
            out["w"] is None
            and out["candidate_history"] == "rederived"
            and out["C_references"] == shared["target_reference_weights"],
            "C reference channel mismatch",
        )
    require(full_error(out["reference"], ji) == 0, "reference lineage changed")
    archived = numerical.finite_array(out["archive"], z.shape)
    require(
        out["archive_edges"] == [edge["edge_id"] for edge in source.edges]
        and np.array_equal(archived, z),
        "whole source archive mismatch",
    )
    numerical.carrier_input(target, out["z"])
    require(np.count_nonzero(out["z"]) == 0, "whole target zero reset mismatch")
    require(
        out["carrier_history"] == case["carrier_policy"]
        and out["carrier_information_loss"] == ["carrier_history_loss"]
        and out["candidate_information_loss"] == [],
        "history loss channels mismatch",
    )
    charge = abs(sum(Q(float(x)) for x in out["c"]) - sum(Q(float(x)) for x in c))
    require(charge <= len(target.nodes) * error, "event charge error unresolved")
    return out, {
        "resource_error": float(error),
        "charge_error": float(charge),
        "archived_frobenius_squared": float(sum(Q(float(x)) ** 2 for x in z.ravel())),
    }


def reference_current(model, candidate, realization, c, w, z):
    """A certified read exposes no hypothetical resource/history/carrier writes."""
    out, _ = numerical.evaluate(model, candidate, realization, c, w, z)
    return out["read"]["J"].copy()


def assert_event_source_stage(source, target, event, c, w, z):
    """Bind every transferred channel to the independently declared source stage."""
    require(
        np.array_equal(event["archive"], z),
        "source archive stage differs from declared physical entry",
    )
    p = common.transfer_matrix(source, target)
    exact_c = vector(
        [sum(a * Q(float(v)) for a, v in zip(row, c, strict=True)) for row in p]
    )
    require(
        full_error(event["c"], exact_c) < numerical.RESOURCE_ERROR_LIMIT,
        "event resource differs from declared physical entry",
    )
    if w is None:
        require(event["w"] is None, "C history must be absent")
    else:
        ids = {edge["edge_id"]: i for i, edge in enumerate(source.edges)}
        expected_w = np.array(
            [
                w[ids[edge["edge_id"]]] if edge["edge_id"] in ids else 1.0
                for edge in target.edges
            ]
        )
        require(
            np.array_equal(event["w"], expected_w),
            "event W differs from declared physical entry",
        )


class CarrierEventCompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(INPUT_PATH.read_text())
        cls.shared = json.loads(common.INPUT_PATH.read_text())
        cls.a_case = json.loads(a_event.INPUT_PATH.read_text())
        validate_inputs(cls.case, cls.shared, cls.a_case)
        cls.source, cls.target = [
            numerical.RepresentedRows(
                copy.deepcopy(cls.shared[key]["nodes"]),
                copy.deepcopy(cls.shared[key]["edges"]),
                PARAMS,
            )
            for key in ("source_graph", "expected_target_roles")
        ]
        for key, model in zip(
            ("source_graph", "expected_target_roles"),
            (cls.source, cls.target),
            strict=True,
        ):
            common.assert_model_binding(cls.shared, key, model)

    def initial(self, candidate, role):
        c = self.source.vector(
            {
                n: Q(v)
                for n, v in self.shared["roles"][role]["initial_resources"].items()
            }
        )
        w = (
            np.array(
                [
                    float(Q(self.a_case["source_W"][role][e["edge_id"]]))
                    for e in self.source.edges
                ]
            )
            if candidate == "A"
            else None
        )
        z = numerical.seed_carrier(self.source, role)
        # Independent endpoint assembly binds the declared seed, including all
        # off-diagonal entries and the role sign, rather than trusting mask use.
        ends = [{e["tail"]["node_id"], e["head"]["node_id"]} for e in self.source.edges]
        expected = np.array(
            [
                [
                    float(
                        (1 if role == "current" else -1)
                        * numerical.exact.CARRIER_RADIUS
                        / 16
                        * (Q(1) if i == j else Q(1, 2) if a & b else Q(0))
                        * (-1) ** (i + j)
                    )
                    for j, b in enumerate(ends)
                ]
                for i, a in enumerate(ends)
            ]
        )
        np.testing.assert_array_equal(z, expected)
        numerical.carrier_input(self.source, z)
        return c, w, z

    def entry(self, candidate, realization, role):
        c, w, z = self.initial(candidate, role)
        if role == "current":
            out, _ = numerical.evaluate(self.source, candidate, realization, c, w, z)
            c, w, z = out["after"], out["history"], out["carrier"]
            rows = IntervalRows(self.source).rows(
                vector(c),
                vector(w) if w is not None else vector([1] * len(self.source.edges)),
            )[self.source.index["source-s"]]
            self.assertTrue(all(endpoint(x, 0) > 0 for x in rows))
            self.assertLess(sum(upper_abs(x) ** 2 for x in rows), Q(1, 4))
        reference = reference_current(self.source, candidate, realization, c, w, z)
        return (c, w, z, reference)

    def declared_source_stage(self, candidate, realization, role):
        # CEC-F1: construct the oracle directly from records and endpoints;
        # neither initial(), entry(), nor event() can supply its expected stage.
        graph = self.shared["source_graph"]
        c = np.array(
            [
                float(Q(self.shared["roles"][role]["initial_resources"][n]))
                for n in graph["nodes"]
            ]
        )
        w = (
            np.array(
                [
                    float(Q(self.a_case["source_W"][role][e["edge_id"]]))
                    for e in graph["edges"]
                ]
            )
            if candidate == "A"
            else None
        )
        ends = [{e["tail"]["node_id"], e["head"]["node_id"]} for e in graph["edges"]]
        radius = Q(self.case["source_carrier"]["radius"])
        sign = self.case["source_carrier"]["role_signs"][role]
        z = np.array(
            [
                [
                    float(
                        sign
                        * radius
                        / 16
                        * (Q(1) if i == j else Q(1, 2) if a & b else Q(0))
                        * (-1) ** (i + j)
                    )
                    for j, b in enumerate(ends)
                ]
                for i, a in enumerate(ends)
            ]
        )
        if role == "current":
            out, _ = numerical.evaluate(self.source, candidate, realization, c, w, z)
            c, w, z = out["after"], out["history"], out["carrier"]
        return c.copy(), None if w is None else w.copy(), z.copy()

    def event(self, candidate, realization, role):
        expected = self.declared_source_stage(candidate, realization, role)
        operands = self.entry(candidate, realization, role)
        out, report = checked_event(
            self.case,
            self.shared,
            self.a_case,
            self.source,
            self.target,
            candidate,
            realization,
            *operands,
        )
        assert_event_source_stage(self.source, self.target, out, *expected)
        return out, report

    def test_physical_source_stage_through_event_consumer(self):
        original_entry = self.entry
        for candidate, realization in PROFILES:
            for role in ("current", "reset"):
                with self.subTest(
                    candidate=candidate, realization=realization, role=role
                ):
                    self.event(candidate, realization, role)
                controls = ["probe_carrier"]
                if role == "current":
                    controls.append("drop_source_writer")
                for mode in controls:

                    def wrong_stage(candidate, realization, role, mode=mode):
                        c, w, z, reference = original_entry(
                            candidate, realization, role
                        )
                        if mode == "probe_carrier":
                            probe, _ = numerical.evaluate(
                                self.source, candidate, realization, c, w, z
                            )
                            z = probe["carrier"]
                        else:
                            z = self.initial(candidate, role)[2]
                        return c, w, z, reference

                    with (
                        self.subTest(
                            candidate=candidate,
                            realization=realization,
                            role=role,
                            mode=mode,
                        ),
                        patch.object(self, "entry", side_effect=wrong_stage),
                        self.assertRaisesRegex(ValueError, "source archive stage"),
                    ):
                        self.event(candidate, realization, role)

    def test_four_profiles_both_roles_actual_reset_continuation(self):
        reports = {}
        for candidate, realization in PROFILES:
            for role in ("current", "reset"):
                event, event_report = self.event(candidate, realization, role)
                c, w, z = event["c"], event["w"], event["z"]
                self.assertGreater(np.count_nonzero(event["archive"]), 0)
                self.assertEqual(np.count_nonzero(z), 0)
                steps = []
                for k in range(bounds.HORIZON):
                    out, truth = numerical.evaluate(
                        self.target, candidate, realization, c, w, z
                    )
                    low = min(endpoint(x, 0) for x in truth["after"])
                    self.assertGreater(low, Q(1, 16384))
                    self.assertLess(max(endpoint(x, 1) for x in truth["after"]), 4)
                    if k == 0:
                        if realization == "PC":
                            np.testing.assert_array_equal(out["H"], self.target.I)
                        self.assertGreater(np.count_nonzero(out["carrier"]), 0)
                        for i, e in enumerate(self.target.edges):
                            if e["edge_id"].startswith("internal/"):
                                self.assertEqual(event["reference"][i], 0)
                                self.assertGreater(abs(out["read"]["J"][i]), 1e-4)
                    steps.append(
                        {
                            "resource_lower": float(low),
                            **{k: float(v) for k, v in truth["certificate"].items()},
                        }
                    )
                    c, w, z = out["after"], out["history"], out["carrier"]
                _, final = numerical.evaluate(
                    self.target, candidate, realization, c, w, z
                )
                reports[candidate + "_" + realization + "_" + role] = {
                    "event": event_report,
                    "steps": steps,
                    "final_current_error": float(final["certificate"]["current_error"]),
                    "final_carrier_norm_squared": float(
                        numerical.frobenius_squared(IV.matrix(z.tolist()))
                    ),
                }
        type(self).continuation_report = reports

    def test_reset_effects_at_declared_consumers(self):
        effects = {}

        def compare(key, *args):
            effects[key] = numerical.checked_separation(key, *args)

        for candidate, realization in PROFILES:
            for role in ("current", "reset"):
                key = candidate + "_" + realization + "_" + role
                event, _ = self.event(candidate, realization, role)
                c, w, z = event["c"], event["w"], event["z"]
                out, truth = numerical.evaluate(
                    self.target, candidate, realization, c, w, z
                )
                high = truth["high"]
                # Zero old Z has no old-carrier effect at entry. PC geometry is
                # exactly identity there; its first observable geometry is at
                # the next read, after the actual same-source writer.
                controls = [("readback", {"feedback": False})]
                if candidate == "C":
                    controls.append(("modulation", {"modulation": False}))
                if realization == "CI_PC":
                    controls.append(("geometry", {"geometry": False}))
                for name, flags in controls:
                    off_i = high.read(
                        candidate, truth["c"], truth["w"], truth["H"], **flags
                    )
                    off = self.target.read(
                        candidate,
                        c.copy(),
                        None if w is None else w.copy(),
                        out["H"].copy(),
                        **flags,
                    )
                    compare(
                        key + "_entry_" + name,
                        out["read"]["J"],
                        off["J"],
                        truth["read"]["J"],
                        off_i["J"],
                    )
                nxt, ni = numerical.evaluate(
                    self.target,
                    candidate,
                    realization,
                    out["after"],
                    out["history"],
                    out["carrier"],
                    ci=truth["after"],
                    wi=truth["history"],
                    zi=truth["carrier"],
                )
                zero, zi = numerical.evaluate(
                    self.target,
                    candidate,
                    realization,
                    out["after"],
                    out["history"],
                    np.zeros_like(z),
                    ci=truth["after"],
                    wi=truth["history"],
                    zi=IV.matrix(z.tolist()),
                )
                compare(
                    key + "_written_carrier_next_current",
                    nxt["read"]["J"],
                    zero["read"]["J"],
                    ni["read"]["J"],
                    zi["read"]["J"],
                )
                off_i = high.read(candidate, ni["c"], ni["w"], ni["H"], geometry=False)
                off = self.target.read(
                    candidate,
                    out["after"].copy(),
                    None if out["history"] is None else out["history"].copy(),
                    nxt["H"].copy(),
                    geometry=False,
                )
                compare(
                    key + "_next_geometry",
                    nxt["read"]["J"],
                    off["J"],
                    ni["read"]["J"],
                    off_i["J"],
                )
                if realization == "CI_PC":
                    pc, pci = numerical.evaluate(self.target, candidate, "PC", c, w, z)
                    compare(
                        key + "_entry_instantaneous_source",
                        out["read"]["J"],
                        pc["read"]["J"],
                        truth["read"]["J"],
                        pci["read"]["J"],
                    )
                # Source-selection control through the same first target writer.
                wrong_i = high.read(
                    candidate, truth["after"], truth["history"], truth["H"]
                )["source"]
                wrong = self.target.read(
                    candidate,
                    out["after"].copy(),
                    None if out["history"] is None else out["history"].copy(),
                    out["H"].copy(),
                )["source"]
                decay, decay_i = math.exp(-float(bounds.DT)), IV.exp(-number(bounds.DT))
                wrong_z = decay * z + (1 - decay) * wrong
                wrong_zi = decay_i * truth["z"] + (1 - decay_i) * wrong_i
                compare(
                    key + "_same_source_carrier",
                    out["carrier"].ravel(),
                    wrong_z.ravel(),
                    IV.matrix(list(truth["carrier"])),
                    IV.matrix(list(wrong_zi)),
                )
                wrong_next, wni = numerical.evaluate(
                    self.target,
                    candidate,
                    realization,
                    out["after"],
                    out["history"],
                    wrong_z,
                    ci=truth["after"],
                    wi=truth["history"],
                    zi=wrong_zi,
                )
                compare(
                    key + "_same_source_next_current",
                    nxt["read"]["J"],
                    wrong_next["read"]["J"],
                    ni["read"]["J"],
                    wni["read"]["J"],
                )
                if candidate == "A":
                    for mode in ("baseline_current", "stale_resource"):
                        wc_i = high.write(
                            truth["after"]
                            if mode == "baseline_current"
                            else truth["c"],
                            truth["w"],
                            truth["read"]["baseline"]
                            if mode == "baseline_current"
                            else truth["read"]["J"],
                        )
                        wc = a_event.checked_counterfactual_writer(
                            self.target,
                            out["after"] if mode == "baseline_current" else c,
                            w,
                            out["read"]["baseline"]
                            if mode == "baseline_current"
                            else out["read"]["J"],
                        )
                        compare(
                            key + "_" + mode + "_W",
                            out["history"],
                            wc,
                            truth["history"],
                            wc_i,
                        )
                        off, oi = numerical.evaluate(
                            self.target,
                            candidate,
                            realization,
                            out["after"],
                            wc,
                            out["carrier"],
                            ci=truth["after"],
                            wi=wc_i,
                            zi=truth["carrier"],
                        )
                        compare(
                            key + "_" + mode + "_next_current",
                            nxt["read"]["J"],
                            off["read"]["J"],
                            ni["read"]["J"],
                            oi["read"]["J"],
                        )
        self.assertEqual(len(effects), 68)
        type(self).effect_report = effects

    def test_policy_binding_and_event_output_controls(self):
        for field, value in (
            ("carrier_policy", "partial_copy"),
            ("carrier_information_loss", []),
            ("tau_PC", "2"),
            ("profiles", ["C_PC"]),
        ):
            bad = copy.deepcopy(self.case)
            bad[field] = value
            with self.assertRaisesRegex(ValueError, "input recipe"):
                validate_inputs(bad, self.shared, self.a_case)
        for candidate in ("A", "C"):
            args = self.entry(candidate, "PC", "reset")

            def consume(candidate=candidate, args=args):
                return checked_event(
                    self.case,
                    self.shared,
                    self.a_case,
                    self.source,
                    self.target,
                    candidate,
                    "PC",
                    *args,
                )

            wrong_reference = (*args[:3], -args[3])
            with self.assertRaisesRegex(ValueError, "source reference-current recipe"):
                checked_event(
                    self.case,
                    self.shared,
                    self.a_case,
                    self.source,
                    self.target,
                    candidate,
                    "PC",
                    *wrong_reference,
                )
            good, _ = consume()
            for mode in (
                "archive",
                "archive_edges",
                "z",
                "loss",
                "candidate_loss",
                "reference",
                "resource",
                "candidate_state",
            ):
                bad = copy.deepcopy(good)
                if mode == "archive":
                    bad["archive"][-1, -1] += 2**-24
                elif mode == "archive_edges":
                    bad["archive_edges"].reverse()
                elif mode == "z":
                    bad["z"][0, 0] = 2**-30
                elif mode == "loss":
                    bad["carrier_information_loss"] = []
                elif mode == "candidate_loss":
                    bad["candidate_information_loss"] = ["history_loss"]
                elif mode == "reference":
                    bad["reference"][-1] += 0.125
                elif mode == "resource":
                    bad["c"][self.target.index["core"]] += 0.125
                elif candidate == "A":
                    bad["w"][-1] += 0.125
                else:
                    bad["C_references"]["old-1"] = "2"
                with (
                    self.subTest(candidate=candidate, mode=mode),
                    patch(__name__ + ".produce_event", return_value=bad),
                    self.assertRaises(ValueError),
                ):
                    consume()

    def test_event_input_ownership_and_scratch(self):
        raw = produce_event
        args = self.entry("A", "PC", "current")
        saved = [a.copy() for a in args]

        def consume():
            return checked_event(
                self.case,
                self.shared,
                self.a_case,
                self.source,
                self.target,
                "A",
                "PC",
                *args,
            )

        for operand in range(4):

            def shifted(shared, candidate, c, w, z, reference, operand=operand):
                (c, w, z, reference)[operand].flat[0] += 0.125
                return raw(shared, candidate, c, w, z, reference)

            with (
                patch(__name__ + ".produce_event", side_effect=shifted),
                self.assertRaises(ValueError),
            ):
                consume()
            for actual, original in zip(args, saved, strict=True):
                np.testing.assert_array_equal(actual, original)

        def scratch(shared, candidate, c, w, z, reference):
            out = raw(shared, candidate, c, w, z, reference)
            for a in (c, w, z, reference):
                a.fill(0)
            return out

        with patch(__name__ + ".produce_event", side_effect=scratch):
            consume()
        for actual, original in zip(args, saved, strict=True):
            np.testing.assert_array_equal(actual, original)


if __name__ == "__main__":
    import sys

    reporting = "--report" in sys.argv
    if reporting:
        sys.argv.remove("--report")
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(
            json.dumps(
                {
                    "continuation": CarrierEventCompanionTests.continuation_report,
                    "effects": CarrierEventCompanionTests.effect_report,
                },
                indent=2,
            )
        )
    sys.exit(not result.result.wasSuccessful())
