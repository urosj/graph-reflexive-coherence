"""P9-7.1: ten concrete profile scopes, one lifecycle publication owner.

Numerical equations remain with the accepted Tranche 4–6 test owners. These
tests exercise actual lifecycle composition, identity, replay and rollback.
No migration/event generalization, formation or new G2 support is inferred.
"""

from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
from fractions import Fraction as F
import math
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4
from pygrc.models.grc_v4_codec import (
    COS_SNAPSHOT_LAYOUT_ID, GENERIC_SNAPSHOT_LAYOUT_ID,
    canonical_json_bytes, payload_identity,
)
from pygrc.models.grc_v4_lifecycle import _lifecycle_state, _profile_step
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, GRCV4State
from pygrc.models.grc_v4_step import _ledger
from typing import Any
from tests.models.test_grc_v4_lifecycle import request
from tests.models.test_grc_v4_realizations import os_fixture, a_os_fixture
from tests.models.test_grc_v4_ci import fixture as ci_fixture
from tests.models.test_grc_v4_pc import fixture as pc_fixture
from tests.models.test_grc_v4_cipc import fixture as cipc_fixture
from tests.models.test_grc_v4_rg2b_graph import graph_fixture

FAMILIES = tuple(c + "_" + r for r in ("OS", "CI", "RG2b", "PC", "CI_PC") for c in ("A", "C"))
RECIPES = {}
EVIDENCE = {}
AUDIT_EVIDENCE = {}
for family in FAMILIES:
    candidate, realization = family.split("_", 1)
    factory = {"OS": a_os_fixture if candidate == "A" else os_fixture,
               "CI": ci_fixture, "PC": pc_fixture, "CI_PC": cipc_fixture,
               "RG2b": graph_fixture}[realization]
    RECIPES[family] = dict(module=factory.__module__, function=factory.__name__,
                           kwargs={} if realization == "OS" else {"candidate": candidate})


@lru_cache(maxsize=10)
def fixture(family):
    """Accepted numerical seed, with separately declared distinct reset history."""
    candidate, realization = family.split("_", 1)
    if realization == "OS":
        before, backend = a_os_fixture() if candidate == "A" else (os_fixture(), None)
    else:
        before, backend = {"CI": ci_fixture, "PC": pc_fixture,
                           "CI_PC": cipc_fixture, "RG2b": graph_fixture}[realization](candidate)
    # Preserve charge exactly for these dyadic inputs; stay within declared
    # entry charts. Different C and every available W/Z defeat a live-only reset.
    resource = list(before.current.C)
    resource[0] += 2**-12
    resource[-1] -= 2**-12
    history = None if before.current.W_A is None else tuple(w - 2**-12 for w in before.current.W_A)
    carrier = None if before.current.Z_4 is None else tuple(z + 2**-16 for z in before.current.Z_4)
    reset = GRCV4AuthoritativeState(tuple(resource), history, carrier)
    return replace(before, reset=reset, receipt_ids=()), backend


def model(family):
    inputs, backend = fixture(family)
    return GRCV4(inputs, differential_reference=backend)


def restore(snapshot):
    return GRCV4.from_state(snapshot, snapshot["reference"]["profile"]["params_resolved"])


def rehash(snapshot):
    """Hash hostile content without schema/domain admission by the builder."""
    def identity(prefix, value):
        return prefix + ":" + sha256(canonical_json_bytes(value)).hexdigest()
    snapshot["reset_digest"] = identity("grcv4-reset-sha256", snapshot["reset"])
    snapshot["scientific_state"]["reset_digest"] = snapshot["reset_digest"]
    snapshot["scientific_state_digest"] = identity("grcv4-state-sha256", snapshot["scientific_state"])
    snapshot["lifecycle"]["scientific_state_digest"] = snapshot["scientific_state_digest"]
    snapshot["lifecycle_digest"] = identity("grcv4-lifecycle-sha256", snapshot["lifecycle"])


