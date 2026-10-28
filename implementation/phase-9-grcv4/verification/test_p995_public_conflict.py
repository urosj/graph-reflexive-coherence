"""P9-9.5: actual public disabled steps, fresh native detection and atomic refusal."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pygrc.models import GRC9V4
from pygrc.models.grc_9_v3 import GRC9V3
from pygrc.models.grc_9_v4 import GRC9V4BranchRequest
from pygrc.models import grc_9_v4_lifecycle as enabled_events
from tests.models.test_grc_9_v4 import configuration, branch_request

EVIDENCE = {}
CODE = "legacy_expansion_target_undefined"


def encoded(value):
    # Preserve native signed zero rather than applying V4 numeric normalization.
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def native(model):
    return GRC9V3._from_snapshot(
        deepcopy(model.state.lifecycle.delegate_snapshot), restore_reset_baseline=True
    )


def detection(model):
    """Independently execute the unchanged native prestages, never synthetic diagnostics."""
    n = native(model)
    n.rebuild_differential_state()
    n.rebuild_transport_state()
    n.rebuild_differential_state()
    n.rebuild_identity_state()
    return n, n.detect_hybrid_spark_candidates()


class ConflictTests(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select a bounded family")

    def model(self, eps_gradient=0.05, eps_spark=0.05):
        model = GRC9V4.from_config(configuration(self.FAMILY))
        request = branch_request(model, "disable").to_payload()
        request["declaration"]["legacy_config"]["evolution"].update(
            eps_gradient=eps_gradient, eps_spark=eps_spark
        )
        result = model.migrate_branch(GRC9V4BranchRequest.from_payload(request))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(model.compatibility_branch, "disabled_grc9v3")
        return model

    def rejected(self, model, before, publication, result):
        self.assertFalse(result.committed)
        self.assertIsNone(result.commit_id)
        self.assertEqual(result.operation_disposition, "rejected")
        f = result.failure
        self.assertEqual((f.stage, f.code), ("target_readmission", CODE))
        self.assertEqual(f.prestate_digest, f.poststate_digest)
        self.assertEqual(f.pre_lifecycle_digest, f.post_lifecycle_digest)
        self.assertEqual(f.pre_lifecycle_digest, model.lifecycle_digest)
        self.assertEqual(f.prestate_digest, model.state.scientific_state_digest)
        self.assertEqual(result.emitted_receipts, (f.failure_receipt,))
        self.assertNotIn(
            f.failure_receipt.receipt_id, [r.receipt_id for r in model.receipt_ledger]
        )
        self.assertIs(model._operation._published, publication)
        self.assertEqual(encoded(model.snapshot()), before)

    def test_public_step_and_run_preserve_entire_publication(self):
        m = self.model()
        n, candidates = detection(m)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0].payload
        node = candidate["candidate_node_id"]
        ports = sorted(
            port + 1
            for eid in n._state.topology.incident_edge_ids(node)
            for endpoint, port in n._state.topology.edge_ports(eid)
            if endpoint == node
        )
        self.assertEqual(ports, list(range(1, 10)))
        self.assertTrue(
            all(
                candidate[k]
                for k in (
                    "saturation_gate",
                    "basin_interior_gate",
                    "signed_hessian_degeneracy_gate",
                )
            )
        )
        current = native(m)
        reset = native(m)
        reset.reset()
        self.assertNotEqual(
            [current._state.nodes[k].coherence for k in sorted(current._state.nodes)],
            [reset._state.nodes[k].coherence for k in sorted(reset._state.nodes)],
        )
        before = encoded(m.snapshot())
        state, obs = m.state, deepcopy(m.compute_observables())
        publication = m._operation._published
        self.assertGreater(
            len(m.receipt_ledger), 0
        )  # Preserve a real successful prefix.
        seen = []
        original = GRC9V3.detect_hybrid_spark_candidates

        def observe(actual):
            found = original(actual)
            seen.append([deepcopy(e.payload) for e in found])
            return found

        with (
            patch.object(GRC9V3, "detect_hybrid_spark_candidates", observe),
            patch.object(
                enabled_events,
                "prepare_expansion",
                side_effect=AssertionError("V4 substitution"),
            ),
        ):
            result = m.step()
            self.rejected(m, before, publication, result)
            repeats = m.run(2)
            for repeat in repeats:
                self.rejected(m, before, publication, repeat)
                self.assertEqual(
                    repeat.failure.to_payload(), result.failure.to_payload()
                )
        self.assertEqual(seen, [[candidate]] * 3)
        self.assertEqual(m.state, state)
        self.assertEqual(m.compute_observables(), obs)
        EVIDENCE["rejection"] = dict(
            candidate=candidate,
            occupied_ports=ports,
            legacy_conflict_endpoint=["s_2", 5],
            current_state_digest=digest(current.snapshot()),
            reset_state_digest=digest(reset.snapshot()),
            before_snapshot_sha256=hashlib.sha256(before).hexdigest(),
            after_snapshot_sha256=digest(m.snapshot()),
            successful_receipts=len(m.receipt_ledger),
            journal_actions=len(m.snapshot()["owner"]["journal"]),
            failure=result.failure.to_payload(),
            rejected_public_calls=3,
            whole_publication_preserved=True,
            successful_history_unchanged=True,
            no_v4_substitution=True,
            fresh_native_candidate_observed=True,
        )

    def test_rejected_operation_is_absent_from_replay_and_reset(self):
        m = self.model()
        before = encoded(m.snapshot())
        result = m.step()
        self.rejected(m, before, m._operation._published, result)
        clone = m.duplicate()
        self.assertEqual(encoded(clone.snapshot()), before)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "checkpoint.json"
            m.save(path)
            loaded = GRC9V4.load(path)
        self.assertEqual(encoded(loaded.snapshot()), before)
        replay_result = loaded.step()
        self.assertEqual(
            replay_result.failure.to_payload(), result.failure.to_payload()
        )
        self.assertEqual(encoded(loaded.snapshot()), before)
        expected = native(clone)
        expected.reset()
        clone.reset()
        self.assertEqual(
            encoded(clone.state.lifecycle.delegate_snapshot),
            encoded(expected.snapshot()),
        )
        self.assertEqual(clone.compute_observables(), expected.compute_observables())
        self.assertEqual(encoded(m.snapshot()), before)
        # The distinct reset history is non-triggering, despite the same occupied ports.
        _, candidates = detection(clone)
        self.assertEqual(candidates, [])
        expected.step()
        clone.step()
        self.assertEqual(
            encoded(clone.state.lifecycle.delegate_snapshot),
            encoded(expected.snapshot()),
        )
        self.assertEqual(clone.compute_observables(), expected.compute_observables())
        EVIDENCE["replay_reset"] = dict(
            checkpoint_sha256=hashlib.sha256(before).hexdigest(),
            duplicate_exact=True,
            save_load_exact=True,
            deterministic_rejection=True,
            reset_native_parity=True,
            reset_next_step_native_parity=True,
            original_unchanged=True,
            rejected_actions_in_journal=0,
        )

    def test_strict_native_trigger_boundaries_not_saturation_alone(self):
        _, candidates = detection(self.model())
        payload = candidates[0].payload
        rows = []
        for parameter, diagnostic in (
            ("eps_gradient", "gradient_norm"),
            ("eps_spark", "min_signed_hessian"),
        ):
            boundary = payload[diagnostic]
            for label, threshold in (
                ("below", math.nextafter(boundary, -math.inf)),
                ("equal", boundary),
                ("above", math.nextafter(boundary, math.inf)),
            ):
                with self.subTest(parameter=parameter, position=label):
                    m = self.model(**{parameter: threshold})
                    _, events = detection(m)
                    self.assertEqual(len(events), int(label == "above"))
                    before = encoded(m.snapshot())
                    publication = m._operation._published
                    expected = native(m)
                    result = m.step()
                    if label == "above":
                        self.rejected(m, before, publication, result)
                    else:
                        expected.step()
                        self.assertEqual(
                            encoded(m.state.lifecycle.delegate_snapshot),
                            encoded(expected.snapshot()),
                        )
                        self.assertEqual(
                            m.compute_observables(), expected.compute_observables()
                        )
                        self.assertEqual(m.state.step_index, expected._state.step_index)
                        self.assertNotEqual(encoded(m.snapshot()), before)
                    rows.append(
                        dict(
                            parameter=parameter,
                            diagnostic=diagnostic,
                            value=boundary,
                            position=label,
                            threshold=threshold,
                            candidate_count=len(events),
                            outcome="rejected_undefined"
                            if events
                            else "native_step_equal",
                        )
                    )
        EVIDENCE["boundaries"] = rows


class COSConflict(ConflictTests):
    FAMILY = "C_OS"


class CCIConflict(ConflictTests):
    FAMILY = "C_CI"


class ACIConflict(ConflictTests):
    FAMILY = "A_CI"


class APCConflict(ConflictTests):
    FAMILY = "A_PC"


if __name__ == "__main__":
    unittest.main()
