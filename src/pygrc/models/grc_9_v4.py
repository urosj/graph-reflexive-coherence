"""Public GRC9V4 interface for all ten declared candidate/realization families.

Contract discovery and configuration are independent of native execution scope.
This facade delegates admission, numerics and atomic publication to its owner.
"""

from collections.abc import Mapping
from pathlib import Path
from threading import RLock

from .grc_v4 import (
    GRCV4,
    GRCV4StepRequest,
    GRCV4StepRequestInput,
    GRCV4MigrationRequest,
    MissingV4StepRequest,
)
from .grc_v4_state import FrozenJSONMap
from .grc_v4_geometry import GRCV4ReferenceGeometry
from .grc_v4_codec import payload_identity
from .grc_9_v4_crossing import GRC9V4BranchRequest
from .grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from .grc_9_v4_api_lifecycle import GRC9V4PublicOperation, _decode, native_bytes
from .grc_9_v4_contracts import (
    GRC9V4Configuration,
    GRC9V4ExecutionOptions,
    GRC9V4ExecutionUnavailable,
    GRC9V4Family,
    GRC9V4State,
    EnabledGRC9V4State,
    DisabledGRC9V3State,
    describe_families,
    describe_family,
    target_references,
)

__all__ = [
    "GRC9V4",
    "GRC9V4Configuration",
    "GRC9V4ExecutionOptions",
    "GRC9V4ExecutionUnavailable",
    "GRC9V4Family",
    "GRC9V4State",
    "EnabledGRC9V4State",
    "DisabledGRC9V3State",
    "GRC9V4BranchRequest",
    "GRC9V4ExpansionRequestInput",
    "describe_families",
    "describe_family",
]
_LAYOUT = "grc9v4-public-checkpoint-v1"