def endpoint(snapshot):
    """Compact inspectable values plus exact snapshot/receipt/commit identities."""
    return dict(scientific_state=snapshot["scientific_state"], reset=snapshot["reset"],
                scientific_state_digest=snapshot["scientific_state_digest"],
                reset_digest=snapshot["reset_digest"], lifecycle_digest=snapshot["lifecycle_digest"],
                snapshot_sha256=sha256(canonical_json_bytes(snapshot)).hexdigest(),
                receipt_ids=[r["receipt_id"] for r in snapshot["receipt_ledger"]],
                commit_ids=[r["commit_id"] for r in snapshot["commit_records"]])


class GenericLifecycleTests(unittest.TestCase):
    # A separate test ID per family makes skipped/omitted routes visible.
    def lifecycle(self, family):
        initial, backend = fixture(family)
        owner = model(family)
        self.assertNotEqual(initial.current, initial.reset)
        expected = _profile_step(initial, backend).next_inputs
        result = owner.step_v4_input(request(initial.dt, "first"))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.state.lifecycle.current, expected.current)
        self.assertEqual(owner.state.lifecycle.reset.authoritative, initial.reset)
        snapshot = owner.snapshot()
        first_endpoint = endpoint(snapshot)
        layout = COS_SNAPSHOT_LAYOUT_ID if family == "C_OS" else GENERIC_SNAPSHOT_LAYOUT_ID
        self.assertEqual(snapshot["implementation_layout_id"], layout)
        self.assertEqual(len(snapshot["receipt_ledger"]), 4)
        for receipt in snapshot["receipt_ledger"]:
            self.assertEqual(receipt["identity_payload"]["core"]["parent_receipt_ids"], [])
        clone = owner.duplicate()
        with TemporaryDirectory(prefix="grcv4-lifecycle-") as directory:
            path = str(Path(directory) / "state.json")
            owner.save(path)
            self.assertEqual(Path(path).read_bytes(), canonical_json_bytes(snapshot))
            loaded = GRCV4.load(path)
            if family in ("A_CI_PC", "C_RG2b"):
                # Cross-process checks of both explicit A backend + W/Z and
                # graph C section reconstruction. No test fixture is imported.
                output = subprocess.check_output([
                    sys.executable, "-c",
                    "import sys; from hashlib import sha256; from pygrc.models.grc_v4 import GRCV4; "
                    "from pygrc.models.grc_v4_codec import canonical_json_bytes; "
                    "print(sha256(canonical_json_bytes(GRCV4.load(sys.argv[1]).snapshot())).hexdigest())",
                    path,
                ], text=True).strip()
                self.assertEqual(output, endpoint(snapshot)["snapshot_sha256"])
        self.assertEqual(clone.snapshot(), snapshot)
        self.assertEqual(loaded.snapshot(), snapshot)
        next_request = request(initial.dt, "replay")
        first = owner.step_v4_input(next_request)
        second = loaded.step_v4_input(next_request)
        self.assertTrue(first.committed, first.failure)
        self.assertEqual(first, second)
        self.assertEqual(owner.snapshot(), loaded.snapshot())
        replay_endpoint = endpoint(owner.snapshot())
        self.assertEqual(clone.snapshot(), snapshot)  # no shared mutable owner
        before_reset = owner.state.lifecycle
        owner.reset()
        reset = owner.state.lifecycle
        self.assertEqual(reset.current, initial.reset)
        self.assertEqual((reset.step_index, reset.time), (before_reset.step_index, before_reset.time))
        self.assertEqual(reset.receipt_ledger[:-4], before_reset.receipt_ledger)
        # The other branch rebases to its new live history, not the old seed.
        before_rebase = loaded.state.lifecycle
        loaded.rebase_reset_baseline()
        self.assertEqual(loaded.state.lifecycle.current, before_rebase.current)
        self.assertEqual(loaded.state.lifecycle.reset.authoritative, before_rebase.current)
        loaded.reset()
        self.assertEqual(loaded.state.lifecycle.current, before_rebase.current)
        self.assertEqual(restore(loaded.snapshot()).snapshot(), loaded.snapshot())
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())
        for target in (owner, loaded):
            rows = target.snapshot()["receipt_ledger"]
            for i in range(4, len(rows), 4):
                for row in rows[i:i+4]:
                    self.assertEqual(row["identity_payload"]["core"]["parent_receipt_ids"], [rows[i-4]["receipt_id"]])
        # No promoted profile family or migration capability from local success.
        if family != "C_OS":
            self.assertNotIn("profile_migration", owner.list_capabilities())
            self.assertNotIn("typed_topology_events", owner.list_capabilities())
        EVIDENCE[family] = dict(
            recipe=RECIPES[family], initial=initial.to_payload(),
            differential_reference=None if backend is None else backend.to_payload(),
            initialization="explicit_supplied_authority_not_formation",
            complete_profile_id=initial.geometry.reference.profile.complete_profile_id,
            first=first_endpoint, replay=replay_endpoint,
            reset=endpoint(owner.snapshot()), rebase_then_reset=endpoint(loaded.snapshot()),
        )

    def pressure(self, family):
        inputs, backend = fixture(family)
        owner = model(family)
        snapshot = owner.snapshot()
        # Detached public data, and a zero-duration operation preserving all
        # scientific authority while emitting a new owned receipt delta.
        detached = owner.snapshot()
        detached["scientific_state"]["authoritative"]["C"][0] = 0
        self.assertEqual(owner.snapshot(), snapshot)
        zero = owner.step_v4_input(request(0, "zero"))
        self.assertTrue(zero.committed, zero.failure)
        self.assertEqual(owner.snapshot()["scientific_state"], snapshot["scientific_state"])
        self.assertEqual(zero.observables["continuity_evaluations"], 0)
        stable = owner.snapshot()
        observations = owner.compute_observables()
        self.assertEqual(observations["candidate_id"], family[0])
        self.assertEqual(observations["abundance_status"], "unavailable_no_admitted_definition")
        self.assertEqual(owner.snapshot(), stable)
        negative = owner.step_v4_input(request(-1, "negative"))
        self.assertFalse(negative.committed)
        self.assertEqual(owner.snapshot(), stable)
        invalid = replace(request(0, "context"), context_value={"unexpected": 1})
        self.assertFalse(owner.step_v4_input(invalid).committed)
        self.assertEqual(owner.snapshot(), stable)
        if family.endswith("RG2b"):
            wrong_beat = owner.step_v4_input(request(2 * inputs.dt, "wrong-completion-beat"))
            self.assertFalse(wrong_beat.committed)
            self.assertEqual(wrong_beat.failure.stage, "admission")
            self.assertEqual(wrong_beat.failure.code, "domain_failure")
            self.assertEqual(owner.snapshot(), stable)
        # Failure after numerical admission and receipt creation must publish
        # neither history, clock, reset, ledger nor commit preimages.
        with patch("pygrc.models.grc_v4_lifecycle._validate_publication", side_effect=RuntimeError("publication control")):
            for operation in (lambda: owner.step_v4_input(request(inputs.dt, "fault")), owner.reset, owner.rebase_reset_baseline):
                with self.assertRaisesRegex(RuntimeError, "publication control"):
                    operation()
                self.assertEqual(owner.snapshot(), stable)
        # Complete, independently changed current authority can be assigned;
        # a reset/clock change cannot be smuggled through set_state.
        assigned = replace(inputs, current=inputs.reset)
        fresh = model(family)
        fresh.set_state(GRCV4State(_lifecycle_state(assigned, ())))
        self.assertEqual(fresh.state.lifecycle.current, inputs.reset)
        with self.assertRaises(ValueError):
            fresh.set_state(GRCV4State(_lifecycle_state(replace(assigned, reset=inputs.current), ())))
        self.assertEqual(fresh.state.lifecycle.current, inputs.reset)
        for field in ("scientific_state_digest", "reset_digest", "lifecycle_digest"):
            bad = deepcopy(snapshot)
            bad[field] = "grcv4-forged-sha256:" + "0" * 64
            with self.assertRaises(ValueError):
                restore(bad)
        bad = deepcopy(snapshot)
        bad["solver_cache"] = {}
        with self.assertRaises(ValueError):
            restore(bad)
        # Only the reduced reset is invalid; the live state remains admissible.
        bad = deepcopy(snapshot)
        bad["reset"]["authoritative"]["C"][0] += 1
        rehash(bad)
        with self.assertRaises(ValueError):
            restore(bad)
        self.assertEqual(owner.snapshot(), stable)
        if backend is not None:
            bad = deepcopy(snapshot)
            bad["differential_reference"] = None
            with self.assertRaises(ValueError):
                restore(bad)
            bad = deepcopy(snapshot)
            bad["differential_reference"]["regularization"] *= 2
            with self.assertRaises(ValueError):
                restore(bad)
            for where in ("scientific_state", "reset"):
                bad = deepcopy(snapshot)
                bad[where]["authoritative"]["W_A"] = None
                rehash(bad)
                with self.assertRaises(ValueError):
                    restore(bad)
            bad = deepcopy(snapshot)
            bad["reset"]["authoritative"]["W_A"][0] = -1
            rehash(bad)
            with self.assertRaises(ValueError):
                restore(bad)
        if inputs.current.Z_4 is not None:
            for where in ("scientific_state", "reset"):
                bad = deepcopy(snapshot)
                bad[where]["authoritative"]["Z_4"] = None
                rehash(bad)
                with self.assertRaises(ValueError):
                    restore(bad)
            bad = deepcopy(snapshot)
            bad["reset"]["authoritative"]["Z_4"][0] = 1e6
            rehash(bad)
            with self.assertRaises(ValueError):
                restore(bad)


