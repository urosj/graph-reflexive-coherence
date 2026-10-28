"""Native public transaction owner; no family-specific public facade subclasses."""

from dataclasses import replace
import json

from .grc_v4 import (
    GRCV4StepRequestInput,
    GRCV4MigrationRequest,
)
from .grc_v4_codec import canonical_json_bytes, payload_identity
from .grc_v4_state import FrozenJSONMap, GRCV4LifecycleResult, GRCV4StepResult
from .grc_v4_geometry import GRCV4ReferenceGeometry
from .grc_v4_exact import exact_backend
from .grc_v4_certification import numerical_policy
from .grc_v4_migration import map_migration, history_digest
from .grc_v4_step import make_commit_receipts
from . import grc_9_v4_crossing as branch
from .grc_9_v4_crossing import GRC9V4BranchRequest
from .grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from .grc_9_v4_topology import (
    GRC9V4PostbeatRows,
    GRC9V4PortField,
    coarse_grain_columns,
)
from .grc_9_v4_lifecycle import GRC9V4CandidateDetection, GRC9SparkPolicy

from .grc_9_v4_contracts import (
    GRC9V4Configuration,
    GRC9V4ExecutionOptions,
    GRC9V4ExecutionUnavailable,
    EnabledGRC9V4State,
    DisabledGRC9V3State,
    describe_family,
)
from .grc_v4_state import GRCV4ResetBaseline

# Public execution selection is independent of available native implementations.
# Contract recognition and conformance acceptance are separate again.
PUBLIC_ENABLED_FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")

native_bytes = branch._bytes


def _decode(raw):
    def unique(items):
        value = {}
        for k, v in items:
            if k in value:
                raise ValueError("duplicate checkpoint key")
            value[k] = v
        return value

    value = json.loads(raw, object_pairs_hook=unique)
    branch._bytes(value)  # Finite native JSON, preserving legacy signed zero.
    return value


