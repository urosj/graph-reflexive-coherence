"""P9-7.2a: actual source/target migration publication, not endpoint substitution."""

from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
import subprocess
import sys
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest
from pygrc.models.grc_v4_codec import canonical_json_bytes, MIGRATION_SNAPSHOT_LAYOUT_ID, payload_identity, V4IdentityError
from pygrc.models.grc_v4_geometry import GeometryDomainError
from pygrc.models.grc_v4_state import GRCV4State
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models import grc_v4_migration as migration_module
from pygrc.models.grc_v4_lifecycle import _state_inputs
from pygrc.models.grc_v4_migration import history_digest, migration_history_policy
from tests.models.test_grc_v4_generic_lifecycle import endpoint, restore
from tests.models.test_grc_v4_lifecycle import request, crossing_history
from tests.models.test_grc_v4_realizations import a_os_fixture, os_fixture
from tests.models.test_grc_v4_ci import fixture as ci_fixture
from tests.models.test_grc_v4_pc import fixture as pc_fixture
from tests.models.test_grc_v4_cipc import fixture as cipc_fixture
from tests.models.test_grc_v4_rg2b import fixture as rg_fixture
from tests.models.test_grc_v4_profile import reidentify
from pygrc.models.grc_v4_profile import resolve_profile

CASES = {
    "A_NH_NH": ("A_OS", "A_CI"), "C_NH_NH": ("C_OS", "C_CI"),
    "A_NH_PC": ("A_CI", "A_PC"), "C_NH_PC": ("C_CI", "C_PC"),
    "A_PC_NH": ("A_PC", "A_RG2b"), "C_PC_NH": ("C_PC", "C_RG2b"),
    "A_PC_CIPC": ("A_PC", "A_CI_PC"), "C_PC_CIPC": ("C_PC", "C_CI_PC"),
    "A_CIPC_PC": ("A_CI_PC", "A_PC"), "C_CIPC_PC": ("C_CI_PC", "C_PC"),
    "A_C_NH": ("A_OS", "C_OS"), "A_C_PC": ("A_PC", "C_PC"),
    "A_C_DROP": ("A_CI_PC", "C_CI"),
}
EVIDENCE = {}
AUDIT_EVIDENCE = {}


@lru_cache(maxsize=10)
def fixture(family):
    candidate, realization = family.split("_", 1)
    if realization == "OS":
        inputs, backend = a_os_fixture(C=(2.125, 1.875), W=(2.0,)) if candidate == "A" else (os_fixture(), None)
    else:
        inputs, backend = {"CI": ci_fixture, "PC": pc_fixture, "CI_PC": cipc_fixture,
                           "RG2b": rg_fixture}[realization](candidate, C=(2.125, 1.875), W=(2.0,))
    current = replace(inputs.current, C=(2.125, 1.875))
    if current.Z_4 is not None:
        current = replace(current, Z_4=(0.125,))
    reset = replace(current, C=(2.0625, 1.9375),
                    W_A=None if current.W_A is None else (1.9375,),
                    Z_4=None if current.Z_4 is None else (-0.0625,))
    inputs = replace(inputs, current=current, reset=reset, receipt_ids=())
    from pygrc.models.grc_v4_lifecycle import _fresh_geometry
    return _fresh_geometry(inputs), backend


def owner_for(source, target, *, source_inputs=None, target_ref=None, include_backend=True):
    inputs, backend = fixture(source)
    inputs = inputs if source_inputs is None else source_inputs
    target_inputs, target_backend = fixture(target)
    target_ref = target_inputs.geometry.reference if target_ref is None else target_ref
    extra = (() if not include_backend or target_backend is None
             or backend is not None and target_backend.identity == backend.identity else (target_backend,))
    return GRCV4(inputs, targets=(target_ref,), differential_reference=backend,
                 target_differential_references=extra), target_ref