for _family in FAMILIES:
    for _case in ("lifecycle", "pressure"):
        def _test(self, family=_family, case=_case):
            getattr(self, case)(family)
        _test.__name__ = "test_" + _family + "_" + _case
        setattr(GenericLifecycleTests, _test.__name__, _test)


def rehash_one_commit(snapshot: dict[str, Any], index: int) -> None:
    """Change only the named commit identity and its receipt-envelope backlinks.

    Receipt identity preimages and IDs, current/reset science and lifecycle IDs
    stay unchanged. This intentionally does not repair semantic contradictions.
    """
    record = snapshot["commit_records"][index]
    old_id = record["commit_id"]
    record["commit_id"] = payload_identity("commit_payload", record["payload"])
    count = 0
    for receipt in snapshot["receipt_ledger"]:
        if receipt["commit_id"] == old_id:
            receipt["commit_id"] = record["commit_id"]
            count += 1
    if count != 4:
        raise AssertionError(f"expected four receipts for the mutated commit, got {count}")


class P971AuditRegressions(unittest.TestCase):
    """Native versions of the supplied audit proposals; no isolated scaffolding."""

    def two_commits(self, family: str) -> tuple[GRCV4, dict[str, Any]]:
        inputs, _ = fixture(family)
        owner = model(family)
        for operation in ("first", "replay"):
            result = owner.step_v4_input(request(inputs.dt, operation))
            self.assertTrue(result.committed, result.failure)
        snapshot = owner.snapshot()
        self.assertEqual(restore(snapshot).snapshot(), snapshot)
        AUDIT_EVIDENCE.setdefault("two_commits", {})[family] = endpoint(snapshot)
        return owner, snapshot

    def exiting_rg_owner(self, candidate: str) -> tuple[GRCV4, Any, Any]:
        from pygrc.models.grc_v4_rg2b import CandidateRG2bSection
        from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain
        from pygrc.models.grc_v4_candidate_a import CandidateACurrent
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        inputs, backend = fixture(candidate + "_RG2b")
        ref = inputs.geometry.reference
        domain = RG2bGraphDomain.from_identity(
            ref.profile.params_resolved.realization.extension_evaluator_id
        )
        resource = [domain.center_C + (domain.inner if i % 2 == 0 else -domain.inner)
                    for i in range(len(inputs.current.C))]
        resource[-1] = float(F(inputs.Q_target) - sum(map(F, resource[:-1]), F()))
        self.assertTrue(all(abs(F(x) - F(domain.center_C)) <= F(domain.inner)
                            for x in resource))
        owner = GRCV4(inputs, differential_reference=backend)
        # Use the actual public current-assignment surface. This is not a new
        # profile, a caller completion, or a reset-baseline substitution.
        assigned = replace(inputs, current=replace(inputs.current, C=tuple(resource)))
        owner.set_state(GRCV4State(_lifecycle_state(assigned, ())))
        zero = owner.step_v4_input(request(0, "boundary-admission"))
        self.assertTrue(zero.committed, zero.failure)
        result = owner.step_v4_input(request(inputs.dt, "leave-inner-chart"))
        self.assertTrue(result.committed, result.failure)
        state = owner.state.lifecycle
        radius = max(abs(F(x) - F(domain.center_C)) for x in state.current.C)
        self.assertGreater(radius, F(domain.inner))
        self.assertLess(radius, F(domain.core))

        # Independently demonstrate native state/section admission on K, without
        # invoking the stricter ordinary-entry K_minus check a second time.
        after = replace(inputs, current=state.current, reset=state.reset.authoritative,
                        step_index=state.step_index, time=state.time, dt=0,
                        receipt_ids=tuple(r["receipt_id"] for r in state.receipt_ledger))
        section = CandidateRG2bSection(after, backend)
        selected = replace(after, geometry=section.geometry, stage="rg2b_section")
        if candidate == "A":
            CandidateACurrent(selected, backend)
        else:
            CandidateCCurrent(selected)
        AUDIT_EVIDENCE.setdefault("RG2b_core_exit", {})[candidate] = dict(
            input=assigned.to_payload(),
            differential_reference=None if backend is None else backend.to_payload(),
            endpoint=endpoint(owner.snapshot()), radius=str(radius),
            inner=domain.inner, core=domain.core,
        )
        return owner, inputs, domain

    def test_rg2b_committed_core_state_roundtrips_without_another_beat(self) -> None:
        for candidate in ("C", "A"):
            with self.subTest(candidate=candidate):
                owner, _, _ = self.exiting_rg_owner(candidate)
                snapshot = owner.snapshot()
                self.assertEqual(restore(snapshot).snapshot(), snapshot)
                self.assertEqual(owner.duplicate().snapshot(), snapshot)
                with TemporaryDirectory(prefix="p971 audit ") as directory:
                    path = Path(directory) / "core state.json"
                    owner.save(str(path))
                    self.assertEqual(path.read_bytes(), canonical_json_bytes(snapshot))
                    self.assertEqual(GRCV4.load(str(path)).snapshot(), snapshot)
                self.assertEqual(owner.snapshot(), snapshot)

    def test_rg2b_core_state_is_observable_but_next_beat_can_reject(self) -> None:
        for candidate in ("C", "A"):
            with self.subTest(candidate=candidate):
                owner, inputs, _ = self.exiting_rg_owner(candidate)
                snapshot = owner.snapshot()
                observed = owner.compute_observables()
                self.assertEqual(observed["candidate_id"], candidate)
                self.assertFalse(observed["authoritative_current"]["consumed_by_continuity"])
                self.assertEqual(owner.snapshot(), snapshot)
                result = owner.step_v4_input(request(inputs.dt, "outside-next-entry"))
                self.assertFalse(result.committed)
                self.assertEqual(result.failure.stage, "pre_read_reconstruction")
                self.assertEqual(owner.snapshot(), snapshot)
                # The same state admission owns assignment and rebase. A core
                # baseline is valid but does not authorize another inner-chart beat.
                rebased = owner.duplicate()
                rebased.set_state(rebased.state)
                rebased.rebase_reset_baseline()
                rebased.reset()
                self.assertEqual(rebased.state.lifecycle.current, owner.state.lifecycle.current)
                self.assertEqual(rebased.state.lifecycle.reset.authoritative, owner.state.lifecycle.current)
                self.assertEqual(restore(rebased.snapshot()).snapshot(), rebased.snapshot())
                owner.reset()
                self.assertEqual(owner.state.lifecycle.current, inputs.reset)
                self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())

    def test_inferred_zero_duration_cannot_change_its_own_scientific_identity(self) -> None:
        for family in FAMILIES:
            with self.subTest(family=family):
                owner, original = self.two_commits(family)
                bad = deepcopy(original)
                first, second = (row["payload"] for row in bad["commit_records"])
                self.assertNotEqual(second["source_state_digest"], second["target_state_digest"])
                first["target_step_index"] = second["target_step_index"]
                first["target_time"] = second["target_time"]
                rehash_one_commit(bad, 0)
                AUDIT_EVIDENCE.setdefault("zero_clock_mutations", {})[family] = dict(
                    first=bad["commit_records"][0], second=bad["commit_records"][1])
                self.assertEqual(bad["scientific_state"], original["scientific_state"])
                self.assertEqual(bad["lifecycle_digest"], original["lifecycle_digest"])
                with self.assertRaises(ValueError):
                    restore(bad)
                self.assertEqual(owner.snapshot(), original)

    def test_rg2b_historical_positive_clock_uses_its_frozen_duration(self) -> None:
        for candidate in ("C", "A"):
            with self.subTest(candidate=candidate):
                family = candidate + "_RG2b"
                inputs, _ = fixture(family)
                owner, original = self.two_commits(family)
                bad = deepcopy(original)
                first, second = (row["payload"] for row in bad["commit_records"])
                first["target_time"] = inputs.dt / 2
                expected = float(F(first["target_time"]) + F(inputs.dt))
                self.assertNotEqual(second["target_time"], expected)
                self.assertEqual(second["target_step_index"] - first["target_step_index"], 1)
                rehash_one_commit(bad, 0)
                AUDIT_EVIDENCE.setdefault("frozen_beat_mutations", {})[candidate] = dict(
                    first=bad["commit_records"][0], second=bad["commit_records"][1], expected_time=expected)
                with self.assertRaises(ValueError):
                    restore(bad)
                self.assertEqual(owner.snapshot(), original)

    def test_lawful_assignment_does_not_require_cross_operation_state_equality(self) -> None:
        for family in FAMILIES:
            with self.subTest(family=family):
                inputs, _ = fixture(family)
                owner = model(family)
                result = owner.step_v4_input(request(inputs.dt, "before-assignment"))
                self.assertTrue(result.committed, result.failure)
                previous_target = owner.snapshot()["commit_records"][-1]["payload"]["target_state_digest"]
                state = owner.state.lifecycle
                ledger = _ledger([r.to_dict() for r in state.receipt_ledger])
                assigned = replace(inputs, current=state.reset.authoritative,
                                   reset=state.reset.authoritative, dt=0,
                                   step_index=state.step_index, time=state.time,
                                   receipt_ids=tuple(r.receipt_id for r in ledger))
                owner.set_state(GRCV4State(_lifecycle_state(assigned, ledger)))
                current_identity = owner.state.lifecycle.scientific_state_digest
                self.assertNotEqual(current_identity, previous_target)
                zero = owner.step_v4_input(request(0, "after-unreceipted-assignment"))
                self.assertTrue(zero.committed, zero.failure)
                own_commit = owner.snapshot()["commit_records"][-1]["payload"]
                self.assertEqual(own_commit["source_state_digest"], own_commit["target_state_digest"])
                self.assertNotEqual(own_commit["source_state_digest"], previous_target)
                self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())

    def test_native_A_postwriter_singularity_preserves_the_seeded_publication(self) -> None:
        # Additional live-owner pressure; not a newly demonstrated defect.
        inputs, backend = a_os_fixture(C=(0.0, 0.0), W=(4.0,), dt=math.log(2.0),
                                      chi_A=1.0, zeta_A=3.0, tau_A=1.0,
                                      alpha=0.0, beta=0.0, gamma=0.0)
        owner = GRCV4(inputs, differential_reference=backend)
        self.assertTrue(owner.step_v4_input(request(0, "seed-ledger")).committed)
        owner.rebase_reset_baseline()
        snapshot = owner.snapshot()
        old = owner.state.lifecycle
        result = owner.step_v4_input(request(inputs.dt, "native-postwriter-singular"))
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage, "final_reconstruction")
        self.assertEqual(result.solver_disposition, "valid_root")
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertIs(owner.state.lifecycle, old)
        self.assertEqual(owner.snapshot(), snapshot)
        self.assertEqual(restore(snapshot).snapshot(), snapshot)
        AUDIT_EVIDENCE["A_native_rollback"] = dict(
            before=endpoint(snapshot), after=endpoint(owner.snapshot()),
            failure_stage=result.failure.stage, solver_disposition=result.solver_disposition,
            emitted_receipts=len(result.emitted_receipts))

    def test_rg2b_state_readmission_still_rejects_outside_core_current_and_reset(self) -> None:
        for candidate in ("C", "A"):
            with self.subTest(candidate=candidate):
                inputs, backend = fixture(candidate + "_RG2b")
                owner = model(candidate + "_RG2b")
                original = owner.snapshot()
                resource = list(inputs.current.C)
                resource[0] += 0.5
                resource[1] -= 0.5
                outside = replace(inputs.current, C=tuple(resource))
                for field in ("current", "reset"):
                    with self.assertRaises(ValueError):
                        GRCV4(replace(inputs, **{field: outside}), differential_reference=backend)
                    bad = deepcopy(original)
                    if field == "current":
                        bad["scientific_state"]["authoritative"]["C"] = resource
                    else:
                        bad["reset"]["authoritative"]["C"] = resource
                    rehash(bad)
                    with self.assertRaises(ValueError):
                        restore(bad)
                with self.assertRaises(ValueError):
                    owner.set_state(GRCV4State(_lifecycle_state(replace(inputs, current=outside), ())))
                self.assertEqual(owner.snapshot(), original)

    def test_rg2b_positive_clock_can_round_to_unchanged_time(self) -> None:
        # Both admitted scalar and graph frozen-completion parsers. Large
        # binary64 time absorbs a positive beat; the index must still advance.
        from tests.models.test_grc_v4_rg2b import fixture as scalar_fixture
        for geometry in ("scalar", "graph"):
            for candidate in ("C", "A"):
                with self.subTest(geometry=geometry, candidate=candidate):
                    inputs, backend = (scalar_fixture(candidate) if geometry == "scalar"
                                       else fixture(candidate + "_RG2b"))
                    inputs = replace(inputs, time=float(2**60))
                    owner = GRCV4(inputs, differential_reference=backend)
                    self.assertTrue(owner.step_v4_input(request(0, "large-clock-seed")).committed)
                    result = owner.step_v4_input(request(inputs.dt, "rounded-positive-beat"))
                    self.assertTrue(result.committed, result.failure)
                    self.assertEqual(owner.state.lifecycle.time, inputs.time)
                    self.assertEqual(owner.state.lifecycle.step_index, inputs.step_index + 1)
                    self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())
                    AUDIT_EVIDENCE.setdefault("rounded_positive_clock", {})[geometry + "_" + candidate] = endpoint(owner.snapshot())

    def test_non_OS_reconstruction_is_not_labeled_reference_geometry(self) -> None:
        for family in FAMILIES:
            if family.endswith("_OS"):
                continue
            with self.subTest(family=family):
                inputs, _ = fixture(family)
                owner = model(family)
                for dt in (0, inputs.dt):
                    result = owner.step_v4_input(request(dt, f"metadata-{dt}"))
                    self.assertTrue(result.committed, result.failure)
                    self.assertNotEqual(result.observables["reconstructed_current"]["stage"],
                                        "commit_reference_readmission")
                    if dt == 0:
                        self.assertNotEqual(result.observables["authoritative_current"]["stage"],
                                            "commit_reference_readmission")



if __name__ == "__main__":
    unittest.main()