class GRC9V4PublicOperation(branch.GRC9V4BranchOperation):
    """Extend the accepted transaction receiver without changing old snapshots."""

    @staticmethod
    def execution_scope():
        if not set(PUBLIC_ENABLED_FAMILIES) <= set(branch.enabled._OWNERS):
            raise RuntimeError("selected public execution has no native implementation")
        return PUBLIC_ENABLED_FAMILIES

    @classmethod
    def require_execution(cls, family):
        describe_family(family)
        if family not in cls.execution_scope():
            raise GRC9V4ExecutionUnavailable(family, cls.execution_scope())

    @classmethod
    def create(cls, initial, execution):
        cls.require_execution(initial.FAMILY)
        with (
            exact_backend(execution.exact_backend),
            numerical_policy(execution.numerical_policy),
        ):
            return cls(branch.enabled.GRC9V4EnabledOperation(initial))

    @classmethod
    def decode_native(cls, payload, execution):
        family = payload["inputs"]["reference"]["profile"]["identity_payload"][
            "profile_family_id"
        ]
        cls.require_execution(family)
        with (
            exact_backend(execution.exact_backend),
            numerical_policy(execution.numerical_policy),
        ):
            return branch.enabled._decode_state(payload, family)

    @classmethod
    def from_configuration(cls, configuration):
        if type(configuration) is not GRC9V4Configuration:
            raise TypeError("typed public configuration required")
        family = configuration.family.profile_family_id
        # Contract validation is available for all ten. Check runtime scope
        # before any admission/kernel invocation for the other six.
        cls.require_execution(family)
        from .grc_v4_geometry import GeometryStageInputs

        ref = configuration.reference
        execution = configuration.execution
        with (
            exact_backend(execution.exact_backend),
            numerical_policy(execution.numerical_policy),
        ):
            inputs = GeometryStageInputs(
                ref.geometry(),
                ref.context,
                configuration.current,
                configuration.reset,
                "public-construction",
                configuration.budget_target,
                (),
                configuration.step_index,
                configuration.time,
                0.0,
                "pre_read",
                0,
                None,
            )
            inputs = branch.generic._fresh_geometry(inputs)
            native = branch.enabled._OWNERS[family].STATE(
                inputs, configuration.specialization
            )
            return cls.create(native, execution)

    @property
    def reference(self):
        return self._published.reference

    @property
    def specialization(self):
        return self._published.specialization

    @property
    def active_model_identity(self):
        return self._endpoints(self._published)["model_identity"]

    @property
    def numerical_policy(self):
        return self._policy

    def parameters(self):
        p = self._published
        return dict(
            profile=p.reference.profile.params_resolved.to_payload(),
            specialization=p.specialization.resolved.to_dict(),
            compatibility_branch=p.branch,
            exact_backend=self._backend.value,
            numerical_policy=self._policy.value,
            legacy_parameters=None
            if p.branch == "enabled_v4"
            else p.owner.snapshot()["metadata"]["resolved_params"],
        )

    def configuration(self, targets=()):
        p = self._published
        if p.branch != "enabled_v4":
            raise ValueError(
                "disabled branch has an exact legacy configuration; use get_params() or snapshot()"
            )
        inputs = p.owner.state.inputs
        return GRC9V4Configuration(
            p.reference,
            p.specialization,
            inputs.current,
            inputs.reset,
            inputs.Q_target,
            GRC9V4ExecutionOptions(self._backend, self._policy),
            inputs.step_index,
            inputs.time,
            targets,
        )

    def scientific_state(self):
        p = self._published
        endpoints = self._endpoints(p)
        clock = self._clock(p)
        if p.branch == "disabled_grc9v3":
            return DisabledGRC9V3State(
                native_bytes(p.owner.snapshot()),
                branch.TARGET_VERSION,
                p.entry_receipt,
                *clock,
                p.owner.get_state().budget_target,
                endpoints["model_identity"],
                endpoints["state_digest"],
                self.lifecycle_digest,
                p.receipts,
            )
        state = p.owner.state
        inputs = state.inputs
        ref = p.reference
        reset = GRCV4ResetBaseline(
            inputs.reset,
            ref.graph.graph_digest,
            ref.graph.orientation_identity,
            state.model_identity,
            inputs.context.contract_id,
            inputs.Q_target,
            state.reset_digest,
        )
        return EnabledGRC9V4State(
            ref.graph.port_graph,
            ref.profile,
            p.specialization,
            inputs.current,
            reset,
            *clock,
            inputs.Q_target,
            state.model_identity,
            state.scientific_digest,
            self.lifecycle_digest,
            p.receipts,
        )

    def legacy_capabilities(self):
        if self.branch != "disabled_grc9v3":
            raise ValueError("not the disabled branch")
        return set(self._published.owner._delegate.list_capabilities())

    def migrate_profile(self, request, target):
        with self._lock:
            if target is None:
                return self._failure(
                    self._published,
                    request.operation_id,
                    "admission",
                    "unsupported_profile",
                    "target is not registered for this graph",
                )
            self.require_execution(target.profile.identity_payload.profile_family_id)
            return self.profile_migrate(request, target)

    def migrate(self, request):
        if type(request) is not GRC9V4BranchRequest:
            raise TypeError("typed crossing request required")
        if request.direction == "enable":
            profile = request.declaration["target_reference"]["profile"][
                "identity_payload"
            ]
            self.require_execution(profile["profile_family_id"])
        return super().migrate(request)

    def _enabled_action(self, kind, request=None):
        with self._lock, exact_backend(self._backend), numerical_policy(self._policy):
            before = self._published
            transition = self._prepare_enabled(before, kind, request)
            result = transition.result
            if not result.committed:
                return result
            after = self._enabled_target(before, transition)
            action = dict(
                kind={
                    "step": "enabled_step",
                    "expand": "expand",
                    "rebase": "enabled_rebase",
                    "reset": "enabled_reset",
                }[kind]
            )
            if request is not None:
                action["request"] = request.to_payload()
            if kind == "step":
                payload = result.to_payload()
                payload["observables"].update(
                    self.observables(after, postbeat=request.dt > 0)
                )
                # Preserve selected current/solver provenance in the step result.
                for key in ("authoritative_current", "stage", "solver_disposition"):
                    payload["observables"][key] = result.observables[key]
                result = GRCV4StepResult.from_payload(payload)
            self._publish(before, after, result.emitted_receipts, action)
            return result

    def step_enabled(self, request):
        return self._enabled_action("step", request)

    def expand(self, request):
        return self._enabled_action("expand", request)

    def reset_enabled(self):
        return self._enabled_action("reset")

    def rebase_enabled(self):
        return self._enabled_action("rebase")

    def rebase_legacy(self, operation_id):
        with self._lock:
            before = self._published
            if before.branch != "disabled_grc9v3":
                raise ValueError("legacy rebase on enabled branch")
            owner = before.owner.duplicate()
            owner.rebase_reset_baseline()
            after = replace(before, owner=owner)
            rows = [
                r.identity_payload.to_dict()
                for r in self._receipts(before, after, operation_id, "step")
            ]
            core = rows[0]["core"]
            rows[0] = dict(
                schema_version="grcv4-rebase-receipt-v1",
                core=core,
                old_reset_digest=self._endpoints(before)["reset_digest"],
                new_reset_digest=self._endpoints(after)["reset_digest"],
            )
            _, emitted = make_commit_receipts(
                rows,
                operation_id=operation_id,
                source_state_digest=core["source_state_digest"],
                target_state_digest=core["target_state_digest"],
                target_step_index=self._clock(after)[0],
                target_time=self._clock(after)[1],
            )
            self._publish(
                before,
                after,
                emitted,
                dict(kind="legacy_rebase", operation_id=operation_id),
            )
            return GRCV4LifecycleResult(
                "committed", True, emitted[0].commit_id, None, emitted
            )

    def profile_migrate(self, request, target):
        self.require_execution(target.profile.identity_payload.profile_family_id)
        if type(request) is not GRCV4MigrationRequest:
            raise TypeError("typed profile migration required")
        with self._lock, exact_backend(self._backend), numerical_policy(self._policy):
            before = self._published
            if before.branch != "enabled_v4":
                return self._failure(
                    before,
                    request.operation_id,
                    "admission",
                    "invalid_migration",
                    "use explicit branch return",
                )
            try:
                state = before.owner.state
                inputs = state.inputs
                if (
                    request.source_state_digest != state.scientific_digest
                    or request.target_profile_id != target.profile.complete_profile_id
                ):
                    raise ValueError("migration identity mismatch")
                if request.target_context_value:
                    raise ValueError("constant-zero context required")
                if (
                    inputs.current.W_A is None
                    and target.profile.identity_payload.candidate == "A"
                ):
                    raise ValueError(
                        "C-to-A requires the explicit native initialization stage via branch entry/return; generic WLS is not a fixed-row initializer"
                    )
                following = map_migration(inputs, target, request.history_policy)
                following = branch.generic._fresh_geometry(
                    replace(following, operation_id=request.operation_id, dt=0)
                )
                native = branch.enabled._OWNERS[
                    target.profile.identity_payload.profile_family_id
                ].STATE(following, before.specialization)
                owner = branch.enabled.GRC9V4EnabledBranch.admit(native)
            except ValueError as exc:
                return self._failure(
                    before,
                    request.operation_id,
                    "target_readmission",
                    "target_readmission_failure",
                    exc,
                )
            after = replace(before, owner=owner, reference=target)
            bundle = request.history_policy.to_payload()
            histories = {}
            losses = []
            for subject in ("candidate", "carrier"):
                channel = bundle[subject]
                histories[subject] = dict(
                    subject=subject,
                    disposition=channel["disposition"],
                    source_history_digest=history_digest(inputs, subject),
                    target_history_digest=history_digest(following, subject),
                    information_loss=channel["information_loss"],
                )
                if channel["information_loss"] != "none":
                    losses.append(channel["information_loss"])
            _, refs = branch.generic._receipt_context(before.reference)
            refs["history_bundle_digest"] = payload_identity(
                "history_bundle_identity_payload",
                dict(
                    schema_version="grcv4-history-bundle-identity-v1",
                    history_bundle=bundle,
                ),
            )
            core = dict(
                operation_id=request.operation_id,
                **refs,
                actual_charge_delta=0.0,
                information_losses=losses,
                disposition="committed",
                parent_receipt_ids=[]
                if not before.receipts
                else [branch.generic._previous_primary(before.receipts)],
            )
            for role, p in [("source", before), ("target", after)]:
                core.update({role + "_" + k: v for k, v in self._endpoints(p).items()})
            rows = [
                dict(
                    schema_version="grcv4-profile-migration-receipt-v1",
                    core=core,
                    history=dict(
                        schema_version="grcv4-history-bundle-receipt-v1", **histories
                    ),
                )
            ]
            rows.extend(
                dict(
                    schema_version="grcv4-history-disposition-receipt-v1",
                    core=core,
                    subject=s,
                    history_disposition=histories[s]["disposition"],
                    information_loss=histories[s]["information_loss"],
                )
                for s in histories
            )
            _, emitted = make_commit_receipts(
                rows,
                operation_id=request.operation_id,
                source_state_digest=state.scientific_digest,
                target_state_digest=native.scientific_digest,
                target_step_index=following.step_index,
                target_time=following.time,
            )
            if losses:
                after = replace(
                    after,
                    artifacts=replace(
                        after.artifacts,
                        archives=after.archives
                        + (
                            FrozenJSONMap(
                                dict(
                                    kind="profile_history_loss",
                                    source_state_digest=state.scientific_digest,
                                    authoritative=state.scientific_payload[
                                        "authoritative"
                                    ],
                                    reset=inputs.to_payload()["reset"],
                                )
                            ),
                        ),
                    ),
                )
            self._publish(
                before,
                after,
                emitted,
                dict(
                    kind="profile_migration",
                    request=request.to_payload(),
                    target_reference=target.to_payload(),
                ),
            )
            return GRCV4LifecycleResult(
                "committed", True, emitted[0].commit_id, None, emitted
            )

    def observables(self, p=None, *, postbeat=False):
        p = self._published if p is None else p
        if p.branch == "disabled_grc9v3":
            return p.owner.compute_observables()
        with exact_backend(self._backend), numerical_policy(self._policy):
            state = p.owner.state
            inputs = state.inputs
            ref = p.reference
            current, charge = branch.generic._readmit_state(
                inputs, branch.enabled._backend(state)
            )
            values = tuple(current.current.values)
            result = branch.generic._public_observables(
                inputs,
                p.receipts,
                charge,
                current,
                stage="read_only_reference",
                current_stage="read_only_reference",
                solver=None,
                consumed=False,
            )
            rows = GRC9V4PostbeatRows(
                ref.graph.port_graph,
                ref.profile,
                inputs.current,
                values,
                inputs.step_index,
                p.specialization.identity_payload["hessian_sign"],
            )
            summaries = rows.evaluate()
            graph = ref.graph.port_graph
            occupied = {v: [] for v in graph.live_node_ids}
            for e in graph.edges:
                occupied[e.tail.node_id].append(e.tail.port)
                occupied[e.head.node_id].append(e.head.port)
            fine = GRC9V4PortField.from_edge_values(graph, "nonnegative", rows.weights)
            coarse = coarse_grain_columns(fine, field_family="nonnegative")
            # Exact derived ratios serialize as strings, never rounded authority.
            columns = [
                [
                    dict(total=str(col.total), profile=[str(x) for x in col.profile])
                    for col in row
                ]
                for row in coarse.columns
            ]
            detection = GRC9V4CandidateDetection(
                rows, GRC9SparkPolicy.from_payload(p.specialization.resolved["spark"])
            )
            result.update(
                active_model_identity=state.model_identity,
                compatibility_branch=p.branch,
                grc9v3_target_version=branch.TARGET_VERSION,
                active_port_degree=[len(occupied[v]) for v in graph.live_node_ids],
                port_occupancy=[sorted(occupied[v]) for v in graph.live_node_ids],
                row_gradient=[list(r.gradient) for r in summaries],
                signed_row_hessian=[
                    list(r.signed_hessian[i][i] for i in range(3)) for r in summaries
                ],
                row_net_flux=[list(r.net_flux) for r in summaries],
                hybrid_spark_candidates=list(detection.candidate_node_ids())
                if postbeat
                else None,
                candidate_stage="fresh_postbeat_candidate_detection"
                if postbeat
                else "unavailable_without_ordinary_postbeat",
                mechanical_expansions=sum(
                    r.identity_payload["schema_version"]
                    == "grcv4-topology-event-receipt-v1"
                    for r in p.receipts
                ),
                coarse_columns=columns,
                coarse_profiles=dict(
                    field="native_row_weights", arithmetic="exact_rational_strings"
                ),
                support_status="bounded_local_GRC9V4_API_pending_P9_9_6_not_full_conformance",
            )
            return FrozenJSONMap(result).to_dict()

    def snapshot(self):
        value = json.loads(super().snapshot())
        value["descriptor_version"] = "grc9v4-public-owner-v1"
        return branch._bytes(value)

    @classmethod
    def from_state(cls, raw):
        data = _decode(raw)
        self_family = data["initial"]["family"]
        cls.require_execution(self_family)
        if data.get("descriptor_version") != "grc9v4-public-owner-v1":
            raise ValueError("unsupported public owner checkpoint")
        owner = cls(
            branch.enabled.GRC9V4EnabledOperation.from_state(
                canonical_json_bytes(data["initial"])
            )
        )
        for action in data["journal"]:
            kind = action.get("kind")
            if kind == "migrate" and set(action) == {"kind", "request"}:
                result = owner.migrate(
                    GRC9V4BranchRequest.from_payload(action["request"])
                )
            elif kind == "enabled_step" and set(action) == {"kind", "request"}:
                result = owner.step_enabled(
                    GRCV4StepRequestInput.from_payload(action["request"])
                )
            elif kind == "expand" and set(action) == {"kind", "request"}:
                result = owner.expand(
                    GRC9V4ExpansionRequestInput.from_payload(action["request"])
                )
            elif kind == "enabled_reset" and set(action) == {"kind"}:
                result = owner.reset_enabled()
            elif kind == "enabled_rebase" and set(action) == {"kind"}:
                result = owner.rebase_enabled()
            elif kind == "legacy_rebase" and set(action) == {"kind", "operation_id"}:
                result = owner.rebase_legacy(action["operation_id"])
            elif kind in ("legacy_step", "legacy_reset") and set(action) == {
                "kind",
                "operation_id",
            }:
                result = owner.legacy_operation(action["operation_id"], kind[7:])
            elif kind == "profile_migration" and set(action) == {
                "kind",
                "request",
                "target_reference",
            }:
                result = owner.profile_migrate(
                    GRCV4MigrationRequest.from_payload(action["request"]),
                    GRCV4ReferenceGeometry.from_payload(action["target_reference"]),
                )
            else:
                raise ValueError("unknown public owner journal action")
            if hasattr(result, "committed") and not result.committed:
                raise ValueError("public journal failed replay")
        if owner.snapshot() != branch._bytes(data):
            raise ValueError("public owner replay mismatch")
        return owner
