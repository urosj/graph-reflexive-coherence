"""Owner-boundary pressure and measured replay, without widening execution scope."""

from dataclasses import FrozenInstanceError, replace
import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from pygrc.models import GRC9V4
from pygrc.models import grc_9_v4_api_lifecycle as public
from pygrc.models import grc_9_v4_lifecycle as events
from pygrc.models import grc_9_v4_owner as enabled
from pygrc.models import grc_9_v4_crossing as crossing
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from pygrc.models.grc_v4_certification import numerical_policy, NumericalPolicy
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_exact import exact_backend, ExactBackend
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_9_v4 import configuration, seed, step_request

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = {}
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")


def request(family):
    action = next(a for a in seed(family)["journal"] if a["kind"] == "expand")
    return GRC9V4ExpansionRequestInput.from_payload(action["request"])


def state(family):
    return enabled._decode_state(configuration(family)["initial"], family)


def predecessor():
    """Load the committed event receiver in memory; no temporary code or patches."""
    name = "pygrc.models._p994b_event_predecessor"
    source = subprocess.check_output(
        ["git", "show", "7b16696a:src/pygrc/models/grc_9_v4_lifecycle.py"], cwd=ROOT
    )
    spec = importlib.util.spec_from_loader(name, loader=None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    module._source = source
    exec(compile(source, "<committed-event-predecessor>", "exec"), module.__dict__)
    return module


class ArchitectureTests(unittest.TestCase):
    def test_execution_selection_is_independent(self):
        expected = GRC9V4.execution_scope()
        self.assertIn("A_RG2b", expected)
        restricted = tuple(f for f in expected if f != "A_RG2b")
        # Synthetic selection tests the registration/authorization distinction;
        # it does not claim the now-accepted A_RG2b owner is unavailable.
        with patch.object(public, "PUBLIC_ENABLED_FAMILIES", restricted), patch.dict(
            enabled._OWNERS, A_RG2b=events.GRC9V4ARG2bOperation
        ):
            self.assertEqual(GRC9V4.execution_scope(), restricted)
            with self.assertRaises(public.GRC9V4ExecutionUnavailable):
                public.GRC9V4PublicOperation.require_execution("A_RG2b")
        with patch.dict(enabled._OWNERS, {}, clear=True):
            with self.assertRaises(RuntimeError):
                GRC9V4.execution_scope()
        EVIDENCE["execution_selection"] = dict(
            registered_owner_does_not_enable=True,
            missing_selected_owner_rejects=True,
            execution_families=list(expected),
        )

    def test_all_ten_dispatch_preserves_closed_scientific_handlers(self):
        old = predecessor()
        import inspect
        import ast

        old_nodes = {getattr(n, "name", None): n for n in ast.parse(old._source).body}
        rows = []
        for family, implementation in events._FAMILY_IMPLEMENTATIONS.items():
            # This is routing pressure only. No admission/numerical claim is
            # made for the five unselected public execution families.
            candidate = object.__new__(implementation.state_type)
            inputs = SimpleNamespace(
                geometry=SimpleNamespace(reference=object()),
                current=object(),
                reset=object(),
            )
            object.__setattr__(candidate, "inputs", inputs)
            names = {
                "C_OS": "_cos_readmit",
                "C_PC": "_cpc_readmit",
                "C_CI": "_cci_readmit",
                "C_CI_PC": "_cci_readmit",
                "C_RG2b": "_crg2b_readmit",
                "A_OS": "_aos_readmit",
                "A_CI": "_aci_readmit",
                "A_CI_PC": "_aci_readmit",
                "A_PC": "_apc_readmit",
                "A_RG2b": "_arg2b_readmit",
            }
            self.assertEqual(implementation.readmit.__name__, names[family])
            self.assertEqual(implementation.candidate, family[0])
            self.assertEqual(
                implementation.persistent,
                family in ("C_PC", "C_CI_PC", "A_PC", "A_CI_PC"),
            )
            self.assertEqual(
                implementation.retains_reference_currents,
                family not in ("C_OS", "C_PC"),
            )
            reader = Mock(return_value="selected-role-reads")
            builder = Mock(return_value="target")
            adapted = replace(implementation, readmit=reader, expansion_type=builder)
            with patch.dict(events._FAMILY_IMPLEMENTATIONS, {family: adapted}):
                self.assertEqual(
                    events._event_readmit(candidate), "selected-role-reads"
                )
                reader.assert_called_once_with(candidate)
                self.assertEqual(adapted.build_target("plan", candidate), "target")
                args = ("plan", inputs.geometry.reference)
                if family.startswith("A_") or family in ("C_PC", "C_CI_PC"):
                    args += (inputs.current, inputs.reset)
                builder.assert_called_once_with(*args)
            # The old selected readmission function's code remains identical.
            self.assertEqual(
                ast.dump(ast.parse(inspect.getsource(implementation.readmit)).body[0]),
                ast.dump(old_nodes[names[family]]),
            )
            subclass = type("UnacceptedSubclass", (implementation.state_type,), {})
            with self.assertRaises(TypeError):
                events.family_implementation(object.__new__(subclass))
            rows.append(family)
        self.assertEqual(
            set(rows),
            {c + "_" + r for c in "AC" for r in ("OS", "CI", "PC", "CI_PC", "RG2b")},
        )
        EVIDENCE["dispatch"] = dict(
            families=sorted(rows),
            exact_type_rejection=True,
            routing_only_for_unselected=True,
        )

    def test_transition_preserves_artifact_prefix_and_never_publishes(self):
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.LEGACY_EXACT),
        ):
            owner = enabled.GRC9V4EnabledOperation(state("A_PC"))
            self.assertTrue(owner.step_v4(step_request("mixed-prefix", 0)).committed)
            markers = events.GRC9V4EventArtifacts(
                (FrozenJSONMap({"test_prefix": "archive"}),),
                (FrozenJSONMap({"test_prefix": "reference"}),),
            )
            owner._published = replace(owner._published, artifacts=markers)
            before = owner._published
            context = events.GRC9V4ExpansionContext(
                before.state, before.receipts, markers
            )
            transition = events.prepare_expansion(context, request("A_PC"))
            self.assertTrue(transition.result.committed, transition.result.failure)
            self.assertIs(owner._published, before)
            self.assertEqual(transition.artifacts.archives[:1], markers.archives)
            self.assertEqual(
                transition.artifacts.reference_currents[:1], markers.reference_currents
            )
            self.assertEqual(len(transition.artifacts.archives), 2)
            self.assertEqual(len(transition.artifacts.reference_currents), 2)
            for key in ("archives", "reference_currents"):
                with self.assertRaises(ValueError):
                    replace(
                        transition, artifacts=replace(transition.artifacts, **{key: ()})
                    )
            with patch.object(events, "prepare_expansion", return_value=transition):
                self.assertTrue(owner.expand(request("A_PC")).committed)
            self.assertIs(owner._published.artifacts, transition.artifacts)
        EVIDENCE["artifact_transfer"] = dict(
            complete_bundle_preserved=True,
            dropped_prefix_rejected=True,
            preparation_has_no_publication=True,
        )

    def test_rejection_and_late_failure_keep_whole_publication(self):
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.LEGACY_EXACT),
        ):
            owner = enabled.GRC9V4EnabledOperation(state("C_OS"))
            before = owner._published
            bad = replace(
                request("C_OS"),
                source_state_digest=request("C_OS").source_state_digest[:-64]
                + "0" * 64,
            )
            result = owner.expand(bad)
            self.assertFalse(result.committed)
            self.assertIs(owner._published, before)
            with patch.object(
                owner, "_publish", side_effect=RuntimeError("late-publication")
            ):
                with self.assertRaisesRegex(RuntimeError, "late-publication"):
                    owner.expand(request("C_OS"))
            self.assertIs(owner._published, before)
        EVIDENCE["rollback"] = dict(
            rejection=True, late_failure=True, whole_publication_unchanged=True
        )

    def test_predecessor_event_checkpoint_bytes_match(self):
        old = predecessor()
        rows = []
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.LEGACY_EXACT),
        ):
            for family in FAMILIES:
                current = state(family)
                operation = enabled._OWNERS[family]
                previous_type = getattr(old, operation.STATE.__name__)
                previous_spec = old.GRC9V4Specialization(
                    current.specialization.resolved,
                    current.specialization.identity_payload,
                )
                previous = getattr(old, operation.__name__)(
                    previous_type(current.inputs, previous_spec)
                )
                following = operation(current)
                first = previous.expand(request(family))
                second = following.expand(request(family))
                self.assertTrue(first.committed, first.failure)
                self.assertEqual(first.to_payload(), second.to_payload())
                self.assertEqual(previous.checkpoint(), following.checkpoint())
                rows.append(family)
        EVIDENCE["event_predecessor_parity"] = dict(
            families=rows,
            results_and_checkpoint_bytes_equal=True,
            predecessor_commit="7b16696a",
        )

    def test_accepted_mixed_checkpoints_replay_unchanged(self):
        rows = []
        for family in FAMILIES:
            raw = canonical_json_bytes(seed(family))
            owner = enabled.GRC9V4EnabledOperation.from_state(raw)
            self.assertEqual(owner.snapshot(), raw)
            rows.append(family)
        EVIDENCE["accepted_replay"] = dict(
            families=rows,
            checkpoint_bytes_equal=True,
            accepted_execution_records_unchanged=True,
        )

    def test_public_replay_counts_and_bounded_cost(self):
        counts = {"ordinary": 0, "expansion": 0}
        step = enabled._prepare_step
        expansion = events.prepare_expansion

        def ordinary(*args, **kwargs):
            counts["ordinary"] += 1
            return step(*args, **kwargs)

        def expand(*args, **kwargs):
            counts["expansion"] += 1
            return expansion(*args, **kwargs)

        start = time.perf_counter()
        model = GRC9V4.from_config(configuration("C_OS"))
        construction = time.perf_counter() - start
        start = time.perf_counter()
        self.assertTrue(model.step_v4_input(step_request("zero", 0)).committed)
        self.assertTrue(model.expand(request("C_OS")).committed)
        self.assertTrue(model.step_v4_input(step_request("positive")).committed)
        forward = time.perf_counter() - start
        snapshot = model.snapshot()
        with (
            patch.object(enabled, "_prepare_step", ordinary),
            patch.object(events, "prepare_expansion", expand),
            patch.object(
                events._GRC9V4EventOperation,
                "replay",
                side_effect=AssertionError("nested event replay"),
            ),
        ):
            start = time.perf_counter()
            restored = GRC9V4.from_state(snapshot)
            loading = time.perf_counter() - start
        self.assertEqual(counts, dict(ordinary=2, expansion=1))
        self.assertEqual(restored.snapshot(), snapshot)
        EVIDENCE["replay_assessment"] = dict(
            family="C_OS",
            construction_seconds=construction,
            forward_seconds=forward,
            load_seconds=loading,
            outer_actions=len(snapshot["owner"]["journal"]),
            initial_prefix_actions=len(snapshot["owner"]["initial"]["journal"]),
            executed_actions=counts,
            standalone_event_checkpoint_replays=0,
            scope="one_small_three_action_case_not_a_scaling_benchmark",
            decision="retain_checkpoint_layouts; revisit_single_owner_single_journal_after_all_ten_enabled",
        )

    def test_branch_owns_the_only_ledger_and_artifact_bundle(self):
        model = GRC9V4.from_config(configuration("A_PC"))
        operation = model._operation
        first = operation._published
        self.assertIs(type(first.owner), enabled.GRC9V4EnabledBranch)
        self.assertFalse(hasattr(first.owner, "receipts"))
        self.assertFalse(hasattr(first.owner, "_published"))
        with self.assertRaises(FrozenInstanceError):
            first.owner.state = None
        prepared = []
        original = enabled.prepare_enabled

        def capture(*args, **kwargs):
            transition = original(*args, **kwargs)
            prepared.append(transition)
            return transition

        with (
            patch.object(enabled, "prepare_enabled", capture),
            patch.object(
                enabled.GRC9V4EnabledOperation,
                "__init__",
                side_effect=AssertionError("nested enabled owner"),
            ),
        ):
            self.assertTrue(
                model.step_v4_input(step_request("single-owner", 0)).committed
            )
            before = operation._published
            result = model.expand(request("A_PC"))
            self.assertTrue(result.committed)
            publication = operation._published
            self.assertIs(publication.artifacts, prepared[-1].artifacts)
            self.assertEqual(
                publication.receipts, before.receipts + result.emitted_receipts
            )
            self.assertEqual(len(publication.archives), 1)
            self.assertEqual(len(publication.initializations), 1)
            artifacts = publication.artifacts
            model.rebase_reset_baseline()
            model.reset()
            self.assertIs(operation._published.artifacts, artifacts)
            rejected = model.step_v4_input(step_request("negative", -1))
            self.assertFalse(rejected.committed)
            self.assertIs(prepared[-1].state, prepared[-1].source.state)
            self.assertIs(prepared[-1].artifacts, artifacts)
        before = operation._published
        # A valid transition for a previous receipt history must not publish now.
        with patch.object(enabled, "prepare_enabled", return_value=prepared[1]):
            with self.assertRaisesRegex(ValueError, "differs from branch source"):
                model.expand(request("A_PC"))
        self.assertIs(operation._published, before)
        transition = prepared[3]
        with self.assertRaisesRegex(ValueError, "discarded retained"):
            replace(transition, artifacts=events.GRC9V4EventArtifacts())
        checkpoint = model.snapshot()
        self.assertEqual(GRC9V4.from_state(checkpoint).snapshot(), checkpoint)
        EVIDENCE["branch_ownership"] = dict(
            immutable_enabled_branch=True,
            sole_receipt_ledger=True,
            complete_artifact_bundle=True,
            no_nested_enabled_owner=True,
            stale_transition_rejected=True,
            artifact_loss_rejected=True,
            mixed_replay_equal=True,
        )

    def test_accepted_crossing_checkpoints_replay_unchanged(self):
        rows = []
        for family in FAMILIES:
            record = json.loads(
                (
                    ROOT
                    / f"implementation/phase-9-grcv4/tranche-9/P9-9.4a-{family}.json"
                ).read_bytes()
            )
            checkpoint = record["evidence"]["roundtrip"]["final_checkpoint"]
            raw = crossing._bytes(checkpoint)
            owner = crossing.GRC9V4BranchOperation.from_state(raw)
            self.assertEqual(owner.snapshot(), raw)
            self.assertIs(type(owner._published.owner), enabled.GRC9V4EnabledBranch)
            rows.append(family)
        EVIDENCE["accepted_crossing_replay"] = dict(
            families=rows,
            checkpoint_bytes_equal=True,
            historical_execution_unchanged=True,
        )


if __name__ == "__main__":
    unittest.main()