class GRC9V4(GRCV4):
    """Shared lifecycle with typed A/C and realization-specific declarations.

    Prefer GRC9V4Configuration. The low-level native payload constructor is
    retained for existing serialized inputs; execution limits remain explicit.
    """

    __slots__ = ("_targets", "_lock")

    def __init__(
        self,
        initial,
        *,
        exact_backend_choice=None,
        numerical_policy_choice=None,
        targets=(),
    ):
        if type(initial) is GRC9V4Configuration:
            if (
                exact_backend_choice is not None
                or numerical_policy_choice is not None
                or targets
            ):
                raise ValueError("configuration owns execution options and targets")
            self._operation = GRC9V4PublicOperation.from_configuration(initial)
            targets = initial.targets
        else:
            self._operation = GRC9V4PublicOperation.create(
                initial,
                GRC9V4ExecutionOptions(exact_backend_choice, numerical_policy_choice),
            )
        self._targets = target_references(targets, self._operation.reference.graph)
        self._lock = RLock()

    @classmethod
    def from_config(cls, config):
        if type(config) is GRC9V4Configuration:
            return cls(config)
        if (
            isinstance(config, Mapping)
            and config.get("schema_version") == "grc9v4-configuration-v1"
        ):
            return cls(GRC9V4Configuration.from_payload(dict(config)))
        if (
            not isinstance(config, Mapping)
            or set(config) - {"initial", "targets", "exact_backend", "numerical_policy"}
            or not {"initial", "exact_backend", "numerical_policy"} <= set(config)
        ):
            raise ValueError("closed explicit native configuration required")
        if type(config.get("targets", [])) is not list:
            raise ValueError("ordered targets required")
        execution = GRC9V4ExecutionOptions(
            config["exact_backend"], config["numerical_policy"]
        )
        initial = GRC9V4PublicOperation.decode_native(config["initial"], execution)
        return cls(
            initial,
            exact_backend_choice=execution.exact_backend,
            numerical_policy_choice=execution.numerical_policy,
            targets=tuple(
                GRCV4ReferenceGeometry.from_payload(t)
                for t in config.get("targets", [])
            ),
        )

    @staticmethod
    def describe_families():
        return describe_families()

    @staticmethod
    def describe_family(profile_family_id):
        return describe_family(profile_family_id)

    @staticmethod
    def execution_scope():
        return GRC9V4PublicOperation.execution_scope()

    @property
    def compatibility_branch(self):
        return self._operation.branch

    @property
    def active_profile_id(self):
        return self._operation.reference.profile.complete_profile_id

    @property
    def active_model_identity(self):
        return self._operation.active_model_identity

    @property
    def lifecycle_digest(self):
        return self._operation.lifecycle_digest

    @property
    def receipt_ledger(self):
        return self._operation.receipts

    @property
    def numerical_policy(self):
        return self._operation.numerical_policy

    def _params(self):
        return self._operation.parameters()

    def get_params(self):
        with self._lock:
            return FrozenJSONMap(self._params())

    @property
    def configuration(self):
        """Current typed construction inputs; use snapshot() to retain lineage."""
        with self._lock:
            return self._operation.configuration(self._targets)

    @property
    def state(self):
        with self._lock:
            return GRC9V4State(
                self._operation.scientific_state(), native_bytes(self.snapshot())
            )

    def get_state(self):
        return self.state

    def set_state(self, state):
        if type(state) is not GRC9V4State:
            raise TypeError("complete immutable GRC9V4State required")
        with self._lock:
            restored = type(self).from_state(
                _decode(state.checkpoint), self.get_params()
            )
            if restored.state != state or restored._targets != self._targets:
                raise ValueError("state metadata/configuration mismatch")
            self._operation = restored._operation

    def snapshot(self):
        with self._lock:
            return dict(
                descriptor_version=_LAYOUT,
                owner=_decode(self._operation.snapshot()),
                targets=[t.to_payload() for t in self._targets],
                params=self._params(),
            )

    @classmethod
    def from_state(cls, state, params=None):
        declared_state = state if type(state) is GRC9V4State else None
        if isinstance(state, GRC9V4State):
            state = _decode(state.checkpoint)
        if (
            not isinstance(state, Mapping)
            or set(state) != {"descriptor_version", "owner", "targets", "params"}
            or state["descriptor_version"] != _LAYOUT
        ):
            raise ValueError("closed public checkpoint required")
        result = cls.__new__(cls)
        result._lock = RLock()
        result._operation = GRC9V4PublicOperation.from_state(
            native_bytes(state["owner"])
        )
        if type(state["targets"]) is not list:
            raise ValueError("ordered target registry required")
        original = GRCV4ReferenceGeometry.from_payload(
            state["owner"]["initial"]["initial"]["inputs"]["reference"]
        )
        result._targets = target_references(
            (GRCV4ReferenceGeometry.from_payload(t) for t in state["targets"]),
            original.graph,
        )
        expected = result._params()
        provided = params.to_dict() if type(params) is FrozenJSONMap else params
        if native_bytes(expected) != native_bytes(state["params"]) or (
            provided is not None and native_bytes(expected) != native_bytes(provided)
        ):
            raise ValueError("snapshot parameters differ from admitted model")
        if native_bytes(result.snapshot()) != native_bytes(state):
            raise ValueError("public snapshot mismatch")
        if declared_state is not None and result.state != declared_state:
            raise ValueError("state metadata differs from replay")
        return result

    def save(self, path):
        Path(path).write_bytes(native_bytes(self.snapshot()))

    @classmethod
    def load(cls, path):
        return cls.from_state(_decode(Path(path).read_bytes()))

    def duplicate(self):
        return type(self).from_state(self.snapshot())

    def step_v4_input(self, request):
        if type(request) is not GRCV4StepRequestInput:
            raise TypeError("typed step input required")
        with self._lock:
            if self.compatibility_branch != "enabled_v4":
                raise ValueError(
                    "disabled branch uses native step(); V4 dt/context cannot be silently discarded"
                )
            return self._operation.step_enabled(request)

    def step(self):
        with self._lock:
            if self.compatibility_branch == "disabled_grc9v3":
                return self._operation.legacy_operation(
                    "legacy-step:" + self.lifecycle_digest
                )
            default = self._operation.reference.profile.params_resolved.common.default_step_request
            if default is None:
                raise MissingV4StepRequest(
                    "active profile has no serialized default_step_request"
                )
            return self.step_v4(GRCV4StepRequest.from_payload(default))

    def reset(self):
        with self._lock:
            return (
                self._operation.reset_enabled()
                if self.compatibility_branch == "enabled_v4"
                else self._operation.legacy_operation(
                    "legacy-reset:" + self.lifecycle_digest, "reset"
                )
            )

    def rebase_reset_baseline(self):
        with self._lock:
            return (
                self._operation.rebase_enabled()
                if self.compatibility_branch == "enabled_v4"
                else self._operation.rebase_legacy(
                    "legacy-rebase:" + self.lifecycle_digest
                )
            )

    def migrate_branch(self, request):
        with self._lock:
            return self._operation.migrate(request)

    def migrate_profile(self, request):
        if type(request) is not GRCV4MigrationRequest:
            raise TypeError("typed profile migration required")
        with self._lock:
            target = next(
                (
                    r
                    for r in (*self._targets, self._operation.reference)
                    if r.profile.complete_profile_id == request.target_profile_id
                    and r.graph == self._operation.reference.graph
                ),
                None,
            )
            return self._operation.migrate_profile(request, target)

    def expand(self, request):
        if type(request) is not GRC9V4ExpansionRequestInput:
            raise TypeError("typed canonical nine-port expansion required")
        with self._lock:
            return self._operation.expand(request)

    def apply_topology_event(self, request):
        return self.expand(request)

    def reconstruct_topology_event(self, request):
        raise ValueError(
            "generic mapped-event replay is not a canonical GRC9V4 expansion; restore the public checkpoint"
        )

    def transport_representation(self, request):
        raise ValueError(
            "generic representation transport cannot replace the fixed port chart"
        )

    def compute_observables(self):
        with self._lock:
            return self._operation.observables()

    def _references(self):
        reference = self._operation.reference
        return {
            t.profile.complete_profile_id: t
            for t in (*self._targets, reference)
            if t.graph == reference.graph
            and t.profile.identity_payload.profile_family_id in self.execution_scope()
        }

    def list_declared_profiles(self):
        """All registered declarations on this graph, including unavailable families."""
        with self._lock:
            ref = self._operation.reference
            return tuple(
                r.profile
                for r in (*self._targets, ref)
                if r.graph == ref.graph
                and (
                    r is ref
                    or r.profile.complete_profile_id != ref.profile.complete_profile_id
                )
            )

    def list_supported_profiles(self):
        with self._lock:
            return frozenset(self._references())

    def get_supported_profile(self, complete_profile_id):
        with self._lock:
            return self._references()[complete_profile_id].profile

    def list_supported_model_identities(self):
        with self._lock:
            return frozenset(
                payload_identity(
                    "complete_model_identity_payload",
                    dict(
                        schema_version="grc9v4-complete-identity-v1",
                        grcv4_complete_profile_id=r.profile.complete_profile_id,
                        specialization_id=self._operation.specialization.specialization_id,
                    ),
                )
                for r in self._references().values()
            )

    def list_capabilities(self):
        if self.compatibility_branch == "disabled_grc9v3":
            return self._operation.legacy_capabilities()
        identity = self._operation.reference.profile.identity_payload
        return {
            "profile_explicit_v4",
            "single_resource_ledger",
            "authoritative_current",
            "structural_hodge_geometry",
            "quadrature_budget",
            "port_graph",
            "mechanical_refinement",
            "column_coarse_graining",
            "intrinsic_frame",
            "profile_migration",
            "explicit_branch_migration",
            "v4_candidate_a_retained_history"
            if identity.candidate == "A"
            else "v4_candidate_c_derived_sector",
            "v4_realization_" + identity.realization.lower().replace("+", "_"),
        }

    def support_status(self):
        return dict(
            disposition="bounded_local_api_pending_P9_9_6",
            declared_families=[f.profile_family_id for f in describe_families()],
            execution_families=list(self.execution_scope()),
            contract_coverage="all_ten_families",
            complete_profile_ids=sorted(self.list_supported_profiles()),
            model_identities=sorted(self.list_supported_model_identities()),
            compatibility_branch=self.compatibility_branch,
            full_GRC9V4_conformance=False,
            optional_completion=False,
            same_graph_crossings_only=True,
            direct_C_to_A="requires_explicit_native_stage_via_branch_crossing",
        )