def migration(owner, target, *, history=None, operation="migration"):
    inputs = _state_inputs(owner._operation.reference, owner.state.lifecycle)
    if history is None:
        if inputs.geometry.reference.profile.identity_payload.profile_family_id == target.profile.identity_payload.profile_family_id == "C_OS":
            history = crossing_history()
        else:
            history = migration_history_policy(inputs, target).to_payload()
    return GRCV4MigrationRequest.from_payload(dict(
        schema_version="grcv4-migration-request-v1", operation_id=operation,
        source_state_digest=inputs.scientific_state_id, target_profile_id=target.profile.complete_profile_id,
        migration_policy=dict(schema_version="grcv4-migration-policy-v1", policy_id="typed_bidirectional_profile_migration_v1",
                              resource_policy_id="identity_resource_transport_v1", target_readmission_policy_id="full_target_fail_closed_v1"),
        history_policy=history, target_context_value={}))


def changed_reference(ref, group, **changes):
    params, identity = ref.profile.params_resolved.to_payload(), ref.profile.identity_payload.to_payload()
    params[group].update(changes)
    reidentify(params, identity)
    return replace(ref, profile=resolve_profile(params, identity))


class MigrationTests(unittest.TestCase):
    def positive(self, case):
        source, target_family = CASES[case]
        inputs, backend = fixture(source)
        owner, target = owner_for(source, target_family)
        self.assertTrue(owner.step_v4_input(request(0, "seed-" + case)).committed)
        before = owner.snapshot()
        source_state = owner.state.lifecycle
        declared = migration(owner, target, operation=case)
        result = owner.migrate_profile(declared)
        self.assertTrue(result.committed, result.failure)
        after = owner.snapshot()
        state = owner.state.lifecycle
        self.assertEqual(after["implementation_layout_id"], MIGRATION_SNAPSHOT_LAYOUT_ID)
        self.assertEqual((state.step_index, state.time, state.Q_target),
                         (source_state.step_index, source_state.time, source_state.Q_target))
        self.assertEqual(state.current.C, source_state.current.C)
        self.assertEqual(state.reset.authoritative.C, source_state.reset.authoritative.C)
        keeps_w = target_family.startswith("A_")
        keeps_z = source.split("_", 1)[1] in ("PC", "CI_PC") and source[0] == target_family[0]
        has_z = target_family.split("_", 1)[1] in ("PC", "CI_PC")
        for old, new in ((source_state.current, state.current), (source_state.reset.authoritative, state.reset.authoritative)):
            self.assertEqual(new.W_A, old.W_A if keeps_w else None)
            self.assertEqual(new.Z_4, old.Z_4 if has_z and keeps_z else (0.0,) if has_z else None)
        history = result.emitted_receipts[0].identity_payload["history"]
        expected_losses = []
        for subject in ("candidate", "carrier"):
            policy = getattr(declared.history_policy, subject)
            self.assertEqual(history[subject]["source_history_digest"], history_digest(_state_inputs(inputs.geometry.reference, source_state), subject))
            self.assertEqual(history[subject]["target_history_digest"], history_digest(_state_inputs(target, state), subject))
            self.assertEqual(history[subject]["disposition"], policy.disposition)
            if policy.information_loss != "none":
                expected_losses.append(policy.information_loss)
        for row in result.emitted_receipts:
            self.assertEqual(list(row.identity_payload["core"]["information_losses"]), expected_losses)
            self.assertEqual(list(row.identity_payload["core"]["parent_receipt_ids"]), [before["receipt_ledger"][0]["receipt_id"]])
        self.assertEqual(restore(after).snapshot(), after)
        duplicate = owner.duplicate()
        with TemporaryDirectory(prefix="p972a-") as directory:
            path = Path(directory) / "migration.json"
            owner.save(str(path))
            self.assertEqual(path.read_bytes(), canonical_json_bytes(after))
            if case in ("A_C_PC", "C_PC_NH"):
                code = "from pygrc.models.grc_v4 import GRCV4; from pygrc.models.grc_v4_codec import canonical_json_bytes; import sys; sys.stdout.buffer.write(canonical_json_bytes(GRCV4.load(sys.argv[1]).snapshot()))"
                loaded = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True, check=True)
                self.assertEqual(loaded.stdout, path.read_bytes())
        owner.reset()
        self.assertEqual(owner.state.lifecycle.current, state.reset.authoritative)
        self.assertEqual(duplicate.snapshot(), after)
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())
        observed = duplicate.compute_observables()
        self.assertEqual(observed["candidate_id"], target_family[0])
        self.assertFalse(observed["authoritative_current"]["consumed_by_continuity"])
        continuation = duplicate.step_v4_input(request(fixture(target_family)[0].dt, "after-" + case))
        self.assertTrue(continuation.committed, continuation.failure)
        self.assertEqual(restore(duplicate.snapshot()).snapshot(), duplicate.snapshot())
        # Replay the actual migration request from the prior full publication.
        replay = restore(before)
        self.assertEqual(replay.migrate_profile(declared), result)
        self.assertEqual(replay.snapshot(), after)
        EVIDENCE[case] = dict(source_family=source, target_family=target_family,
            initial=inputs.to_payload(), differential_reference=None if backend is None else backend.to_payload(),
            target_reference=target.to_payload(), request=declared.to_payload(),
            before=endpoint(before), after=endpoint(after), reset=endpoint(owner.snapshot()),
            continuation=endpoint(duplicate.snapshot()),
            receipts=[r.to_payload() for r in result.emitted_receipts],
            accepted_G2=False, migration_class=case)

    def assert_rejected(self, owner, declaration, stage="admission", message=None):
        snapshot, live = owner.snapshot(), owner.state.lifecycle
        result = owner.migrate_profile(declaration)
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage, stage)
        if message is not None:
            self.assertIn(message, result.failure.message)
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertIs(owner.state.lifecycle, live)
        self.assertEqual(owner.snapshot(), snapshot)
        return result

    def test_C_to_A_initializer_is_unresolved_not_fabricated(self):
        for source, target_family in (("C_OS", "A_OS"), ("C_PC", "A_PC")):
            owner, target = owner_for(source, target_family)
            self.assertTrue(owner.step_v4_input(request(0, "existing-ledger")).committed)
            for fake_source in (None, "supplied_flux_is_not_source_authority"):
                bundle = crossing_history()
                bundle["candidate"].update(policy_id="graph_generic_A_history_free_v1", disposition="target_initializer", target_initializer_id=fake_source)
                self.assert_rejected(owner, migration(owner, target, history=bundle), message="initializer source")

    def test_unlisted_target_stale_source_context_and_history_substitution(self):
        owner, target = owner_for("A_PC", "C_PC")
        good = migration(owner, target).to_payload()
        mutations = []
        for field, value in (("source_state_digest", "grcv4-state-sha256:" + "0"*64),
                             ("target_profile_id", fixture("C_OS")[0].geometry.reference.profile.complete_profile_id),
                             ("target_context_value", {"external": 1})):
            bad = deepcopy(good)
            bad[field] = value
            mutations.append(bad)
        for subject in ("candidate", "carrier"):
            for field, value in (("source_history_digest", None), ("information_loss", "none"),
                                 ("policy_id", "unresolved-policy"), ("target_initializer_id", "unresolved-initializer")):
                bad = deepcopy(good)
                bad["history_policy"][subject][field] = value
                mutations.append(bad)
        # A live-only hash must not be accepted in place of both history halves.
        bad = deepcopy(good)
        bad["history_policy"]["candidate"]["source_history_digest"] = payload_identity("history_content_identity_payload", dict(
            schema_version="grcv4-history-content-identity-v1", subject="candidate", content=[2.0]))
        mutations.append(bad)
        for bad in mutations:
            with self.subTest(mutation=bad):
                self.assert_rejected(owner, GRCV4MigrationRequest.from_payload(bad))

    def test_reset_only_target_failure_is_atomic(self):
        inputs, _ = fixture("A_OS")
        inputs = replace(inputs, reset=replace(inputs.reset, W_A=(3.0,)))
        owner, target = owner_for("A_OS", "A_PC", source_inputs=inputs)
        self.assertTrue(owner.step_v4_input(request(0, "seed-reset-negative")).committed)
        self.assert_rejected(owner, migration(owner, target), "target_readmission")

    def test_missing_target_differential_recipe_is_typed_and_atomic(self):
        target = fixture("A_CI")[0].geometry.reference
        identity = target.profile.params_resolved.candidate.descriptor_backend_id
        target = changed_reference(target, "candidate", descriptor_backend_id=identity.rsplit(":", 1)[0] + ":" + "0"*64)
        owner, target = owner_for("A_OS", "A_CI", target_ref=target, include_backend=False)
        self.assert_rejected(owner, migration(owner, target), "target_readmission", "registered differential")

    def test_target_geometry_failure_before_readmission_is_atomic(self):
        from pygrc.models.grc_v4_geometry import GeometryDomainError
        owner, target = owner_for("A_CI_PC", "A_PC")
        declaration = migration(owner, target)
        # Exercise the earlier construction boundary, not only target-root
        # admission. The full current/reset publication must remain untouched.
        with patch("pygrc.models.grc_v4_pc.carrier_geometry", side_effect=GeometryDomainError("target geometry outside SPD domain")):
            self.assert_rejected(owner, declaration, "target_construction", "SPD domain")

    def test_carrier_preservation_checks_exact_contract_before_target_root(self):
        inputs, _ = fixture("A_PC")
        target = fixture("A_CI_PC")[0].geometry.reference
        good_owner, good_target = owner_for("A_PC", "A_CI_PC")
        good_history = migration(good_owner, good_target).history_policy.to_payload()
        for group, values in (("realization", {"tau_PC": 1.0}), ("realization", {"radius": 32.0}),
                              ("geometry", {"kappa_H": 2e-5}), ("candidate", {"gamma": 0.2})):
            bad_target = changed_reference(target, group, **values)
            owner, ref = owner_for("A_PC", "A_CI_PC", source_inputs=inputs, target_ref=bad_target)
            self.assert_rejected(owner, migration(owner, ref, history=good_history), message="exact carrier")

    def test_late_failure_does_not_swap_reference_backend_or_archive(self):
        for pair in (("A_PC", "C_PC"), ("A_PC", "A_CI_PC")):
            owner, target = owner_for(*pair)
            before = owner.snapshot()
            backend = owner._operation._backend
            with patch("pygrc.models.grc_v4_lifecycle._validate_publication", side_effect=RuntimeError("late publication fault")):
                with self.assertRaisesRegex(RuntimeError, "late publication fault"):
                    owner.migrate_profile(migration(owner, target))
            self.assertIs(owner._operation._backend, backend)
            self.assertEqual(owner.snapshot(), before)

    def test_core_state_migration_readmission_does_not_require_another_RG_beat(self):
        for candidate in ("C", "A"):
            inputs, _ = fixture(candidate + "_PC")
            inputs = replace(inputs, current=replace(inputs.current, C=(2.375, 1.625)))
            owner, target = owner_for(candidate + "_PC", candidate + "_RG2b", source_inputs=inputs)
            self.assertTrue(owner.migrate_profile(migration(owner, target)).committed)
            before = owner.snapshot()
            self.assertEqual(restore(before).snapshot(), before)
            owner.compute_observables()
            result = owner.step_v4_input(request(fixture(candidate + "_RG2b")[0].dt, "outside-inner"))
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.stage, "pre_read_reconstruction")
            self.assertEqual(owner.snapshot(), before)
            owner.reset()

    def test_archive_and_backend_substitution_and_no_event_generalization(self):
        owner, target = owner_for("A_PC", "C_PC")
        self.assertTrue(owner.migrate_profile(migration(owner, target)).committed)
        original = owner.snapshot()
        for mutation in ("backend", "target", "reset", "history", "event"):
            bad = deepcopy(original)
            row = bad["transition_records"][0]
            if mutation == "backend":
                bad["differential_reference_registry"] = []
            elif mutation == "target":
                row["target"]["authoritative"]["Z_4"] = [0.125]
            elif mutation == "reset":
                row["target_reset"]["authoritative"]["Z_4"] = [-0.0625]
                row["target"]["reset_digest"] = payload_identity("grcv4_reset_payload", row["target_reset"])
            elif mutation == "history":
                row["request"]["history_policy"]["candidate"]["information_loss"] = "none"
            else:
                row["request"]["schema_version"] = "grcv4-mapped-topology-event-request-v1"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                restore(bad)
        from tests.models.test_grc_v4_lifecycle import event_request
        event = event_request(owner._operation, target, [1, 0, 0, 1], [0, 0])
        result = owner.apply_topology_event(event)
        self.assertFalse(result.committed)
        self.assertEqual(owner.snapshot(), original)
        self.assertNotIn("typed_topology_events", owner.list_capabilities())


for _case in CASES:
    def _positive(self, case=_case):
        self.positive(case)
    setattr(MigrationTests, "test_positive_" + _case, _positive)


def audit_identity(prefix: str, payload: Any) -> str:
    """Hash hostile bytes without scientific or relationship validation."""
    return prefix + ":" + sha256(canonical_json_bytes(payload)).hexdigest()


def rehash_receipt_chain(snapshot: dict[str, Any]) -> None:
    """Rehash a structurally intact ledger after changing receipt core claims.

    Commit-group sizes and original order are retained. Historical primary
    references are redirected to their rehashed IDs; no state preimage changes.
    """
    receipt_replacements: dict[str, str] = {}
    commit_replacements: dict[str, str] = {}
    position = 0
    for record in snapshot["commit_records"]:
        old_commit_id = record["commit_id"]
        payload = record["payload"]
        count = len(payload["emitted_receipt_ids"])
        group = snapshot["receipt_ledger"][position:position + count]
        if len(group) != count:
            raise AssertionError("reproducer requires an intact ledger partition")
        for row in group:
            old_receipt_id = row["receipt_id"]
            core = row["identity_payload"]["core"]
            core["parent_receipt_ids"] = [
                receipt_replacements.get(parent, parent)
                for parent in core["parent_receipt_ids"]
            ]
            row["receipt_id"] = audit_identity("grc-receipt-sha256", row["identity_payload"])
            receipt_replacements[old_receipt_id] = row["receipt_id"]
        payload["emitted_receipt_ids"] = [row["receipt_id"] for row in group]
        record["commit_id"] = audit_identity("grc-commit-sha256", payload)
        commit_replacements[old_commit_id] = record["commit_id"]
        for row in group:
            row["commit_id"] = record["commit_id"]
        position += count
    if position != len(snapshot["receipt_ledger"]):
        raise AssertionError("reproducer left uncovered receipts")
    for archive in snapshot["transition_records"]:
        archive["commit_id"] = commit_replacements.get(archive["commit_id"], archive["commit_id"])
    snapshot["lifecycle"]["receipt_ids"] = [row["receipt_id"] for row in snapshot["receipt_ledger"]]
    snapshot["lifecycle_digest"] = audit_identity("grcv4-lifecycle-sha256", snapshot["lifecycle"])


class P972aAuditRegressions(unittest.TestCase):
    """Seven auditor proposals plus native prospective/identity/type pressure."""
    def _seeded(self, source: str = "A_OS", target: str = "A_CI") -> tuple[Any, Any]:
        owner, reference = owner_for(source, target)
        result = owner.step_v4_input(request(0, "audit-seed"))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(len(owner.snapshot()["receipt_ledger"]), 4)
        return owner, reference

    def _unchanged(self, owner: Any, publication: Any, snapshot: dict[str, Any]) -> None:
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual(owner.snapshot(), snapshot)

    def test_programmer_mapper_exceptions_propagate_without_failure_result(self) -> None:
        for error_type in (ValueError, V4IdentityError, RuntimeError):
            with self.subTest(error_type=error_type.__name__):
                owner, target = self._seeded()
                declaration = migration(owner, target, operation="audit-map-fault")
                old, snapshot = owner._operation._owned, owner.snapshot()
                error = error_type("explicit programmer/invariant fault")
                try:
                    with patch.object(migration_module, "map_migration", side_effect=error):
                        with self.assertRaises(error_type) as caught:
                            owner.migrate_profile(declaration)
                        self.assertIs(caught.exception, error)
                finally:
                    self._unchanged(owner, old, snapshot)

    def _readmission_fault(self, source: bool) -> None:
        for error_type in (ValueError, V4IdentityError, RuntimeError):
            with self.subTest(source=source, error_type=error_type.__name__):
                owner, target = self._seeded()
                declaration = migration(owner, target, operation="audit-read-fault")
                old, snapshot = owner._operation._owned, owner.snapshot()
                source_id = owner.active_profile_id
                real = lifecycle._readmit_state
                error = error_type("explicit programmer/invariant fault")

                def fail_selected(inputs: Any, backend: Any) -> Any:
                    is_source = inputs.geometry.reference.profile.complete_profile_id == source_id
                    if is_source == source:
                        raise error
                    return real(inputs, backend)

                try:
                    with patch.object(lifecycle, "_readmit_state", side_effect=fail_selected):
                        with self.assertRaises(error_type) as caught:
                            owner.migrate_profile(declaration)
                        self.assertIs(caught.exception, error)
                finally:
                    self._unchanged(owner, old, snapshot)

    def test_programmer_source_readmission_exceptions_propagate(self) -> None:
        self._readmission_fault(True)

    def test_programmer_target_readmission_exceptions_propagate(self) -> None:
        self._readmission_fault(False)

    def test_typed_geometry_failure_remains_atomic_noncommitted_result(self) -> None:
        owner, target = self._seeded("A_CI_PC", "A_PC")
        declaration = migration(owner, target, operation="audit-typed-geometry")
        old, snapshot = owner._operation._owned, owner.snapshot()
        with patch("pygrc.models.grc_v4_pc.carrier_geometry",
                   side_effect=GeometryDomainError("explicit semantic geometry-domain control")):
            result = owner.migrate_profile(declaration)
        self.assertFalse(result.committed)
        self.assertIsNotNone(result.failure)
        self.assertEqual(result.failure.stage, "target_construction")
        self.assertIsNone(result.failure.solver_disposition)
        self.assertEqual(len(result.emitted_receipts), 1)
        self._unchanged(owner, old, snapshot)

    def test_archived_preimage_contradiction_rejects_after_complete_rehash(self) -> None:
        for source, destination in (("A_PC", "C_PC"), ("C_OS", "C_CI")):
            with self.subTest(source=source, destination=destination):
                owner, target = self._seeded(source, destination)
                result = owner.migrate_profile(migration(owner, target, operation="audit-cross"))
                self.assertTrue(result.committed, result.failure)
                original = owner.snapshot()
                self.assertEqual(restore(original).snapshot(), original)
                unchanged = deepcopy(original)
                rehash_receipt_chain(unchanged)
                self.assertEqual(unchanged, original)

                bad = deepcopy(original)
                false_authority = "grcv4-authoritative-sha256:" + "0" * 64
                for row in bad["receipt_ledger"][:4]:
                    core = row["identity_payload"]["core"]
                    core["source_authoritative_digest"] = false_authority
                    core["target_authoritative_digest"] = false_authority
                rehash_receipt_chain(bad)
                archived_source = bad["transition_records"][0]["source"]
                science = audit_identity("grcv4-state-sha256", archived_source)
                real_authority = audit_identity("grcv4-authoritative-sha256", {
                    "schema_version": "grcv4-authoritative-state-identity-v1",
                    "authoritative": archived_source["authoritative"],
                })
                first = bad["receipt_ledger"][0]["identity_payload"]["core"]
                crossing = bad["receipt_ledger"][4]["identity_payload"]["core"]
                self.assertEqual(first["target_state_digest"], science)
                self.assertEqual(crossing["source_state_digest"], science)
                self.assertNotEqual(first["target_authoritative_digest"], real_authority)
                self.assertEqual(crossing["source_authoritative_digest"], real_authority)
                self.assertEqual(bad["scientific_state"], original["scientific_state"])
                self.assertEqual(bad["reset"], original["reset"])
                with self.assertRaises(ValueError):
                    restore(bad)
                self.assertEqual(owner.snapshot(), original)
                AUDIT_EVIDENCE[source + "_archived_contradiction"] = dict(
                    original=endpoint(original), mutated=endpoint(bad),
                    false_authority=false_authority, known_authority=real_authority,
                    state_identity=science, rejected=True)

    def test_lawful_assignment_does_not_require_historical_state_adjacency(self) -> None:
        owner, target = self._seeded("C_OS", "C_CI")
        before = owner.snapshot()
        state = owner.state.lifecycle
        inputs = lifecycle._state_inputs(owner._operation.reference, state)
        # Same charge, new current only; preserve reset and existing ledger.
        assigned = replace(inputs, current=replace(inputs.current, C=(1.875, 2.125)))
        ledger = lifecycle._ledger([row.to_dict() for row in state.receipt_ledger])
        owner.set_state(GRCV4State(lifecycle._lifecycle_state(assigned, ledger)))
        self.assertNotEqual(owner.state.lifecycle.scientific_state_digest,
                            before["commit_records"][-1]["payload"]["target_state_digest"])
        self.assertEqual(owner.snapshot()["receipt_ledger"], before["receipt_ledger"])
        result = owner.migrate_profile(migration(owner, target, operation="after-assignment"))
        self.assertTrue(result.committed, result.failure)
        snapshot = owner.snapshot()
        self.assertEqual(restore(snapshot).snapshot(), snapshot)
        AUDIT_EVIDENCE["lawful_assignment"] = dict(before=endpoint(before), after=endpoint(snapshot))

    def test_distinct_A_backend_is_selected_and_old_recipe_remains_archived(self) -> None:
        inputs, original_backend = fixture("A_OS")
        self.assertIsNotNone(original_backend)
        new_backend = replace(original_backend,
                              regularization=2 * original_backend.regularization)
        target = changed_reference(fixture("A_CI")[0].geometry.reference,
                                   "candidate", descriptor_backend_id=new_backend.identity)
        owner = GRCV4(inputs, targets=(target,), differential_reference=original_backend,
                      target_differential_references=(new_backend,))
        self.assertTrue(owner.step_v4_input(request(0, "backend-seed")).committed)
        result = owner.migrate_profile(migration(owner, target, operation="backend-change"))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner._operation._backend.identity, new_backend.identity)
        self.assertNotEqual(new_backend.identity, original_backend.identity)
        snapshot = owner.snapshot()
        self.assertEqual(len(snapshot["differential_reference_registry"]), 2)
        self.assertEqual(restore(snapshot).snapshot(), snapshot)
        # Source numerical reconstruction still needs the OLD recipe after migration.
        bad = deepcopy(snapshot)
        bad["differential_reference_registry"] = [new_backend.to_payload()]
        with self.assertRaises(ValueError):
            restore(bad)
        continuation = owner.step_v4_input(request(fixture("A_CI")[0].dt, "new-backend-step"))
        self.assertTrue(continuation.committed, continuation.failure)
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())
        AUDIT_EVIDENCE["distinct_backend"] = dict(
            original=original_backend.to_payload(), target=new_backend.to_payload(),
            migrated=endpoint(snapshot), continuation=endpoint(owner.snapshot()))

    def test_typed_declaration_and_readmission_failures_remain_semantic(self):
        owner, target = self._seeded()
        declaration = migration(owner, target)
        old, snapshot = owner._operation._owned, owner.snapshot()
        real = lifecycle._readmit_state
        for source in (True, False):
            def fail_selected(inputs, backend):
                if (inputs.geometry.reference == old.reference) == source:
                    raise GeometryDomainError("typed readmission control")
                return real(inputs, backend)
            with patch.object(lifecycle, "_readmit_state", side_effect=fail_selected):
                result = owner.migrate_profile(declaration)
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.stage, "pre_read_reconstruction" if source else "target_readmission")
            self.assertEqual(len(result.emitted_receipts), 1)
            self._unchanged(owner, old, snapshot)
        for family, group, values in (("A_CI", "common", {"gauge_id": "unsupported_gauge_v1"}),
                                      ("A_CI", "candidate", {"site_potential_id": "unsupported_potential_v1"}),
                                      ("A_OS", "realization", {"split_residual_norm_id": "unsupported_norm_v1"})):
            ref = fixture(family)[0].geometry.reference
            params, identity = ref.profile.params_resolved.to_payload(), ref.profile.identity_payload.to_payload()
            params[group].update(values)
            if group == "common":
                identity.update(values)
            reidentify(params, identity)
            ref = replace(ref, profile=resolve_profile(params, identity))
            owner, ref = owner_for("A_OS", family, target_ref=ref)
            old, snapshot = owner._operation._owned, owner.snapshot()
            result = owner.migrate_profile(migration(owner, ref))
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.stage, "target_readmission")
            self._unchanged(owner, old, snapshot)
        # Generic identity faults from lookup itself must not inherit the
        # explicit missing/mismatched-backend admission classification.
        owner, target = self._seeded()
        old, snapshot = owner._operation._owned, owner.snapshot()
        error = V4IdentityError("backend lookup invariant fault")
        with patch.object(lifecycle, "_backend_for", side_effect=error):
            with self.assertRaises(V4IdentityError) as caught:
                owner.migrate_profile(migration(owner, target))
        self.assertIs(caught.exception, error)
        self._unchanged(owner, old, snapshot)

    def test_known_preimages_bind_every_component_and_commit_clock(self):
        owner, _ = self._seeded("C_OS", "C_CI")
        snapshot = owner.snapshot()
        science = snapshot["scientific_state"]
        ledger = lifecycle._ledger(snapshot["receipt_ledger"])
        commits = owner._operation._owned.commits
        check = lifecycle._validate_scientific_commitments
        check(ledger, commits, (science,))
        for prefix in ("source", "target"):
            for field in ("graph_digest", "model_identity", "authoritative_digest", "reset_digest"):
                rows = deepcopy(snapshot["receipt_ledger"])
                key = prefix + "_" + field
                value = rows[0]["identity_payload"]["core"][key]
                for row in rows:
                    row["identity_payload"]["core"][key] = value.rsplit(":", 1)[0] + ":" + "0"*64
                    row["receipt_id"] = audit_identity("grc-receipt-sha256", row["identity_payload"])
                with self.subTest(prefix=prefix, component=field), self.assertRaises(V4IdentityError):
                    check(lifecycle._ledger(rows), commits, (science,))
        for changes in ({"target_time": 1.0}, {"target_step_index": 1}):
            with self.subTest(clock=changes), self.assertRaises(V4IdentityError):
                check(ledger, (replace(commits[0], **changes),), (science,))

    def test_repeated_unknown_state_claims_are_consistent_without_adjacency(self):
        owner, target = self._seeded("C_OS", "C_CI")
        self.assertTrue(owner.step_v4_input(request(0, "same-unknown-state")).committed)
        old_state = owner.state.lifecycle.scientific_state_digest
        state = owner.state.lifecycle
        inputs = lifecycle._state_inputs(owner._operation.reference, state)
        assigned = replace(inputs, current=replace(inputs.current, C=(1.875, 2.125)))
        owner.set_state(GRCV4State(lifecycle._lifecycle_state(
            assigned, lifecycle._ledger([r.to_dict() for r in state.receipt_ledger]))))
        self.assertTrue(owner.migrate_profile(migration(owner, target)).committed)
        original = owner.snapshot()
        self.assertNotEqual(old_state, original["scientific_state_digest"])
        self.assertNotEqual(old_state, original["transition_records"][0]["request"]["source_state_digest"])
        self.assertEqual(restore(original).snapshot(), original)
        bad = deepcopy(original)
        for row in bad["receipt_ledger"][:4]:
            for prefix in ("source", "target"):
                row["identity_payload"]["core"][prefix + "_authoritative_digest"] = "grcv4-authoritative-sha256:" + "0"*64
        rehash_receipt_chain(bad)
        with self.assertRaises(V4IdentityError):
            restore(bad)
        # All claims for an unavailable historical preimage may be internally
        # consistent without being externally authenticated. Preserve that ceiling.
        for row in bad["receipt_ledger"][4:8]:
            for prefix in ("source", "target"):
                row["identity_payload"]["core"][prefix + "_authoritative_digest"] = "grcv4-authoritative-sha256:" + "0"*64
        rehash_receipt_chain(bad)
        self.assertEqual(restore(bad).snapshot(), bad)
        AUDIT_EVIDENCE["unknown_history_ceiling"] = dict(
            original=endpoint(original), consistent_unattested=endpoint(bad),
            inconsistent_rejected=True, external_execution_authenticated=False)

    def test_prospective_ledger_rejects_known_state_contradiction_atomically(self):
        owner, target = self._seeded("C_OS", "C_CI")
        bad = owner.snapshot()
        for row in bad["receipt_ledger"]:
            for prefix in ("source", "target"):
                row["identity_payload"]["core"][prefix + "_authoritative_digest"] = "grcv4-authoritative-sha256:" + "0"*64
        rehash_receipt_chain(bad)
        owned = owner._operation._owned
        inputs = lifecycle._state_inputs(owned.reference, owned.state)
        # Deliberate internal fault injection, not a supported state-import path.
        owner._operation._owned = replace(owned,
            state=lifecycle._lifecycle_state(inputs, lifecycle._ledger(bad["receipt_ledger"])),
            commits=tuple(lifecycle.CommitPayload.from_payload(r["payload"]) for r in bad["commit_records"]))
        old, snapshot = owner._operation._owned, owner.snapshot()
        with self.assertRaisesRegex(V4IdentityError, "commitments"):
            owner.migrate_profile(migration(owner, target))
        self._unchanged(owner, old, snapshot)


if __name__ == "__main__":
    unittest.main()
